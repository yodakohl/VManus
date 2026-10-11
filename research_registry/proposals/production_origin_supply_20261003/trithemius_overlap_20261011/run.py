from pathlib import Path
import json,collections,itertools
B=Path(__file__).resolve().parent

def run():
 d=json.loads((B/'TABLE.json').read_text());results={}
 for spelling, null_spelling, mode in itertools.product(['preferred','alternative'],['preferred','alternative'],['literal_casefold','uv_fold']):
  def norm(s):
   s=s.lower();return s.replace('v','u') if mode=='uv_fold' else s
  columns=[]
  for c in d['columns']:
   words=c['words'].copy()
   if c['number']==8 and spelling=='alternative':words[d['alphabet_labels'].index('l')]=d['uncertain_cells'][0]['alternative']
   columns.append([norm(w) for w in words])
  assert all(len(c)==24 and len(set(c))==24 for c in columns)
  adjacent=[{'columns':[j+1,j+2],'common_cells':sorted(set(columns[j])&set(columns[j+1]))} for j in range(9)]
  occurrences=collections.defaultdict(list)
  for i,col in enumerate(columns):
   for j,w in enumerate(col):occurrences[w].append({'column':i+1,'label':d['alphabet_labels'][j]})
  shared={w:v for w,v in occurrences.items() if len(v)>1};modules=[]
  for i,col in enumerate(columns,1):
   modules.append({'slot':f'column{i}','options':[w.split() for w in col]})
   for slot0 in d['null_slots']:
    slot=json.loads(json.dumps(slot0))
    if slot['after_column']==8 and null_spelling=='alternative':slot['alternatives'][1][1]=d['uncertain_nulls'][0]['alternative']
    if slot['after_column']==i:modules.append({'slot':f'null{i}','options':[[norm(w) for w in a] for a in slot['alternatives']]})
  tails={():[]};witness={2:{},3:{}};states=[];edges=0
  for stage,m in enumerate(modules):
   nexttails={}
   for tail,path in sorted(tails.items()):
    for opt,words in enumerate(m['options']):
     chain=tail+tuple(words);newpath=path+[opt];edges+=1
     for length in [2,3]:
      for start in range(len(chain)-length+1):
       sub=chain[start:start+length]
       if len(set(sub))==1:witness[length].setdefault(sub[0],{'through_slot':m['slot'],'choices':newpath})
     nexttails.setdefault(chain[-2:],newpath)
   tails=nexttails;states.append(len(tails))
  minimum=sum(min(len(w) for w in m['options']) for m in modules);maximum=sum(max(len(w) for w in m['options']) for m in modules)
  results[spelling+'_'+null_spelling+'_'+mode]={'adjacent_cell_intersections':adjacent,'shared_whole_cells_across_any_columns':shared,'modules':len(modules),'surface_word_count_range':[minimum,maximum],'tail_state_counts':states,'transitions_examined':edges,'repeated_word_witnesses':witness}
 out={'status':'FIRST_PERIOD_NO_ADJACENT_REPEAT_NONADJACENT_CELL_REUSE','columns':10,'cells':240,'cases':results,'scope':'Only first ten BookIcolumns with prescribed null slots, no resets or cyclic closure; source-informed transcription with explicit uncertainty sensitivity. No native comparison or fullbook conclusion.'};(B/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'cases':{k:{'overlap':v['shared_whole_cells_across_any_columns'],'runs':v['repeated_word_witnesses'],'words':v['surface_word_count_range']} for k,v in results.items()}}))
if __name__=='__main__':run()
