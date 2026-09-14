from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text());expected=[]
for p in ps:
 for l in p['lines']:
  for i,w in enumerate(l['words']):
   if w not in ('okain','solchey'):continue
   expected.append((p['edition'],p['id'],l['source_ids'][i],w,l['words'][i-1] if i else 'LINE_START',l['words'][i+1] if i+1<len(l['words']) else 'LINE_END',' '.join(l['words'])))
rs=list(csv.DictReader((D/'ALL_OCCURRENCES.tsv').open(),delimiter='\t'))
assert expected==[(r['edition'],r['paragraph'],r['at'],r['word'],r['left'],r['right'],r['full_line']) for r in rs] and len(rs)==16
v=dict(status='PASS',scope='all16exact word occurrences and full-line contexts',meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
