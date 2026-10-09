# GDT1188 — direct greedy dictionary works reversibly, all nine statistical designs fail

All nine systems preserve every word of all1054 recipes, with a simpler longest-match writing rule instead of ordered merge passes. None passes all necessary conditions across the four exposed books. No alphabet fitting ran;9486 whole-recipe roundtrips are an engineering validation, not a statistical pass.
| T512 source | edit1 | mean | SD | type share |
|---|---:|---:|---:|---:|
| b4 | 0.03872406 | 3.64262 | 0.73852 | 0.14838 |
| w1 | 0.03778057 | 3.64538 | 0.74052 | 0.14113 |
| bs1 | 0.03380164 | 3.62712 | 0.75670 | 0.13337 |
| gr1 | 0.03691322 | 3.66012 | 0.74707 | 0.12512 |


The H codes retain the previous pattern:512 inventory has too little diversity;1024 fails bs1/gr1 diversity;2048 fails gr1 length-TV (IT0.215375,RF0.213125,ZL0.200625 versus unchanged0.20). Even the small ZL miss remains failed.

Dense R/T codebooks can naturally reach adjacent edit-one rates around3–6% under the fixed alphabet; they fail length distribution and word-form diversity. For example T512 has edit1 rates in the table above, but means3.63–3.66, SD0.74–0.76 and type ratios0.125–0.148. R2048 type ratio is only0.196–0.206. These partial positives are not full fits or selected candidates. Exact values are in RESULT.json.

Mechanistic account: dense allocation fills all7initial values for each ternary body. Counter rotation then makes multiple different source fragments share the same visible form in different contexts, constraining the total visible vocabulary. Inverse decoding remains unique given public prior state, but public source reversibility alone does not preserve word-form diversity. A potential different design would deliberately reserve some initial alternatives for contextual spelling rather than filling all of them with different source entries. That is not executed here and requires a new fixed grid; no threshold repair.

Human improvement is limited but concrete: an indexed forward dictionary now supports longest matching at the current source position; its whole ordered merge list is no longer executed. Reverse dictionary lookup and six-state counter remain necessary; large table size and desynchronization after omissions remain. No independent manual test or historical use is established. No native word values or manuscript/reserve access. Local checkpoint.
