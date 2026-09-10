#!/usr/bin/env python3
"""Complete sound finite necessary word domains and operator-pair projections."""
import itertools
from collections import Counter
def build(source,paragraphs):
 records=source['records'];atoms=source['atoms']
 if len(paragraphs)<len(records):return {'status':'CAPACITY_STOP','required':len(records),'available':len(paragraphs)}
 pc=[Counter(p['words']) for p in paragraphs];rc=[Counter(r['sequence']) for r in records]
 words=sorted({w for p in paragraphs for w in p['words']});observed={w:Counter(c[w] for c in pc) for w in words}
 needed={a:Counter(c[a] for c in rc) for a in atoms};domains={a:[] for a in atoms};exclusions={a:[] for a in atoms}
 for a in atoms:
  for w in words:
   bad=[(m,n,observed[w][m]) for m,n in needed[a].items() if observed[w][m]<n]
   if bad:
    m,n,available=sorted(bad)[0];exclusions[a].append([w,m,n,available])
   else:domains[a].append(w)
 empty=[a for a in atoms if not domains[a]]
 out={'required':len(records),'available':len(paragraphs),'word_type_count':len(words),'domains':domains,'empty_atoms':empty,
      'required_histograms':{a:dict(sorted(c.items())) for a,c in needed.items()},'exclusions':exclusions}
 if empty:
  out['status']='EMPTY_ATOM_DOMAINS_UNSAT';return out
 required_ns=[r['row_count'] for r in records];assert len(set(required_ns))==len(required_ns)
 pairs=[];rejected=[]
 for f,e in itertools.product(domains['OP:fia'],domains['OP:fa']):
  if f==e:continue
  support={n:[] for n in required_ns}
  for j,p in enumerate(paragraphs):
   n=pc[j][f]
   if n not in support or pc[j][e]!=n:continue
   if [w for w in p['words'] if w in (f,e)]==[f,e]*n:support[n].append(j)
  missing=[n for n in required_ns if not support[n]]
  if missing:rejected.append({'fia':f,'fa':e,'missing_row_counts':missing})
  else:pairs.append({'fia':f,'fa':e,'paragraph_support_by_row_count':support})
 out.update(status='OPERATOR_PAIR_DOMAINS_UNSAT' if not pairs else 'FULL_DECIMAL_SOLVER_REQUIRED',operator_pairs=pairs,rejected_operator_pairs=rejected)
 return out
