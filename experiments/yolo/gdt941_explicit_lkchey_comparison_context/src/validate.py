"""Independent source/coverage/operand checks; validates execution, not semantics."""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import json,csv,hashlib,re
import run
EXP=Path(__file__).resolve().parents[1];ROOT=EXP.parents[2];ART=EXP/'artifacts'
def j(p):return json.loads(p.read_text())
def t(name):return list(csv.DictReader((ART/name).open(),delimiter='\t'))
m=j(EXP/'src/MODEL.json');lock=j(EXP/'PREREG_LOCK.json')
for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
spec=j(ROOT/m['inventory_spec']);allow=set(j(ROOT/spec['allow_source'])['allowed_selectors']);assert len(allow)==179 and not any(x.startswith('f84') or x=='f116v' for x in allow)
lines={};sources={}
for p in spec['sources']:
 d=j(ROOT/p);assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==spec['hashes'][p]
 for line in d['lines']:
  meta=line['metadata'];assert meta['page'] in allow and not meta['page'].startswith('f84')
  rr=[dict(**meta,**dict(zip(d['group_columns'],g))) for g in line['groups']];key=meta['edition'],meta['locus'];assert key not in lines;lines[key]=rr
  for r in rr:assert r['source_group_id'] not in sources;sources[r['source_group_id']]=r
assert len(sources)==96184
hits={sid:r for sid,r in sources.items() if r['ivtff_group_raw']=='lkchey'};assert len(hits)==24
loci={r['locus'] for r in hits.values()};assert len(loci)==9
cases=t('MARKER_CASES.tsv');assert len(cases)==len({(r['candidate'],r['marker_id']) for r in cases})==96
assert {(r['candidate'],r['marker_id']) for r in cases}=={(c,s) for c in m['candidates'] for s in hits}
for c in cases:
 r=hits[c['marker_id']];rr=lines[r['edition'],r['locus']];i=rr.index(r);pred=m['candidates'][c['candidate']]
 left=rr[i-1] if i else None;right=rr[i+1] if i+1<len(rr) else None
 assert c['left_raw']==(left['ivtff_group_raw'] if left else '') and c['right_raw']==(right['ivtff_group_raw'] if right else '')
 assert c['predicted_marker']==pred['marker_gloss']
 a=re.fullmatch(r'lka(i+)n',c['left_raw']);b=re.fullmatch(r'lka(i+)n',c['right_raw'])
 status='UNBOUND_OPERANDS';x=y='';consequence=''
 if left is None or right is None:status='LINE_EDGE'
 elif any(s!='DEFINITE_SPACE' for s in [left['right_separator'],r['left_separator'],r['right_separator'],right['left_separator']]):status='UNCERTAIN_BOUNDARY'
 elif a and b:
  x=len(a[1])+pred['i_offset'];y=len(b[1])+pred['i_offset']
  if pred['operation']=='RATIO':consequence=f'{x}:{y} = {Fraction(x,y)}';status='CONDITIONAL_LOCAL_COMPATIBILITY'
  else:consequence=f'{x}>{y} is {x>y}';status='CONDITIONAL_LOCAL_COMPATIBILITY' if x>y else 'CONTRADICTION'
 assert (c['status'],c['left_value'],c['right_value'],c['consequence'])==(status,str(x),str(y),consequence)
variants=t('MARKER_VARIANTS.tsv');assert len(variants)==27 and {(r['edition'],r['locus']) for r in variants}=={(ed,l) for ed in run.EDS for l in loci}
sep={'DEFINITE_SPACE':' ','UNCERTAIN_SMALL_SPACE':' / ','DRAWING_INTERRUPTION':' // ','DRAWING_INTERRUPTION_UNALIGNED':' ⟪DRAWING_INTERRUPTION_UNALIGNED⟫ '}
def raw(rr):return rr[0]['ivtff_group_raw']+''.join(sep[r['left_separator']]+r['ivtff_group_raw'] for r in rr[1:])
for v in variants:
 rr=lines[v['edition'],v['locus']];assert v['raw_line']==raw(rr) and int(v['exact_marker_count'])==sum(r['ivtff_group_raw']=='lkchey' for r in rr)
 assert v['source_ids']=='|'.join(r['source_group_id'] for r in rr)
pp=j(ROOT/m['paragraph_source']);expected={}
for ed in ['ZL3b','IT2a']:
 for para in pp[ed]:
  if any(l['locus'] in loci for l in para['lines']) or (para['page']=='f111v' and para['id']=='f111v|f111v.1-f111v.25'):expected[ed,para['id']]=para
actual=j(ART/'CONTEXT_PARAGRAPHS.json');assert {(p['edition'],p['id']) for p in actual}==set(expected) and len(actual)==20
selected={ed:set(loci) for ed in run.EDS}
for para in actual:
 ed=para['edition'];assert {k:v for k,v in para.items() if k!='edition'}==expected[ed,para['id']]
 for line in para['lines']:
  rr=lines[ed,line['locus']];assert line['source_ids']==[r['source_group_id'] for r in rr] and line['words']==[r['ivtff_group_raw'] for r in rr]
  selected[ed].add(line['locus']);selected['RF1b'].add(line['locus'])
assert pp['RF1b']==[] and all(len(x)==67 for x in selected.values())
base=j(ROOT/m['base_lexicons']);assert all(len(x)==33 for x in base.values())
align=t('CONTEXT_ALIGNMENT.tsv');work=t('WORKING_ALIGNMENT.tsv');assert len(align)==8288 and len(work)==3960
expected_ids={sid for sid,r in sources.items() if r['locus'] in selected[r['edition']]}
for cid in base:assert {r['source_group_id'] for r in align if r['candidate']==cid}==expected_ids
for r in align:
 src=sources[r['source_group_id']];assert all(r[k]==str(v) for k,v in src.items())
 assert [r['gloss'],r['role']]==base[r['candidate']].get(src['ivtff_group_raw'],['⟦'+src['ivtff_group_raw']+'⟧','UNREAD'])
for ed in run.EDS:
 doc=(ART/f'CONTEXT_{ed}.md').read_text()
 for locus in selected[ed]:assert '`'+raw(lines[ed,locus])+'`' in doc
 # In the four-line second working paragraph only the old copula is assigned.
 newp=[r for r in work if r['candidate']=='R_C' and r['edition']==ed and r['page']=='f115v']
 assert [r['ivtff_group_raw'] for r in newp if r['role']!='UNREAD']==['qokain']
for cid in m['candidates']:
 cc=[r for r in cases if r['candidate']==cid];assert Counter(r['status'] for r in cc)==Counter({'CONDITIONAL_LOCAL_COMPATIBILITY':3,'UNBOUND_OPERANDS':20,'UNCERTAIN_BOUNDARY':1})
 assert {r['locus'] for r in cc if r['status']=='CONDITIONAL_LOCAL_COMPATIBILITY'}=={'f115v.39'}
for name,value in run.build().items():assert (ART/name).read_text()==value,name
res=j(ART/'RESULT.json');assert res['status']=='NO_TRANSFER_CAPACITY' and res['confirmed_words']==res['independent_meaning_tests']==res['new_admissions']==0
out={'status':'PASS','checks':['21 fixed input/model/protocol hashes','independent24 exact marker census and27 whole variant lines','all96 operand/calibration/operator cases independently recomputed','20 full existing ZL/IT paragraphs; RF67line union only','all8288 context and3960 working alignment rows preserve33 old values','only qokain assigned in second four-line paragraph','only design locus binds numeric pair;20 unbound and1 uncertain per candidate','deterministic replay'],'semantics_validated':False}
(ART/'VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
