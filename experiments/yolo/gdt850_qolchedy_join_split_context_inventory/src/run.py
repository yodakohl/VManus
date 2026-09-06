import argparse,collections,importlib.util,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def definite(a,b):return a is not None and b is not None and int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE'
def inventory(rows):
 lines=collections.defaultdict(dict)
 for r in rows:
  d=lines[r['edition'],r['locus']];i=int(r['source_group_index']);assert i not in d;d[i]=r
 hits=[]
 for (ed,locus),line in sorted(lines.items()):
  for i,first in sorted(line.items()):
   if first['ivtff_group_raw']=='qolchedy':kind='JOINED';end=i
   elif first['ivtff_group_raw']=='qol' and line.get(i+1,{}).get('ivtff_group_raw')=='chedy' and definite(first,line.get(i+1)):kind='SPLIT';end=i+1
   else:continue
   left=[line.get(i-2),line.get(i-1)];right=[line.get(end+1),line.get(end+2)];target=[line[j] for j in range(i,end+1)]
   strict={'LEFT':definite(left[-1],first),'RIGHT':definite(target[-1],right[0])};strict['FOUR']=all([strict['LEFT'],strict['RIGHT'],definite(*left),definite(*right)])
   missing={}
   for name,pos in [('L2',i-2),('L1',i-1),('R1',end+1),('R2',end+2)]:
    if pos not in line:missing[name]='LINE_EDGE' if pos<1 or pos>int(first['source_group_count']) else 'MISSING_INDEX'
   hits.append(dict(occurrence_id=f'{ed}|{locus}|{i}-{end}',edition=ed,locus=locus,page=first['page'],folio=re.match(r'f[0-9]+',first['page']).group(),surface=kind,target=target,left=left,right=right,strict=strict,missing=missing))
 return hits
def summarize(hits):
 freq=collections.Counter();strata=collections.Counter();missing=collections.Counter();contexts=collections.defaultdict(lambda:collections.defaultdict(list))
 for h in hits:
  ed=h['edition'];surface=h['surface'];t=h['target'][0];strata[ed,surface,t['section'],t['hand']]+=1
  for edge,reason in h['missing'].items():missing[ed,surface,edge,reason]+=1
  for side,neighbor in [('LEFT',h['left'][-1]),('RIGHT',h['right'][0])]:
   if neighbor is not None:
    freq[ed,surface,side,neighbor['ivtff_group_raw'],h['strict'][side]]+=1
    if h['strict'][side]:contexts[ed,side,(neighbor['ivtff_group_raw'],)][surface].append(h['occurrence_id'])
  if h['strict']['FOUR']:contexts[ed,'FOUR',tuple(x['ivtff_group_raw'] for x in h['left']+h['right'])][surface].append(h['occurrence_id'])
 locus={h['occurrence_id']:h['locus'] for h in hits}
 shared=[dict(edition=key[0],side=key[1],context=list(key[2]),occurrences=dict(value),loci={s:[locus[i] for i in ids] for s,ids in value.items()}) for key,value in sorted(contexts.items()) if set(value)=={'JOINED','SPLIT'}]
 tables=dict(immediate_frequencies=[dict(edition=k[0],surface=k[1],side=k[2],neighbor=k[3],definite_boundary=k[4],n=v) for k,v in sorted(freq.items())],section_hand=[dict(edition=k[0],surface=k[1],section=k[2],hand=k[3],n=v) for k,v in sorted(strata.items())],missing_edges=[dict(edition=k[0],surface=k[1],edge=k[2],reason=k[3],n=v) for k,v in sorted(missing.items())])
 result=dict(status='COMPLETE_LITERAL_JOIN_SPLIT_DISCOVERY_NO_SEMANTIC_TEST',hits=len(hits),counts={ed:{s:sum(h['edition']==ed and h['surface']==s for h in hits) for s in ['JOINED','SPLIT']} for ed in ['ZL3b','IT2a','RF1b']},shared_contexts={ed:{side:sum(x['edition']==ed and x['side']==side for x in shared) for side in ['LEFT','RIGHT','FOUR']} for ed in ['ZL3b','IT2a','RF1b']})
 return tables,shared,result
def main():
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();s=json.loads((E/'src/SPEC.json').read_text())
 if a.check:rows=json.loads((E/'artifacts/CANDIDATE_LINES.json').read_text())
 else:
  path=ROOT/'experiments/yolo/gdt829_repeated_passage_reflow_capacity/src/run.py';sp=importlib.util.spec_from_file_location('guard_reader',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);allrows,guard=m.query(s)
  keys={(r['edition'],r['locus']) for r in allrows if r['ivtff_group_raw'] in ('qol','qolchedy')};rows=[r for r in allrows if (r['edition'],r['locus']) in keys]
  (E/'artifacts/CANDIDATE_LINES.json').write_text(enc(rows));(E/'artifacts/GUARD.json').write_text(enc(guard))
 hits=inventory(rows);tables,shared,result=summarize(hits)
 for name,obj in [('HITS.json',hits),('TABLES.json',tables),('SHARED_CONTEXTS.json',shared),('RESULT.json',result)]:
  target=E/'artifacts'/name
  if a.check:assert target.read_text()==enc(obj),name
  else:target.write_text(enc(obj))
 print(enc(result))
if __name__=='__main__':main()
