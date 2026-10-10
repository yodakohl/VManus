import collections,csv,gzip,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def save(n,o):
 d=(json.dumps(o,indent=2)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(d,mtime=0) if n.endswith('.gz') else d)
def graph(edges):
 nodes=sorted({v for e in edges for v in e});parent={v:v for v in nodes}
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 forest=[]
 for a,b in sorted(edges):
  x,y=find(a),find(b)
  if x!=y:parent[max(x,y)]=min(x,y);forest.append((a,b))
 groups=collections.defaultdict(list)
 for v in nodes:groups[find(v)].append(v)
 return sorted(groups.values()),forest

def fixtures():
 # A complete toy: each source bit becomes entry-current / payload-bit / exit-bit.
 state=0;words=[]
 for bit in [1,0,1]:words.append([f'I{state}',f'M{bit}',f'O{bit}']);state=bit
 edges={(words[i][-1],words[i+1][0]) for i in range(len(words)-1)};assert len(graph(edges)[0])==2;assert len(graph(edges|{('O0','I1')})[0])==1
 assert len(graph({('O:g','I:a'),('O:b','I:g')})[0])==2
 return {'status':'PASS','toy_message_bits':[1,0,1],'toy_words':words,'two_state_components':2,'after_cross_edge':1,'same_glyph_roles_kept_separate':True}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};results={};packets={};edge_out={};joins=0
 for ed,rows in data.items():
  source={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    for g in line['groups']:source[g[0]]=(line['metadata'],g)
  by={}
  for row in rows:
   m,g=source[row['id']];assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert m['page']==row['page'] and m['locus']==row['locus'] and m['edition']==ed and m['kind']==row['kind']=='P';assert g[2]==row['ivtff_group_raw'] and int(g[1])==int(row['source_group_index']) and g[3]==g[4]==row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert ''.join(row['units'])==g[2] and set(row['units'])<=set(A);key=(row['locus'],int(row['source_group_index']));assert key not in by;by[key]=row;joins+=1
  pairs=[];edges={}
  for (locus,i),left in sorted(by.items()):
   if (locus,i+1) not in by:continue
   right=by[locus,i+1];a='O:'+left['units'][-1];b='I:'+right['units'][0];p={'left':left,'right':right,'edge':[a,b]};pairs.append(p);z=edges.setdefault((a,b),{'count':0,'selectors':set(),'witness':p});z['count']+=1;z['selectors'].add(left['page'])
  components,forest=graph(edges);nodes=sorted({v for c in components for v in c});labels={v:i for i,c in enumerate(components) for v in c};assert all(labels[a]==labels[b] for a,b in edges);C=len(components);status='NO_CAPACITY' if not edges else ('ACTIVE_MARKER_CHANNEL_CONSTANT' if C==1 else 'MULTIPLE_MARKER_STATES_CAPACITY')
  results[ed]={'status':status,'groups':len(rows),'pairs':len(pairs),'distinct_edges':len(edges),'active_nodes':nodes,'inactive_nodes':[role+g for role in ['I:','O:'] for g in A if role+g not in nodes],'components':components,'max_observed_state_values':C,'forest_edges':[list(e) for e in forest],'forest_size':len(forest)};packets[ed]=pairs;edge_out[ed]=[{'edge':list(k),'count':v['count'],'selectors':sorted(v['selectors']),'witness':v['witness']} for k,v in sorted(edges.items())];print(ed,len(pairs),len(edges),len(nodes),'components',C,flush=True)
 status='ACTIVE_CHANNEL_CONSTANT_ALL_READINGS' if all(r['max_observed_state_values']==1 for r in results.values()) else 'READER_SPECIFIC_MARKER_STATE_CAPACITY';save('RESULT.json',{'status':status,'source_joins':joins,'fixtures':fx,'readers':results,'ceiling':'Exact marker-interface capacity only; no full writer-state count, informationless text, meaning or general state-cipher rejection.'});save('EDGES.json',edge_out);save('PAIRS.json.gz',packets)
if __name__=='__main__':main()
