#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: DockerRequirement
    dockerPull: alpine
  - class: InitialWorkDirRequirement
    listing:
      - entryname: $(inputs.parent_file.basename)
        entry: $(input.parent_file)
      - entryname: $(inputs.child_file.basename)
        entry: $(input.child_file)

class: CommandLineTool

inputs:
  parent_file:
    type: File

  child_file:
    type: file

outputs:
  output:
    type: File
    outputBinding:
      glob: |
        ${
           return {"class": "File", "path": inputs.parent_file.basename, 
                   "secondaryFiles": [{"class": "File", "path": inputs.child_file.basename}]} 
         }

baseCommand: "true"
