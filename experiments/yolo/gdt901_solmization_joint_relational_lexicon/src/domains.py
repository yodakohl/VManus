#!/usr/bin/env python3
"""Sound complete count-capacity domains for the registered global lexicon."""
from collections import Counter

def build(source,paragraphs):
 records=source['records'];atoms=source['atoms']
 if len(paragraphs)<len(records):
  return {'status':'CAPACITY_STOP','required':len(records),'available':len(paragraphs)}
 counts=[Counter(p['words']) for p in paragraphs]
 words=sorted(set().union(*(set(c) for c in counts)))
 heads={p['words'][0] for p in paragraphs}
 source_counts=[Counter(p['sequence']) for p in records]
 needed={a:Counter(c[a] for c in source_counts) for a in atoms}
 observed={w:Counter(c[w] for c in counts) for w in words}
 head_atoms={r['head_atom'] for r in records}
 domains={a:[w for w in words if (a not in head_atoms or w in heads) and all(observed[w][m]>=n for m,n in needed[a].items())] for a in atoms}
 excluded={a:[] for a in atoms}
 for a in atoms:
  allowed=set(domains[a])
  for w in words:
   if w in allowed:continue
   if a in head_atoms and w not in heads:
    excluded[a].append({'word':w,'reason':'NOT_ANY_PARAGRAPH_HEAD'});continue
   m=next(m for m,n in sorted(needed[a].items()) if observed[w][m]<n)
   excluded[a].append({'word':w,'reason':'EXACT_MULTIPLICITY_CAPACITY','count':m,'required_paragraphs':needed[a][m],'available_paragraphs':observed[w][m]})
 return {'status':'EMPTY_ATOM_DOMAINS_UNSAT' if any(not v for v in domains.values()) else 'DOMAINS_NONEMPTY_MODEL_NOT_SOLVED',
         'required':len(records),'available':len(paragraphs),'word_type_count':len(words),
         'required_histograms':{a:dict(sorted(h.items())) for a,h in needed.items()},
         'domains':domains,'empty_atoms':[a for a,v in domains.items() if not v],
         'exclusions':excluded}
