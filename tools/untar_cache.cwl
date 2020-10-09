cwlVersion: v1.0
class: CommandLineTool
id: untar_cache
requirements:
  - class: DockerRequirement
    dockerPull: alpine
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing: |
      ${
           return [{"entry": {"class": "Directory", "basename": inputs.cache_dir, "listing": []}, "writable": true}]
       }
  - class: ResourceRequirement
    coresMin: 1
    ramMin: 1024

inputs:
  cache_dir:
    type: string?
    default: "cache"
    inputBinding:
      position: 0
      prefix: -C

  input_tar:
    type: File
    doc: The tarfile to process
    inputBinding:
      position: 1
      prefix: -f

outputs:
  out_directory:
    type: Directory
    outputBinding:
      glob: $(inputs.cache_dir)

baseCommand: [/bin/tar, -xz]
