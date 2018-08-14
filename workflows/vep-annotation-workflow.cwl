#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

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

  run_vep:
    run: ../tools/vep.cwl
    in:
      input_file: stage_workflow/input_vcf
      fasta: stage_workflow/vep_reference
      dir_cache: stage_workflow/vep_cache
      shift_hgvs:
        default: 1
      failed:
        default: 1
      flag_pick_allele:
        default: true
      pick_order:
        default:
          - canonical
          - tsl
          - biotype
          - rank
          - ccds
          - length
      minimal:
        default: true
      tabix:
        default: true
      output_file:
        source: get_filename_prefix/output
        valueFrom: $(self + '.somatic_annotation.vcf.gz')
      vcf:
        default: true 
      stats_file:
        source: get_filename_prefix/output
        valueFrom: $(self + '.somatic_annotation.stats.txt')
      stats_text:
        default: true
      fork: threads 
      no_progress:
        default: true
      everything:
        default: true
      xref_refseq:
        default: true
      total_length:
        default: true
      allele_number:
        default: true
      check_alleles:
        default: true
      check_existing:
        default: true
      assembly:
        default: "GRCh38" 
      gdc_entrez: stage_workflow/vep_entrez_json 
      gdc_evidence: stage_workflow/vep_evidence_vcf 
    out: [ vep_out, vep_index_out, stats_out_file, warning_out_file ]

  upload_vep_vcf:
    run: ./subworkflows/upload_and_emit.cwl
    in:
      bioclient_config: bioclient_config
      bioclient_load_bucket: bioclient_load_bucket
      upload_prefix: upload_prefix
      job_uuid: job_uuid
      input_file: run_vep/vep_out 
    out: [ indexd_uuid ]

  upload_vep_vcf_index:
    run: ./subworkflows/upload_and_emit.cwl
    in:
      bioclient_config: bioclient_config
      bioclient_load_bucket: bioclient_load_bucket
      upload_prefix: upload_prefix
      job_uuid: job_uuid
      input_file: run_vep/vep_index_out
    out: [ indexd_uuid ]

  upload_vep_stats:
    run: ./subworkflows/upload_and_emit.cwl
    in:
      bioclient_config: bioclient_config
      bioclient_load_bucket: bioclient_load_bucket
      upload_prefix: upload_prefix
      job_uuid: job_uuid
      input_file: run_vep/stats_out_file
    out: [ indexd_uuid ]
