import argparse,csv,hashlib,io,json,re,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(n,x,check=False):
 p=E/'artifacts'/n
 if check:assert p.read_text()==enc(x),n
 else:p.write_text(enc(x))
def face(x):
 m=re.fullmatch(r'(f[0-9]+[rv])[0-9]*',x);assert m and not x.startswith('f84'),x
 return m[1]
def leaf(x):return re.match(r'f[0-9]+',face(x))[0]
def partition(events,f):
 train=[e for e in events if e['axis']==f['source_axis'] and e['carrier']!=f['held_carrier'] and e['physical_folio']!=f['held_physical_folio']]
 test=[e for e in events if e['axis']==f['target_axis'] and e['carrier']==f['held_carrier'] and e['physical_folio']==f['held_physical_folio']]
 opposite=[e for e in train if leaf(e['page'])==leaf(f['held_physical_folio']) and face(e['page'])!=f['held_physical_folio']]
 return train,test,opposite
def controls():
 assert face('f86v3')=='f86v' and leaf('f86v3')=='f86';assert face('f104r')!=face('f104v') and leaf('f104r')==leaf('f104v')
 for p in ['f84','f84r','f84v2']:
  try:face(p)
  except AssertionError:pass
  else:raise AssertionError('seal')
 events=[dict(event_id=str(i),carrier=c,axis=a,page=p,physical_folio=face(p)) for i,(c,a,p) in enumerate([('A','L','f86v3'),('B','L','f86r'),('A','L','f86r'),('B','DY','f86r'),('B','L','f86v2')])]
 f=dict(source_axis='L',target_axis='L',held_carrier='A',held_physical_folio='f86v');tr,te,op=partition(events,f)
 assert [x['event_id'] for x in tr]==['1'] and [x['event_id'] for x in te]==['0'] and op==tr
 assert not [x for x in tr if leaf(x['page'])!=leaf(f['held_physical_folio'])]
 return dict(status='PASS',controls=['face_vs_leaf','panel','seal','opposite_face_survives','same_carrier_excluded','other_axis_excluded','same_face_panel_excluded','whole_leaf_excludes'])
def query(q):
 assert hashlib.sha256((ROOT/q['source']).read_bytes()).hexdigest()==q['source_sha256']
 cmd=['./vmanus-exp','query-tsv',q['source'],'--selector',q['selector']]
 for v in q['allow']:cmd+=['--allow',v]
 cmd+=['--columns',','.join(q['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r'];p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True);reader=csv.DictReader(io.StringIO(p.stdout),delimiter='\t');assert reader.fieldnames==q['columns'];rows=list(reader);stats=[json.loads(x[len('GUARD_STATS '):]) for x in p.stderr.splitlines() if x.startswith('GUARD_STATS ')];assert len(stats)==1 and stats[0]['selected']==len(rows)
 assert all(r[q['selector']] in q['allow'] and not r[q['selector']].startswith('f84') for r in rows)
 return rows,dict(command=cmd,stats=stats[0],projection_sha256=hashlib.sha256(p.stdout.encode()).hexdigest())
def derive(data,s):
 events=data['EVENTS'];assert len({e['event_id'] for e in events})==len(events)
 assert all(e['physical_folio']==face(e['page']) for e in events)
 folds=sorted([f for f in data['FOLDS'] if f['model_id'] in s['models'] and f['population']==s['population']],key=lambda f:(f['model_id'],f['held_carrier'],f['held_physical_folio']))
 assert len({(f['model_id'],f['held_carrier'],f['held_physical_folio']) for f in folds})==len(folds)
 rows=[];issues=[]
 for f in folds:
  train,test,opposite=partition(events,f);opposite.sort(key=lambda e:e['event_id']);test.sort(key=lambda e:e['event_id'])
  flags=dict(carrier_excluded=int(all(e['carrier']!=f['held_carrier'] for e in train)),physical_folio_excluded=int(all(e['physical_folio']!=f['held_physical_folio'] for e in train)))
  mismatch=[k for k,v in dict(train_events=len(train),test_events=len(test),**flags).items() if int(f[k])!=v]
  if f['source_axis']!=s['models'][f['model_id']] or f['target_axis']!=s['models'][f['model_id']]:mismatch.append('AXIS')
  row=dict(fold=f,reconstructed_train_events=len(train),reconstructed_test_events=len(test),reconstructed_flags=flags,opposite_face_train_events=len(opposite),opposite_face_event_ids=[e['event_id'] for e in opposite],witness=dict(train=opposite[0],test=test[0]) if opposite and test else None,mismatch=mismatch)
  rows.append(row)
  if mismatch:issues.append(dict(model=f['model_id'],carrier=f['held_carrier'],face=f['held_physical_folio'],mismatch=mismatch))
 counts={m:sum(f['model_id']==m for f in folds) for m in s['models']}
 if counts!=s['static_expected_primary_folds']:issues.append(dict(coverage=counts,expected=s['static_expected_primary_folds']))
 selectors=sorted({e['page'] for e in events});faces=sorted({face(p) for p in selectors});leaves=sorted({leaf(p) for p in selectors});both=[l for l in leaves if l+'r' in faces and l+'v' in faces]
 affected=sum(r['opposite_face_train_events']>0 for r in rows)
 result=dict(status='SOURCE_RECONSTRUCTION_MISMATCH' if issues else 'PRIMARY_FACE_HOLDOUT_RETAINS_OPPOSITE_LEAF_FACE' if affected else 'NO_OPPOSITE_FACE_IN_AUDITED_PRIMARY_FOLDS',issues=issues,primary_folds=counts,primary_total=len(rows),affected_folds=affected,affected_by_model={m:sum(r['fold']['model_id']==m and r['opposite_face_train_events']>0 for r in rows) for m in s['models']},projected_event_count=len(events),event_selectors=selectors,event_faces=faces,event_leaves=leaves,both_face_leaves=both)
 return rows,result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls',action='store_true');ap.add_argument('--check',action='store_true');a=ap.parse_args()
 if a.controls:save('CONTROLS.json',controls());print('CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text())
 if a.check:data=json.loads((E/'artifacts/PROJECTED_METADATA.json').read_text())
 else:
  data={};guards={}
  for q in s['queries']:data[q['name']],guards[q['name']]=query(q)
  save('PROJECTED_METADATA.json',data);save('GUARD.json',guards)
 rows,result=derive(data,s);save('PRIMARY_FOLDS.json',rows,a.check);save('RESULT.json',result,a.check);print(enc(result))
if __name__=='__main__':main()
