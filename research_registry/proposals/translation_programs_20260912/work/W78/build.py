from pathlib import Path
import json,csv,collections
D=Path(__file__).parent
src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());loci={'f19v.3','f18v.6','f2v.3','f56r.10'};ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}];lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];rows=[];events=[];md=['# Ganze Absatzfassungen N und Q','','Alle Wortwerte und Bindungen hypothetisch, keine Zustandsprüfung.','']
for p in ps:
 for m in ['N','Q']:
  dd={w:dict(v) for w,v in lex.items()};dd['otchy']=dict(meaning='Material T' if m=='N' else 'Eigenschaft T',kind='MATERIAL' if m=='N' else 'QUALITY_OR_STATE');last=None
  md+=['## '+m+' '+p['edition']+' '+p['id'],'']
  for l in p['lines']:
   ws=l['words'];ids=l['source_ids'];md += [l['locus']+' `'+ ' '.join(ws)+'`','', ' · '.join(dd[w]['meaning'] if w in dd else '⟦'+w+'⟧' for w in ws),'']
   for i,w in enumerate(ws):
    rows.append(dict(model=m,edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,hypothesis=dd[w]['meaning'] if w in dd else '⟦'+w+'⟧'))
    kind=dd.get(w,{}).get('kind')
    if kind=='MATERIAL':last=(ids[i],w)
    carrier=None;rule='';evkind=''
    if kind=='QUALITY_OR_STATE':
     evkind='QUALITY'
     if w=='otchy':
      choices=[j for j in [i-1,i+1] if 0<=j<len(ws) and dd.get(ws[j],{}).get('kind')=='MATERIAL'];carrier=(ids[choices[0]],ws[choices[0]]) if choices else None;rule='IMMEDIATE_LEFT_ELSE_RIGHT'
     else:carrier=last;rule='LAST_PRIOR_MATERIAL'
    elif w in {'qotaiin','qotchy','shey','chkaiin'}:
     evkind='ACTION';carrier=(ids[i+1],ws[i+1]) if i+1<len(ws) else None;rule='IMMEDIATE_RIGHT_INPUT'
    if evkind:
     r=dict(model=m,edition=p['edition'],paragraph=p['id'],at=ids[i],word=w,kind=evkind,carrier=carrier[0] if carrier else '',carrier_word=carrier[1] if carrier else '',rule=rule,recipient=last[0] if w in {'qotchy','chkaiin'} and last else '')
     events.append(r);md+=['- '+ids[i]+' '+evkind+' '+w+' → '+(r['carrier_word']+' @'+r['carrier'] if carrier else 'TRÄGER/EINGABE FEHLT')]
   md+=['']
by=collections.defaultdict(dict)
for e in events:by[(e['edition'],e['paragraph'],e['at'])][e['model']]=e
changes=[]
for key,mm in by.items():
 a=mm.get('N');b=mm.get('Q')
 if not a or not b or any(a[k]!=b[k] for k in ['carrier','recipient','kind']):changes.append(dict(edition=key[0],paragraph=key[1],at=key[2],word=(a or b)['word'],N_carrier=a['carrier'] if a else 'MATERIAL_NOT_PREDICATE',Q_carrier=b['carrier'] if b else '',N_word=a['carrier_word'] if a else 'otchy',Q_word=b['carrier_word'] if b else '',N_recipient=a['recipient'] if a else '',Q_recipient=b['recipient'] if b else ''))
for name,data in [('ALIGNMENT.tsv',rows),('EVENTS.tsv',events),('CHANGES.tsv',changes)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),delimiter='\t');w.writeheader();w.writerows(data)
(D/'PARAGRAPHS.json').write_text(json.dumps(ps,indent=2)+'\n');(D/'READING.md').write_text('\n'.join(md)+'\n');res=dict(paragraphs=len(ps),alignment_rows=len(rows),event_rows=len(events),changed_positions=len(changes),meaning_confirmed=False,selected=None);(D/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res));print(json.dumps(changes))
