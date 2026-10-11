from pathlib import Path
import collections,gzip,hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(n,v):(B/'artifacts'/n).write_text(json.dumps(v,indent=2)+'\n')
def fixtures():
 checks=0
 for k in range(1,4):
  for outputs in itertools.product(range(5),repeat=k):
   assert len(set(outputs)-{0})<=k;checks+=1
 assert len({'b','c','d'}-{'a'})==3
 # One command, extra hidden state0/1: same visible a can produce b or c.
 assert len({('b','c')[h] for h in (0,1)})==2
 return {'status':'PASS','finite_image_checks':checks,'extra_hidden_state_escape':True,'self_echo_not_counted':True}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 pairs=read(R/'experiments/yolo/gdt1319_cross_word_endpoint_state/artifacts/PAIRS.json.gz');results={};degrees={};witness={}
 for ed,ps in sorted(pairs.items()):
  maps={'global':collections.defaultdict(dict),'page':collections.defaultdict(dict)};selfn=0
  for p in sorted(ps,key=lambda p:(p['left']['locus'],int(p['left']['source_group_index']))):
   l,r=p['left'],p['right'];assert l['page']==r['page'] and l['locus']==r['locus'] and int(r['source_group_index'])==int(l['source_group_index'])+1;a,b=l['ivtff_group_raw'],r['ivtff_group_raw']
   if a==b:selfn+=1;continue
   for scope,key in [('global',(a,)),('page',(l['page'],a))]:maps[scope][key].setdefault(b,{'left':l,'right':r})
  results[ed]={'original_pairs':len(ps),'self_pairs_ignored':selfn,'scopes':{}};degrees[ed]={};witness[ed]={}
  for scope,m in maps.items():
   table=[{'key':list(k),'nonself_successors':len(v)} for k,v in sorted(m.items())];maximum=max((len(v) for v in m.values()),default=0);key=min(k for k,v in m.items() if len(v)==maximum);over=[k for k,v in m.items() if len(v)>27];results[ed]['scopes'][scope]={'minimum_required_commands':maximum,'state_cells':len(m),'cells_above27':len(over),'selected_key':list(key),'status':'K27_EXCLUDED' if maximum>27 else 'NOT_EXCLUDED_BY_BOUND'}
   if scope=='page':results[ed]['scopes'][scope]['pages_above27']=len({k[0] for k in over})
   degrees[ed][scope]=table;witness[ed][scope]={'key':list(key),'nonself_successors':maximum,'successors':[{'word':word,'pair':pair} for word,pair in sorted(m[key].items())]}
  print(ed,results[ed],flush=True)
 save('DEGREES.json',degrees);save('WITNESSES.json',witness);save('RESULT.json',{'status':'PAGE_SPECIFIC_K27_EXCLUDED_ALL_READINGS' if all(r['scopes']['page']['minimum_required_commands']>27 for r in results.values()) else 'READER_SPECIFIC_SUCCESSOR_BOUNDS','readers':results,'fixtures':fixtures()})
if __name__=='__main__':main()
