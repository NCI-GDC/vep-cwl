cwlVersion: v1.0
class: Workflow
id: gdc_vep_annotation_wf
requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: SubworkflowFeatureRequirement

inputs:
  project_id:
    type: string?
    doc: GDC project id used for output filenames
  experimental_strategy: 
    type: string
    doc: GDC experimental strategy used for output filenames
  caller_id: 
    type: string
    doc: GDC variant caller id used for output filenames
  bioclient_config:
    type: File
    doc: Bioclient configuration file
  bioclient_load_bucket:
    type: string
    doc: Bucket to load files to
  input_vcf_gdc_id:
    type: string
    doc: input VCF uuid for bioclient 
  input_vcf_index_gdc_id:
    type: string
    doc: input VCF index uuid for bioclient 
  input_vep_fasta_gdc_id:
    type: string
    doc: input VEP fasta uuid for bioclient 
  input_vep_fasta_fai_gdc_id:
    type: string
    doc: input VEP fasta fai uuid for bioclient 
  input_vep_fasta_gzi_gdc_id:
    type: string
    doc: input VEP fasta gzi uuid for bioclient 
  input_vep_cache_gdc_id:
    type: string
    doc: input VEP cache tar.gz uuid for bioclient 
  input_vep_entrez_json_gdc_id:
    type: string
    doc: input VEP ENTREZ plugin json uuid for bioclient 
  input_vep_evidence_vcf_gdc_id:
    type: string
    doc: input VEP evidence VCF uuid for bioclient 
  input_vep_evidence_index_gdc_id:
    type: string
    doc: input VEP evidence VCF index uuid for bioclient 
  job_uuid:
    type: string
    doc: uuid for this job
  upload_prefix:
    type: string?
    doc: optional s3 key prefix
  threads:
    type: int?
    doc: number of threads to use for VEP

outputs:
  indexd_vcf_uuid:
    type: string
    outputSource: upload_vep_vcf/indexd_uuid 
  indexd_vcf_index_uuid:
    type: string
    outputSource: upload_vep_vcf_index/indexd_uuid 
  indexd_vep_stats_uuid:
    type: string
    outputSource: upload_vep_stats/indexd_uuid 

steps:
  stage_workflow:
    run: ./subworkflows/stage.cwl
    in:
      bioclient_config: bioclient_config
      input_vcf_gdc_id: input_vcf_gdc_id 
      input_vep_fasta_gdc_id: input_vep_fasta_gdc_id 
      input_vep_fasta_fai_gdc_id: input_vep_fasta_fai_gdc_id 
      input_vep_fasta_gzi_gdc_id: input_vep_fasta_gzi_gdc_id 
      input_vep_cache_gdc_id: input_vep_cache_gdc_id 
      input_vep_entrez_json_gdc_id: input_vep_entrez_json_gdc_id 
      input_vep_evidence_vcf_gdc_id: input_vep_evidence_vcf_gdc_id 
      input_vep_evidence_index_gdc_id: input_vep_evidence_index_gdc_id 
    out: [ input_vcf, vep_evidence_vcf, vep_reference, vep_cache, vep_entrez_json ]

  get_filename_prefix:
    run: ../tools/make_file_prefix.cwl
    in:
      project_id: project_id
      job_id: job_uuid
      experimental_strategy: experimental_strategy
      caller_id: caller_id
    out: [ output ]

  run_main_vep:
    run: ./subworkflows/gdc_main_annotation_workflow.cwl
    in:
      input_vcf: stage_workflow/input_vcf
      input_vep_reference: stage_workflow/vep_reference
      input_vep_cache: stage_workflow/vep_cache
      output_filename_base: get_filename_prefix/output
      threads: threads
      input_vep_entrez_json: stage_workflow/vep_entrez_json
      input_vep_evidence_vcf: stage_workflow/vep_evidence_vcf
    out: [ annotated_vcf, annotated_vcf_index, vep_stats, vep_warning ]

  upload_vep_vcf:
    run: ./subworkflows/upload_and_emit.cwl
    in:
      bioclient_config: bioclient_config
      bioclient_load_bucket: bioclient_load_bucket
      upload_prefix: upload_prefix
      job_uuid: job_uuid
      input_file: run_main_vep/annotated_vcf
    out: [ indexd_uuid ]

  upload_vep_vcf_index:
    run: ./subworkflows/upload_and_emit.cwl
    in:
      bioclient_config: bioclient_config
      bioclient_load_bucket: bioclient_load_bucket
      upload_prefix: upload_prefix
      job_uuid: job_uuid
      input_file: run_main_vep/annotated_vcf_index
    out: [ indexd_uuid ]

  upload_vep_stats:
    run: ./subworkflows/upload_and_emit.cwl
    in:
      bioclient_config: bioclient_config
      bioclient_load_bucket: bioclient_load_bucket
      upload_prefix: upload_prefix
      job_uuid: job_uuid
      input_file: run_main_vep/vep_stats
    out: [ indexd_uuid ]
