from pathlib import Path
import csv,json,collections
D=Path(__file__).parent
src=json.loads((D.parent/'P09/INPUT.json').read_text());base=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['D1']['lexicon'];lines=src['lines'];rows=[];rels=[];md=['# Ganze Katalogfassungen E und C','','Alle Wortwerte unbestätigt; Argumente bleiben unbekannte Rohformen. Keine gelesene Heilwirkung.','']
for model in ['E','C']:
 lex={w:x['meaning'] for w,x in base.items()}
 if model=='C':lex.update(qotaiin='verursacht [Beschwerde]',shey='verursacht [Beschwerde]')
 last={};md+=['## '+model,'']
 for l in lines:
  page=l['locus'].split('.')[0];ws=l['groups'];md += [l['locus']+' `'+l['raw_line']+'`',''];out=[]
  for i,w in enumerate(ws):
   at=l['locus']+':'+str(i+1);gl=lex.get(w,'⟦'+w+'⟧');rows.append(dict(model=model,at=at,word=w,hypothesis=gl));out.append(gl)
   if w in {'qotaiin','shey','qotchy'}:
    arg=ws[i+1] if i+1<len(ws) else '';argat=l['locus']+':'+str(i+2) if arg else '';harm=w!='qotchy';linked=last.get(page)
    r=dict(model=model,page=page,at=at,word=w,kind='HARM' if harm else 'CORRECTION',argument=arg,argument_at=argat,argument_type=('UNKNOWN_RECIPIENT' if model=='E' else 'UNKNOWN_CONDITION') if harm else 'UNKNOWN_CORRECTIVE',linked_harm='' if harm or not linked else linked['at'],linked_target='' if harm or not linked else linked['argument'],obligation=('harms recipient' if model=='E' else 'causes condition') if harm else 'protect same recipient' if model=='E' else 'reduce/remove same condition',observed_effect='NOT_IDENTIFIED')
    rels.append(r)
    if harm:last[page]=r
  md += [' · '.join(out),'']
  for r in [r for r in rels if r['model']==model and r['at'].rsplit(':',1)[0]==l['locus']]:md+=['- '+r['at']+': '+r['kind']+' '+r['argument_type']+' ⟦'+r['argument']+'⟧; '+r['obligation']+(' ⟦'+r['linked_target']+'⟧' if r['linked_target'] else '')+'; Wirkung nicht identifiziert.']
  md+=['']
forms={r['argument'] for r in rels if r['argument']};occ=[dict(at=l['locus']+':'+str(i+1),word=w) for l in lines for i,w in enumerate(l['groups']) if w in forms or w=='chkaiin']
for name,data in [('ALIGNMENT.tsv',rows),('RELATIONS.tsv',rels),('ALL_ARGUMENT_AND_EFFICACY_OCCURRENCES.tsv',occ)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),delimiter='\t');w.writeheader();w.writerows(data)
(D/'READING.md').write_text('\n'.join(md)+'\n');r=dict(alignment_rows=len(rows),source_groups=len(rows)//2,relation_rows=len(rels),per_model={m:dict(harms=sum(r['model']==m and r['kind']=='HARM' for r in rels),corrections=sum(r['model']==m and r['kind']=='CORRECTION' for r in rels)) for m in ['E','C']},argument_occurrences=dict(collections.Counter(r['word'] for r in occ)),confirmed_meanings=0,observed_corrective_effects=0,selected=None)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
