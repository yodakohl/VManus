#!/usr/bin/env python3
"""Independent full taper replay. Does not import the primary runner."""
import collections,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];OLD=E.parent/'gdt915_terminal_lr_phrase_transfer';WORD='abracadabra'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def group_valid(gs,complete=False,n=None):
 if not gs or any(re.fullmatch('[a-z]+',g['ivtff_group_raw']) is None for g in gs):return False
 ix=[int(g['source_group_index']) for g in gs]
 if ix!=list(range(ix[0],ix[0]+len(ix))):return False
 if complete and ix!=list(range(1,n+1)):return False
 return all(a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:]))
def fit(rungs,side):
 if len(rungs)!=11 or not all(rungs):return False,None
 chunks=[]
 for a,b in zip(rungs,rungs[1:]):
  if len(a)<=len(b):return False,None
  if side=='RIGHT':
   if a[:len(b)]!=b:return False,None
   chunks.append(a[len(b):])
  else:
   if a[-len(b):]!=b:return False,None
   chunks.append(a[:-len(b)])
 chunks=([rungs[-1]]+chunks[::-1]) if side=='RIGHT' else chunks+[rungs[-1]]
 mapping={}
 for letter,chunk in zip(WORD,chunks):
  if letter in mapping and mapping[letter]!=chunk:return True,None
  mapping[letter]=chunk
 if len(set(mapping.values()))!=5:return True,None
 return True,mapping

def main():
 lock=load(E/'PREREG_LOCK.json')
 for path,digest in lock['files'].items():assert sha(ROOT/path)==digest
 # Unequal code lengths, complete11rung positives and a nested false repetition.
 mapping=dict(a='xy',b='z',r='pqrs',c='ttt',d='uv');chunks=[mapping[x] for x in WORD]
 for side in ['RIGHT','LEFT']:
  make=lambda cs:[''.join(cs[:11-i] if side=='RIGHT' else cs[i:]) for i in range(11)]
  assert fit(make(chunks),side)==(True,mapping)
  bad=chunks[:];bad[3]='ww';assert fit(make(bad),side)==(True,None)
 gs=[dict(ivtff_group_raw='xy',source_group_index=str(i),left_separator='DEFINITE_SPACE',right_separator='DEFINITE_SPACE') for i in [1,2]]
 assert group_valid(gs,True,2);gs[0]['right_separator']='UNCERTAIN_SPACE';assert not group_valid(gs,True,2)
 summaries={}
 for ed in ['ZL3b','IT2a','RF1b']:
  lines=[]
  for phase in ['DISCOVERY','EVALUATION']:
   data=load(OLD/'artifacts'/f'SOURCE_{phase}_{ed}.json')
   for row in data['lines']:
    m=row['metadata'];assert m['edition']==ed and not m['page'].startswith('f84')
    lines.append((m,[dict(zip(data['group_columns'],g)) for g in row['groups']]))
  den={kind:dict(windows=0,eligible=0,RIGHT_nested=0,LEFT_nested=0,RIGHT_fits=0,LEFT_fits=0) for kind in ['GROUP','LINE']};hits=[]
  def check(rungs,kind,where):
   for side in ['RIGHT','LEFT']:
    nested,key=fit(rungs,side);den[kind][side+'_nested']+=int(nested)
    if key is not None:den[kind][side+'_fits']+=1;hits.append((where,kind,side,key))
  pages=collections.defaultdict(list)
  for m,gs in lines:
   pages[m['page']].append((m,gs))
   for end in range(11,len(gs)+1):
    den['GROUP']['windows']+=1;window=gs[end-11:end]
    if group_valid(window):
     den['GROUP']['eligible']+=1;check([g['ivtff_group_raw'] for g in window],'GROUP',m['locus'])
  for page,rows in pages.items():
   rows.sort(key=lambda row:int(row[0]['source_row_index']))
   for end in range(11,len(rows)+1):
    den['LINE']['windows']+=1;window=rows[end-11:end]
    if all(group_valid(gs,True,int(m['source_group_count'])) for m,gs in window):
     den['LINE']['eligible']+=1;check([''.join(g['ivtff_group_raw'] for g in gs) for m,gs in window],'LINE',page)
  census=load(E/'artifacts'/f'CENSUS_{ed}.json');assert census['denominators']==den and census['lines']==len(lines) and census['selectors']==len(pages)
  assert hits==census['hits']==[], 'Positive target fit requires independent full hit-schema comparison'
  summaries[ed]=dict(denominators=den,fits=len(hits),lines=len(lines),selectors=len(pages))
 result=load(E/'artifacts/RESULT.json');assert result['readings']==summaries and result['status']=='NO_COMPLETE_FIXED_CHARM_FIT' and result['meaning_claims']==0 and result['significance_claim'] is False and result['source_exposed'] is True
 receipt=dict(status='PASS',validator_sha256=sha(Path(__file__)),prereg_lock_sha256=sha(E/'PREREG_LOCK.json'),readings=summaries,synthetic_checks=dict(positive_variable_length_keys=2,nested_repeated_letter_mismatches=2,valid_seam=1,invalid_seam=1),scope='Complete real census and zero fits independently replayed; synthetic exact-fit tests pass; no claim to exhaust historical charm realizations or identify meaning')
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
