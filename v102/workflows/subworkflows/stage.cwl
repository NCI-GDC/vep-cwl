cwlVersion: v1.0
class: Workflow
id: gdc_annotation_stage_wf
requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  bioclient_config:
    type: File
    doc: Bioclient configuration file
  input_vcf_gdc_id: string
  input_vep_fasta_gdc_id: string
  input_vep_fasta_fai_gdc_id: string
  input_vep_fasta_gzi_gdc_id: string
  input_vep_cache_gdc_id: string

outputs:
  input_vcf:
    type: File
    outputSource: extract_vcf/output

  vep_reference:
    type: File
    outputSource: make_vep_ref/output

  vep_cache:
    type: Directory
    outputSource: decompress_cache/out_directory

steps:
  extract_cache:
    run: ../../../tools/bio_client_download.cwl
    in:
      config_file: bioclient_config
      download_handle: input_vep_cache_gdc_id
    out: [ output ]

  decompress_cache:
    run: ../../../tools/untar_cache.cwl
    in:
      input_tar: extract_cache/output
    out: [ out_directory ]

  extract_vcf:
    run: ../../../tools/bio_client_download.cwl
    in:
      config_file: bioclient_config
      download_handle: input_vcf_gdc_id
    out: [ output ]

  extract_fasta:
    run: ../../../tools/bio_client_download.cwl
    in:
      config_file: bioclient_config
      download_handle: input_vep_fasta_gdc_id
    out: [ output ]

  extract_fai:
    run: ../../../tools/bio_client_download.cwl
    in:
      config_file: bioclient_config
      download_handle: input_vep_fasta_fai_gdc_id
    out: [ output ]

  extract_gzi:
    run: ../../../tools/bio_client_download.cwl
    in:
      config_file: bioclient_config
      download_handle: input_vep_fasta_gzi_gdc_id
    out: [ output ]

  make_vep_ref:
    run: ../../../tools/make_ref_pair.cwl
    in:
      fa_file: extract_fasta/output
      gzi_file: extract_fai/output
      fai_file: extract_gzi/output
    out: [ output ]
