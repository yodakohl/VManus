"""Necessary two-terminal capacity on three prior source-bound groups only."""
from pathlib import Path
import json,hashlib
from functools import lru_cache
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 cp=P/'HAND_WRITER_IDEA940_CONTRACT_20261005.json';c=json.loads(cp.read_text())
 for p,h in c['files'].items():assert sha(ROOT/p)==h,p
 raw=json.loads((P/'HUMAN_SOURCE_EIGHT_FRAGMENT_CACHE_RAW_20261005.json').read_text());book=raw['design']['concrete_carrier'];alphabet=book['working_glyphs'];assert len(alphabet)==len(set(alphabet))==22
 markers=[book['end_sign'],book['continue_sign']];assert len(set(markers))==2 and set(markers)<=set(alphabet)
 @lru_cache(None)
 def parses(s):
  if not s:return [()]
  return [(a,)+r for a in alphabet if s.startswith(a) for r in parses(s[len(a):])]
 lines=json.loads((ROOT/'experiments/yolo/gdt1208_f45r_repeated_dal_body/artifacts/TARGET_LINES.json').read_text());assert len(lines)==3
 out=[]
 for code,form in c['targets'].items():
  evidence=[]
  for line in lines:
   assert line['locus']==c['locus'];gg=[g for g in line['groups'] if g['source_group_id'].endswith('|'+code)];assert len(gg)==1
   g=gg[0];assert g['ivtff_group_raw']==form and g['left_separator']=='DEFINITE_SPACE' and g['right_separator'] in {'DEFINITE_SPACE','LINE_END'};evidence.append(g)
  pp=parses(form);assert pp
  out.append({'form':form,'source_groups':evidence,'all_working_glyph_parses':[list(p) for p in pp],'possible_terminal_glyphs':sorted({p[-1] for p in pp})})
 assert {g['edition'] for g in out[0]['source_groups']}=={'ZL3b','IT2a','RF1b'}
 forced={r['possible_terminal_glyphs'][0] for r in out if len(r['possible_terminal_glyphs'])==1}
 status='FIXED_WORKING_INVENTORY_TWO_TERMINALS_CONTRADICTED' if len(forced)>len(markers) else 'TERMINAL_BOUND_NOT_CONTRADICTED'
 r={'status':status,'contract_sha256':sha(cp),'runner_sha256':sha(Path(__file__)),'working_inventory':alphabet,'original_final_markers':markers,'forced_target_terminals':sorted(forced),'anchors':out,'fixed_bijective_relabeling_also_excluded':status.endswith('CONTRADICTED') and status!='TERMINAL_BOUND_NOT_CONTRADICTED','reset_independent':True,'native_atom_binding_proven':False,'native_meanings_assigned':0,'new_manuscript_discovery':False,'new_frequency_census':False,'independent_confirmation_capacity':0}
 (P/'HAND_WRITER_IDEA940_RESULT_20261005.json').write_text(json.dumps(r,indent=2)+'\n')
 print(json.dumps({k:r[k] for k in ['status','original_final_markers','forced_target_terminals','fixed_bijective_relabeling_also_excluded','reset_independent']},indent=2))
if __name__=='__main__':main()
