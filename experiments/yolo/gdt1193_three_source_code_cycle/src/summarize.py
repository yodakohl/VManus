"""Post-fit reporting of registered results and already cached extra diagnostics."""
from pathlib import Path
import json
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts';r=json.loads((A/'RESULT.json').read_text());s=r['selected'];assert s;targets=json.loads((ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json').read_text())['targets'];source=json.loads((ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text());diagnostics=['q_followed_o','q_count','y_final','word_entropy','glyph_entropy'];extras={group:{name:{k:value[k] for k in diagnostics} for name,value in data.items()} for group,data in [('cached_target',targets),('fixed_writer',s['metrics'])]};extras['scope']='Descriptive post-fit critique using existing cached metrics. Not a preregistered extra gate, refit, independent test or native discovery. Original basic-screen pass retained.';(A/'EXTRA_DIAGNOSTICS.json').write_text(json.dumps(extras,indent=2)+'\n')
keys=['mean_length','sd_length','top10_share','type_ratio','conditional_entropy','exact_repeat','edit1_repeat','first_last_js','length_tv','glyph_js'];rows=['book\treader\tmetric\tdifference\tlimit\tpass']
for b,comparisons in s['comparison'].items():
 for ed,cc in comparisons.items():
  for key in keys:
   d=cc['diagnostics'][key];rows.append('\t'.join(map(str,[b,ed,key,d['difference'],d['limit'],d['difference']<=d['limit']])))
  diff=abs(s['metrics'][b]['edit1_repeat']-targets[ed]['edit1_repeat']);rows.append('\t'.join(map(str,[b,ed,'edit1_tight',diff,.01,diff<=.01])))
(A/'SCREEN.tsv').write_text('\n'.join(rows)+'\n')
summary={'registered_screen':'PASS','source_books':len(source),'source_recipes':sum(map(len,source.values())),'source_words':sum(len(rec['words']) for rs in source.values() for rec in rs),'sample_groups_per_book':8000,'alternate_readers':len(targets),'comparisons_are_not_independent':True,'public_table_entries':2130,'candidate_cycle':s['cycle'],'complete_recipe_roundtrips':s['complete_recipe_roundtrips'],'actual_sample_glyph_counts':{b:len(m['glyph_counts']) for b,m in s['metrics'].items()},'additional_diagnostics':'q-to-o, final-y and marginal glyph entropy remain visibly mismatched; no historical/native adoption'};(A/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
