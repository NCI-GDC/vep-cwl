GDC VEP Annotation Workflow 
---

## Overview

Annotate variants using the 
[Variant Effect Predictor](http://useast.ensembl.org/info/docs/tools/vep/index.html)
v84 with our customized cache file (see [VEP-SETUP.md](VEP-SETUP.md) for more information).

### CWL Inputs

* `project_id` (**optional** string) - the project ID, only used if you want the output file prefix to contain this string
* `experimental_strategy` (string) - experimental strategy the data comes from (used in file name)
* `caller_id` (string) - the caller used to generate the variants (used in file name)
* `bioclient_config` (file) - the bioclient configuration file
* `bioclient_load_bucket` (string) - s3 bucket to load the outputs into
* `input_vcf_gdc_id` (string) - input VCF uuid
* `input_vcf_index_gdc_id` (string) - input VCF index uuid
* `input_vep_fasta_gdc_id` (string) - the VEP fasta uuid
* `input_vep_fasta_fai_gdc_id` (string) - the VEP fasta fai uuid
* `input_vep_fasta_gzi_gdc_id` (string) - the VEP fasta gzi uuid
* `input_vep_cache_gdc_id` (string) - the VEP cache tar uuid
* `input_vep_entrez_json_gdc_id` (string) - the entrez JSON mapping file uuid
* `input_vep_evidence_vcf_gdc_id` (string) - the VEP evidence vcf file uuid
* `input_vep_evidence_index_gdc_id` (string) - the VEP evidence vcf index file uuid
* `job_uuid` (string) - the job uuid assigned by GPAS (used in output file names)
* `upload_prefix` (**optional** string) - additional s3 prefix to add if wanted
* `threads` (**optional** int) - number of threads to use for VEP

### CWL Outputs

* `indexd_vcf_uuid` (string) - annotated VCF uuid
* `indexd_vcf_index_uuid` (string) - annotated VCF index uuid
* `indexd_vep_stats_uuid` (string) - VEP stats file uuid
