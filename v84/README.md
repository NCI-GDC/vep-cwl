# GDC VEP Annotation Workflow
![Version badge](https://img.shields.io/badge/VEP-v84-<COLOR>.svg)

This workflow takes a VCF file and adds [Variant Effect Predictor](http://useast.ensembl.org/info/docs/tools/vep/index.html)
annotations using particular settings for the GDC harmonization process.

## Notes

* Tested on [cwltool](https://github.com/common-workflow-language/cwltool) version `1.0.20180306163216`
* See [GDC Reference Files](https://gdc.cancer.gov/about-data/data-harmonization-and-generation/gdc-reference-files)
* Plugins and Dockerfile available at https://github.com/NCI-GDC/vep-tool
* We were using VEP v84 with our customized cache file (see [VEP-SETUP.md](VEP-SETUP.md) for more information).

## External Users

The entrypoint CWL workflow for external users is `workflows/subworkflows/gdc_main_annotation_workflow.cwl`.

### Inputs

| Name | Type | Description |
| ---- | ---- | ----------- |
| `input_vcf` | `File` | VCF file you want to annotate. |
| `input_vep_reference` | `File` | VEP reference fasta with .fai and .gzi indices |
| `input_vep_cache` | `Directory` | VEP cache directory |
| `input_vep_entrez_json` | `File` | Entrez JSON file needed by plugin |
| `input_vep_evidence_vcf` | `File` | VEP evidence VCF file with tabix index (.tbi) |
| `output_filename_base` | `string` | Base name to use for all outputs |
| `threads` | `int?` | Optional number of threads to use for VEP |

### Outputs

| Name | Type | Description |
| ---- | ---- | ----------- |
| `annotated_vcf` | `File` | Annotated and bgzipped VCF. |
| `annotated_vcf_index` | `File` | Tabix index for annotated VCF. |
| `vep_stats` | `File?` | Optional VEP stats file. (generated default) |
| `vep_warning` | `File?` | Optional VEP warnings file. |

## GPAS Users

The entrypoint CWL workflow for GPAS is `workflows/vep-annotation-workflow.cwl`.

### Inputs

| Name | Type | Description |
| ---- | ---- | ----------- |
| `project_id` | `string?` | optional project ID, only used if you want the output file prefix to contain this string |
| `experimental_strategy` | `string` | experimental strategy the data comes from (used in file name) |
| `caller_id` | `string` | the caller used to generate the variants (used in file name) |
| `bioclient_config` | `File` | the bioclient configuration file |
| `bioclient_load_bucket` | `string` | s3 bucket to load the outputs into |
| `input_vcf_gdc_id` | `string` | input VCF uuid |
| `input_vcf_index_gdc_id` | `string` | input VCF index uuid |
| `input_vep_fasta_gdc_id` | `string` | the VEP fasta uuid |
| `input_vep_fasta_fai_gdc_id` | `string` | the VEP fasta fai uuid |
| `input_vep_fasta_gzi_gdc_id` | `string` | the VEP fasta gzi uuid |
| `input_vep_cache_gdc_id` | `string` | the VEP cache tar uuid |
| `input_vep_entrez_json_gdc_id` | `string` | the entrez JSON mapping file uuid |
| `input_vep_evidence_vcf_gdc_id` | `string` | the VEP evidence vcf file uuid |
| `input_vep_evidence_index_gdc_id` | `string` | the VEP evidence vcf index file uuid |
| `job_uuid` | `string` | the job uuid assigned by GPAS (used in output file names) |
| `upload_prefix` | `string?` | additional s3 prefix to add if wanted |
| `threads` | `int?` | number of threads to use for VEP |

### Outputs

| Name | Type | Description |
| ---- | ---- | ----------- |
| `indexd_vcf_uuid` | `string` | annotated VCF uuid |
| `indexd_vcf_index_uuid` | `string` | annotated VCF index uuid |
| `indexd_vep_stats_uuid` | `string` | VEP stats file uuid |
