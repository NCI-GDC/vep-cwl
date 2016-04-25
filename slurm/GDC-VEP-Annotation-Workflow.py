'''
Main wrapper script for staging a VEP run.
'''
import os
import time
import argparse
import logging
import sys

import utils.s3
import utils.pipeline

import postgres.status
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

    # Database setup
    s = open(args.config, 'r').read()
    config = eval(s)

    DATABASE = {
        'drivername': 'postgres',
        'host': 'pgreadwrite.osdc.io',
        'port': '5432',
        'username': config['username'],
        'password': config['password'],
        'database': 'prod_bioinfo'
    }

    engine = postgres.status.db_connect(DATABASE)

    try:
        cases = postgres.status.get_vep_inputs(engine, 'vep_cwl_status')
    except NoSuchTableError:
        print "HERE" 

def get_args():
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
    p_slurm.add_argument('--config', required=True, help='Path to the postgres config file')
    p_slurm.add_argument('--cache_dir', required=True, help='Path to the directory containing the VEP cache files')
    p_slurm.add_argument('--thread_count', required=True, help='number of threads to use')
    p_slurm.add_argument('--mem', required=True, help='mem for each node')
    p_slurm.add_argument('--reference_fasta', required=True, help='Path to VEP appropriate reference file')
    p_slurm.add_argument('--outdir', default="./", help='output directory for slurm scripts [./]')
    p_slurm.add_argument('--s3dir', default="s3://vep_annotation", help='s3bin for output files [s3://vep_annotation/]')
    p_slurm.add_argument('--log_file', type=str, help='If you want to write the logs to a file. By default stdout')

    # Args
    return p.parse_args()

if __name__ == '__main__':
    # Get args
    args = get_args()

    # Run tool 
    if args.choice == 'stage': sys.exit(run_stage_cache(args))
    elif args.choice == 'slurm': run_build_slurm_scripts(args)
