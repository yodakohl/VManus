"""Independent direct left/right scans; no builder import or group-based binding."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4]
def read(n):return list(csv.DictReader((H/n).open(),delimiter='\t'))
manifest=json.loads((H/'SOURCE.json').read_text())
for item in manifest['files']:assert hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256']
model=json.loads((R/manifest['files'][1]['path']).read_text());mats={w for w,x in model['names'].items() if x['type']=='MATERIAL'};verbs=set(model['actions']);known=set(model['names'])|verbs
lines=list(csv.DictReader((R/manifest['files'][0]['path']).open(),delimiter='\t'));raw=[]
for line in lines:
 assert line['page']=='f83r'
 raw.extend((line['record_id'],line['locus'],line['locus']+':'+str(n),w) for n,w in enumerate(line['zl3b_line'].split(),1))
assert len(raw)==341 and len(lines)==51
keys=['record','locus','at','word'];assert [tuple(x[k] for k in keys) for x in read('INPUT.tsv')]==raw
idx={x[2]:i for i,x in enumerate(raw)}
def pos(i):return raw[i][2] if i is not None else 'NONE'
parsed=[]
for row in read('ALL_GROUPS.tsv'):
 start,end=idx[row['start']],idx[row['end']];part=raw[start:end+1];assert len({x[0] for x in part})==1
 assert row['raw']==' '.join(x[3] for x in part) and int(row['groups'])==len(part)
 assert not any(x[3] in mats for x in part[:-1])
 assert row['target']==(part[-1][2] if part[-1][3] in mats else 'NONE')
 assert row['actions']==(','.join(x[2] for x in part if x[3] in verbs) or 'NONE')
 assert int(row['action_count'])==sum(x[3] in verbs for x in part)
 assert int(row['open_groups'])==sum(x[3] not in known for x in part)
 parsed+=part
assert parsed==raw
res=json.loads((H/'RESULT.json').read_text());all_events={}
for v in ['L','S','X']:
 events=read('ACTIONS_'+v+'.tsv');align=read('ALIGNMENT_'+v+'.tsv');assert [tuple(x[k] for k in keys) for x in align]==raw
 assert [x['at'] for x in events]==[x[2] for x in raw if x[3] in verbs]
 for e in events:
  i=idx[e['at']];word=raw[i][3];before=[j for j in range(i) if raw[j][0]==raw[i][0]];after=[j for j in range(i+1,len(raw)) if raw[j][0]==raw[i][0]]
  left=next((j for j in reversed(before) if raw[j][3] in mats),None);right=next((j for j in after if raw[j][3] in mats),None)
  if v=='L':p=left;reason='BOUND' if p is not None else 'NO_LEFT_MATERIAL'
  elif right is None:p=None;reason='NO_RIGHT_MATERIAL'
  elif v=='X' and any(raw[j][3] in verbs for j in range(i+1,right)):p=None;reason='SUPERSEDED_UNBOUND'
  else:p=right;reason='BOUND'
  dest=next((j for j in reversed(before) if raw[j][3]=='qokaiin'),None) if word=='qokeedy' else None
  assert e['patient']==pos(p) and e['destination']==pos(dest) and e['binding']==reason
  missing=[]
  if p is None:missing.append('MATERIAL')
  if word=='qokeedy' and dest is None:missing.append('VESSEL')
  assert e['status']==('MISSING_'+'_AND_'.join(missing) if missing else 'COMPLETE')
  assert e['patient_word']==(raw[p][3] if p is not None else 'NONE')
  if p is not None:
   assert int(e['intervening_groups'])==abs(p-i)-1
   assert int(e['intervening_open'])==sum(raw[j][3] not in known for j in range(min(i,p)+1,max(i,p)))
 for a,x in zip(align,raw):
  assert a['read_status']==('HYPOTHESIS' if x[3] in known else 'OPEN')
  assert x[3]+' → '+a['render'] in (H/('READING_'+v+'.md')).read_text()
 assert res['variants'][v]['action_statuses']==dict(Counter(e['status'] for e in events))
 assert res['variants'][v]['patient_bindings']==dict(Counter(e['binding'] for e in events))
 assert res['variants'][v]['hypothetical_positions']==50 and res['variants'][v]['open_positions']==291
 all_events[v]=events
comparisons=read('ALL_COMPARISONS.tsv')
for c,l,s,x in zip(comparisons,all_events['L'],all_events['S'],all_events['X']):
 assert c['at']==l['at']==s['at']==x['at']
 assert (c['L_patient'],c['S_patient'],c['X_patient'])==(l['patient'],s['patient'],x['patient'])
clusters=read('MULTI_PREDICATE_GROUPS.tsv');assert len(clusters)==res['multiple_predicate_groups']==5
assert {c['group'] for c in clusters}=={g['group'] for g in read('ALL_GROUPS.tsv') if int(g['action_count'])>=2}
for c in clusters:
 events=[e for e in all_events['S'] if e['group']==c['group']]
 assert c['all_roles_complete']==str(all(e['status']=='COMPLETE' for e in events))
assert res['L_to_S_type_changes_when_both_bound']==sum(l['patient_word']!='NONE' and s['patient_word']!='NONE' and l['patient_word']!=s['patient_word'] for l,s in zip(all_events['L'],all_events['S']))==9
assert res['L_to_S_newly_complete']==1 and res['L_to_S_lost_complete']==2
out={'status':'PASS','source_hashes':4,'groups_per_reading':341,'readings':3,'action_rows':60,'full_group_partition':30,'multi_predicate_groups':5,'complete_mixed_action_groups':1,'limit':'Independent source and syntax-rule replay only; shared role capacity is constructed, not independent meaning'}
(H/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
