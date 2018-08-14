#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task={THREAD_COUNT}
#SBATCH --ntasks=1
#SBATCH --workdir={BASEDIR}
#SBATCH --mem={MEM}

# Runtime
thread_count="{THREAD_COUNT}"

# IDS
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
object_store="{OBJECT_STORE}"

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

/home/ubuntu/.virtualenvs/p2/bin/python vep-cwl/slurm/GDC-VEP-Annotation-MuTecT2-dbSNP-Rerun-Workflow.py run \
--basedir $wkdir \
--refdir $refdir \
--input_vcf $input_vcf \
--object_store $object_store \
--src_vcf_id $src_vcf_id \
--case_id $case_id \
--patient_barcode $patient_barcode \
--tumor_barcode $tumor_barcode \
--tumor_aliquot_uuid $tumor_aliquot_uuid \
--tumor_bam_uuid $tumor_bam_uuid \
--normal_barcode $normal_barcode \
--normal_aliquot_uuid $normal_aliquot_uuid \
--normal_bam_uuid $normal_bam_uuid \
--caller_workflow_id "{CALLER_WORKFLOW_ID}" \
--caller_workflow_name "{CALLER_WORKFLOW_NAME}" \
--caller_workflow_description "{CALLER_WORKFLOW_DESCRIPTION}" \
--caller_workflow_version "{CALLER_WORKFLOW_VERSION}" \
--annotation_workflow_id "{ANNOTATION_WORKFLOW_ID}" \
--annotation_workflow_name "{ANNOTATION_WORKFLOW_NAME}" \
--annotation_workflow_description "{ANNOTATION_WORKFLOW_DESCRIPTION}" \
--annotation_workflow_version "{ANNOTATION_WORKFLOW_VERSION}" \
--fork $thread_count \
--s3dir $s3dir \
--cwl $wkdir/vep-cwl/workflows/vep-workflow.cwl.yaml
