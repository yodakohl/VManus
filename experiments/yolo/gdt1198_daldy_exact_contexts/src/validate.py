"""Independent source-bound check; no import of the concordance runner."""
from pathlib import Path
import sys,json,csv,io,subprocess,hashlib
from collections import Counter,defaultdict
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
FORMS=['daldy','daly','dal','aldy','dy'];EDS=['ZL3b','IT2a','RF1b']

def main():
 p=json.loads((A/'CONTEXT_PACKET.json').read_text());res=json.loads((A/'RESULT.json').read_text());review=json.loads((A/'BOUNDARY_REVIEW.json').read_text());receipt=p['source_receipt'];inp=receipt['inputs'];allowed=set(inp['selectors'])
 for name,digest in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 for key in ['source','allowlist','code']:assert hashlib.sha256((ROOT/inp[key]).read_bytes()).hexdigest()==inp[key+'_sha256']
 assert len(allowed)==179 and all(not x.startswith('f84') and x!='f116v' for x in allowed)
 loci=sorted({c['target']['locus'] for c in p['contexts']})
 assert all(c['target']['page'] in allowed for c in p['contexts'])
 assert all(not x.startswith('f84') and not x.startswith('f116v') for x in loci)
 cols=inp['columns'];cmd=[str(ROOT/'vmanus-exp'),'query-tsv',inp['source'],'--selector','locus']
 for locus in loci:cmd.extend(['--allow',locus])
 cmd.extend(['--columns',','.join(cols),'--forbid-prefix','f84','--forbid-prefix','f84r'])
 proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);assert proc.returncode==0,'Guarded source query failed'
 stats=json.loads(next(x[12:] for x in proc.stderr.splitlines() if x.startswith('GUARD_STATS ')))
 rows=[]
 for r in csv.DictReader(io.StringIO(proc.stdout),delimiter='\t'):
  for k in ['source_group_index','source_group_count']:r[k]=int(r[k])
  assert r['page'] in allowed and r['locus'] in loci
  rows.append(r)
 assert len(rows)==stats['selected'];byid={r['source_group_id']:r for r in rows};assert len(byid)==len(rows)
 line=defaultdict(list)
 for r in rows:line[r['edition'],r['page'],r['locus']].append(r)
 for v in line.values():v.sort(key=lambda r:r['source_group_index'])
 seen=set()
 for c in p['contexts']:
  t=c['target'];sid=t['source_group_id'];assert sid not in seen;seen.add(sid);assert t==byid[sid]
  full=line[t['edition'],t['page'],t['locus']];i=t['source_group_index']-1
  assert full[i]==t and c['window']==full[max(0,i-2):i+3]
  assert c['previous']==(full[i-1] if i else None)
  assert c['next']==(full[i+1] if i+1<len(full) else None)
 assert seen=={r['source_group_id'] for r in rows if r['ivtff_group_raw'] in FORMS}
 profiles=json.loads((ROOT/'experiments/yolo/gdt1197_letter_memory_frequency/artifacts/STRUCTURAL_PROFILES.json').read_text())
 counts={e:{f:sum(r['edition']==e and r['ivtff_group_raw']==f for r in rows) for f in FORMS} for e in EDS}
 # Frozen profile totals establish completeness outside the queried locus subset.
 expected={'ZL3b':{'daldy':17,'daly':23,'dal':191,'aldy':10,'dy':225},'IT2a':{'daldy':16,'daly':25,'dal':201,'aldy':9,'dy':221},'RF1b':{'daldy':8,'daly':21,'dal':158,'aldy':5,'dy':170}}
 assert profiles['source_receipt']['inputs']==inp
 assert counts==expected
 for e in EDS:
  for f in FORMS:
   own=[r for r in rows if r['edition']==e and r['ivtff_group_raw']==f];s=res['summaries'][e][f]
   assert s['count']==len(own) and s['loci']==len({r['locus'] for r in own})
   for side,delta in [('previous',-1),('next',1)]:
    c=Counter()
    for r in own:
     v=line[e,r['page'],r['locus']];i=r['source_group_index']-1+delta
     c[v[i]['ivtff_group_raw'] if 0<=i<len(v) else '<LINE_START>' if i<0 else '<LINE_END>']+=1
    assert [list(x) for x in sorted(c.items(),key=lambda x:(-x[1],x[0]))]==s[side]
 shared=[]
 for e in EDS:
  frames=defaultdict(lambda:defaultdict(list))
  for c in p['contexts']:
   t=c['target'];f=t['ivtff_group_raw']
   if t['edition']!=e or f not in ['daldy','daly','dal'] or not c['previous'] or not c['next']:continue
   key=(c['previous']['ivtff_group_raw'],c['next']['ivtff_group_raw'],t['left_separator'],t['right_separator'])
   frames[key][f].append(t['source_group_id'])
  shared.extend((e,k) for k,v in frames.items() if len(v)>1)
 assert shared==[] and res['exact_two_sided_shared_frames']==[]
 dloci={(r['page'],r['locus']) for r in rows if r['ivtff_group_raw']=='daldy'}
 assert len(dloci)==res['daldy_locus_union']==19
 assert len(p['daldy_lines'])==len(dloci)*3
 for saved in p['daldy_lines']:assert saved['groups']==line[saved['edition'],saved['page'],saved['locus']]
 for c in review['cases']:
  raw=[]
  for g in c['groups']:
   r=byid[g['source_group_id']];assert r['edition']==c['edition'] and r['locus']==c['locus'];assert all(r[k]==v for k,v in g.items());raw.append(r['ivtff_group_raw'])
  cat=c['classification']
  options={'exact_whole':[['daldy']],'split_literal':[['dal','dy']],'split_with_entity':[['dal','@152;y']],'correction_annotation':[['daldy<!corr?>']],'embedded_in_longer_group':[['daldaldy']],'entity_bearing_single_group':[['@152;al@152;y'],['dal@152;y'],['@152;aldy']]}
  assert raw in options[cat]
 # Explicit physical-location comparisons, no ordinal cross-reader alignment.
 for locus in ['f103r.1','f75v.22','f89v1.13']:
  zz=next(c for c in review['cases'] if c['locus']==locus and c['edition']=='ZL3b')
  ii=next(c for c in review['cases'] if c['locus']==locus and c['edition']=='IT2a')
  assert zz['classification']=='exact_whole' and ii['classification']=='split_literal'
  assert ''.join(g['ivtff_group_raw'] for g in zz['groups'])==''.join(g['ivtff_group_raw'] for g in ii['groups'])=='daldy'
  assert ii['groups'][0]['right_separator']==ii['groups'][1]['left_separator']=='DEFINITE_SPACE'
 result={'status':'PASS','scope':'Source identities, literal groups/separators, completeness against frozen exact-word profile totals and descriptive counts only','guard_stats':stats,'unique_target_occurrences':len(seen),'daldy_loci':len(dloci),'complete_daldy_reader_lines':len(p['daldy_lines']),'boundary_cases':len(review['cases']),'exact_two_sided_shared_frames':len(shared),'images_or_meanings_validated':False,'scientific_status':'DESCRIPTIVE_CONTEXTS_NO_SEMANTIC_SELECTION'}
 (A/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
