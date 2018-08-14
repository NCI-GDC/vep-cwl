GDC VEP Annotation Workflow 
---

## Overview

Filter scaffolds that aren't the main assembly, annotate variants using the 
[Variant Effect Predictor](http://useast.ensembl.org/info/docs/tools/vep/index.html)
v84 with our customized cache file, and reheader the VCF file with the GDC
IDs.

## Making VEP Custom Cache

```
        1. Download the two cache archives:

                Download v80 cache: ftp://ftp.ensembl.org/pub/release-80/variation/VEP/homo_sapiens_vep_80_GRCh38.tar.gz
                Download v84 cache: ftp://ftp.ensembl.org/pub/release-84/variation/VEP/homo_sapiens_vep_84_GRCh38.tar.gz

        2. Decompress (tar -xzf)

        3. Copy v80 transcript files to v84 cache directory:

                rsync -rv --exclude="*var*" --exclude="*reg*" --exclude="*info*" ./homo_sapiens/80_GRCh38/ ./homo_sapiens/84_GRCh38/

        4. Update v84 info.txt with correct gencode and genebuild version

                grep -v source_gen ./homo_sapiens/84_GRCh38/info.txt > new_info.txt
                grep source_gen ./homo_sapiens/80_GRCh38/info.txt >> new_info.txt
                mv new_info.txt  ./homo_sapiens/84_GRCh38/info.txt

        5. Download and index GRCh38 fasta:
                wget ftp://ftp.ensembl.org/pub/release-84/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
                gzip -d Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
                bgzip Homo_sapiens.GRCh38.dna.primary_assembly.fa
                # Must run vep once with some vcf to index the fasta
                perl variant_effect_predictor.pl --dir_cache /path/to/cache/ -i input.vcf \
                        --offline --hgvs --fasta Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz

	6. Index the cache (tabix needed):
		# Note: This takes time
		perl ensembl-tools-release-84/scripts/variant_effect_predictor/convert_cache.pl \
			--species homo_sapiens --version 84_GRCh38 -r
```

## Making VEP Custom Files

```
        1. Download VEP variation VCF/index and rename for clarity (these must go in the 'custom' dir):
                wget ftp://ftp.ensembl.org/pub/release-84/variation/vcf/homo_sapiens/Homo_sapiens.vcf.gz
                wget ftp://ftp.ensembl.org/pub/release-84/variation/vcf/homo_sapiens/Homo_sapiens.vcf.gz.tbi
                mv Homo_sapiens.vcf.gz Homo_sapiens.VEP.v84.variation.vcf.gz
                mv Homo_sapiens.vcf.gz.tbi Homo_sapiens.VEP.v84.variation.vcf.gz.tbi

        2. Download the files for the ENTREZ plugin and make the JSON file (the JSON file must go in the 'custom' dir
           and should be named 'ensembl_entrez_names.json'):

                # Gencode Entrez Gene IDs file:
                wget ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_22/gencode.v22.metadata.EntrezGene.gz
                # NCBI human gene info file:
                wget ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz
                # Run the make_ensembl_entrez_json.py script in the vep-tool/vep-plugins/utils git repo
                python make_ensembl_entrez_json.py <gencode_entrez_gene_file> <ncbi_gene_info_file> <output_json_file>

        3. Add the uniprot canonical transcripts mapping file (for vcf2maf) to the top-level cache directory:
                # Git repo: https://github.com/mskcc/vcf2maf.git
                # File is located in vcf2maf/data/isoform_overrides_uniprot
```

## Running Workflow

The simplest way to run the workflow is to use the scripts and documentation available in the
slurm directory and pulling from the `develop` branch.

### Steps

1. Stage nodes if not done
2. Pull down input VCF file
3. Run workflow (`contig filter -> annotate -> reheader`)
4. Upload to `s3://ceph_vep` 
