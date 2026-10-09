#!/usr/bin/env python3
"""Generate the complete relaxed word language through length4; no old parser."""
from pathlib import Path
from itertools import product,permutations
from datetime import datetime,timezone
import hashlib,json
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def main():
 for rel,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
 s=json.loads((D/'src/SPEC.json').read_text())
 assert len(s['glyphs'])==22 and len(set(s['glyphs']))==22
 assert s['statement_marker']=='m' and s['inflection_marker']=='y'
 assert s['literal_start']=='l' and s['literal_end']=='r'
 # (sign sequence, open argument count, complete nominal, bare builder)
 cores={(tuple(r['glyphs']),r['arity'],r['arity']==0,False) for r in s['roots']}
 cores|={(tuple(r),0,True,False) for r in s['references']}
 for k in (1,2):
  for letters in product(s['letters'],repeat=k):
   body=tuple(g for code in letters for g in code)
   if len(body)<=2:cores.add((('l',)+body+('r',),0,True,False))
 cores|={((g,),v['arity'],False,True) for g,v in s['builders'].items()}
 changed=True
 while changed:
  before=set(cores)
  inner=[c for c in before if not c[3]]
  for bits,holes,nominal,bare in inner:
   if len(bits)+1<=4:
    if holes==0 and nominal:
     cores.add((('n',)+bits,0,True,False))
     cores.add((('a',)+bits,1,False,False))
    if holes==1:cores.add((('o',)+bits,2,False,False))
  # Nominal ORIGIN/KIND need 1+2+2 signs minimum; QUOTE needs5.
  # Neither contributes a core of length<=4. Bare versions are already present.
  changed=cores!=before
 words=set()
 for bits,holes,nominal,bare in cores:
  if len(bits)>4:continue
  words.add(bits)
  for count in range(1,4-len(bits)):
   for tags in product(s['tags'],repeat=count):words.add(bits+('y',)+tags)
 words|={('m',)+w for w in list(words) if len(w)<4}
 r=json.loads((A/'RESULT.json').read_text());expected=[]
 for a,b in permutations(s['glyphs'],2):
  base=(a,b) in words;double=(a,b,a,b) in words
  expected.append({'A':a,'B':b,'base_readable':base,'double_readable':double,'both_readable':base and double})
 assert r['grid']==expected and len(expected)==462
 for field,key in [('base_readable_pairs','base_readable'),('double_readable_pairs','double_readable'),('joint_readable_pairs','both_readable')]:assert r[field]==sum(x[key] for x in expected)
 assert r['status']==('NO_SHORT_SQUARE_GRAMMAR_RENAMING' if not any(x['both_readable'] for x in expected) else 'SHORT_SQUARE_GRAMMAR_RENAMING_NOT_EXCLUDED')
 old=json.loads((ROOT/'research_registry/proposals/production_origin_supply_20261003/PAIRED_PIECE_GLOBAL_UD_RESULT_20261005.json').read_text())
 assert r['binding']==[{'edition':w['edition'],'base_id':w['base']['source_group_id'],'double_id':w['double']['source_group_id'],'base':w['base']['ivtff_group_raw'],'double':w['double']['ivtff_group_raw']} for w in old['witnesses']]
 out={'status':'PASS','same_author':True,'old_parser_imported':False,'finite_relaxed_words_length_at_most4':len(words),'ordered_pairs_checked':462,'exact_prior_witnesses':6,'method':'Independent generation of all fixed-grammar short cores, inflection tails and optional statement prefixes; every462 result cell agrees.','claim_ceiling':'Fixed grammar accounting and inherited literal binding, not new image review or native semantic evidence.','completed_utc':datetime.now(timezone.utc).isoformat()}
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
