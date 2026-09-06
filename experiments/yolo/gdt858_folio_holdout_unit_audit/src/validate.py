import argparse,csv,hashlib,io,json,re,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def load(n):return json.loads((E/'artifacts'/n).read_text())
def units(p):
 m=re.fullmatch(r'f(\d+)([rv])\d*',p);assert m and not p.startswith('f84')
 return 'f'+m[1]+m[2],'f'+m[1]
def select(events,f):
 byid={e['event_id']:e for e in events};assert len(byid)==len(events)
 axis={k for k,e in byid.items() if e['axis']==f['source_axis']};samecarrier={k for k,e in byid.items() if e['carrier']==f['held_carrier']};sameface={k for k,e in byid.items() if e['physical_folio']==f['held_physical_folio']}
 train=axis-samecarrier-sameface;test={k for k,e in byid.items() if e['axis']==f['target_axis']} & samecarrier & sameface
 opposite={k for k in train if units(byid[k]['page'])[1]==units(f['held_physical_folio'])[1] and units(byid[k]['page'])[0]!=f['held_physical_folio']}
 return byid,train,test,opposite
def controls():
 assert units('f104r')[1]==units('f104v')[1] and units('f104r')[0]!=units('f104v')[0];assert units('f86v3')==('f86v','f86')
 for p in ['f84','f84r','f84v2']:
  try:units(p)
  except AssertionError:pass
  else:raise AssertionError('seal')
 es=[dict(event_id=str(i),page=p,physical_folio=units(p)[0],carrier=c,axis=a) for i,(p,c,a) in enumerate([('f86v3','A','L'),('f86r','B','L'),('f86r','A','L'),('f86r','B','DY'),('f86v2','B','L')])]
 f=dict(source_axis='L',target_axis='L',held_carrier='A',held_physical_folio='f86v');_,tr,te,op=select(es,f);assert tr==op=={'1'} and te=={'0'}
 assert not {k for k in tr if units(es[int(k)]['page'])[1]!=units(f['held_physical_folio'])[1]}
def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');a=p.parse_args();controls()
 if a.controls:print('INDEPENDENT CONTROLS PASS');return
 s=json.loads((E/'src/SPEC.json').read_text());data=load('PROJECTED_METADATA.json');guards=load('GUARD.json');rows=load('PRIMARY_FOLDS.json');result=load('RESULT.json')
 for q in s['queries']:
  assert hashlib.sha256((ROOT/q['source']).read_bytes()).hexdigest()==q['source_sha256']
  args=['./vmanus-exp','query-tsv',q['source'],'--selector',q['selector']]
  for value in q['allow']:args.extend(['--allow',value])
  args.extend(['--columns',','.join(q['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']);out=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,check=True)
  assert hashlib.sha256(out.stdout.encode()).hexdigest()==guards[q['name']]['projection_sha256'];reader=csv.DictReader(io.StringIO(out.stdout),delimiter='\t');assert reader.fieldnames==q['columns'];fresh=list(reader);assert fresh==data[q['name']]
  assert all(r[q['selector']] in q['allow'] and not r[q['selector']].startswith('f84') for r in fresh)
 events=data['EVENTS'];assert all(e['physical_folio']==units(e['page'])[0] for e in events)
 ff=[f for f in data['FOLDS'] if f['population']=='CORE13' and f['model_id'] in s['models']];ff.sort(key=lambda f:(f['model_id'],f['held_carrier'],f['held_physical_folio']));assert [r['fold'] for r in rows]==ff
 problems=[];counts={m:0 for m in s['models']};affected={m:0 for m in s['models']}
 for f,r in zip(ff,rows):
  ids,tr,te,op=select(events,f);flags=dict(carrier_excluded=int(not any(ids[k]['carrier']==f['held_carrier'] for k in tr)),physical_folio_excluded=int(not any(ids[k]['physical_folio']==f['held_physical_folio'] for k in tr)))
  assert r['reconstructed_train_events']==len(tr) and r['reconstructed_test_events']==len(te) and r['reconstructed_flags']==flags
  assert r['opposite_face_event_ids']==sorted(op) and r['opposite_face_train_events']==len(op)
  witness=dict(train=ids[min(op)],test=ids[min(te)]) if op and te else None;assert r['witness']==witness
  mismatch=[k for k,v in dict(train_events=len(tr),test_events=len(te),**flags).items() if int(f[k])!=v]
  if f['source_axis']!=s['models'][f['model_id']] or f['target_axis']!=s['models'][f['model_id']]:mismatch.append('AXIS')
  assert r['mismatch']==mismatch
  if mismatch:problems.append(dict(model=f['model_id'],carrier=f['held_carrier'],face=f['held_physical_folio'],mismatch=mismatch))
  counts[f['model_id']]+=1;affected[f['model_id']]+=bool(op)
 if counts!=s['static_expected_primary_folds']:problems.append(dict(coverage=counts,expected=s['static_expected_primary_folds']))
 pages=sorted({e['page'] for e in events});faces=sorted({units(p)[0] for p in pages});leaves=sorted({units(p)[1] for p in pages});both=sorted(l for l in leaves if l+'r' in faces and l+'v' in faces)
 expected=dict(status='SOURCE_RECONSTRUCTION_MISMATCH' if problems else 'PRIMARY_FACE_HOLDOUT_RETAINS_OPPOSITE_LEAF_FACE' if sum(affected.values()) else 'NO_OPPOSITE_FACE_IN_AUDITED_PRIMARY_FOLDS',issues=problems,primary_folds=counts,primary_total=len(ff),affected_folds=sum(affected.values()),affected_by_model=affected,projected_event_count=len(events),event_selectors=pages,event_faces=faces,event_leaves=leaves,both_face_leaves=both)
 assert result==expected
 validation=dict(status='PASS',independent_set_reconstruction=True,guard_queries_reissued=2,byte_projection_parity=True,primary_folds=len(ff),direct_witnesses_checked=sum(affected.values()),controls='PASS')
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(validation,sort_keys=True,separators=(',',':'))+'\n');print(json.dumps(validation))
if __name__=='__main__':main()
