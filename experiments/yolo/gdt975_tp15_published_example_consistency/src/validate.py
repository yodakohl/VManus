import csv,hashlib,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def main():
 for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 if not (E/'artifacts/RESULT.json').exists():print('PASS_DECLARATION_ONLY');return
 s=json.loads((E/'src/SOURCE.json').read_text());r=json.loads((E/'artifacts/RESULT.json').read_text())
 # Independent fixed constituent decomposition; no runner or upstream decoder import.
 units={'okaiin':['o','k','aiin'],'shey':['sh','ey'],'qokeey':['qok','e','ey'],'okey':['o','k','ey'],'chedy':['ch','e','dy'],'daiin':['d','aiin'],'sheey':['sh','e','ey'],'qokeedy':['qok','e','e','dy']}
 values={'o':'ra','k':'?','aiin':'n','sh':'se','ey':'','qok':'be','e':'ra','ch':'co','dy':'','d':'di'}
 checks={};rows=[]
 for x,y in zip(s['examples']+s['reproduction_cases'],r['rows']+r['reproduction']):
  u=units[x['token']];parts=[dict(eva=t,role='CODA_MARKER' if t in ['aiin','ey','dy'] else 'SYLLABIC',value=values[t]) for t in u];out=''.join(values[t] for t in u)
  # A free completion can append between fixed prefix/suffix, never rewrite either.
  if '?' in out:
   prefix,suffix=out.split('?');match=x['claimed'].startswith(prefix) and x['claimed'].endswith(suffix) and len(x['claimed'])>=len(prefix)+len(suffix)
  else:match=out==x['claimed']
  decision=('COMPATIBLE_UNRESOLVED' if '?' in out else 'MATCH') if match else 'CONTRADICTION'
  expected=dict(**x,components=parts,decoded=out,unknown_count=out.count('?'),decision=decision,immutable_prefix=out.split('?')[0]);rows.append(expected)
 checks['all_rows_exact']=rows==r['rows']+r['reproduction']
 checks['all_cases_accounted']=len(r['rows'])==len(s['examples'])==8 and len(r['reproduction'])==3
 checks['reproduction']=all(x['decision']=='MATCH' for x in r['reproduction'])
 checks['contradictions']=r['contradictions']==7 and r['matches']==1 and r['status']=='PUBLISHED_EXAMPLES_INCONSISTENT'
 checks['e_branch']=r['e_ambiguous_branch_identical']
 checks['ceilings']=not any(r[k] for k in ['full_table_available','full_passage_tested','manuscript_corpus_read','reserve_access','translated_words','independent_confirmation_capacity']) and r['prior_source_exposure']
 expected_table=[['id','paper_folio','eva','paper_output','components','fixed_fragment_output','unknowns','decision']]+[[str(v) for v in [x['id'],x['paper_folio'],x['token'],x['claimed'],' + '.join(p['value'] or 'EMPTY' for p in x['components']),x['decoded'],x['unknown_count'],x['decision']]] for x in rows[:8]]
 with (E/'artifacts/CANDIDATE_PREDICTIONS.tsv').open() as f:checks['table']=list(csv.reader(f,delimiter='\t'))==expected_table
 checks['vendor_receipts']=all(hashlib.sha256((R/x['local_excerpt']).read_bytes()).hexdigest()==x['excerpt_sha256'] for x in s['receipts'])
 v=dict(status='PASS' if all(checks.values()) else 'FAIL',checks=checks,independent_semantic_confirmation=False);(E/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v));assert v['status']=='PASS'
if __name__=='__main__':main()
