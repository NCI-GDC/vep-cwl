#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task={THREAD_COUNT}
#SBATCH --ntasks=1
#SBATCH --workdir={BASEDIR}
#SBATCH --mem={MEM}

# Runtime
thread_count="{THREAD_COUNT}"

# IDS
vcf_source="{VCF_SOURCE}"
src_vcf_id="{SRC_VCF_ID}"
case_id="{CASE_ID}"
patient_barcode="{PATIENT_BARCODE}"
tumor_barcode="{TUMOR_BARCODE}"
tumor_aliquot_uuid="{TUMOR_ALIQUOT_UUID}"
tumor_bam_uuid="{TUMOR_BAM_UUID}"
normal_barcode="{NORMAL_BARCODE}"
normal_aliquot_uuid="{NORMAL_ALIQUOT_UUID}"
normal_bam_uuid="{NORMAL_BAM_UUID}"

# Input
input_vcf="{INPUT_VCF}"

# Reference DB
refdir="{REFDIR}"

# Outputs
s3dir="{S3DIR}"
basedir="{BASEDIR}"
repository="git@github.com:NCI-GDC/vep-cwl.git"
wkdir=`sudo mktemp -d vep.XXXXXXXXXX -p $basedir`
sudo chown ubuntu:ubuntu $wkdir

cd $wkdir

function cleanup (){{
    echo "cleanup tmp data";
    sudo rm -rf $wkdir;
}}

sudo git clone -b feat/slurm $repository
sudo chown ubuntu:ubuntu -R vep-cwl

trap cleanup EXIT

/home/ubuntu/.virtualenvs/p2/bin/python vep-cwl/slurm/GDC-VEP-Annotation-Workflow.py run \
--basedir $wkdir \
--refdir $refdir \
--vcf_source $vcf_source \
--input_vcf $input_vcf \
--src_vcf_id $src_vcf_id \
--case_id $case_id \
--patient_barcode $patient_barcode \
--tumor_barcode $tumor_barcode \
--tumor_aliquot_uuid $tumor_aliquot_uuid \
--tumor_bam_uuid $tumor_bam_uuid \
--normal_barcode $normal_barcode \
--normal_aliquot_uuid $normal_aliquot_uuid \
--normal_bam_uuid $normal_bam_uuid \
--fork $thread_count \
--s3dir $s3dir \
--cwl $wkdir/vep-cwl/workflows/vep-no-aws-workflow.cwl.yaml
