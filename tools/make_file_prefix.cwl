#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

class: ExpressionTool

inputs:
  project_id:
    type: string?

  aliquot_id:
    type: string

  experimental_strategy:
    type: string

outputs:
  output:
    type: string 

expression: |
  ${
     var exp = inputs.experimental_strategy.toLowerCase().replace(/[-\s]/g, "_");

     var pfx = inputs.project_id 
       ? inputs.project_id + '.' + inputs.aliquot_id + '.' + exp
       : inputs.aliquot_id + '.' + exp;

     return {'output': pfx};
   }
