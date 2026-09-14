from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);expected=[]
for path in s['sources']:
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==s['hashes'][path]
 d=json.loads(Path(path).read_text());cols=d['group_columns'];wi=cols.index('ivtff_group_raw');ai=cols.index('source_group_id')
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');ws=[g[wi] for g in l['groups']]
  expected.extend((m['edition'],m['locus'],g[ai],ws) for g in l['groups'] if g[wi]=='qoteey')
o=json.loads((D/'OCCURRENCES.json').read_text());assert expected==[(r['edition'],r['locus'],r['at'],r['words']) for r in o] and len(o)==121
loci={r['locus'] for r in o};src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}];assert ps==json.loads((D/'PARAGRAPHS.json').read_text()) and len(ps)==76
lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];lex.update(otchy=dict(meaning='Material T',kind='MATERIAL'),qoteey=dict(meaning='Material U',kind='MATERIAL'));vals={'dair':'A','dain':'B','daiin':'C'};al=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));vv=list(csv.DictReader((D/'VALUES.tsv').open(),delimiter='\t'));aa=list(csv.DictReader((D/'OPERATIONS.tsv').open(),delimiter='\t'));exp=[];nv=na=0
for p in ps:
 last=''
 for l in p['lines']:
  for i,(sid,w) in enumerate(zip(l['source_ids'],l['words'])):
   g='Masse '+vals[w]+'·Uₚ' if w in vals else lex[w]['meaning'] if w in lex else '⟦'+w+'⟧';exp.append(dict(edition=p['edition'],paragraph=p['id'],at=sid,word=w,hypothesis=g))
   if lex.get(w,{}).get('kind')=='MATERIAL':last=sid
   if w in vals:
    r=next(r for r in vv if r['edition']==p['edition'] and r['at']==sid);assert r['material']==last;nv+=1
   if w in {'qotchy','qotaiin','shey','chkaiin'}:
    r=next(r for r in aa if r['edition']==p['edition'] and r['at']==sid);assert r['input']==(l['words'][i+1] if i+1<len(l['words']) else '') and r['recipient']==(last if w in {'qotchy','chkaiin'} else '');na+=1
assert exp==al and len(al)==4272 and nv==len(vv)==110 and na==len(aa)==54
v=dict(status='PASS',all_occurrences=121,full_paragraphs=76,all_groups=4272,values=110,operations=54,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
