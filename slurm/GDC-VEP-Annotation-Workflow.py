'''
Main wrapper script for staging a VEP run.
'''
import os
import time
import argparse
import logging
import sys
import uuid
import tempfile
import utils.s3
import utils.pipeline
import datetime

import postgres.status
import postgres.utils
import postgres.time
from sqlalchemy.exc import NoSuchTableError

def run_stage_cache(args):
    '''
    Pulls the VEP cache files from s3
    '''
    # Time
    start = time.time()

    # Setup logger
    logger = utils.pipeline.setup_logging(logging.INFO, 'VEPstage', args.log_file)

    # Pull down files
    logger.info('Downloading cache files...')
    if args.cache_s3bin.startswith("s3://ceph_"):
        s3_exit_code = utils.s3.aws_s3_get(logger, args.cache_s3bin, args.output_directory,
                                        "ceph", "http://gdc-cephb-objstore.osdc.io/")
    else:
        s3_exit_code = utils.s3.aws_s3_get(logger, args.cache_s3bin, args.output_directory,
                                        "cleversafe", "http://gdc-accessors.osdc.io/")
    if s3_exit_code != 0: return s3_exit_code

    # Change dir 
    os.chdir(args.output_directory)

    # Unzipping files
    custom_tar = os.path.join(args.output_directory, 'custom.tar.gz')
    logger.info('Decompressing {0}...'.format(custom_tar))
    custom_tar_exit_code = utils.pipeline.targz_decompress(logger, custom_tar)
    if custom_tar_exit_code != 0: return custom_tar_exit_code

    fasta_tar = os.path.join(args.output_directory, 'vep_fasta.tar.gz')
    logger.info('Decompressing {0}...'.format(fasta_tar))
    fasta_tar_exit_code = utils.pipeline.targz_decompress(logger, fasta_tar)
    if fasta_tar_exit_code != 0: return fasta_tar_exit_code

    cache_tar = os.path.join(args.output_directory, 'homo_sapiens.tar.gz')
    logger.info('Decompressing {0}...'.format(cache_tar))
    cache_tar_exit_code = utils.pipeline.targz_decompress(logger, cache_tar)
    if cache_tar_exit_code != 0: return cache_tar_exit_code

    # Clean up
    logger.info("Cleaning up tar archives...")
    os.remove(custom_tar)
    os.remove(fasta_tar)
    os.remove(cache_tar)

    # Completed
    logger.info("Completed VEP cache staging.")
    logger.info("Took {0:.4f} minutes.".format((time.time() - start) / 60.0))
    return 0

def run_build_slurm_scripts(args):
    '''
    Builds the slurm scripts to run VEP
    '''
    # Time
    start = time.time()

    # Check paths
    if not os.path.isdir(args.outdir):
        raise Exception("Cannot find output directory: %s" %args.outdir)

    if not os.path.isfile(args.config):
        raise Exception("Cannot find config file: %s" %args.config)

    # Setup logger
    logger = utils.pipeline.setup_logging(logging.INFO, 'VEPslurm', args.log_file)

    # Load template
    template_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'etc/template.sh')
    template_str  = None
    with open(template_file, 'r') as fh:
        template_str = fh.read()
 
    # Database setup
    engine = postgres.utils.get_db_engine(args.config)

    try:
        cases = postgres.status.get_vep_inputs_from_status(engine, 'vep_cwl_status')
        write_slurm_script(cases, args, template_str)
    except NoSuchTableError:
        cases = postgres.status.get_all_vep_inputs(engine)
        write_slurm_script(cases, args, template_str)

def write_slurm_script(cases, args, template_str):
    '''
    Writes the actual slurm script file
    '''
    for case in cases:
        dat   = cases[case]
        if all([dat.src_vcf_id, dat.src_vcf_location, dat.case_id,
           dat.patient_barcode, dat.tumor_barcode, dat.tumor_aliquot_id,
           dat.tumor_bam_gdcid, dat.normal_barcode, dat.normal_aliquot_id,
           dat.normal_bam_gdcid, dat.objectstore, 
           dat.workflow_id_01, dat.workflow_name_01, dat.workflow_description_01, dat.workflow_version_01,
           dat.workflow_id_02, dat.workflow_name_02, dat.workflow_description_02, dat.workflow_version_02]):

            slurm = os.path.join(args.outdir, 'vep_cwl.{0}.sh'.format(dat.src_vcf_id))
            val   = template_str.format(
                THREAD_COUNT                    = args.thread_count,
                MEM                             = args.mem,
                SRC_VCF_ID                      = dat.src_vcf_id,
                INPUT_VCF                       = dat.src_vcf_location,
                OBJECT_STORE                    = dat.objectstore,
                CASE_ID                         = dat.case_id,
                PATIENT_BARCODE                 = dat.patient_barcode,
                TUMOR_BARCODE                   = dat.tumor_barcode,
                TUMOR_ALIQUOT_UUID              = dat.tumor_aliquot_id,
                TUMOR_BAM_UUID                  = dat.tumor_bam_gdcid,
                NORMAL_BARCODE                  = dat.normal_barcode,
                NORMAL_ALIQUOT_UUID             = dat.normal_aliquot_id,
                NORMAL_BAM_UUID                 = dat.normal_bam_gdcid,
                REFDIR                          = args.refdir,
                S3DIR                           = args.s3dir,
                BASEDIR                         = args.run_basedir,
                CALLER_WORKFLOW_ID              = dat.workflow_id_01,
                CALLER_WORKFLOW_NAME            = dat.workflow_name_01,
                CALLER_WORKFLOW_DESCRIPTION     = dat.workflow_description_01,
                CALLER_WORKFLOW_VERSION         = dat.workflow_version_01,
                ANNOTATION_WORKFLOW_ID          = dat.workflow_id_02,
                ANNOTATION_WORKFLOW_NAME        = dat.workflow_name_02,
                ANNOTATION_WORKFLOW_DESCRIPTION = dat.workflow_description_02,
                ANNOTATION_WORKFLOW_VERSION     = dat.workflow_version_02
            )

            with open(slurm, 'w') as o:
                o.write(val)

def run_cwl(args):
    '''
    Executes the CWL pipeline and adds status table
    '''
    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)

    #generate a random uuid
    vcf_uuid = uuid.uuid4()

    #create directory structure
    uniqdir = tempfile.mkdtemp(prefix="vep_%s_" % str(vcf_uuid), dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=uniqdir)
    inp     = tempfile.mkdtemp(prefix="input_", dir=uniqdir)
    index   = args.refdir

    #setup logger
    log_file = os.path.join(workdir, "%s.vep.cwl.log" %str(vcf_uuid))
    logger = utils.pipeline.setup_logging(logging.INFO, str(vcf_uuid), log_file)

    #logging inputs
    logger.info("normal_barcode: %s" %(args.normal_barcode))
    logger.info("normal_aliquot_uuid: %s" %(args.normal_aliquot_uuid))
    logger.info("normal_bam_uuid: %s" %(args.normal_bam_uuid))
    logger.info("tumor_barcode: %s" %(args.tumor_barcode))
    logger.info("tumor_aliquot_uuid: %s" %(args.tumor_aliquot_uuid))
    logger.info("tumor_bam_uuid: %s" %(args.tumor_bam_uuid))
    logger.info("case_id: %s" %(args.case_id))
    logger.info("src_vcf_id: %s" %(args.src_vcf_id))
    logger.info("vcf_id: %s" %(str(vcf_uuid)))
    logger.info("caller_workflow_id: %s" %(args.caller_workflow_id))
    logger.info("caller_workflow_name: %s" %(args.caller_workflow_name))
    logger.info("caller_workflow_description: %s" %(args.caller_workflow_description))
    logger.info("caller_workflow_version: %s" %(args.caller_workflow_version))
    logger.info("annotation_workflow_id: %s" %(args.annotation_workflow_id))
    logger.info("annotation_workflow_name: %s" %(args.annotation_workflow_name))
    logger.info("annotation_workflow_description: %s" %(args.annotation_workflow_description))
    logger.info("annotation_workflow_version: %s" %(args.annotation_workflow_version))

    #Get datetime
    datetime_now = str(datetime.datetime.now())
    #Get CWL start time
    cwl_start = time.time()

    # getting refs
    logger.info("getting refs")
    ref_fasta    = os.path.join(index, "vep_fasta/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz")
    gdc_entrez   = os.path.join(index, "custom/ensembl_entrez_names.json")
    gdc_evidence = os.path.join(index, "custom/Homo_sapiens.VEP.v84.variation.vcf.gz")
    pg_config    = os.path.join(index, "postgres_config")

    # Download input vcf
    logger.info("getting input VCF")
    input_vcf = os.path.join(inp, os.path.basename(args.input_vcf))
    if args.object_store == 'ceph':
        s3_exit_code = utils.s3.aws_s3_get(logger, args.input_vcf, inp,
                                        "ceph", "http://gdc-cephb-objstore.osdc.io/", recursive=False)
    else:
        s3_exit_code = utils.s3.aws_s3_get(logger, args.input_vcf, inp, 
                                        "cleversafe", "http://gdc-accessors.osdc.io/", recursive=False)

    # If we can't download files error
    if s3_exit_code != 0:
        cwl_end = time.time()
        cwl_elapsed = cwl_end - cwl_start
        engine = postgres.utils.get_db_engine(pg_config)
        postgres.status.set_download_error(s3_exit_code, args.case_id, str(vcf_uuid), 
            args.src_vcf_id, [args.normal_bam_uuid, args.tumor_bam_uuid],
            args.object_store, datetime_now, str(args.fork), cwl_elapsed, engine, logger)

        #remove work and input directories
        logger.info("Removing files")
        utils.pipeline.remove_dir(uniqdir)

        # Exit
        sys.exit(s3_exit_code)

    # If downloaded file is size 0
    elif utils.pipeline.get_file_size(input_vcf) == 0: 
        cwl_end = time.time()
        cwl_elapsed = cwl_end - cwl_start
        engine = postgres.utils.get_db_engine(pg_config)
        postgres.status.set_download_error(s3_exit_code, args.case_id, str(vcf_uuid), 
            args.src_vcf_id, [args.normal_bam_uuid, args.tumor_bam_uuid],
            args.object_store, datetime_now, str(args.fork), cwl_elapsed, engine, logger)

        #remove work and input directories
        logger.info("Removing files")
        utils.pipeline.remove_dir(uniqdir)

        # Exit
        sys.exit()

    # Run CWL
    else:
        os.chdir(workdir)

        #run cwl command
        logger.info("running CWL workflow")
        cmd = ['/home/ubuntu/.virtualenvs/p2/bin/cwltool',
                "--debug",
                "--tmpdir-prefix", inp,
                "--tmp-outdir-prefix", workdir,
                args.cwl,
                "--postgres_config", pg_config,
                "--host", args.host,
                "--input_vcf", input_vcf, 
                "--vcf_id", str(vcf_uuid),
                "--src_vcf_id", args.src_vcf_id,
                "--case_id", args.case_id,
                "--patient_barcode", args.patient_barcode,
                "--tumor_barcode", args.tumor_barcode,
                "--tumor_aliquot_uuid", args.tumor_aliquot_uuid,
                "--tumor_bam_uuid", args.tumor_bam_uuid, 
                "--normal_barcode", args.normal_barcode,
                "--normal_aliquot_uuid", args.normal_aliquot_uuid,
                "--normal_bam_uuid", args.normal_bam_uuid, 
                "--caller_workflow_id", args.caller_workflow_id,
                "--caller_workflow_name", args.caller_workflow_name,
                "--caller_workflow_description", args.caller_workflow_description,
                "--caller_workflow_version", args.caller_workflow_version,
                "--annotation_workflow_id", args.annotation_workflow_id,
                "--annotation_workflow_name", args.annotation_workflow_name,
                "--annotation_workflow_description", args.annotation_workflow_description,
                "--annotation_workflow_version", args.annotation_workflow_version,
                "--ref", ref_fasta,
                "--dir_cache", index,
                "--gdc_entrez", gdc_entrez,
                "--gdc_evidence", gdc_evidence,
                "--vcf",
                "--stats_file",
                "--fork", str(args.fork)] 
        cwl_exit = utils.pipeline.run_command(cmd, logger)

        cwl_failure = False
        if cwl_exit:
            cwl_failure = True

        #upload results to s3

        logger.info("Uploading to s3")
        vep_location        = os.path.join(args.s3dir, str(vcf_uuid))
        vcf_file            = "%s.vep.reheader.vcf.gz" %(str(vcf_uuid))
        vcf_upload_location = os.path.join(vep_location, vcf_file)
        s3put_exit          = utils.s3.aws_s3_put(logger, vep_location, workdir, 
                                                  "ceph", "http://gdc-cephb-objstore.osdc.io/")

        full_vcf_file_path  = os.path.join(workdir, vcf_file)
        
        cwl_end = time.time()
        cwl_elapsed = cwl_end - cwl_start

        #establish connection with database
        engine = postgres.utils.get_db_engine(pg_config)

        # Get status info
        status, loc = postgres.status.get_status(s3put_exit, cwl_failure, vcf_upload_location, 
                                                 vep_location, logger)

        # Set metrics table
        met = postgres.time.Time(case_id = args.case_id,
                   datetime_now = datetime_now,
                   vcf_id = str(vcf_uuid),
                   src_vcf_id = args.src_vcf_id, 
                   files = [args.normal_bam_uuid, args.tumor_bam_uuid],
                   elapsed = cwl_elapsed,
                   thread_count = str(args.fork),
                   status = str(status))

        postgres.utils.create_table(engine, met)
        postgres.utils.add_metrics(engine, met)

        # Get md5
        md5 = 'UNKNOWN' 
        if os.path.isfile(full_vcf_file_path):
            md5 = utils.pipeline.get_md5(full_vcf_file_path)
 
        # Set status table
        logger.info("Updating status")
        postgres.status.add_status(engine, args.case_id, str(vcf_uuid), args.src_vcf_id,  
                                  [args.normal_bam_uuid, args.tumor_bam_uuid], status, 
                                  loc, datetime_now, md5)

        #remove work and input directories
        logger.info("Removing files")
        utils.pipeline.remove_dir(uniqdir)

def get_args():
    '''
    Loads the parser
    '''
    # Main parser
    p  = argparse.ArgumentParser(prog='GDC-VEP-Annotation-Workflow')

    # Sub parser 
    sp = p.add_subparsers(help='Choose the process you want to run', dest='choice')

    # Stage
    p_stage = sp.add_parser('stage', help='Options for staging VEP cache. This should be the first step.')
    p_stage.add_argument('--cache_s3bin', required=True,
        help='s3bin containing custom.tar.gz, homo_sapiens.tar.gz, vep_fasta.tar.gz')
    p_stage.add_argument('--output_directory', required=True,
        help='The directory you want to store the cache files')
    p_stage.add_argument('--log_file', type=str,
        help='If you want to write the logs to a file. By default stdout')

    # Build slurm scripts
    p_slurm = sp.add_parser('slurm', help='Options for building slurm scripts. This should be the second step.')
    p_slurm.add_argument('--refdir', required=True, help='Path to the reference directory')
    p_slurm.add_argument('--config', required=True, help='Path to the postgres config file')
    p_slurm.add_argument('--thread_count', required=True, help='number of threads to use')
    p_slurm.add_argument('--mem', required=True, help='mem for each node')
    p_slurm.add_argument('--outdir', default="./", help='output directory for slurm scripts [./]')
    p_slurm.add_argument('--s3dir', default="s3://ceph_vep", help='s3bin for output files [s3://ceph_vep/]')
    p_slurm.add_argument('--run_basedir', default="/mnt/SCRATCH", help='basedir for cwl runs')
    p_slurm.add_argument('--log_file', type=str, help='If you want to write the logs to a file. By default stdout')

    # Args
    p_run = sp.add_parser('run', help='Wrapper for running the VEP cwl workflow.')
    p_run.add_argument('--refdir', required=True, help='Path to reference directory')
    p_run.add_argument('--basedir', default='/mnt/SCRATCH', help='Path to the postgres config file')
    p_run.add_argument('--object_store', required=True, choices=['ceph', 'cleversafe'], help='The s3 object store id')
    p_run.add_argument('--host', default="10.64.0.97", help='postgres host name')
    p_run.add_argument('--input_vcf', required=True, help='s3 url for input vcf file')
    p_run.add_argument('--src_vcf_id', required=True, help='Input VCF ID')
    p_run.add_argument('--case_id', required=True, help='case id')
    p_run.add_argument('--patient_barcode', required=True, help='The patient barcode') 
    p_run.add_argument('--tumor_barcode', required=True, help='The tumor barcode') 
    p_run.add_argument('--tumor_aliquot_uuid', required=True, help='The tumor aliquot unique ID') 
    p_run.add_argument('--tumor_bam_uuid', required=True, help='The tumor bam unique ID') 
    p_run.add_argument('--normal_barcode', required=True, help='The normal barcode') 
    p_run.add_argument('--normal_aliquot_uuid', required=True, help='The normal aliquot unique ID') 
    p_run.add_argument('--normal_bam_uuid', required=True, help='The normal bam unique ID') 
    p_run.add_argument('--caller_workflow_id', required=True, help='vcf header workflow id for caller')
    p_run.add_argument('--caller_workflow_name', required=True, help='vcf header workflow name for caller')
    p_run.add_argument('--caller_workflow_description', required=True, help='vcf header workflow description for caller')
    p_run.add_argument('--caller_workflow_version', required=True, help='vcf header workflow version for caller')
    p_run.add_argument('--annotation_workflow_id', required=True, help='vcf header workflow id for annotation')
    p_run.add_argument('--annotation_workflow_name', required=True, help='vcf header workflow name for annotation')
    p_run.add_argument('--annotation_workflow_description', required=True, help='vcf header workflow description for annotation')
    p_run.add_argument('--annotation_workflow_version', required=True, help='vcf header workflow version for annotation')
    p_run.add_argument('--fork', type=int, default=1, help='Number of VEP threads to use')
    p_run.add_argument('--s3dir', default="s3://ceph_vep", help='s3bin for uploading output files')
    p_run.add_argument('--cwl', required=True, help='Path to VEP CWL workflow YAML')

    return p.parse_args()

if __name__ == '__main__':
    # Get args
    args = get_args()

    # Run tool 
    if args.choice == 'stage': sys.exit(run_stage_cache(args))
    elif args.choice == 'slurm': run_build_slurm_scripts(args)
    elif args.choice == 'run': run_cwl(args)
