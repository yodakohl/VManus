"""Independent direct-index reconstruction; no builder import."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P03')
def rr(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
source=json.loads((D/'SOURCE.json').read_text())
for p,h in source['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
orig=json.loads((D.parent/'P11/INPUT.json').read_text())['lines'];flat=[]
for r in orig:
 for i,w in enumerate(r['groups'],1):flat.append((r['locus'].split('.')[0],r['locus'],f'{r["locus"]}:{i}',w))
assert [(r['record'],r['line'],r['locus'],r['word']) for r in rr('INPUT.tsv')]==flat
lex=list(csv.DictReader((D.parent/'P11/COMMON_LEXICON.tsv').open(),delimiter='\t'));mat={r['word'] for r in lex if r['type']=='MATERIAL'}
v={'cphos','cpho','qotchy','shytchy','shot'};q={'dair':'A','dain':'B','daiin':'C','dary':'D','ar':'E'}
ops=rr('OPERATIONS.tsv');ends=rr('ENDPOINTS.tsv');quant=rr('QUANTITIES.tsv');inventory=rr('INVENTORY.tsv')
byloc={r[2]:j for j,r in enumerate(flat)};expected_ops=[];expected_ends=[];expected_quant=[]
for j,(rec,line,loc,w) in enumerate(flat):
 prefix=[r for r in flat[:j] if r[0]==rec];nm=[r for r in prefix if r[3] in mat];pp=[r for r in prefix if r[3]=='she'];last=nm[-1] if nm else None
 if w in v or w=='sho':
  if w=='sho':
   suffix=[]
   for t in flat[j+1:]:
    if t[1]!=line or t[3] in v|{'sho'}:break
    suffix.append(t)
   mm=[t for t in suffix if t[3] in mat];arg=mm[0] if mm else None
   status='BOUND' if arg and pp else 'MISSING_RECIPIENT' if arg else 'MISSING_MATERIAL_AND_OR_RECIPIENT'
  else:arg=last;status=('BOUND_PRIMARY_MISSING_LIQUID' if w=='shytchy' else 'BOUND') if arg else 'MISSING_MATERIAL'
  old=[x for x in expected_ops if x['record']==rec and x['kind']=='MANUFACTURE' and arg and x['material']==arg[3]]
  dose=[x for x in expected_quant if x['record']==rec and arg and x['material']==arg[3]]
  expected_ops.append({'record':rec,'locus':loc,'word':w,'kind':'APPLICATION' if w=='sho' else 'MANUFACTURE','material':arg[3] if arg else 'NA','material_source':arg[2] if arg else 'NA','recipient':'E' if w=='sho' and pp else 'NA','recipient_source':pp[-1][2] if w=='sho' and pp else 'NA','prior_manufacture':old[-1]['locus'] if old else 'NA','amount':dose[-1]['value'] if w=='sho' and dose else 'NA','amount_source':dose[-1]['locus'] if w=='sho' and dose else 'NA','status':status})
 if w in q:expected_quant.append({'record':rec,'locus':loc,'word':w,'material':last[3] if last else 'NA','material_source':last[2] if last else 'NA','value':q[w],'status':'BOUND' if last else 'MISSING_MATERIAL'})
 if w in {'shey','sy'}:
  app=[x for x in expected_ops if x['record']==rec and x['kind']=='APPLICATION' and x['status']=='BOUND']
  expected_ends.append({'record':rec,'locus':loc,'word':w,'recipient':'E' if pp else 'NA','recipient_source':pp[-1][2] if pp else 'NA','prior_application':app[-1]['locus'] if app else 'NA','status':'REFERENCE_MISSING' if not pp else 'AFTER_APPLICATION' if app else 'BEFORE_APPLICATION'})
for actual,expected in [(ops,expected_ops),(ends,expected_ends),(quant,expected_quant)]:
 for mode in ['T','M']:
  subset=[r for r in actual if r['mode']==mode];assert len(subset)==len(expected)
  for a,e in zip(subset,expected):assert all(a[k]==val for k,val in e.items()),(mode,e,a)
# Exact graph equality after removing only declared semantic labels.
for rows,drop in [(ops,{'mode','operation'}),(ends,{'mode','meaning'}),(quant,{'mode'})]:
 normal=lambda mode:[{k:v for k,v in r.items() if k not in drop} for r in rows if r['mode']==mode]
 assert normal('T')==normal('M')
for mode in ['T','M']:
 aa=rr(f'ALIGNMENT_{mode}.tsv');assert [(r['record'],r['line'],r['locus'],r['word']) for r in aa]==flat
 assert len([r for r in aa if r['kind']=='OPEN'])==56
 assert all(r['rendering']=='⟦'+r['word']+'⟧' for r in aa if r['kind']=='OPEN')
 assert all(r['kind']=='OPEN' for r in aa if r['word']=='sheey')
 assert [(r['record'],r['line'],r['locus'],r['word']) for r in inventory if r['mode']==mode]==[r for r in flat if r[3] in mat]
 for dim in ['D','H','G']:
  text=(D/f'READING_{mode}_{dim}.md').read_text()
  assert all('`'+line['raw_line']+'`' in text for line in orig)
  assert '{DIM}' not in text
 result=json.loads((D/'RESULT.json').read_text())['worlds'][mode]
 assert result['manufacturing']==dict(Counter(r['status'] for r in expected_ops if r['kind']=='MANUFACTURE'))
 assert result['applications']==dict(Counter(r['status'] for r in expected_ops if r['kind']=='APPLICATION'))
 assert result['endpoints']==dict(Counter(r['status'] for r in expected_ends))
 assert result['quantity_bindings']==dict(Counter(r['status'] for r in expected_quant))
 assert result['applications_with_written_dose']==0 and result['applications_with_prior_same_material_manufacture']==0
assert len(expected_ops)==10 and len(expected_ends)==3 and len(expected_quant)==12
assert all(r['status']!='AFTER_APPLICATION' for r in expected_ends)
assert all(r['D_application']=='NONE' for r in rr('QUANTITY_CONSEQUENCES.tsv'))
receipt={'status':'PASS','source_hashes':len(source['inputs']),'complete_groups_per_world':len(flat),'independent_operation_rows':len(ops),'independent_endpoint_rows':len(ends),'independent_quantity_rows':len(quant),'complete_readings':6,'graph_renaming_equality':True,'checks':['prefix and same-line bounded forward references','all operation endpoint and amount occurrences','whole-form distinction shey/sheey','no dose or manufacture-to-application link','no after-application effect','six full source-preserving readings'],'limit':'Execution consistency, not meanings, therapeutic efficacy or scientific significance.'}
(D/'VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
