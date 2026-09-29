"""Check all seven external source mappings; no Voynich meaning validation."""
from pathlib import Path
import csv, hashlib, html, json, re
from html.parser import HTMLParser
B=Path(__file__).resolve().parent
receipt=json.loads((B/'AY_SOURCE_RECEIPT.json').read_text())
for name,key in [('AY_PTOLEMY_III12.html','chapter_html_sha256'),('AY_PTOLEMY_III12.txt','chapter_text_sha256'),('AY_DECISION.md','decision_note_sha256')]:
    assert hashlib.sha256((B/name).read_bytes()).hexdigest()==receipt[key],name
class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)
    def handle_starttag(self,tag,attrs):
        if tag in ('p','h2'):self.parts.append('\n\n')
p=Text();p.feed((B/'AY_PTOLEMY_III12.html').read_text())
replay='\n\n'.join(' '.join(x.split()) for x in ''.join(p.parts).split('\n\n') if x.strip())+'\n'
assert replay==(B/'AY_PTOLEMY_III12.txt').read_text()
# Independent enumeration from the full source sentence; pagination and footnote
# markers are editorial metadata, not parts of the correspondence list.
s=' '.join(re.sub(r'\bp\d+\b|\u2060\d+',' ',replay).split())
sentence=s[s.index('Saturn is lord'):s.index('For the most part it is a general principle')].strip().rstrip('.')
clauses=sentence.split('; ')
assert len(clauses)==7
expected=[]
for clause in clauses:
    m=re.fullmatch(r'(Saturn|Jupiter|Mars|the sun|Venus|Mercury|the moon)(?: is lord)? of (.*)',clause)
    assert m,clause
    body=m[1].replace('the ','').upper()
    members=re.split(r',\s*|\s+and\s+',m[2])
    members=[re.sub(r'^(?:and\s+)?(?:the\s+)?','',x).strip() for x in members if x.strip()]
    for idx,member in enumerate(members,1):expected.append((body,str(idx),member))
rows=list(csv.DictReader((B/'AY_ALL_CORRESPONDENCES.tsv').open(),delimiter='\t'))
observed=[(r['body'],r['member_index'],r['member']) for r in rows]
assert observed==expected,(observed,expected)
assert len(rows)==32 and len({r['body'] for r in rows})==7
assert all(r['relation']=='GOVERNS' for r in rows)
sun={r['member'] for r in rows if r['body']=='SUN'}
moon={r['member'] for r in rows if r['body']=='MOON'}
assert {'brain','heart'}.issubset(sun) and 'brain' not in moon
assert 'blindness in one eye' in s and 'moon by itself' in s
assert 'in company with Mercury' in s and 'drugs and the aid of good physicians' in s
result={'status':'PASS_EXTERNAL_SOURCE_COMPLETENESS_NOT_MEANING','mapping_rows':32,'bodies':7,'SUN_heart_MOON_brain_pair':'NOT_THIS_SOURCE','SUN_members':sorted(sun),'MOON_members':sorted(moon),'role_distinction':'governing part versus causing injury versus mitigating disease','target_meanings_selected':0,'independent_target_confirmation_capacity':0,'scope':'verifies retained source bytes, full mapping enumeration, explicit source-role examples; not Greek edition, medieval transmission or Voynich interpretation'}
(B/'AY_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
