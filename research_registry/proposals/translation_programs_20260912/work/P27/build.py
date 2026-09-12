#!/usr/bin/env python3
import csv,json,hashlib
from pathlib import Path
from collections import defaultdict,deque
D=Path('research_registry/proposals/translation_programs_20260912/work/P27');P=D.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,x):(D/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def tab(n,rs,fields=None):
 with (D/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
herb=json.loads((P/'P11/INPUT.json').read_text())['lines'];bath=list(csv.DictReader((P/'P12/PROSE.tsv').open(),delimiter='\t'));labels=json.loads((P/'P25/INPUT.json').read_text())['labels']
lines=[{'record':r['locus'].split('.')[0],'locus':r['locus'],'raw':r['raw_line'],'groups':r['groups']} for r in herb]+[{'record':r['record_id'],'locus':r['locus'],'raw':r['zl3b_line'],'groups':r['zl3b_line'].split()} for r in bath]
records=defaultdict(list)
for r in lines:
 for i,w in enumerate(r['groups'],1):records[r['record']].append({'locus':r['locus']+':'+str(i),'word':w})
assert sum(map(len,records.values()))==486 and len(records)==11
M=dict(zip('tcho cthy chor shor cthold shan okaiin shedy lchedy qokaiin'.split(),['Pflanzengut','Kraut','Blüten','Früchte','Pflanzenrückstand','Feinanteil','Auszug','Flüssigkeit','Pressrückstand','Gefäß']))
B=dict(zip(M,['Pflanze','oberirdisches Kraut','Blüten','Früchte','Rinde','Blütenstaub','Pflanzensaft','Saft','Mark','Fruchtkapsel']))
rels={'ol':'PART_OF','sho':'CONTAINS','chedy':'BECOMES','qokeedy':'FROM'};german={'PART_OF':'ist Teil von','CONTAINS':'enthält','BECOMES':'wird zu','FROM':'stammt aus'}
js('MODEL.json',{'M':M,'B':B,'relations':rels,'all_hypothetical':True,'identities':['FRESH','REUSE'],'right_rule':'first noun before next relation or record end; unknown interveners retained','topic_rule':'latest unclaimed noun; BECOMES promotes result'})
js('SOURCE.json',{'sources':[{'path':str(x),'sha256':sha(x)} for x in [P/'P11/INPUT.json',P/'P12/PROSE.tsv',P/'P25/INPUT.json']],'decision_sha256':sha(D/'DECISION.md'),'image_url':'https://collections.library.yale.edu/iiif/2/1006224/full/2000,/0/default.jpg','image_sha256':'b1bfd576a701497126d444e48801a86da610073c9d66c0b232aa1724d4fb2b77','new_image_admissions':0})
allrel=[];allchain=[];allcycles=[];summaries=[];coverage=[]
for world,lex in [('M',M),('B',B)]:
 for identity in ['FRESH','REUSE']:
  tag=world+'_'+identity;alignment=[];rr=[];chains=[]
  for rec,words in records.items():
   topic=None;claimed={};promote={};produced={}
   ent=lambda k:rec+':'+(words[k]['locus'] if identity=='FRESH' else words[k]['word'])
   for j,w in enumerate(words):
    word=w['word'];loc=w['locus'];reading=lex.get(word,'['+word+']');role='NOUN' if word in lex else 'OPEN';eid=ent(j) if word in lex else 'NA'
    if word in lex:
     if j not in claimed or j in promote:topic=j
    elif word in rels:
     role=rels[word];right=None;interveners=[]
     for k in range(j+1,len(words)):
      if words[k]['word'] in rels:break
      if words[k]['word'] in lex:right=k;break
      interveners.append(words[k]['word'])
     left=topic;issues=[]
     if left is None:issues.append('MISSING_LEFT')
     if right is None:issues.append('MISSING_RIGHT')
     if right is not None and interveners:issues.append('UNREAD_INTERVENERS')
     lword=words[left]['word'] if left is not None else 'MISSING';rword=words[right]['word'] if right is not None else 'MISSING'
     lid=ent(left) if left is not None else 'MISSING';rid=ent(right) if right is not None else 'MISSING'
     if left is not None and right is not None:
      if lid==rid:issues.append('SELF_'+role)
      if world=='M' and role in ['BECOMES','FROM'] and ((lword=='qokaiin')!=(rword=='qokaiin')):issues.append('VESSEL_MATERIAL_CHANGE_OR_ORIGIN_DEBT')
     reading=lex.get(lword,'?Gegenstand')+' '+german[role]+' '+lex.get(rword,'?Gegenstand')
     event={'world':world,'identity':identity,'record':rec,'locus':loc,'relation':role,'left_locus':words[left]['locus'] if left is not None else 'MISSING','right_locus':words[right]['locus'] if right is not None else 'MISSING','left_word':lword,'right_word':rword,'left_id':lid,'right_id':rid,'intervening_words':' '.join(interveners) if right is not None and interveners else 'NONE','issues':';'.join(issues) or 'NONE','reading':reading}
     rr.append(event)
     if lid in produced:
      producer=produced[lid]
      chains.append({'world':world,'identity':identity,'record':rec,'producer':producer,'consumer':loc,'consumer_relation':role,'product_id':lid,'product_word':lword,'producer_complete':int(next(e for e in rr if e['locus']==producer)['left_id']!='MISSING'),'consumer_complete':int(right is not None),'consumer_issues':event['issues']})
     if right is not None:
      claimed[right]=loc
      if role=='BECOMES':promote[right]=loc;produced[rid]=loc
    alignment.append({'record':rec,'locus':loc,'word':word,'role':role,'entity_id':eid,'claimed_by':claimed.get(j,'NA'),'reading':reading})
  # Cycle audit, separately typed relation graphs; containment inverse of part-of.
  cycles=[]
  for rec in records:
   for graph in ['MEREOLOGY','ORIGIN','TRANSFORMATION']:
    edges=[]
    for e in rr:
     if e['record']!=rec or 'MISSING' in [e['left_id'],e['right_id']]:continue
     role=e['relation'];a,b=e['left_id'],e['right_id']
     if graph=='MEREOLOGY' and role in ['PART_OF','CONTAINS']:edges.append((b,a,e['locus']) if role=='PART_OF' else (a,b,e['locus']))
     if graph=='ORIGIN' and role=='FROM':edges.append((a,b,e['locus']))
     if graph=='TRANSFORMATION' and role=='BECOMES':edges.append((a,b,e['locus']))
    for a,b,loc in edges:
     q=deque([(b,[])]);visited=set();witness=None
     while q:
      v,path=q.popleft()
      if v==a:witness=path;break
      if v in visited:continue
      visited.add(v)
      q.extend((y,path+[z]) for x,y,z in edges if x==v)
     if witness is not None:cycles.append({'world':world,'identity':identity,'record':rec,'graph':graph,'edge':loc,'return_path':','.join(witness) or 'SELF','status':'IMPOSSIBLE_STRICT_PART_WHOLE' if graph=='MEREOLOGY' else 'IDENTITY_OR_TEMPORAL_DEBT_NOT_GENERAL_IMPOSSIBILITY'})
  assert len(alignment)==486
  tab('ALIGNMENT_'+tag+'.tsv',alignment)
  prose=['# P27 '+tag+' — ganze hypothetische Lesung','','Alle Klammerwörter bleiben offen. Ausgeschriebene Relationsargumente sind Referenzhilfen, keine zusätzlichen Quellwörter.']
  for r in lines:
   a=[x for x in alignment if x['locus'].rsplit(':',1)[0]==r['locus']]
   prose+=['','## '+r['record']+' / '+r['locus'],'','Quelle: `'+r['raw']+'`','','Lesung: '+' · '.join(x['reading'] for x in a)]
  (D/('READING_'+tag+'.md')).write_text('\n'.join(prose)+'\n')
  for rec in records:
   a=[x for x in alignment if x['record']==rec];e=[x for x in rr if x['record']==rec]
   coverage.append({'world':world,'identity':identity,'record':rec,'groups':len(a),'hypothesis_positions':sum(x['role']!='OPEN' for x in a),'relations':len(e),'complete_relations':sum('MISSING' not in [x['left_id'],x['right_id']] for x in e)})
  summaries.append({'world':world,'identity':identity,'relation_positions':len(rr),'complete_relations':sum('MISSING' not in [x['left_id'],x['right_id']] for x in rr),'missing_left':sum(x['left_id']=='MISSING' for x in rr),'missing_right':sum(x['right_id']=='MISSING' for x in rr),'complete_with_unread_interveners':sum(x['intervening_words']!='NONE' and x['left_id']!='MISSING' for x in rr),'vessel_material_debts':sum('VESSEL_' in x['issues'] for x in rr),'self_relations':sum('SELF_' in x['issues'] for x in rr),'cycle_edges':len(cycles),'product_use_positions':len(chains),'product_uses_with_complete_consumer':sum(x['consumer_complete'] for x in chains),'complete_two_relation_chains':sum(x['producer_complete'] and x['consumer_complete'] for x in chains)})
  allrel+=rr;allchain+=chains;allcycles+=cycles
  if tag=='M_FRESH':hyp=sum(x['role']!='OPEN' for x in alignment)
tab('RELATIONS.tsv',allrel);tab('PRODUCT_USES.tsv',allchain,['world','identity','record','producer','consumer','consumer_relation','product_id','product_word','producer_complete','consumer_complete','consumer_issues']);tab('CYCLES.tsv',allcycles,['world','identity','record','graph','edge','return_path','status']);tab('RECORD_COVERAGE.tsv',coverage)
labelrows=[{'locus':r['locus']+':'+str(i),'word':w,'noun_match':int(w in M),'relation_match':int(w in rels)} for r in labels for i,w in enumerate(r['raw'].split(),1)];tab('LABEL_TRANSFER.tsv',labelrows)
inventory=[{'word':w,'role':'NOUN' if w in M else rels[w],'HERB4':sum(t['word']==w for r,ts in records.items() if not r.startswith('F83') for t in ts),'f83r':sum(t['word']==w for r,ts in records.items() if r.startswith('F83') for t in ts)} for w in list(M)+list(rels)]
tab('WORD_INVENTORY.tsv',inventory)
res={'status':'PARTIAL_RELATIONAL_WORLD_COMPARISON','groups_each':486,'noun_forms':10,'relation_forms':4,'hypothesis_positions':hyp,'open_positions':486-hyp,'summaries':summaries,'shared_noun_forms_between_packets':sum(x['role']=='NOUN' and x['HERB4']>0 and x['f83r']>0 for x in inventory),'label_groups':len(labelrows),'label_matches':sum(x['noun_match']+x['relation_match'] for x in labelrows),'independent_confirmation_capacity':0,'confirmed_meanings':0,'held_pages_opened':0};js('RESULT.json',res);print(json.dumps(res,indent=2))
