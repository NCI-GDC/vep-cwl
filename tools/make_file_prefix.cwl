cwlVersion: v1.0
class: ExpressionTool
id: make_file_prefix
requirements:
  - class: InlineJavascriptRequirement

inputs:
  project_id: string?

  caller_id: string?

  job_id: string

  experimental_strategy: string

outputs:
  output: string

expression: |
  ${

     function cleanString( rawstring, makeLower ) {
         var curr = rawstring.replace(" - ", " ").replace(/\s/g, "_").replace("-", "_");
         var res = makeLower ? curr.toLowerCase() : curr;
         return res
     }

     var exp = cleanString(inputs.experimental_strategy, true);

     var pid = inputs.project_id ? cleanString(inputs.project_id, false) + '.': '';
     var cid = inputs.caller_id ? '.' + cleanString(inputs.caller_id, false) : '';
     var pfx = pid + inputs.job_id + '.' + exp + cid;

     return {'output': pfx};
   }
