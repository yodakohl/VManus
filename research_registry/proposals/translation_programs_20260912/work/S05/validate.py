import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4]
def read(n):return list(csv.DictReader((H/n).open(),delimiter='\t'))
manifest=json.loads((H/'SOURCE.json').read_text())
for item in manifest['files']:assert hashlib.sha256((R/item['path']).read_bytes()).hexdigest()==item['sha256']
old=json.loads((R/manifest['files'][1]['path']).read_text());materials=dict(old['materials']);materials.update({w:t['neutral'] for w,t in old['targets'].items()});verbs=old['verbs'];known=set(materials)|set(verbs)
assert json.loads((H/'MODEL.json').read_text())['materials']==materials
source=json.loads((R/manifest['files'][0]['path']).read_text())['lines'];raw=[]
for line in source:
 record=line['locus'].split('.')[0];assert record in {'f17r','f21r','f32v','f29v'}
 raw.extend((record,line['locus'],line['locus']+':'+str(n),w) for n,w in enumerate(line['groups'],1))
assert len(raw)==145 and len(source)==17
keys=['record','locus','at','word'];assert [tuple(x[k] for k in keys) for x in read('INPUT.tsv')]==raw
idx={x[2]:i for i,x in enumerate(raw)};total=0;ingredients_count=0;results=json.loads((H/'RESULT.json').read_text())
for mode in ['ONE','LINE','SPAN']:
 actions=read('ACTIONS_'+mode+'.tsv');align=read('ALIGNMENT_'+mode+'.tsv');assert [tuple(x[k] for k in keys) for x in align]==raw
 assert [a['at'] for a in actions]==[x[2] for x in raw if x[3] in verbs]
 selections={};expected_ingredients=[]
 for a in actions:
  i=idx[a['at']];end=i;selected=[]
  for j in range(i+1,len(raw)):
   if raw[j][0]!=raw[i][0] or raw[j][3] in verbs:break
   if mode=='LINE' and raw[i][3]=='sho' and raw[j][1]!=raw[i][1]:break
   end=j
   if raw[j][3] in materials:
    selected.append(j)
    if mode=='ONE' or raw[i][3]=='qotchy':break
  assert a['scope_end']==raw[end][2] and a['scope_text']==' '.join(x[3] for x in raw[i+1:end+1])
  assert a['inputs']==(','.join(raw[j][2] for j in selected) or 'NONE')
  assert a['input_words']==(','.join(raw[j][3] for j in selected) or 'NONE')
  assert int(a['input_count'])==len(selected) and int(a['word_classes'])==len({raw[j][3] for j in selected})
  assert a['mass']==(' + '.join('m('+raw[j][2]+')' for j in selected) or 'UNRESOLVED')
  assert a['product_written']=='NO'
  status='MISSING_INPUT' if not selected else 'ONE_INPUT_UNSPECIFIED_PARTNER' if raw[i][3]=='sho' and len(selected)==1 else 'MULTI_INPUT_MIX' if raw[i][3]=='sho' else 'ONE_INPUT_PROCESS'
  assert a['status']==status
  selections[i]=(end,selected)
  expected_ingredients.extend((a['at'],raw[j][2],raw[j][3],raw[end][2]) for j in selected)
  total+=1
 ingredients=read('INGREDIENTS_'+mode+'.tsv');assert [(x['operation'],x['input'],x['input_word'],x['product_completion']) for x in ingredients]==expected_ingredients;ingredients_count+=len(ingredients)
 targets=read('TARGETS_'+mode+'.tsv');assert [t['at'] for t in targets]==[x[2] for x in raw if x[3] in old['targets']]
 for t in targets:
  i=idx[t['at']];current=[raw[a][2] for a,(end,sel) in selections.items() if i in sel]
  previous=['P@'+raw[a][2] for a,(end,sel) in selections.items() if raw[a][0]==raw[i][0] and end<i and any(raw[j][3]==raw[i][3] for j in sel)]
  assert t['current_input_operations']==(','.join(current) or 'NONE') and t['earlier_products_with_same_word_class']==(','.join(previous) or 'NONE')
  assert t['prior_product_identity']=='UNBOUND'
 for a,x in zip(align,raw):
  assert a['read_status']==('HYPOTHESIS' if x[3] in known else 'OPEN')
  assert x[3]+' → '+a['render'] in (H/('READING_'+mode+'.md')).read_text()
 result=results['variants'][mode];assert result['sho_statuses']==dict(Counter(a['status'] for a in actions if a['word']=='sho'))
 assert result['sho_input_mentions']==sum(int(a['input_count']) for a in actions if a['word']=='sho')
 assert result['target_current_inputs']==sum(t['current_input_operations']!='NONE' for t in targets)
 assert sum(a['read_status']=='HYPOTHESIS' for a in align)==42 and sum(a['read_status']=='OPEN' for a in align)==103
assert total==18 and ingredients_count==31
out={'status':'PASS','source_hashes':4,'groups_per_reading':145,'readings':3,'action_rows':18,'ingredient_rows':31,'target_rows':27,'scope':'independent full-range and completion audit, not verified mixtures or product identities'}
(H/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
