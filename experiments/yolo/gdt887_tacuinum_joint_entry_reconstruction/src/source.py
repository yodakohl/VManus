"""Frozen source-first lexical serialization of the complete three-entry passage."""
import json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1]
ENTITIES=['LACTUCA','PIRETRUM','APIUM','FENICULUM']
ALIASES={'lactuce':'@LACTUCA','lactucis':'@LACTUCA','apium':'@APIUM','apio':'@APIUM','appio':'@APIUM','feniculo':'@FENICULUM','calida':'CALIDUS','calidis':'CALIDUS','frigida':'FRIGIDUS','frigidis':'FRIGIDUS','sicca':'SICCUS','siccis':'SICCUS','humida':'HUMIDUS','primi':'DEGREE_I','1':'DEGREE_I','2':'DEGREE_II','nocumenti':'NOCUMENTUM','generant':'GENERARE','generat':'GENERARE','conueniunt':'CONVENIRE','conuenit':'CONVENIRE'}
IMPLICIT={'et','in','cum'}

def tokenize(s):
 words=re.findall('[A-Za-z]+|[0-9]+',s)
 return [ALIASES.get(w.lower(),w.upper()) for w in words if w.lower() not in IMPLICIT]

def templates(headers):
 source=json.loads((E/'src/SOURCE.json').read_text());out=[]
 for r in source['entries']:
  slots=[dict(field='head',atom='@'+r['entity'],context='head',source=r['written_head'])]
  for f in r['fields']:
   if headers:
    slots.extend(dict(field=f['field'],atom=a,context='ordinary',source=f['heading']) for a in tokenize(f['heading']))
   if r['entity']=='APIUM' and f['field']=='corrective':
    slots.append(dict(field=f['field'],atom='@HELD',context='corrective',source='SOURCE_IDENTITY_WITHHELD'))
   else:
    for a in tokenize(f['text']):
     slots.append(dict(field=f['field'],atom=a,context='corrective' if a.startswith('@') else 'ordinary',source=f['text']))
  out.append(dict(entity=r['entity'],external_folio=r['external_folio'],slots=slots))
 assert sum(s['atom']=='@HELD' for r in out for s in r['slots'])==1
 return out

if __name__=='__main__':
 for h in [False,True]:print(json.dumps(dict(headers=h,counts={r['entity']:len(r['slots']) for r in templates(h)},templates=templates(h)),sort_keys=True))
