#!/usr/bin/env python3
"""Reuse the unchanged GDT893 matcher; screen its windows by a fixed word map."""
import argparse,csv,gzip,hashlib,json,re,subprocess,tempfile
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parent.parent; ROOT=E.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
def records(p,rs,ids):
 with p.open('w') as f:
  f.write(str(len(rs))+'\n')
  for r in rs:f.write(r['id']+' '+str(len(r['words']))+' '+' '.join(str(ids[w]) for w in r['words'])+'\n')
def conflict(words,plain,key):
 rev={v:k for k,v in key.items()}
 for i,(w,v) in enumerate(zip(words,plain)):
  if w in key and key[w]!=v:return ('forward',w,i)
  if v in rev and rev[v]!=w:return ('inverse',rev[v],i)
 return None

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=E/'artifacts');a=ap.parse_args();out=a.output_dir;out.mkdir(parents=True,exist_ok=True)
 assert not (out/'RESULT.json').exists(),'refuse result overwrite'
 spec=json.loads((E/'src/SOURCE.json').read_text())
 for b in spec['inputs']:assert sha(ROOT/b['path'])==b['sha256'],b['path']
 src=E/'artifacts/SOURCE_UNITS.json';assert sha(src)==spec['source_units_sha256']
 original=ROOT/'experiments/yolo/gdt893_global_source_montage_word_code'
 lock=json.loads((original/'artifacts/INPUT_LOCK.json').read_text());assert sha(src)==lock['source_units_sha256']
 units=json.loads(src.read_text())['units'];assert len(units)==1318 and sum(len(u['words']) for u in units)==153031
 key=json.loads((original/'artifacts/RF_FORCED_SOURCE.json').read_text())['conditional_global_map'];assert len(key)==len(set(key.values()))==26
 frames=json.loads((ROOT/lock['target_cache_path']).read_text())['frames'];panels={ed:[] for ed in spec['editions']};intake=Counter();pred=[]
 for f in frames:
  assert re.fullmatch('f[0-9]+',f['physical_folio']);assert not f['page'].startswith('f84')
  leaf=int(f['physical_folio'][1:])
  if leaf%2: intake['odd_frames_not_screened']+=1;continue
  intake['even_frames']+=1
  for ed in panels:
   reading=f['readings'][ed]
   if not reading['eligible']:intake[ed+'_ineligible']+=1;continue
   gs=reading['groups'];assert gs and all(g['kind']=='P' and re.fullmatch('[a-z]+',g['raw']) for g in gs)
   words=[g['raw'] for g in gs];known=sorted(set(words)&key.keys())
   row=dict(id=f['paragraph_id'],page=f['page'],physical_folio=f['physical_folio'],fold='A' if leaf%4==0 else 'B',words=words,source_group_ids=[g['source_group_id'] for g in gs],locked_types=known,locked_tokens=sum(w in key for w in words),informative=len(known)>=2)
   panels[ed].append(row)
   for i,g in enumerate(gs):pred.append(dict(edition=ed,paragraph=row['id'],page=row['page'],physical_folio=row['physical_folio'],fold=row['fold'],index=i,source_group_id=g['source_group_id'],cipher_word=g['raw'],prediction=key.get(g['raw'],'UNKNOWN')))
 # Complete predictions are emitted and hashed before any source-window matching.
 dump(out/'PREDICTION_PACKET.json',dict(schema='GDT923_FROZEN_KEY_PREDICTIONS',key=key,intake=dict(intake),panels=panels))
 with (out/'PREDICTIONS.tsv').open('w') as f:
  writer=csv.DictWriter(f,fieldnames=['edition','paragraph','page','physical_folio','fold','index','source_group_id','cipher_word','prediction'],delimiter='\t');writer.writeheader();writer.writerows(pred)
 dump(out/'PREDICTION_LOCK.json',{p.name:sha(p) for p in [out/'PREDICTION_PACKET.json',out/'PREDICTIONS.tsv']})
 results={};all_rows=[];witnesses=[];perkey={ed:{k:dict(value=v,paragraphs=0,positions=0,first_forward_conflicts=0,first_inverse_conflicts=0,compatible_paragraphs=0) for k,v in key.items()} for ed in panels}
 with tempfile.TemporaryDirectory(prefix='gdt923_') as tmp:
  tmp=Path(tmp);binary=tmp/'match';subprocess.run(['g++','-O3','-std=c++17','-fopenmp',str(original/'src/match.cpp'),'-o',str(binary)],check=True)
  si={w:i for i,w in enumerate(sorted({w for u in units for w in u['words']}))};records(tmp/'SOURCE.txt',units,si)
  for ed,rows in panels.items():
   ci={w:i for i,w in enumerate(sorted({w for r in rows for w in r['words']}))};records(tmp/'TARGET.txt',rows,ci)
   proc=subprocess.run([str(binary),str(tmp/'TARGET.txt'),str(tmp/'SOURCE.txt'),str(tmp/'MATCHES.csv')],check=True,capture_output=True,text=True);matcher=json.loads(proc.stdout)
   stats=[dict(edition=ed,paragraph=r['id'],page=r['page'],physical_folio=r['physical_folio'],fold=r['fold'],length=len(r['words']),locked_tokens=r['locked_tokens'],locked_types=len(r['locked_types']),informative=r['informative'],baseline_windows=0,compatible_windows=0,distinct_compatible_plaintexts=0,first_conflicts={}) for r in rows];hashsets=[set() for _ in rows];conflicts=[Counter() for _ in rows]
   raw=(tmp/'MATCHES.csv').read_bytes();(out/(ed+'_BASELINE_WINDOWS.csv.gz')).write_bytes(gzip.compress(raw,mtime=0))
   with (tmp/'MATCHES.csv').open() as f:
    for m in csv.DictReader(f):
     ti,ui,start,n=(int(m[k]) for k in ['target_index','source_index','start','length']);r=rows[ti];u=units[ui];plain=u['words'][start:start+n];assert n==len(r['words'])==len(plain)
     stats[ti]['baseline_windows']+=1;fail=conflict(r['words'],plain,key)
     if fail:
      direction,k,i=fail;conflicts[ti][direction+':'+k]+=1;perkey[ed][k]['first_'+direction+'_conflicts']+=1
     else:
      stats[ti]['compatible_windows']+=1;digest=hashlib.sha256(json.dumps(plain,ensure_ascii=False,separators=(',',':')).encode()).hexdigest();hashsets[ti].add(digest)
      witnesses.append(dict(edition=ed,paragraph=r['id'],source=u['source'],unit=u['id'],start=start,length=n,plaintext_sha256=digest,informative=r['informative']))
   for i,(r,s) in enumerate(zip(rows,stats)):
    s['distinct_compatible_plaintexts']=len(hashsets[i]);s['first_conflicts']=dict(conflicts[i]);assert s['baseline_windows']==s['compatible_windows']+sum(conflicts[i].values())
    s['outcome']='COMPATIBLE' if s['compatible_windows'] else 'FIXED_KEY_CONTRADICTION' if s['baseline_windows'] else 'NO_BASELINE_PATTERN_WINDOW'
    for k in r['locked_types']:
     perkey[ed][k]['paragraphs']+=1;perkey[ed][k]['positions']+=r['words'].count(k);perkey[ed][k]['compatible_paragraphs']+=bool(s['compatible_windows'])
   def summary(sub):
    info=[s for s in sub if s['informative']];return dict(paragraphs=len(sub),physical_leaves=len({s['physical_folio'] for s in sub}),informative_paragraphs=len(info),informative_leaves=len({s['physical_folio'] for s in info}),baseline_positive_paragraphs=sum(s['baseline_windows']>0 for s in sub),informative_baseline_positive=sum(s['baseline_windows']>0 for s in info),compatible_paragraphs=sum(s['compatible_windows']>0 for s in sub),informative_compatible_paragraphs=sum(s['compatible_windows']>0 for s in info),informative_compatible_leaves=len({s['physical_folio'] for s in info if s['compatible_windows']}),baseline_windows=sum(s['baseline_windows'] for s in sub),compatible_windows=sum(s['compatible_windows'] for s in sub),zero_key_paragraphs=sum(s['locked_types']==0 for s in sub),one_key_paragraphs=sum(s['locked_types']==1 for s in sub))
   result=summary(stats);result['folds']={fold:summary([s for s in stats if s['fold']==fold]) for fold in ['A','B']};result['matcher']=matcher;results[ed]=result;all_rows+=stats
 rf=results['RF1b'];status='CAPACITY_STOP' if not rf['informative_paragraphs'] else 'HAS_INFORMATIVE_COMPATIBILITY' if rf['informative_compatible_paragraphs'] else 'NO_INFORMATIVE_COMPATIBILITY'
 dump(out/'PARAGRAPH_RESULTS.json',all_rows);dump(out/'WITNESSES.json',witnesses);dump(out/'KEY_RESULTS.json',perkey)
 with (out/'PARAGRAPH_RESULTS.tsv').open('w') as f:
  fields=[k for k in all_rows[0] if k!='first_conflicts'] if all_rows else ['edition','paragraph'];wr=csv.DictWriter(f,fieldnames=fields,delimiter='\t',extrasaction='ignore');wr.writeheader();wr.writerows(all_rows)
 result=dict(status=status,panels=results,intake=dict(intake),prediction_lock_sha256=sha(out/'PREDICTION_LOCK.json'),confirmed_meanings=0,limitation='Per-paragraph existential compatibility only, not a joint extended key or the GDT893 held-decoding gate. No significance.');dump(out/'RESULT.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
