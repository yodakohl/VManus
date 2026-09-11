#!/usr/bin/env python3
import collections,hashlib,json,random,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def dump(n,o):(E/'artifacts'/n).write_text(json.dumps(o,separators=(',',':'),sort_keys=True)+'\n')
def acquire(ed):
 rows=[]
 for part in ['DISCOVERY','EVALUATION']:rows+=json.loads((ROOT/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{part}_{ed}.json').read_text())['lines']
 rows.sort(key=lambda r:(r['metadata']['page'],int(r['metadata']['source_row_index'])))
 return rows
def census(rows):
 tokens=[];pairs=[];strata=collections.defaultdict(list)
 for row in rows:
  m=row['metadata'];assert not m['page'].startswith('f84')
  if m['kind']!='P':continue
  local={};count=int(m['source_group_count']);leaf=re.match(r'f\d+',m['page']).group()
  for g in row['groups']:
   word=g[2];idx=int(g[1]);match=re.fullmatch('(ch|sh)([a-z]+)',word)
   if not match or g[3] not in ['LINE_START','DEFINITE_SPACE'] or g[4] not in ['LINE_END','DEFINITE_SPACE']:continue
   pos='SINGLE' if count==1 else 'FIRST' if idx==1 else 'LAST' if idx==count else 'INTERNAL'
   R=match[2];key=(leaf,R,pos);n=len(tokens);x=int(match[1]=='ch')
   tokens.append({'id':g[0],'page':m['page'],'locus':m['locus'],'row':int(m['source_row_index']),'index':idx,'leaf':leaf,'R':R,'position':pos,'x':x,'word':word,'stratum':list(key)})
   strata[key].append(n);local[idx]=n
  for idx,a in sorted(local.items()):
   if idx+1 in local:
    b=local[idx+1]
    if tokens[a]['R']==tokens[b]['R']:pairs.append({'a':a,'b':b,'leaf':leaf,'R':tokens[a]['R'],'primary':tokens[a]['R'] not in ['or','ol'],'locus':m['locus'],'words':[tokens[a]['word'],tokens[b]['word']]})
 primary=[p for p in pairs if p['primary']];by_leaf=collections.defaultdict(list)
 for p in primary:by_leaf[p['leaf']].append(p)
 probs={k:sum(tokens[i]['x'] for i in ix)/len(ix) for k,ix in strata.items()}
 mean=lambda v:sum(v)/len(v) if v else 0
 def score(xs):return mean([sum(xs[p['a']]-xs[p['b']] for p in ps)/len(ps) for ps in by_leaf.values()])
 xs=[t['x'] for t in tokens];T=score(xs);mu=mean([sum(probs[tuple(tokens[p['a']]['stratum'])]-probs[tuple(tokens[p['b']]['stratum'])] for p in ps)/len(ps) for ps in by_leaf.values()])
 mob={p['leaf'] for p in primary if any(0<probs[tuple(tokens[i]['stratum'])]<1 for i in [p['a'],p['b']])}
 forms=sorted(set(p['R'] for p in primary));cells=collections.Counter(('C' if xs[p['a']] else 'S')+('C' if xs[p['b']] else 'S') for p in primary)
 table=[]
 for R in sorted(set(p['R'] for p in pairs)):
  ps=[p for p in pairs if p['R']==R];cc=collections.Counter(('C' if xs[p['a']] else 'S')+('C' if xs[p['b']] else 'S') for p in ps)
  table.append({'R':R,'primary':R not in ['or','ol'],'cells':{k:cc[k] for k in ['CC','CS','SC','SS']},'leaves':sorted(set(p['leaf'] for p in ps)),'witnesses':[{'locus':p['locus'],'group_indices':[tokens[p['a']]['index'],tokens[p['b']]['index']],'words':p['words']} for p in ps]})
 leaf_table=[]
 for leaf,ps in sorted(by_leaf.items()):
  cc=collections.Counter(('C' if xs[p['a']] else 'S')+('C' if xs[p['b']] else 'S') for p in ps)
  leaf_table.append({'leaf':leaf,'pairs':len(ps),'cells':{k:cc[k] for k in ['CC','CS','SC','SS']},'T':sum(xs[p['a']]-xs[p['b']] for p in ps)/len(ps),'mu':sum(probs[tuple(tokens[p['a']]['stratum'])]-probs[tuple(tokens[p['b']]['stratum'])] for p in ps)/len(ps)})
 stats={'T':T,'mu':mu,'residual':T-mu,'eligible_tokens':len(tokens),'all_pairs':len(pairs),'primary_pairs':len(primary),'primary_R_count':len(forms),'primary_leaves':len(by_leaf),'mobile_leaves':len(mob),'capacity':len(forms)>=5 and len(mob)>=5,'cells':{k:cells[k] for k in ['CC','CS','SC','SS']}}
 return {'tokens':tokens,'pairs':pairs,'strata':[{'key':list(k),'indices':ix,'pCH':probs[k]} for k,ix in sorted(strata.items())],'R_table':table,'leaf_table':leaf_table,'statistics':stats},score

def main():
 for p,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 results={};z=None;score=None
 for ed in ['ZL3b','IT2a','RF1b']:
  c,fn=census(acquire(ed));dump(f'CENSUS_{ed}.json',c);results[ed]=c['statistics']
  if ed=='ZL3b':z=c;score=fn
 worlds=[];obs=abs(results['ZL3b']['residual']);mu=results['ZL3b']['mu']
 for j in range(1024):
  rng=random.Random(922000+j);xs=[t['x'] for t in z['tokens']]
  for s in z['strata']:
   ix=s['indices'];vals=[xs[i] for i in ix];rng.shuffle(vals)
   for i,x in zip(ix,vals):xs[i]=x
  t=score(xs);worlds.append({'world':j,'T':t,'residual':t-mu,'absolute_residual':abs(t-mu)})
 ge=sum(w['absolute_residual']>=obs-1e-12 for w in worlds);rank=(ge+1)/1025;nonconst=max(w['T'] for w in worlds)-min(w['T'] for w in worlds)>1e-12
 cap=results['ZL3b']['capacity'] and nonconst
 status='PROVISIONAL_WRITTEN_ORDERING' if cap and rank<=.05 and obs>1e-12 else 'ORDER_NOT_ESTABLISHED' if cap else 'CAPACITY_STOP'
 dump('WORLDS.json',worlds);out={'experiment':'GDT922','status':status,'editions':results,'worlds_ge_observed':ge,'rank_fraction':rank,'null_nonconstant':nonconst,'fresh_confirmation_leaves':0,'confirmed_meanings':0};dump('RESULT.json',out);print(json.dumps(out,indent=2))
if __name__=='__main__':main()
