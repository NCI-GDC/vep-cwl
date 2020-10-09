cwlVersion: v1.0
class: Workflow
id: gdc_main_annotation_wf
requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  input_vcf: File
  input_vep_reference:
    type: File
    secondaryFiles:
      - .fai
      - .gzi
  input_vep_cache: Directory
  input_vep_entrez_json: File
  input_vep_evidence_vcf:
    type: File
    secondaryFiles:
      - .tbi
  output_filename_base: string
  threads: int?

outputs:
  annotated_vcf:
    type: File
    outputSource: run_vep/vep_out
  annotated_vcf_index:
    type: File?
    outputSource: run_vep/vep_index_out
  vep_stats:
    type: File?
    outputSource: run_vep/stats_out_file
  vep_warning:
    type: File?
    outputSource: run_vep/warning_out_file

steps:
  run_vep:
    run: ../../tools/vep.cwl
    in:
      input_file: input_vcf
      fasta: input_vep_reference
      dir_cache: input_vep_cache
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
        source: output_filename_base
        valueFrom: $(self + '.somatic_annotation.vcf.gz')
      vcf:
        default: true 
      stats_file:
        source: output_filename_base
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
      gdc_entrez: input_vep_entrez_json
      gdc_evidence: input_vep_evidence_vcf
    out: [ vep_out, vep_index_out, stats_out_file, warning_out_file ]
