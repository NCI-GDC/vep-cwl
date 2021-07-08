cwlVersion: v1.0
class: Workflow
id: gdc_annotation_upload_and_emit_wf
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
  upload_prefix:
    type: string?
    doc: the s3 key prefix
  job_uuid:
    type: string
    doc: the job uuid which will come after the upload_prefix
  input_file:
    type: File
    doc: the file you want to upload

outputs:
  indexd_uuid:
    type: string
    outputSource: extract_indexd_info/output

steps:
  upload_file:
    run: ../../../tools/bio_client_upload_pull_uuid.cwl
    in:
      config_file: bioclient_config
      local_file: input_file
      upload_bucket: bioclient_load_bucket
      upload_key:
        source: [upload_prefix, job_uuid, input_file]
        valueFrom: |
          ${
             var pfx = self[0] ? self[0] + '/' : "";
             return pfx + self[1] + '/' + self[2].basename
           }
    out: [ output ]

  extract_indexd_info:
    run: ../../../tools/emit_json_value.cwl
    in:
      input: upload_file/output
      key:
        default: 'did'
    out: [ output ]
