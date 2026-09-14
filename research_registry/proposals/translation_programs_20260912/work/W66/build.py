from pathlib import Path
import csv,json
D=Path(__file__).parent;base=[r for r in csv.DictReader((D.parent/'W63/ALIGNMENT.tsv').open(),delimiter='\t') if r['model']=='N']
variants={'F':{'solchey':'dasselbe Material','okain':'Maß P'},'T':{'solchey':'nächster Arbeitsgang','okain':'Zusatz E'}}
rows=[];changes=[];md=['# Zwei vollständige gekoppelte Arbeitsentwürfe','', 'Alle deutschen Werte sind Annahmen. Bezug von „dasselbe“, Maßwert und Zusatzidentität sind nicht gebunden. ⟦…⟧ bleibt offen.','']
for model,lex in variants.items():
 for ed,para in dict.fromkeys((r['edition'],r['paragraph']) for r in base):
  md+=['## '+ed+' '+para+' / '+model,''];rr=[r for r in base if (r['edition'],r['paragraph'])==(ed,para)]
  for locus in dict.fromkeys(r['at'].split('|')[1] for r in rr):
   ll=[r for r in rr if r['at'].split('|')[1]==locus];out=[]
   for b in ll:
    r=dict(b,model=model);r['hypothesis']=lex.get(r['word'],r['hypothesis']);rows.append(r);out.append(r['hypothesis'])
    if r['word'] in lex:changes.append(r)
   md+=[locus+' `'+ ' '.join(r['word'] for r in ll)+'`','', ' · '.join(out),'']
for n,rs in [('ALIGNMENT.tsv',rows),('NEW_ASSUMPTIONS.tsv',changes)]:
 with (D/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]),delimiter='\t');w.writeheader();w.writerows(rs)
(D/'READINGS.md').write_text('\n'.join(md)+'\n')
r=dict(alignment_rows=len(rows),new_assumed_positions=len(changes),variant_glosses=variants,selected=None,reference_identity_bound=False,meaning_confirmations=0)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
