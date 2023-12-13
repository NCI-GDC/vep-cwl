cwlVersion: v1.0
class: CommandLineTool
id: make_pair
requirements:
  - class: DockerRequirement
    dockerPull: "{{ docker_repo }}/bio-alpine:{{ bio_alpine }}"
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entryname: $(inputs.parent_file.basename)
        entry: $(inputs.parent_file)
      - entryname: $(inputs.children.basename)
        entry: $(inputs.children)

inputs:
  parent_file: 
    type: File
  children: 
    type: File

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.parent_file.basename)
    secondaryFiles: 
      - ^.tbi  

baseCommand: "true"
