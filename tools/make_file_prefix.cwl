#!/usr/bin/env cwl-runner

cwlVersion: v1.0

requirements:
  - class: InlineJavascriptRequirement

class: ExpressionTool

inputs:
  project_id:
    type: string?

  caller_id:
    type: string?

  job_id:
    type: string

  experimental_strategy:
    type: string

outputs:
  output:
    type: string

expression: |
  ${

     function cleanString( rawstring, makeLower ) {
         var curr = rawstring.replace(" - ", " ").replace(" ", "_").replace("-", "_");
         var res = makeLower ? curr.toLowerCase() : curr;
         return res
     }

     var exp = cleanString(inputs.experimental_strategy, true);

     var pid = inputs.project_id ? cleanString(inputs.project_id, false) + '.': '';
     var cid = inputs.caller_id ? '.' + cleanString(inputs.caller_id, false) : '';
     var pfx = pid + inputs.job_id + '.' + exp + cid;

     return {'output': pfx};
   }
