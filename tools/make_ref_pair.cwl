cwlVersion: v1.0
class: CommandLineTool
id: make_pair
requirements:
  - class: DockerRequirement
    dockerPull: alpine
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entryname: $(inputs.fa_file.basename)
        entry: $(inputs.parent_file)
      - entryname: $(inputs.gzi_file.basename)
        entry: $(inputs.gzi_file)
      - entryname: $(inputs.fai_file.basename)
        entry: $(inputs.fai_file)

inputs:
  fa_file: 
    type: File
  gzi_file: 
    type: File
  fai_file:
    type: File

outputs:
  output:
    type: File
    outputBinding:
      glob: $(inputs.parent_file.basename)
    secondaryFiles: 
      - ^.fai
      - ^.gzi  

baseCommand: "true"
