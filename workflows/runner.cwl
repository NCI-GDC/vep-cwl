#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement

inputs:
  bioclient_config:
	type: File
	doc: Bioclient configuration file
  bioclient_load_bucket:
	type: string
	doc: Bucket to load files to
  input_vcf_gdc_id: string
  input_vep_fasta_gdc_id: string
  input_vep_fasta_index_gdc_id: string
  input_vep_cache_gdc_id: string
  input_vep_entrez_json_gdc_id: string
  input_vep_evidence_vcf_gdc_id: string
  input_vep_evidence_index_gdc_id: string
  job_uuid: string

outputs:
  indexd_vcf_uuid:
	type: string
	outputSource: emit_vcf_uuid/output
  indexd_vcf_index_uuid:
	type: string
	outputSource: emit_vcf_index_uuid/output
  indexd_vep_stats_uuid:
	type: string
	outputSource: emit_vep_stats_uuid/output

steps:
  extract_cache:
	run: ../tools/bio_client_download.cwl
	in:
	  config-file: bioclient_config
	  download_handle: vep_cache_gdc_id
	out: [ output ]

  decompress_cache:
    run: ../tools/untar.cwl
    in:
      input_tar: extract_cache/output
    out: [ out_directory ]

  extract_vcf:
	run: ../tools/bio_client_download.cwl
	in:
	  config-file: bioclient_config
	  download_handle: input_vcf_gdc_id
	out: [ output ]

  extract_fasta:
	run: ../tools/bio_client_download.cwl
	in:
	  config-file: bioclient_config
	  download_handle: input_vep_fasta_gdc_id
	out: [ output ]

  extract_fasta_index:
	run: ../tools/bio_client_download.cwl
	in:
	  config-file: bioclient_config
	  download_handle: input_vep_fasta_index_gdc_id
	out: [ output ]

  make_vep_ref:
    run: ../tools/make_pair.cwl
    in:
      parent_file: extract_fasta/output
      child_file: extract_fasta_index/output
    out: [ output ]

  extract_entrez:
	run: ../tools/bio_client_download.cwl
	in:
	  config-file: bioclient_config
	  download_handle: input_vep_entrez_json_gdc_id
	out: [ output ]

  extract_evidence_vcf:
	run: ../tools/bio_client_download.cwl
	in:
	  config-file: bioclient_config
	  download_handle: input_vep_evidence_vcf_gdc_id
	out: [ output ]

  extract_evidence_vcf_index:
	run: ../tools/bio_client_download.cwl
	in:
	  config-file: bioclient_config
	  download_handle: input_vep_evidence_index_gdc_id
	out: [ output ]

  make_vep_evidence:
    run: ../tools/make_pair.cwl
    in:
      parent_file: extract_evidence_vcf/output
      child_file: extract_evidence_vcf_index/output
    out: [ output ]

  run_vep:
    run: ../tools/vep.cwl
    in:
      input_file: extract_vcf/output
      fasta: make_vep_ref/output
      dir_cache: decompress_cache/out_directory
      output_file:
        source: [run_uuid]
        valueFrom: "$(self[0] + '.vep.vcf')"
      vcf:
        default: true 
      stats_file:
        source: [run_uuid]
        valueFrom: "$(self[0] + '.vep.stats.txt')"
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
      gdc_entrez: extract_entrez/output 
      gdc_evidence: make_vep_evidence/output 
    out: [ vep_out, stats_file, warning_file, time_file ]
