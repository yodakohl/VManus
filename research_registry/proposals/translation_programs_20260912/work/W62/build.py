from pathlib import Path
import json,csv,hashlib,collections
D=Path(__file__).parent;s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);occ=[]
for src in s['sources']:
 assert hashlib.sha256(Path(src).read_bytes()).hexdigest()==s['hashes'][src]
 data=json.loads(Path(src).read_text())
 for l in data['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84')
  gs=[dict(zip(data['group_columns'],g)) for g in l['groups']]
  for i,g in enumerate(gs):
   if g['ivtff_group_raw']!='sheckhy':continue
   n=gs[i+1] if i+1<len(gs) else None
   occ.append(dict(edition=m['edition'],locus=m['locus'],id=g['source_group_id'],right=n['ivtff_group_raw'] if n else None,right_definite=bool(n and g['right_separator']==n['left_separator']=='DEFINITE_SPACE' and int(n['source_group_index'])==int(g['source_group_index'])+1),words=[x['ivtff_group_raw'] for x in gs]))
(D/'OCCURRENCES.json').write_text(json.dumps(occ,indent=2)+'\n')
base=[r for r in csv.DictReader((D.parent/'W61/ALIGNMENT.tsv').open(),delimiter='\t') if r['model']=='R'];out=[];md=['# Vollständige Nomen-/Handlungsfassungen','', 'Alle deutschen Werte sind Annahmen; keine bestätigte Übersetzung.','']
for model,gloss in [('N','Mischung'),('A','vermische')]:
 for ed,para in dict.fromkeys((r['edition'],r['paragraph']) for r in base):
  md+=['## '+ed+' '+para+' / '+model,''];rows=[r for r in base if (r['edition'],r['paragraph'])==(ed,para)]
  for locus in dict.fromkeys(r['at'].split('|')[1] for r in rows):
   ll=[r for r in rows if r['at'].split('|')[1]==locus];vv=[]
   for r in ll:
    r=dict(r,model=model);r['hypothesis']=gloss if r['word']=='sheckhy' else r['hypothesis'];out.append(r);vv.append(r['hypothesis'])
   md+=[locus+' `'+ ' '.join(r['word'] for r in ll)+'`','', ' · '.join(vv),'']
(D/'READINGS.md').write_text('\n'.join(md)+'\n')
with (D/'ALIGNMENT.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]),delimiter='\t');w.writeheader();w.writerows(out)
r=dict(counts=dict(collections.Counter(x['edition'] for x in occ)),direct_qokain=[x for x in occ if x['right']=='qokain'],qolshey_successor=[x for x in occ if x['right']=='qolshey'],new_gloss_confirmed=False,selection=None)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k not in ['direct_qokain','qolshey_successor']}))
for x in r['direct_qokain']:print(x['edition'],x['locus'],x['right_definite'])
