#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import hashlib,json,unicodedata,xml.etree.ElementTree as E
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def local(n):return n.tag.rsplit('}',1)[-1]
def text(n):
 out=n.text or ''
 for c in n:
  if local(c)!='note':out+=text(c)
  out+=c.tail or ''
 return out

def partition(words,join):
 result=[];pending=[]
 for w in words:
  pending.append(w)
  if w not in join:result.append(pending);pending=[]
 if pending:result.append(pending)
 return result

def metrics(groups,n):
 flat=[tuple(g) for row in groups for g in row][:n]
 if len(flat)!=n:return {'status':'INSUFFICIENT_GROUPS','available':len(flat)}
 c=Counter(flat)
 return {'status':'MEASURED','groups':n,'types':len(c),'type_ratio':len(c)/n,'top10_share':sum(v for _,v in c.most_common(10))/n}

def execute():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
 spec=json.loads((D/'src/SPEC.json').read_text());source_specs=json.loads((ROOT/spec['source_specs']).read_text())
 targets=json.loads((ROOT/spec['target_summary']).read_text())['targets']
 records={};excluded={};groups={};observed={};comparison={}
 for col in spec['collections']:
  sp=next(s for s in source_specs['data'] if s['collection_id']==col)
  p=ROOT/sp['path'];assert sha(p)==sp['sha256']
  recipes=E.parse(p).getroot().findall('.//*[@type="recipe"]')
  records[col]=[];excluded[col]=[]
  for i,node in enumerate(recipes,1):
   s=' '.join(unicodedata.normalize('NFC',text(node)).lower().split())
   rid=node.get('{http://www.w3.org/XML/1998/namespace}id',f'{col}.ordinal{i}')
   reasons=sorted({local(n) for n in node.iter() if local(n) in {'gap','unclear','supplied'}})
   if any(c in s for c in ['[',']','…','...']):reasons.append('VISIBLE_EDITORIAL_UNCERTAINTY')
   if not s:reasons.append('EMPTY')
   if reasons:excluded[col].append({'id':rid,'reasons':reasons,'words':len(s.split())});continue
   records[col].append({'id':rid,'text':s,'words':s.split()})
  groups[col]={};observed[col]={}
  for name,sets in spec['partitions'].items():
   join={w for st in sets for w in spec['sets'][st]}
   gs=[partition(r['words'],join) for r in records[col]]
   assert [[w for g in row for w in g] for row in gs]==[r['words'] for r in records[col]]
   groups[col][name]=gs;observed[col][name]=metrics(gs,spec['sample_groups'])
 for name in spec['partitions']:
  details=[]
  for col in spec['collections']:
   m=observed[col][name]
   for ed,t in targets.items():
    for key in ('type_ratio','top10_share'):
     measured=m.get(key);diff=None if measured is None else abs(measured-t[key])
     details.append({'collection':col,'reader':ed,'metric':key,'source':measured,'target':t[key],'difference':diff,'within':diff is not None and diff<=spec['necessary_tolerance_absolute']})
  comparison[name]={'all_necessary_gates':all(d['within'] for d in details),'details':details}
 result={'experiment':'GDT1176','source_scope':{c:{'complete_recipes':len(records[c]),'excluded_recipes':len(excluded[c]),'source_words':sum(len(r['words']) for r in records[c])} for c in records},'metrics':observed,'comparison':comparison,'passing_partitions':[k for k,v in comparison.items() if v['all_necessary_gates']], 'claim_ceiling':'Two necessary word-frequency conditions only; no glyph writer or full Voynich fit.'}
 return records,excluded,groups,result

def main():
 records,excluded,groups,result=execute()
 save(A/'SOURCE_TEXTS.json',records);save(A/'EXCLUDED.json',excluded);save(A/'PARTITIONS.json',groups);save(A/'RESULT.json',result)
 print(json.dumps({'scope':result['source_scope'],'metrics':result['metrics'],'passing_partitions':result['passing_partitions']},indent=2))
if __name__=='__main__':main()
