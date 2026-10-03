#!/usr/bin/env python3
"""Mechanical fixed windows; no semantic inference. Full text stays external."""
import argparse, hashlib, json, re
from pathlib import Path
EXP=Path(__file__).resolve().parents[1]
def digest(b): return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);a=p.parse_args()
 source=json.loads((a.cache/'annotation_units.json').read_text())
 meta=json.loads((EXP/'artifacts/SOURCE_UNITS.json').read_text())
 rows=[]
 for work,body in source['bodies'].items():
  text=body['text']; assert digest(text.encode())==meta['bodies'][work]['text_sha256']
  tokens=list(re.finditer(r'\S+',text))
  assert len(tokens)==body['words']
  for start in range(0,len(tokens),100):
   stop=min(start+100,len(tokens)); lo=tokens[start].start();hi=tokens[stop-1].end()
   snippet=text[lo:hi]
   rows.append(dict(id=f'{work}:{start//100+1:04d}',work=work,index=start//100,
      word_start=start,word_end=stop,char_start=lo,char_end=hi,text=snippet,
      text_sha256=digest(snippet.encode()),
      source_units=[u['unit_id'] for u in source['units'] if u['work']==work and u['body_word_start']<stop and u['body_word_end_exclusive']>start]))
 (a.cache/'windows.json').write_text(json.dumps({'windows':rows},ensure_ascii=False,indent=2)+'\n')
 public={'base_words':100,'scales':[100,200,400],'complete_works':list(source['bodies']),
   'windows':[{k:v for k,v in r.items() if k!='text'} for r in rows]}
 (EXP/'artifacts/WINDOWS.json').write_text(json.dumps(public,indent=2)+'\n')
 print({w:sum(r['work']==w for r in rows) for w in source['bodies']})
if __name__=='__main__': main()
