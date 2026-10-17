#!/usr/bin/env python3
"""Replay known singleton witnesses and a conditional source-code completion bound."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,runpy
D=Path(__file__).resolve().parent;ROOT=D.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 note=json.loads((D/'GERMAN14_COMPLETION_NOTE_20261017.json').read_text())
 for p,h in note['pins'].items():assert sha(ROOT/p)==h,p
 raw=json.loads((D/'GERMAN14_RAW_TABLE_20261017.json').read_text());encode=runpy.run_path(str(D/'GERMAN14_FORWARD_20261017.py'))['encode']
 for r in raw['source_word_output_pairs']:assert encode(r['source_word'])==r['output_raw_form']
 assert encode('e')=='y' and encode('n')=='in' and encode('s')=='q'
 path=ROOT/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
 data=json.loads(gzip.decompress(path.read_bytes()));by_reader={}
 for ed,rows in data.items():
  assert ed in ['IT2a','ZL3b','RF1b']
  selected={s:[] for s in ['a','k','l']}
  for r in rows:
   assert not r['page'].startswith('f84') and r['page'] not in ['f116v','f1r']
   if r['ivtff_group_raw'] not in selected:continue
   assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE'
   assert r['units']==[r['ivtff_group_raw']]
   selected[r['ivtff_group_raw']].append(r)
  by_reader[ed]={'strict_counts':{s:len(rs) for s,rs in selected.items()},'witnesses':selected,'exclusive_completion_excluded':bool(selected['a'] or selected['k'] or selected['l'])}
 # Countermodel: same codeword at disjoint source positions need not break a
 # word-level inverse on a specified lexicon. All fourteen old rows survive.
 words=[r['source_word'] for r in raw['source_word_output_pairs']]+['x','ee']
 outputs={w:('a' if w=='x' else encode(w)) for w in words}
 assert len(set(outputs.values()))==len(outputs)
 models={'alias':{'extra_rule':'new source x emits a','word_outputs':outputs,'all_16_words_have_distinct_outputs':True,'limit':'Source-free finite lexicon witness only; not a German reading or universal uniquely decodable code.'},'null':{'word':'ex','tokens':[{'origin':'E_nonfinal','output':'a'},{'origin':'X_final','output':''}],'output':'a','relaxed_assumption':'nonempty emissions'},'boundary':{'source_word':'ee','source_output':encode('ee'),'split_visible_groups':['a','y'],'relaxed_assumption':'one complete source word per visible group'},'S_single_priority':{'old_source_s_output':encode('s'),'alternative_final_priority_output':'l','all14_source_words_have_length_at_least3':all(len(w)>=3 for w in words[:14]),'limit':'An alternate one-letter-S priority does not affect the14fits but changes the frozen encoder. A/E obstruction does not depend on this choice.'}}
 out={'status':'EXCLUSIVE_NONEMPTY_COMPLETION_EXCLUDED_ON_EACH_CACHED_PANEL','basis':'One-symbol target + nonempty emissions implies exactly one source token. Exclusive origin must be legal as a complete word; E_nonfinal/N_nonfinal are not; singleton S emits q under frozen priority. No sourcebook, prefix or free-UD assumption.','source_cache_sha256':sha(path),'note_sha256':sha(D/'GERMAN14_COMPLETION_NOTE_20261017.json'),'panels':by_reader,'countermodels':models,'native_word_meanings_assigned':0,'limits':['Conditional on original group/working-unit boundaries; no new palaeography.','Common a is one physical locus, not three confirmations.','l supports only the frozen singleton-S priority; changing it does not repair a.','Origin-exclusive completion is an added submodel; contextual aliases remain open and can preserve word-level uniqueness.','No general German, phonetic or arbitrary-code exclusion; parent raw proposal remains inconclusive.']}
 print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
