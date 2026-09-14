from pathlib import Path
import json,csv
D=Path(__file__).parent
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text());lex={r['form']:r for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')}
materials={w for w,r in lex.items() if r['role'] in ('MATERIAL','MATERIAL_DOSE')}|{'sheedy','shey','sheckhy'}
actions={w for w,r in lex.items() if r['role'] in ('ACTION','ACTION_TYPED','REPEAT_ACTION','REPEAT_COOL','MIX')}
occ=[];chains=[]
for p in ps:
 flat=[(sid,w) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
 for i,(sid,w) in enumerate(flat):
  if w!='qokain':continue
  direct=i>0 and flat[i-1][1]=='sheckhy'
  occ.append(dict(edition=p['edition'],paragraph=p['id'],at=sid,left=flat[i-1][1] if i else 'BOUNDARY',right=flat[i+1][1] if i+1<len(flat) else 'BOUNDARY',direct_sheckhy=direct))
  if not direct:continue
  aa=[j for j in range(i+1,len(flat)) if flat[j][1] in actions];j=aa[0] if aa else len(flat)
  intervening=flat[i+1:j];mm=[(a,w) for a,w in intervening if w in materials]
  chains.append(dict(edition=p['edition'],at=sid,first_later_action=flat[j][0] if aa else 'NONE',action_word=flat[j][1] if aa else 'NONE',action_gloss=lex[flat[j][1]]['hypothesis'] if aa else 'NONE',intervening_materials=';'.join(a+':'+w for a,w in mm),intervening_words=' '.join(w for _,w in intervening),capacity='POSSIBLE_UNDER_LEFT_RULE' if aa and not mm else 'MATERIAL_REPLACED' if aa else 'NO_ACTION',full_future=' '.join(w for _,w in flat[i+1:])))
for name,rows in [('ALL_QOKAIN.tsv',occ),('FOLLOWUPS.tsv',chains)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
res=dict(qokain_reading_positions=len(occ),direct_reading_positions=len(chains),capacity_reading_positions=sum(r['capacity']=='POSSIBLE_UNDER_LEFT_RULE' for r in chains),new_identity_model=False,meaning_confirmations=0)
(D/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res));print(json.dumps(chains,indent=2))
