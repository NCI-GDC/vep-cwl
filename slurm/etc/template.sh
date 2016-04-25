#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task={THREAD_COUNT}
#SBATCH --ntasks=1
#SBATCH --workdir="/mnt/SCRATCH/"
#SBATCH --mem={MEM}

refdir="{REFDIR}"
thread_count="{THREAD_COUNT}"

normal="{NORMAL}"
tumor="{TUMOR}"
normal_id="{NORMAL_ID}"
tumor_id="{TUMOR_ID}"
case_id="{CASE_ID}"

s3dir="{S3DIR}"
repository="git@github.com:NCI-GDC/vep-cwl.git"
wkdir=`sudo mktemp -d vep.XXXXXXXXXX -p /mnt/SCRATCH/`
sudo chown ubuntu:ubuntu $wkdir

cd $wkdir

function cleanup (){{
    echo "cleanup tmp data";
    sudo rm -rf $wkdir;
}}

sudo git clone -b feat/slurm $repository
sudo chown ubuntu:ubuntu -R vep-cwl

trap cleanup EXIT

/home/ubuntu/.virtualenvs/p2/bin/python vep-cwl/slurm/run_cwl.py \
--refdir $refdir \
--block $block \
--thread_count $thread_count \
--java_heap $java_heap \
--contEst $contEst \
--normal $normal \
--normal_id $normal_id \
--tumor $tumor \
--tumor_id $tumor_id \
--case_id $case_id \
--basedir $wkdir \
--s3dir $s3dir \
--cwl $wkdir/mutect-cwl/workflows/mutect2-vc-workflow.cwl.yaml
