#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: Untar a tar.gz

requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/tar-tool:latest
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - $(inputs.input_tar)

class: CommandLineTool

inputs:
  input_tar:
    type: File
    doc: The tarfile to process
    inputBinding:
      position: 0
      valueFrom: $(self.basename)

outputs:
  out_directory:
    type: Directory
    outputBinding:
      glob: $(inputs.input_tar.basename.substr(0, inputs.input_tar.basename.lastIndexOf('.tar.gz')))

baseCommand: [/bin/tar, -xf]
