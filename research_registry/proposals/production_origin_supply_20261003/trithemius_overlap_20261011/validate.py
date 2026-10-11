from pathlib import Path
import json,itertools,re,hashlib,collections
B=Path(__file__).resolve().parent;R=B.parents[3]
def main():
 for p,h in json.loads((B/'INPUTS.json').read_text()).items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 d=json.loads((B/'TABLE.json').read_text());res=json.loads((B/'RESULT.json').read_text());nwindows=0
 assert len(d['columns'])==10 and sum(len(x['words']) for x in d['columns'])==240
 for spelling,null_spelling,mode in itertools.product(['preferred','alternative'],['preferred','alternative'],['literal_casefold','uv_fold']):
  def normalize(t):return t.lower().translate(str.maketrans('v','u')) if mode=='uv_fold' else t.lower()
  cells=[]
  for i,c in enumerate(d['columns']):
   col=list(c['words'])
   if i==7 and spelling=='alternative':col[10]=d['uncertain_cells'][0]['alternative']
   cells.append([normalize(w) for w in col])
  key=f'{spelling}_{null_spelling}_{mode}';result=res['cases'][key];adj=[];shared=collections.defaultdict(list)
  for i,c in enumerate(cells):
   assert len(set(c))==24
   for j,w in enumerate(c):shared[w].append({'column':i+1,'label':d['alphabet_labels'][j]})
   if i<9:adj.append({'columns':[i+1,i+2],'common_cells':sorted(w for w in c if any(w==v for v in cells[i+1]))})
  assert adj==result['adjacent_cell_intersections'];assert {w:v for w,v in shared.items() if len(v)>1}==result['shared_whole_cells_across_any_columns']
  stages=[]
  for i,c in enumerate(cells,1):
   stages.append([tuple(re.findall(r'\S+',w)) for w in c])
   if i==8:
    nullword=d['uncertain_nulls'][0][null_spelling];stages.append([('cum','omnibus'),('cum',normalize(nullword))])
   if i==9:stages.append([('suis','in')])
   if i==10:stages.append([('amen',)])
  found={2:set(),3:set()}
  # Every module is nonempty: a word run of length<=3 spans at most3modules.
  for span in range(1,4):
   for start in range(len(stages)-span+1):
    for choice in itertools.product(*stages[start:start+span]):
     words=tuple(itertools.chain.from_iterable(choice));nwindows+=1
     for size in [2,3]:
      for pos in range(len(words)-size+1):
       if all(words[pos+k]==words[pos] for k in range(size)):found[size].add(words[pos])
  assert all(found[k]==set(result['repeated_word_witnesses'][str(k)]) for k in [2,3]);assert not found[2] and not found[3]
  lengths=[sum(f(s) for s in stages) for f in [lambda choices:min(map(len,choices)),lambda choices:max(map(len,choices))]];assert lengths==result['surface_word_count_range']==[15,16]
  assert all(not x['common_cells'] for x in adj)
 assert res['status']=='FIRST_PERIOD_NO_ADJACENT_REPEAT_NONADJACENT_CELL_REUSE'
 # Full-cell inequality is not sufficient in general: shared boundary words can repeat.
 fixture=[('a','b'),('b','c')];assert fixture[0]!=fixture[1] and fixture[0][-1]==fixture[1][0]
 out={'status':'PASS','source_cells':240,'reading_normalization_cases':8,'local_module_windows_exhausted':nwindows,'adjacent_equal_word_runs':0,'consecutive_equal_triples':0,'shared_whole_cell':'vitam','shared_cell_coordinates':['4z','7a'],'scope':'Independent local-window exhaustion versus primary tail-state traversal; manual source uncertainty retained. First period only, no wholebook or native claim.'};(B/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
