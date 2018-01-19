#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: SubworkflowFeatureRequirement

inputs:
  bioclient_config:
    type: File
    doc: Bioclient configuration file
  bioclient_load_bucket:
    type: string
    doc: Bucket to load files to
  input_vcf_gdc_id: string
  input_vep_fasta_gdc_id: string
  input_vep_fasta_fai_gdc_id: string
  input_vep_fasta_gzi_gdc_id: string
  input_vep_cache_gdc_id: string
  input_vep_entrez_json_gdc_id: string
  input_vep_evidence_vcf_gdc_id: string
  input_vep_evidence_index_gdc_id: string
  job_uuid: string
  upload_prefix:
    type: string?
    doc: optional s3 key prefix
  threads:
    type: int
    default: 1

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
  indexd_vep_time_uuid:
    type: string
    outputSource: upload_vep_time/indexd_uuid 

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

  run_vep:
    run: ../tools/vep.cwl
    in:
      input_file: stage_workflow/input_vcf 
      fasta: stage_workflow/vep_reference 
      dir_cache: stage_workflow/vep_cache 
      tabix:
        default: true
      output_file:
        source: job_uuid
        valueFrom: $(self + '.vep.vcf.gz')
      vcf:
        default: true 
      stats_file:
        source: job_uuid
        valueFrom: $(self + '.vep.stats.txt')
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
      assembly:
        default: "GRCh38" 
      gdc_entrez: stage_workflow/vep_entrez_json 
      gdc_evidence: stage_workflow/vep_evidence_vcf 
    out: [ vep_out, vep_index_out, stats_out_file, warning_out_file, time_file ]

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

  upload_vep_time:
    run: ./subworkflows/upload_and_emit.cwl
    in:
      bioclient_config: bioclient_config
      bioclient_load_bucket: bioclient_load_bucket
      upload_prefix: upload_prefix
      job_uuid: job_uuid
      input_file: run_vep/time_file
    out: [ indexd_uuid ]
