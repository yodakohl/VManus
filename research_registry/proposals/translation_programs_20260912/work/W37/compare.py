from pathlib import Path
import csv,json,collections,hashlib
E=Path(__file__).resolve().parent;B=E.parent/'W36'
def rows(p):return list(csv.DictReader(p.open(),delimiter='\t'))
def js(x):return json.dumps(x,sort_keys=True,ensure_ascii=False)
def table(n,rr,cols):
 with (E/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(dict(r,row_status='recorded') for r in rr)
changes=[];candidates=[];groups=[];bad=[]
for sm in ['Q','A']:
 for scope in ['S','I']:
  full={}
  for name,keys in [('ARGUMENTS',['paragraph','grammar','operation']),('QUALITY',['paragraph','grammar','mention']),('TAKE_ARGUMENTS',['paragraph','grammar','target']),('EVENTS',['paragraph','grammar','model','timing','kind','location','assertion'])]:
   old={tuple(r[k] for k in keys):r for r in rows(B/('PK_'+sm+'_'+name+'.tsv'))};new={tuple(r[k] for k in keys):r for r in rows(E/(scope+'_'+sm+'_'+name+'.tsv'))};full[name]=list(new.values())
   assert old.keys()==new.keys()
   for key,a in old.items():
    b=new[key];fields=[k for k in a if k not in ['source_event','execution_index','row_status'] and a[k]!=b[k]]
    if fields:changes.append(dict(scope=scope,shol=sm,table=name,key='|'.join(key),fields=';'.join(fields),baseline=js(a),new=js(b)))
    if name=='EVENTS' and b['status'] in ['CONFLICT','ARGUMENT_INCOMPLETE'] and b['status']!=a['status']:bad.append(dict(scope=scope,shol=sm,key='|'.join(key),old_status=a['status'],new_status=b['status']))
  ff=rows(E/(scope+'_'+sm+'_SOURCE_FLAT.tsv'));byid={r['id']:r for r in ff}
  for marker in [r for r in ff if r['form']=='cfhy']:
   for g in ['B','J','M']:
    cross=[]
    for n,field in [('ARGUMENTS','operation'),('QUALITY','mention'),('TAKE_ARGUMENTS','target')]:
     for r in full[n]:
      if (r['paragraph'],r['grammar'])!=(marker['paragraph'],g):continue
      for slot in ['patient','coingredient']:
       target=r.get(slot,'')
       if target and min(int(byid[r[field]]['offset']),int(byid[target]['offset']))<int(marker['offset'])<=max(int(byid[r[field]]['offset']),int(byid[target]['offset'])):cross.append(dict(kind=n,origin=r[field],slot=slot,target=target))
    a=next(r for r in full['ARGUMENTS'] if (r['grammar'],r['operation'])==(g,'f32v.9:1'))
    for m in ['D','H']:
     for t in ['O','I']:
      event=next(r for r in full['EVENTS'] if (r['grammar'],r['model'],r['timing'],r['kind'],r['location'])==(g,m,t,'ACTION','f32v.9:1'))
      candidates.append(dict(scope=scope,shol=sm,grammar=g,model=m,timing=t,marker=marker['id'],prediction='dependent argument fields retained' if scope=='S' else 'independent field loses prior imperative arguments',patient=a['patient'],partner=a['coingredient'],observed_status=event['status'],cross_boundary_links=js(cross),remaining_unknown='skey',independent_confirmation_capacity=0))
  groups.append(dict(scope=scope,shol=sm,sha256=hashlib.sha256(js(full).encode()).hexdigest(),meaning='Complete arguments, quality, take and event tables; not independent semantic confirmation'))
table('ALL_CHANGES.tsv',changes,['scope','shol','table','key','fields','baseline','new']);table('NEW_FAILURES.tsv',bad,['scope','shol','key','old_status','new_status']);table('CANDIDATES.tsv',candidates,list(candidates[0]));table('PREDICTION_GROUPS.tsv',groups,list(groups[0]))
r=dict(idea='IDEA000234',source_groups=1045,source_paragraphs=17,new_worlds=816,new_events=sum(json.loads((E/(s+'_'+q+'_RESULT.json')).read_text())['events'] for s in ['S','I'] for q in ['Q','A']),candidate_rows=len(candidates),changes=dict(collections.Counter(x['scope']+'_'+x['table'] for x in changes)),new_failure_rows=len(bad),new_conflict_rows=sum(x['new_status']=='CONFLICT' for x in bad),semantic_gloss_positions=611,structural_hypothesis_positions=1,unread_positions=433,confirmed_meanings=0,independent_confirmation_capacity=0,held_access=False)
(E/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(js(r))
