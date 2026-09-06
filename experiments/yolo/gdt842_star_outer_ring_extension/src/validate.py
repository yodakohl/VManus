import json
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1]
a=json.loads((E/'artifacts/VIEWER_A.json').read_text());b=json.loads((E/'artifacts/VIEWER_B.json').read_text());r=json.loads((E/'artifacts/RESULT.json').read_text())
a={x['id']:x['state'] for x in a['judgments']};b={x['id']:x['state'] for x in b['judgments']};assert set(a)==set(b)=={f'O{i}' for i in range(1,11)}
c=Counter((a[k],b[k]) for k in a);agreement=sum(n for (x,y),n in c.items() if x==y);p=c['PIGMENTED_CENTRE','PIGMENTED_CENTRE'];o=c['OUTLINE_CENTRE','OUTLINE_CENTRE'];status='VISUAL_RING_EXTENSION_PASS' if agreement>=8 and p>=2 and o>=2 else 'STOP_VISUAL_CAPACITY'
assert (r['agreement'],r['agreed_pigmented'],r['agreed_outline'],r['status'])==(agreement,p,o,status)
obj=dict(status='PASS',confusion_matrix=[dict(A=x,B=y,count=n) for (x,y),n in sorted(c.items())],independent_arithmetic=True)
(E/'artifacts/VALIDATION.json').write_text(json.dumps(obj,indent=2)+'\n');print(obj)
