import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path(__file__).parent;S=json.loads((D/'SPEC.json').read_text())
for p,h in S['hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
allowed=set(json.loads(Path(S['allow_source']).read_text())['allowed_selectors'])
reported=list(csv.DictReader((D/'OCCURRENCES.tsv').open(),delimiter='\t'));counts=Counter();expected=[];all_lines={}
for source in S['sources']:
 d=json.loads(Path(source).read_text());cols=d['group_columns'];wi=cols.index('ivtff_group_raw');si=cols.index('source_group_id')
 for r in d['lines']:
  m=r['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
  key=(m['edition'],m['locus']);assert key not in all_lines;all_lines[key]=(m,r['groups'],cols)
  counts[m['edition'],'lines']+=1;counts[m['edition'],'groups']+=len(r['groups'])
  for g in r['groups']:
   if g[wi]=='ysheol':expected.append((m['edition'],m['locus'],g[si]));counts[m['edition'],'exact_hits']+=1
assert sorted(expected)==sorted((r['edition'],r['locus'],r['source_id']) for r in reported)
result=json.loads((D/'RESULT.json').read_text())
for ed,dd in result['counts'].items():
 for k,v in dd.items():assert counts[ed,k]==v
context=json.loads((D/'CONTEXTS.json').read_text());paras=json.loads(Path(S['paragraphs']).read_text())
for p in context['paragraphs']:
 assert {k:v for k,v in p.items() if k!='edition'}==next(x for x in paras[p['edition']] if x['id']==p['id'])
 for l in p['lines']:
  m,gs,cols=all_lines[p['edition'],l['locus']]
  assert l['words']==[g[cols.index('ivtff_group_raw')] for g in gs]
for h in reported:
 m,gs,cols=all_lines[h['edition'],h['locus']];ids=[g[cols.index('source_group_id')] for g in gs];i=ids.index(h['source_id'])
 assert h['previous']==(gs[i-1][cols.index('ivtff_group_raw')] if i else 'NONE')
 assert h['raw_line']==' '.join(g[cols.index('ivtff_group_raw')] for g in gs)
 assert h['old_locus']==str(m['locus']==S['old_locus'])
assert result['additional_loci']==sorted({loc for ed,loc,sid in expected if loc!=S['old_locus']})
assert {(l['metadata']['edition'],l['metadata']['locus']) for l in context['same_locus_source_lines']}=={key for key in all_lines if key[1] in {loc for ed,loc,sid in expected}}
res=dict(status='PASS',bound_files=len(S['hashes']),source_lines=sum(v for (ed,k),v in counts.items() if k=='lines'),source_groups=sum(v for (ed,k),v in counts.items() if k=='groups'),exact_hits=len(expected),complete_target_paragraphs=len(context['paragraphs']),independent_meaning_validation=False)
(D/'VALIDATION.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2))
