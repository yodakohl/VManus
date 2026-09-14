import csv,json,hashlib
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent;M=json.loads((D/'MODEL.json').read_text())
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def table(n,rows,fields):
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
rows=list(csv.DictReader((D/'PROSE.tsv').open(),delimiter='\t'));assert {r['page'] for r in rows}=={'f83r'}
tokens=[];byline={}
for r in rows:
 line=[]
 for i,w in enumerate(r['zl3b_line'].split(),1):
  t={'record':r['record_id'],'line':r['locus'],'at':r['locus']+':'+str(i),'word':w,'index':len(tokens)};tokens.append(t);line.append(t)
 byline[r['locus']]=line
entries=[];errors=[];body_owners={};quote_owners={};marker_owners={}
for line,ts in byline.items():
 start=0
 for i,t in enumerate(ts):
  if t['word']!=M['marker']:continue
  body=ts[start:i];target=ts[i+1] if i+1<len(ts) else None
  issue='EMPTY_BODY' if not body else 'MISSING_TARGET' if target is None else 'MARKER_AS_TARGET' if target['word']==M['marker'] else ''
  e={'id':'D%02d'%(len(entries)+1),'record':t['record'],'marker':t['at'],'marker_index':t['index'],'name':target['word'] if target else '', 'name_at':target['at'] if target else '', 'name_index':target['index'] if target else -1,'body':[b['word'] for b in body],'body_loci':[b['at'] for b in body],'status':issue or 'BOUND'};entries.append(e)
  if issue:errors.append({'id':e['id'],'issue':issue})
  else:
   for b in body:assert b['at'] not in body_owners;body_owners[b['at']]=e['id']
   quote_owners[target['at']]=e['id'];marker_owners[t['at']]=e['id']
  start=i+2
lex={}
for e in entries:
 if e['status']!='BOUND':continue
 if e['name'] in lex and lex[e['name']]['body']!=e['body']:errors.append({'name':e['name'],'issue':'INCOMPATIBLE_DEFINITIONS'})
 lex[e['name']]=e
# Full nonrecursive expansion tracks definitions used; a cycle is explicit failure.
def expand(word, cutoff=None, stack=()):
 if word not in lex:return [word],[],[]
 e=lex[word]
 if cutoff is not None and e['name_index']>=cutoff:return [word],[],[word]
 if word in stack:raise ValueError('CYCLE:'+','.join(stack+(word,)))
 leaves=[];used=[e['id']];blocked=[]
 for child in e['body']:
  a,b,c=expand(child,cutoff,stack+(word,));leaves+=a;used+=b;blocked+=c
 return leaves,used,blocked
for name in lex:
 try:expand(name)
 except ValueError as ex:errors.append({'name':name,'issue':str(ex)})
assert not errors,errors
app=[]
for t in tokens:
 if t['word'] not in lex or t['at'] in quote_owners:continue
 seq,used,future=expand(t['word'],t['index']);full,allused,_=expand(t['word'])
 e=lex[t['word']];prior=e['name_index']<t['index']
 app.append({'record':t['record'],'at':t['at'],'index':t['index'],'name':t['word'],'definition':e['id'],'location_role':'DEFINITION_BODY' if t['at'] in body_owners else 'OTHER_TEXT','body_of':body_owners.get(t['at'],''),'declaration_precedes':prior,'sequential_expansion':seq,'sequential_definitions':used,'unintroduced_names':future,'retrospective_expansion':full,'retrospective_definitions':allused,'future_definition_ids':sorted(set(allused)-set(used)),'context':' '.join(x['word'] for x in byline[t['line']]),'interpretive_distinction':'MENTION_VS_OBJECT_UNTESTED'})
deps=[]
for e in entries:
 for w,at in zip(e['body'],e['body_loci']):
  if w in lex:deps.append({'definition':e['id'],'name':e['name'],'body_at':at,'dependency':w,'dependency_definition':lex[w]['id'],'dependency_precedes':lex[w]['name_index']<e['marker_index']})
counts=Counter(t['word'] for t in tokens)
summary=[]
for name,e in lex.items():
 aa=[a for a in app if a['name']==name];full,uses,_=expand(name)
 summary.append({'name':name,'definition':e['id'],'body':' '.join(e['body']),'all_occurrences':counts[name],'declarations':sum(x['name']==name for x in entries),'uses':len(aa),'before_declaration':sum(not a['declaration_precedes'] for a in aa),'after_declaration':sum(a['declaration_precedes'] for a in aa),'after_outside_definitions':sum(a['declaration_precedes'] and a['location_role']=='OTHER_TEXT' for a in aa),'fully_resolved_after':sum(a['declaration_precedes'] and not a['unintroduced_names'] for a in aa),'retrospective_leaf_count':len(full)})
# Exploratory application diagnostic: retain all direct written explanation matches,
# including the defining occurrence; classify rather than selecting favorable ones.
body_matches=[]
for e in entries:
 for rid in dict.fromkeys(t['record'] for t in tokens):
  rr=[t for t in tokens if t['record']==rid];n=len(e['body'])
  for k in range(len(rr)-n+1):
   chunk=rr[k:k+n]
   if [t['word'] for t in chunk]!=e['body']:continue
   overlap=any(t['at'] in body_owners or t['at'] in quote_owners or t['at'] in marker_owners for t in chunk)
   body_matches.append({'definition':e['id'],'name':e['name'],'record':rid,'start':chunk[0]['at'],'end':chunk[-1]['at'],'body':' '.join(e['body']),'outside_all_definition_units':not overlap})
table('BODY_MATCHES.tsv',body_matches,['definition','name','record','start','end','body','outside_all_definition_units'])
readings=['# W92 — vollständige N/C-Arbeitslesungen','', 'N: Benennung; C: Zusammensetzung/Beschreibung. Alle Formwörter in ⟦ ⟧ sind unübersetzt. Aufgelöste Namen verweisen auf ebenfalls unübersetzte Ausdrücke. Keine flüssige Inhaltsübersetzung.',''];alignment=[]
for r in rows:
 ts=byline[r['locus']]
 if not readings[-1:].count('## '+r['record_id']) and (not any(x=='## '+r['record_id'] for x in readings)):readings+=['## '+r['record_id'],'']
 readings+=[r['locus']+' — `'+r['zl3b_line']+'`','']
 for mode in ['N','C']:
  words=[]
  for t in ts:
   if t['at'] in marker_owners:render='[nennt man?]' if mode=='N' else '[beschreibt/bildet?]'
   elif t['at'] in quote_owners:render='«'+t['word']+'»' if mode=='N' else '[Objekt/Typ '+t['word']+']'
   elif t['word'] in lex:
    e=lex[t['word']];render='⟦'+t['word']+'⟧'+('〔→'+e['id']+'〕' if e['name_index']<t['index'] else '〔noch nicht eingeführt〕')
   else:render='⟦'+t['word']+'⟧'
   words.append(render);alignment.append({'record':t['record'],'at':t['at'],'word':t['word'],'mode':mode,'role':'MARKER' if t['at'] in marker_owners else 'DECLARATION_TARGET' if t['at'] in quote_owners else 'DEFINITION_BODY' if t['at'] in body_owners else 'OTHER_TEXT','reading':render})
  readings+=[mode+': '+' '.join(words),'']
(D/'READINGS.md').write_text('\n'.join(readings).rstrip()+'\n')
dump('DEFINITIONS.json',entries);dump('APPLICATIONS.json',app)
application_md=['# W92 — alle Anwendungen der vorgeschlagenen Namen','', 'Vorher/nachher bezieht sich auf die angesetzte Einführung. Auflösung ist nur Ersetzung durch ebenfalls unübersetzte Formen. Definitionen sind Hypothesen.','', '| Stelle | Name | Einführung vorher? | Rolle | Zeitgerecht verfügbare Auflösung | Noch nicht eingeführte Namen | Ganze Quellzeile |','|---|---|---|---|---|---|---|']
for a in app:
 application_md.append('| '+a['at']+' | '+a['name']+' | '+('ja' if a['declaration_precedes'] else 'nein')+' | '+a['location_role']+' | '+' '.join(a['sequential_expansion'])+' | '+', '.join(a['unintroduced_names'])+' | '+a['context']+' |')
(D/'APPLICATIONS.md').write_text('\n'.join(application_md)+'\n')
table('CANDIDATES.tsv',summary,list(summary[0]));table('DEPENDENCIES.tsv',deps,['definition','name','body_at','dependency','dependency_definition','dependency_precedes']);table('ALIGNMENT.tsv',alignment,list(alignment[0]))
result={'status':'EXPLORATORY_FIXED_NAMING_GRAMMAR_APPLICATION_AUDIT','source_groups':len(tokens),'lines':len(rows),'records':len({r['record_id'] for r in rows}),'marker_occurrences':len(entries),'definition_targets':len(quote_owners),'distinct_names':len(lex),'names_without_other_use':sum(s['uses']==0 for s in summary),'body_positions':len(body_owners),'name_uses':len(app),'uses_before_declaration':sum(not a['declaration_precedes'] for a in app),'uses_after_declaration':sum(a['declaration_precedes'] for a in app),'after_outside_definitions':sum(a['declaration_precedes'] and a['location_role']=='OTHER_TEXT' for a in app),'fully_resolved_after':sum(a['declaration_precedes'] and not a['unintroduced_names'] for a in app),'uses_in_definitions':sum(a['location_role']=='DEFINITION_BODY' for a in app),'dependency_occurrences':len(deps),'forward_dependency_occurrences':sum(not d['dependency_precedes'] for d in deps),'cycles':0,'conflicting_definitions':0,'applications_with_shared_N_C_substitution_policy':len(app),'confirmed_meanings':0,'nonmarker_content_positions_untranslated':len(tokens)-len(entries),'independent_confirmation_capacity':0,'reserved_access':False,'grammar_selected':False,'concrete_content_glosses':0,'direct_body_matches':len(body_matches),'direct_body_matches_outside_definition_units':sum(b['outside_all_definition_units'] for b in body_matches)}
dump('RESULT.json',result)
origin=D.parent/'W91/PROSE.tsv'
dump('SOURCE.json',{'source':str(origin.relative_to(Path.cwd())) if origin.is_relative_to(Path.cwd()) else 'research_registry/proposals/translation_programs_20260912/work/W91/PROSE.tsv','source_sha256':hashlib.sha256(origin.read_bytes()).hexdigest(),'guard':'query-tsv --selector page --allow f83r --columns page,panel_id,record_id,locus,zl3b_line','local_hashes':{n:hashlib.sha256((D/n).read_bytes()).hexdigest() for n in ['PROSE.tsv','DECISION.md','MODEL.json']},'sealed':['f84','f84r'],'exposure':'all previously exposed; exploratory, no independent held data'})
print(json.dumps(result,indent=2));print('\n'.join(str(s) for s in summary))
