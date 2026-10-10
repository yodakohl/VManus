"""Check the manually collated finite segment, not a Voynich or full-book decoder."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent;R=B.parents[3]
t=json.loads((B/'TABLE.json').read_text());s=json.loads((B/'SOURCES.json').read_text())
for x in s['images']:
 p=R/x['path'];assert p.stat().st_size==x['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==x['sha256']
a=t['alphabet_labels'];assert len(a)==len(set(a))==24
checked=0
for c in t['columns']:
 words=c['words'];assert len(words)==len(set(words))==24
 forward=dict(zip(a,words));reverse={w:k for k,w in forward.items()}
 for k in a:assert reverse[forward[k]]==k;checked+=1
ex=t['author_example'];encoded=[c['words'][a.index(k)] for c,k in zip(t['columns'],ex['table_label_sequence'])];assert encoded==ex['cover_words'];decoded=''.join(a[c['words'].index(w)] for c,w in zip(t['columns'],ex['cover_words']));assert decoded=='cave';assert ex['printed_plaintext_prefix']=='caue'
r={'status':'PASS','image_hashes':len(s['images']),'manually_collated_cells':checked,'author_example_cover':encoded,'table_label_inverse':decoded,'printed_plaintext':'caue','scope':'Integrity, per-column injectivity and source-authored four-letter example. No independent full96-cell transcription check, no full-book decoder, no arbitrary-message roundtrip or Voynich result.'}
(B/'VALIDATION.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
