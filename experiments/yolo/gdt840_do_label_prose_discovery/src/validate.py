import json
from pathlib import Path
E=Path(__file__).resolve().parents[1]
p=E/'artifacts/CARDS.json'
if not p.exists():print('Source/protocol registered; no data validation claimed');raise SystemExit(0)
cards=json.loads(p.read_text());rows=json.loads((E/'artifacts/OCCURRENCES.json').read_text());ids={r['id']:r for r in rows};assert len(ids)==len(rows)
for c in cards:
 assert c['extended']==c['base']+'do'
 for key,word,role in [('extended_labels',c['extended'],'label'),('bare_labels',c['base'],'label'),('extended_prose',c['extended'],'prose'),('bare_prose',c['base'],'prose')]:
  expected=sorted(r['id'] for r in rows if r['edition']==c['edition'] and r['word']==word and r[role]);assert sorted(c[key])==expected
 assert c['same_page_forward']==sorted({ids[x]['page'] for x in c['extended_labels'] for y in c['bare_prose'] if ids[x]['page']==ids[y]['page']})
r=json.loads((E/'artifacts/RESULT.json').read_text())
for ed,s in r['summary'].items():
 subset=[c for c in cards if c['edition']==ed];assert s['candidates']==len(subset)
 for direction,left,right in [('forward','extended_labels','bare_prose'),('reverse','bare_labels','extended_prose')]:assert s[direction+'_bases']==[c['base'] for c in subset if c[left] and c[right]]
result=dict(status='PASS',cards=len(cards),occurrences=len(rows),independent_card_reconstruction=True,shared_extraction=True)
(E/'artifacts/VALIDATION.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print(result)
