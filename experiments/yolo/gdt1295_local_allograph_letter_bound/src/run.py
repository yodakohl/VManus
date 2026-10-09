#!/usr/bin/env python3
import collections,gzip,hashlib,itertools,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
def contexts(rows):
 cells=collections.defaultdict(lambda:collections.defaultdict(list))
 for q in rows:
  w=q['units'];n=len(w)
  for i,u in enumerate(w):
   k=(q['page'],n,i,w[i-1] if i else 'BOS',w[i+1] if i+1<n else 'EOS')
   cells[k][u].append(q['id'])
 return cells

def maximum_clique(units,edges):
 adjacency={u:set() for u in units}
 for x,y in edges:adjacency[x].add(y);adjacency[y].add(x)
 best=[]
 def visit(chosen,candidates):
  nonlocal best
  if len(chosen)>len(best) or len(chosen)==len(best) and chosen<best:best=chosen
  if len(chosen)+len(candidates)<len(best):return
  while candidates:
   x=candidates[0];candidates=candidates[1:]
   visit(chosen+[x],[y for y in candidates if y in adjacency[x]])
   if len(chosen)+len(candidates)<len(best):break
 visit([],list(units));return best

def edge_graph(cells):
 e=collections.defaultdict(list)
 for key,v in cells.items():
  for pair in itertools.combinations(sorted(v),2):e[pair].append(key)
 return e

def fixtures():
 def rows(words):return [{'id':str(i),'page':'f1r','units':list(w)} for i,w in enumerate(words)]
 e=edge_graph(contexts(rows(['axb','ayb'])));assert ('x','y') in e
 separated=rows(['axb','ayb']);separated[1]['page']='f2r';assert ('x','y') not in edge_graph(contexts(separated))
 words=[];truth={'x':'a','y':'a','z':'b'}
 for n in range(1,6):
  for w in map(''.join,itertools.product('ab',repeat=n)):
   out=''.join('z' if c=='b' else 'y' if i and w[i-1]=='b' else 'x' for i,c in enumerate(w));assert ''.join(truth[c] for c in out)==w;words.append(out)
 e=edge_graph(contexts(rows(words)));assert all(truth[a]!=truth[b] for a,b in e);assert len(maximum_clique(['x','y','z'],e))==2
 empty=edge_graph(contexts(rows(['axb','cyd'])));assert not empty
 cycle=[('a','b'),('b','c'),('c','d'),('d','e'),('a','e')];assert len(maximum_clique(list('abcde'),cycle))==2
 assert not any(all(colors[ord(a)-97]!=colors[ord(b)-97] for a,b in cycle) for colors in itertools.product([0,1],repeat=5))
 return {'status':'PASS','valid_two_letter_allograph_words':len(words),'same_frame_conflict':True,'page_change_blocks_edge':True,'merged_neighbor_converse_counterexample':True,'odd_cycle_clique_not_chromatic':True}

def main():
 s=json.loads((B/'src/SPEC.json').read_text())
 for p,h in json.loads((B/'src/LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 source=(ROOT/s['source']).read_bytes();assert hashlib.sha256(source).hexdigest()==s['source_sha256'];data=json.loads(gzip.decompress(source));res={};packet={}
 for reader in s['readers']:
  rows=data[reader]
  for q in rows:
   assert q['kind']=='P' and q['left_separator']==q['right_separator']=='DEFINITE_SPACE'
   assert not q['page'].startswith('f84') and q['page']!='f116v'
  cells=contexts(rows);conflicts={k:v for k,v in cells.items() if len(v)>1};edges=edge_graph(conflicts);erows=[]
  for pair,keys in sorted(edges.items()):
   keys.sort();key=keys[0];v=conflicts[key];erows.append({'units':list(pair),'contexts':len(keys),'selectors':len(set(k[0] for k in keys)),'physical_leaves':len(set(re.match(r'f(\d+)',k[0])[1] for k in keys)),'first_context':list(key),'first_ids':[min(v[pair[0]]),min(v[pair[1]])]})
  graphs={}
  for name,minleaves in [('FULL',1),('DISPERSED',s['dispersed_min_physical_leaves'])]:
   es=[tuple(e['units']) for e in erows if e['physical_leaves']>=minleaves];clique=maximum_clique(s['units'],es)
   graphs[name]={'edges':len(es),'maximum_clique':clique,'necessary_letter_lower_bound':len(clique),'excludes_K_at_most11':len(clique)>s['small_alphabet_cap'],'clique_edge_witnesses':[e for e in erows if tuple(e['units']) in set(itertools.combinations(clique,2))]}
  res[reader]={'groups':len(rows),'positions':sum(len(q['units']) for q in rows),'all_contexts':len(cells),'repeated_observation_contexts':sum(sum(map(len,v.values()))>1 for v in cells.values()),'multi_center_contexts':len(conflicts),'graphs':graphs}
  packet[reader]={'conflicting_contexts':[{'key':list(k),'centers':{u:sorted(ids) for u,ids in sorted(v.items())}} for k,v in sorted(conflicts.items())],'edges':erows}
 overall='ALL_READERS_SMALL_LOCAL_ALLOGRAPH_ALPHABET_EXCLUDED' if all(z['graphs']['FULL']['excludes_K_at_most11'] for z in res.values()) else 'READER_SPECIFIC_NECESSARY_BOUNDS_ONLY'
 out={'status':overall,'readers':res,'scope':'Necessarygloballettercountunderdeterministiclocalallographyonly; nofullcoloring,writer,phonemeornativemeaning'}
 (B/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n');(B/'artifacts/CONFLICTS.json.gz').write_bytes(gzip.compress(json.dumps(packet,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 print(json.dumps({'status':overall,'readers':{r:{'contexts':v['multi_center_contexts'],'graphs':{g:{'bound':z['necessary_letter_lower_bound'],'clique':z['maximum_clique'],'edges':z['edges']} for g,z in v['graphs'].items()}} for r,v in res.items()}},indent=2))
if __name__=='__main__':
 import sys
 if '--fixtures' in sys.argv:
  z=fixtures();(B/'artifacts/FIXTURES.json').write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(z))
 else:main()
