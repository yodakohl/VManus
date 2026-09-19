"""Compile only the unchanged source and old public candidate/outcome list."""
import collections,csv,gzip,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2]
OLD=R/'experiments/yolo/gdt976_dioscorides_shared_referent_projection'
LAST=R/'experiments/yolo/gdt977_dioscorides_leaf_breadth_projection'
SOURCE=R/'experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json'
def compile_source(source):
 counts=collections.Counter(a for r in source['records'] for a in r['atoms']);recurrent=sorted(a for a,n in counts.items() if n>1);rs=[]
 for r in source['records']:
  terms=[];gaps=[];pending=[]
  def flush():
   if pending:
    name=r['id']+':gap:'+str(len(gaps));gaps.append(dict(id=name,minimum=len(pending),source_indices=list(pending)));terms.append(dict(gap=name));pending.clear()
  for i,a in enumerate(r['atoms']):
   if counts[a]>1:flush();terms.append(dict(atom=a,source_index=i))
   else:pending.append(i)
  flush();rs.append(dict(id=r['id'],source_atoms=len(r['atoms']),terms=terms,gaps=gaps,counts=dict(collections.Counter(r['atoms']))))
 return dict(recurrent_atoms=recurrent,recurrent_occurrences=sum(counts[a] for a in recurrent),source_occurrences=sum(counts.values()),singleton_occurrences=sum(n==1 for n in counts.values()),singleton_runs=sum(len(r['gaps']) for r in rs),adjacent_recurrent_pairs=sum('atom' in a and 'atom' in b for r in rs for a,b in zip(r['terms'],r['terms'][1:])),records=rs)
def main():
 model=compile_source(json.loads(SOURCE.read_text()));(E/'src/SOURCE_MODEL.json').write_text(json.dumps(model,ensure_ascii=False,indent=2)+'\n')
 with gzip.open(OLD/'artifacts/CANDIDATES.json.gz','rt') as f:base=json.load(f)
 with gzip.open(LAST/'artifacts/CASES.json.gz','rt') as f:previous=json.load(f)
 assert [x['id'] for x in previous]==list(range(len(base)))
 parts=collections.defaultdict(list)
 for i,(c,old) in enumerate(zip(base,previous)):
  if old['status']=='PARTIAL_FOUR_ATOM_WITNESS':parts[c['edition'],c['iris_page']].append(i)
  else:assert old['status']=='FOUR_ATOM_PROJECTION_CONTRADICTED'
 predictions=[dict(id=i,edition=key[0],iris_page=key[1],base_ids=ids,case_count=len(ids),consequence='All78recurrent atomvalues shared across four complete pages;358occurrences;208zero-gap seams;four distinct leaves; singleton150spans only') for i,(key,ids) in enumerate(sorted(parts.items()))]
 (E/'artifacts/PARTITION_PREDICTIONS.json').write_text(json.dumps(predictions,indent=2)+'\n')
 with (E/'artifacts/SOURCE_CONSEQUENCES.tsv').open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['record','source_index','atom','global_count','obligation'])
  s=json.loads(SOURCE.read_text());cnt=collections.Counter(a for r in s['records'] for a in r['atoms'])
  for r in s['records']:
   for i,a in enumerate(r['atoms']):w.writerow([r['id'],i,a,cnt[a],'shared_nonempty_prefix_free_code' if cnt[a]>1 else 'member_of_fixed_singleton_run'])
 print(json.dumps({k:v for k,v in model.items() if k not in ['records','recurrent_atoms']}));print('Partitions',len(predictions),'base rows',sum(x['case_count'] for x in predictions))
if __name__=='__main__':main()
