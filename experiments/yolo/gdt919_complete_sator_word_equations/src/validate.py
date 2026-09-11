#!/usr/bin/env python3
"""Independent generic word-equation replay, without primary runner code."""
import collections,hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];OLD=E.parent/'gdt915_terminal_lr_phrase_transfer'
WORDS=['sator','arepo','tenet','opera','rotas']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def valid(gs,n=None):
 if not gs or any(re.fullmatch('[a-z]+',g['ivtff_group_raw']) is None for g in gs):return False
 ix=[int(g['source_group_index']) for g in gs]
 if ix!=list(range(ix[0],ix[0]+len(ix))) or (n is not None and ix!=list(range(1,n+1))):return False
 return all(a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(gs,gs[1:]))
def lengths(w):return len(set(w))==5 and min(map(len,w))>=5 and len(w[0])==len(w[4]) and len(w[1])==len(w[3])
def solve(target):
 if not lengths(target):return []
 # Central repeated variables first; generic recursive string substitution thereafter.
 equations=[(WORDS[i],target[i]) for i in [2,0,4,1,3]]; solutions=[]
 def equation(k,m):
  if k==5:
   assert len(m)==8 and len(set(m.values()))==8
   assert [''.join(m[c] for c in w) for w in WORDS]==target
   solutions.append(dict(m));return
  pattern,text=equations[k]
  def match(i,j):
   if i==len(pattern):
    if j==len(text):equation(k+1,m)
    return
   c=pattern[i]
   if c in m:
    value=m[c]
    if text.startswith(value,j):match(i+1,j+len(value))
   else:
    rest=sum(len(m[x]) if x in m else 1 for x in pattern[i+1:])
    for end in range(j+1,len(text)-rest+1):
     value=text[j:end]
     if value in m.values():continue
     m[c]=value;match(i+1,end);del m[c]
  match(0,0)
 equation(0,{})
 return solutions

def fixtures():
 for key in [dict(zip('satorepn',['ab','c','de','f','gh','i','jk','l'])),dict(zip('satorepn',['za','yb','xc','wd','ve','uf','tg','sh']))]:
  w=[''.join(key[c] for c in x) for x in WORDS]
  assert w[0][::-1]!=w[4] and key in solve(w)
  bad=w[:];bad[4]=bad[4][:-1]+'q';assert not solve(bad)
 collision=dict.fromkeys('satorepn','a');assert not solve([''.join(collision[c] for c in w) for w in WORDS])
 gs=[dict(ivtff_group_raw='ab',source_group_index=str(i),left_separator='DEFINITE_SPACE',right_separator='DEFINITE_SPACE') for i in range(1,6)]
 assert valid(gs,5);gs[2]['right_separator']='UNCERTAIN_SPACE';assert not valid(gs)
 return dict(nonpalindromic_variable_length_positive_keys=2,one_character_negative=2,collision_negative=1,seam_checks=2)
def main():
 lock=load(E/'PREREG_LOCK.json')
 for p,h in lock['files'].items():assert sha(ROOT/p)==h,p
 assert load(E/'src/SOURCE.json')['formula']==WORDS
 synthetic=fixtures();summaries={}
 for ed in ['ZL3b','IT2a','RF1b']:
  lines=[]
  for phase in ['DISCOVERY','EVALUATION']:
   data=load(OLD/'artifacts'/f'SOURCE_{phase}_{ed}.json')
   for line in data['lines']:
    m=line['metadata'];assert m['edition']==ed and not m['page'].startswith('f84')
    lines.append((m,[dict(zip(data['group_columns'],g)) for g in line['groups']]))
  den={k:dict(windows=0,eligible=0,length_and_distinct=0,fit_windows=0,keys=0) for k in ['GROUP','LINE']};hits=[]
  def check(w,kind):
   if not lengths(w):return
   den[kind]['length_and_distinct']+=1
   keys=solve(w)+solve(w[::-1])
   den[kind]['keys']+=len(keys);den[kind]['fit_windows']+=bool(keys)
   if keys:hits.append((w,kind,keys))
  pages=collections.defaultdict(list)
  for m,gs in lines:
   pages[m['page']].append((m,gs))
   for start in range(len(gs)-4):
    den['GROUP']['windows']+=1;window=gs[start:start+5]
    if valid(window):den['GROUP']['eligible']+=1;check([g['ivtff_group_raw'] for g in window],'GROUP')
  for page,rows in pages.items():
   rows.sort(key=lambda r:int(r[0]['source_row_index']))
   for start in range(len(rows)-4):
    den['LINE']['windows']+=1;window=rows[start:start+5]
    if all(valid(gs,int(m['source_group_count'])) for m,gs in window):
     den['LINE']['eligible']+=1;check([''.join(g['ivtff_group_raw'] for g in gs) for m,gs in window],'LINE')
  actual=load(E/'artifacts'/f'CENSUS_{ed}.json')
  assert actual['denominators']==den and actual['lines']==len(lines) and actual['selectors']==len(pages)
  assert hits==actual['hits']==[], 'Nonzero result needs full occurrence schema comparison'
  summaries[ed]=dict(denominators=den,fit_records=0,lines=len(lines),selectors=len(pages))
 result=load(E/'artifacts/RESULT.json')
 assert result==dict(meaning_claims=0,readings=summaries,significance_claim=False,source_exposed=True,status='NO_COMPLETE_SATOR_EQUATION_FIT')
 receipt=dict(status='PASS',validator_sha256=sha(Path(__file__)),prereg_lock_sha256=sha(E/'PREREG_LOCK.json'),locked_files_verified=len(lock['files']),output_sha256={p.name:sha(p) for p in sorted((E/'artifacts').glob('*.json')) if p.name!='VALIDATION.json'},readings=summaries,synthetic_checks=synthetic,scope='Complete six-cache census and generic exhaustive word equations in both orders; all zero fits verified. Fixed source/map/layout conjunction only, no translation, significance or general charm exclusion.')
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
