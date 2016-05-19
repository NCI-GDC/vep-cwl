# VEP Annotation CWL Pipeline - SLURM

## Stage the compute nodes

The cache is located on both ceph and cleversafe at `s3://bioinformatics_scratch/vep_cache_84/`

```
# You will need to change the location to AV2/AV2 and if you wish to store the cache elsewhere
# Make directory
sudo salt -C 'G@az:AV1' cmd.run 'mkdir -p /mnt/SCRATCH/vep/cache'

# Pull cache
sudo salt -C 'G@az:AV1' cmd.run 's3cmd --config /home/ubuntu/.s3cfg sync s3://bioinformatics_scratch/vep_cache_84 /mnt/SCRATCH/vep/cache --recursive'

# Decompress files
sudo salt -C 'G@az:AV1' cmd.run 'cd /mnt/SCRATCH/vep/cache/vep_cache_84 && tar -xzf /mnt/SCRATCH/vep/cache/vep_cache_84/custom.tar.gz'
sudo salt -C 'G@az:AV1' cmd.run 'cd /mnt/SCRATCH/vep/cache/vep_cache_84 && tar -xzf /mnt/SCRATCH/vep/cache/vep_cache_84/vep_fasta.tar.gz'
sudo salt -C 'G@az:AV1' cmd.run 'cd /mnt/SCRATCH/vep/cache/vep_cache_84 && tar -xzf /mnt/SCRATCH/vep/cache/vep_cache_84/homo_sapiens.tar.gz'

# Remove tar.gz
sudo salt -C 'G@az:AV1' cmd.run 'rm /mnt/SCRATCH/vep/cache/vep_cache_84/custom.tar.gz'
sudo salt -C 'G@az:AV1' cmd.run 'rm /mnt/SCRATCH/vep/cache/vep_cache_84/vep_fasta.tar.gz'
sudo salt -C 'G@az:AV1' cmd.run 'rm /mnt/SCRATCH/vep/cache/vep_cache_84/homo_sapiens.tar.gz'

# Change owner
sudo salt -C 'G@az:AV1' cmd.run 'sudo chown ubuntu:ubuntu -R /mnt/SCRATCH/vep'
```

**Note**: You will also need to add your postgres credentials to the cache dir on each node

## Running build command

To build the SLURM scripts, you can run this command:

```
$ python GDC-VEP-Annotation-Workflow.py slurm --help
usage: GDC-VEP-Annotation-Workflow slurm [-h] --refdir REFDIR --config CONFIG
                                         --thread_count THREAD_COUNT --mem MEM
                                         [--outdir OUTDIR] [--s3dir S3DIR]
                                         [--run_basedir RUN_BASEDIR]
                                         [--log_file LOG_FILE]

optional arguments:
  -h, --help            show this help message and exit
  --refdir REFDIR       Path to the reference directory
  --config CONFIG       Path to the postgres config file
  --thread_count THREAD_COUNT
                        number of threads to use
  --mem MEM             mem for each node
  --outdir OUTDIR       output directory for slurm scripts [./]
  --s3dir S3DIR         s3bin for output files [s3://ceph_vep/]
  --run_basedir RUN_BASEDIR
                        basedir for cwl runs
  --log_file LOG_FILE   If you want to write the logs to a file. By default
                        stdout
```

This script expect that the metadata is located in the PG tabe: `vep_input`
with this structure:

```
         Column          |       Type        | Modifiers 
-------------------------+-------------------+-----------
 program                 | text              | 
 project                 | text              | 
 case_id                 | uuid              | 
 study                   | text              | 
 disease                 | text              | 
 patient_barcode         | text              | 
 participant_id          | text              | 
 src_vcf_id              | character varying | 
 src_vcf_location        | character varying | 
 normal_barcode          | text              | 
 normal_aliquot_id       | uuid              | 
 old_normal_bam_gdcid    | character varying | 
 normal_bam_gdcid        | text              | 
 tumor_barcode           | text              | 
 tumor_aliquot_id        | uuid              | 
 old_tumor_bam_gdcid     | character varying | 
 tumor_bam_gdcid         | text              | 
 pipeline                | text              | 
 workflow_id_01          | text              | 
 workflow_name_01        | text              | 
 workflow_description_01 | text              | 
 workflow_version_01     | text              | 
 workflow_id_02          | text              | 
 workflow_name_02        | text              | 
 workflow_description_02 | text              | 
 workflow_version_02     | text              | 
 bucket                  | text              | 
 objectstore             | text              |
```

## Run Command

If you wish to directly run the workflow, you can use this:

```
$ python GDC-VEP-Annotation-Workflow.py run --help
usage: GDC-VEP-Annotation-Workflow run [-h] --refdir REFDIR
                                       [--basedir BASEDIR] --object_store
                                       {ceph,cleversafe} [--host HOST]
                                       --input_vcf INPUT_VCF --src_vcf_id
                                       SRC_VCF_ID --case_id CASE_ID
                                       --patient_barcode PATIENT_BARCODE
                                       --tumor_barcode TUMOR_BARCODE
                                       --tumor_aliquot_uuid TUMOR_ALIQUOT_UUID
                                       --tumor_bam_uuid TUMOR_BAM_UUID
                                       --normal_barcode NORMAL_BARCODE
                                       --normal_aliquot_uuid
                                       NORMAL_ALIQUOT_UUID --normal_bam_uuid
                                       NORMAL_BAM_UUID --caller_workflow_id
                                       CALLER_WORKFLOW_ID
                                       --caller_workflow_name
                                       CALLER_WORKFLOW_NAME
                                       --caller_workflow_description
                                       CALLER_WORKFLOW_DESCRIPTION
                                       --caller_workflow_version
                                       CALLER_WORKFLOW_VERSION
                                       --annotation_workflow_id
                                       ANNOTATION_WORKFLOW_ID
                                       --annotation_workflow_name
                                       ANNOTATION_WORKFLOW_NAME
                                       --annotation_workflow_description
                                       ANNOTATION_WORKFLOW_DESCRIPTION
                                       --annotation_workflow_version
                                       ANNOTATION_WORKFLOW_VERSION
                                       [--fork FORK] [--s3dir S3DIR] --cwl CWL

optional arguments:
  -h, --help            show this help message and exit
  --refdir REFDIR       Path to reference directory
  --basedir BASEDIR     Path to the postgres config file
  --object_store {ceph,cleversafe}
                        The s3 object store id
  --host HOST           postgres host name
  --input_vcf INPUT_VCF
                        s3 url for input vcf file
  --src_vcf_id SRC_VCF_ID
                        Input VCF ID
  --case_id CASE_ID     case id
  --patient_barcode PATIENT_BARCODE
                        The patient barcode
  --tumor_barcode TUMOR_BARCODE
                        The tumor barcode
  --tumor_aliquot_uuid TUMOR_ALIQUOT_UUID
                        The tumor aliquot unique ID
  --tumor_bam_uuid TUMOR_BAM_UUID
                        The tumor bam unique ID
  --normal_barcode NORMAL_BARCODE
                        The normal barcode
  --normal_aliquot_uuid NORMAL_ALIQUOT_UUID
                        The normal aliquot unique ID
  --normal_bam_uuid NORMAL_BAM_UUID
                        The normal bam unique ID
  --caller_workflow_id CALLER_WORKFLOW_ID
                        vcf header workflow id for caller
  --caller_workflow_name CALLER_WORKFLOW_NAME
                        vcf header workflow name for caller
  --caller_workflow_description CALLER_WORKFLOW_DESCRIPTION
                        vcf header workflow description for caller
  --caller_workflow_version CALLER_WORKFLOW_VERSION
                        vcf header workflow version for caller
  --annotation_workflow_id ANNOTATION_WORKFLOW_ID
                        vcf header workflow id for annotation
  --annotation_workflow_name ANNOTATION_WORKFLOW_NAME
                        vcf header workflow name for annotation
  --annotation_workflow_description ANNOTATION_WORKFLOW_DESCRIPTION
                        vcf header workflow description for annotation
  --annotation_workflow_version ANNOTATION_WORKFLOW_VERSION
                        vcf header workflow version for annotation
  --fork FORK           Number of VEP threads to use
  --s3dir S3DIR         s3bin for uploading output files
  --cwl CWL             Path to VEP CWL workflow YAML
```
