#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import json,hashlib
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
SOURCE=ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json'
TARGET=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json'
def partition(words,k):
 groups=[];pending=[]
 for w in words:
  pending.append(w)
  if not(w.isalpha() and len(w)<=k):groups.append(pending);pending=[]
 if pending:groups.append(pending)
 return groups

def execute():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 source=json.loads(SOURCE.read_text());targets=json.loads(TARGET.read_text())['targets']
 result={'experiment':'GDT1178','metrics':{},'comparison':{},'passing_partitions':[]};allgroups={}
 for col,records in source.items():
  result['metrics'][col]={};allgroups[col]={}
  for k in (2,3):
   name='L'+str(k);gs=[partition(r['words'],k) for r in records]
   assert [[w for g in row for w in g] for row in gs]==[r['words'] for r in records]
   allgroups[col][name]=gs;flat=[tuple(g) for row in gs for g in row][:8000];assert len(flat)==8000
   c=Counter(flat)
   result['metrics'][col][name]={'groups':8000,'types':len(c),'type_ratio':len(c)/8000,'top10_share':sum(v for _,v in c.most_common(10))/8000}
 for name in ('L2','L3'):
  rows=[]
  for col in source:
   for ed,t in targets.items():
    for key in ('type_ratio','top10_share'):
     v=result['metrics'][col][name][key];rows.append({'collection':col,'reader':ed,'metric':key,'value':v,'target':t[key],'within':abs(v-t[key])<=.05})
  result['comparison'][name]={'all_necessary_gates':all(x['within'] for x in rows),'details':rows}
  if result['comparison'][name]['all_necessary_gates']:result['passing_partitions'].append(name)
 return allgroups,result

def main():
 gs,r=execute()
 for name,x in [('PARTITIONS',gs),('RESULT',r)]: (A/(name+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'metrics':r['metrics'],'passing_partitions':r['passing_partitions']},indent=2))
if __name__=='__main__':main()
