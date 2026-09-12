"""S05 fixed variable-arity ingredient lists on exposed HERB4."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
H=Path(__file__).resolve().parent;R=H.parents[4];P=H.parent
S=P/'P11/INPUT.json';L=P/'P13/MODEL.json'
def js(n,x):(H/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rows):
 with (H/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
old=json.loads(L.read_text());materials=dict(old['materials']);materials.update({w:x['neutral'] for w,x in old['targets'].items()});verbs=old['verbs'];known=set(materials)|set(verbs)
js('MODEL.json',{'materials':materials,'verbs':verbs,'variants':['ONE','LINE','SPAN'],'portion_identity':'one unknown-positive-mass portion per material occurrence','product':'implicit model object, no written product name','completion':'after selected list, not before its input mentions'})
js('SOURCE.json',{'files':[{'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [S,L,H/'DECISION.md',H/'MODEL.json']],'sealed':['f84','f84r'],'exposure':'all HERB4 and motivating lists previously exposed'})
lines=json.loads(S.read_text())['lines'];raw=[]
for line in lines:
 rec=line['locus'].split('.')[0];assert rec in {'f17r','f21r','f32v','f29v'}
 for n,w in enumerate(line['groups'],1):raw.append({'record':rec,'locus':line['locus'],'at':line['locus']+':'+str(n),'word':w})
assert len(raw)==145 and len(lines)==17
tab('INPUT.tsv',[dict(x,row_status='recorded') for x in raw])
all_actions={};all_targets={};result={}
for mode in ['ONE','LINE','SPAN']:
 actions=[];internal=[];ingredients=[]
 for i,x in enumerate(raw):
  if x['word'] not in verbs:continue
  stop=next((j for j in range(i+1,len(raw)) if raw[j]['record']!=x['record'] or raw[j]['word'] in verbs),len(raw))
  if mode=='LINE' and x['word']=='sho':stop=min(stop,next((j for j in range(i+1,len(raw)) if raw[j]['locus']!=x['locus']),len(raw)))
  selected=[j for j in range(i+1,stop) if raw[j]['word'] in materials]
  if mode=='ONE' or x['word']=='qotchy':
   selected=selected[:1]
   if selected:stop=selected[0]+1
  end=stop-1;classes=list(dict.fromkeys(raw[j]['word'] for j in selected));n=len(selected)
  status='MISSING_INPUT' if n==0 else 'ONE_INPUT_UNSPECIFIED_PARTNER' if x['word']=='sho' and n==1 else 'MULTI_INPUT_MIX' if x['word']=='sho' else 'ONE_INPUT_PROCESS'
  product='P@'+x['at'] if selected else 'NONE'
  row=dict(x,mode=mode,scope_end=raw[end]['at'],scope_groups=stop-i-1,scope_open=sum(raw[j]['word'] not in known for j in range(i+1,stop)),scope_text=' '.join(raw[j]['word'] for j in range(i+1,stop)),inputs=','.join(raw[j]['at'] for j in selected) or 'NONE',input_words=','.join(raw[j]['word'] for j in selected) or 'NONE',input_glosses=' + '.join(materials[raw[j]['word']] for j in selected) or 'NONE',input_count=n,word_classes=len(classes),status=status,product=product,product_written='NO',mass=' + '.join('m('+raw[j]['at']+')' for j in selected) or 'UNRESOLVED',row_status='recorded')
  actions.append(row);internal.append((i,end,selected,product))
  for j in selected:ingredients.append({'mode':mode,'operation':x['at'],'word':x['word'],'input':raw[j]['at'],'input_word':raw[j]['word'],'product':product,'product_completion':raw[end]['at'],'row_status':'recorded'})
 targets=[]
 for i,x in enumerate(raw):
  if x['word'] not in old['targets']:continue
  current=[raw[a]['at'] for a,end,sel,p in internal if i in sel]
  earlier=[p for a,end,sel,p in internal if raw[a]['record']==x['record'] and end<i and any(raw[j]['word']==x['word'] for j in sel)]
  targets.append(dict(x,mode=mode,current_input_operations=','.join(current) or 'NONE',earlier_products_with_same_word_class=','.join(earlier) or 'NONE',prior_product_identity='UNBOUND',status='CURRENT_INPUT_NOT_PRIOR_PRODUCT' if current else 'NO_PROCESS_BINDING',row_status='recorded'))
 tab('ACTIONS_'+mode+'.tsv',actions);tab('INGREDIENTS_'+mode+'.tsv',ingredients);tab('TARGETS_'+mode+'.tsv',targets)
 amap={a['at']:a for a in actions};align=[]
 for x in raw:
  w=x['word'];render=materials.get(w,'['+w+' — offen]')
  if w in verbs:
   a=amap[x['at']];render=verbs[w]+' {'+a['input_glosses']+'}; '+a['status']+'; Modellprodukt '+a['product']+' erst nach '+a['scope_end']
  align.append(dict(x,mode=mode,render=render,read_status='HYPOTHESIS' if w in known else 'OPEN',row_status='recorded'))
 tab('ALIGNMENT_'+mode+'.tsv',align)
 text=['# S05 '+mode+' — ganze HERB4-Lesung; Bedeutungen hypothetisch','']
 for line in lines:text+=['**'+line['locus']+'**','', ' · '.join(x['word']+' → '+x['render'] for x in align if x['locus']==line['locus']),'']
 (H/('READING_'+mode+'.md')).write_text('\n'.join(text).rstrip()+'\n')
 all_actions[mode]=actions;all_targets[mode]=targets
 result[mode]={'hypothetical_positions':sum(x['read_status']=='HYPOTHESIS' for x in align),'open_positions':sum(x['read_status']=='OPEN' for x in align),'sho_statuses':dict(Counter(a['status'] for a in actions if a['word']=='sho')),'sho_input_mentions':sum(a['input_count'] for a in actions if a['word']=='sho'),'target_current_inputs':sum(t['current_input_operations']!='NONE' for t in targets),'target_prior_product_identity_bindings':0,'written_product_names':0}
comparison=[]
for a,b,c in zip(all_actions['ONE'],all_actions['LINE'],all_actions['SPAN']):
 comparison.append({'at':a['at'],'word':a['word'],'ONE_inputs':a['input_words'],'LINE_inputs':b['input_words'],'SPAN_inputs':c['input_words'],'ONE_end':a['scope_end'],'LINE_end':b['scope_end'],'SPAN_end':c['scope_end'],'row_status':'recorded'})
tab('ALL_COMPARISONS.tsv',comparison)
js('RESULT.json',{'status':'PARTIAL_VARIADIC_MIXTURE_READING_NO_WRITTEN_PRODUCT_BINDING','groups_per_reading':145,'readings':3,'operations_per_reading':6,'variants':result,'confirmed_meanings':0,'independent_confirmation_capacity':0,'decision':'Keep local multi-input alternative; wide scope adds unverified ingredients; no processed-name or output identity inferred'})
print(json.dumps(result,ensure_ascii=False))
