from pathlib import Path
import json,hashlib,itertools,sys
from collections import Counter
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
BOOKS=['b4','w1','bs1','gr1']
def partitions(n,cap,maximum=None):
 if n==0:yield ();return
 if cap==0:return
 maximum=min(n,maximum if maximum is not None else n)
 for value in range(maximum,0,-1):
  for tail in partitions(n-value,cap-1,value):yield (value,)+tail

def fixtures():
 checks=0
 for a in range(1,5):
  for n,m in itertools.product(range(1,8),repeat=2):
   def even(k):q,r=divmod(k,a);return sorted([q+1]*r+([q]*(a-r) if q else []),reverse=True)
   target=sorted(even(n)+even(m),reverse=True)
   for left,right in itertools.product(partitions(n,a),partitions(m,a)):
    trial=sorted(left+right,reverse=True)
    for k in range(1,n+m+1):assert sum(trial[:k])>=sum(target[:k])
    checks+=1
 return checks

def chunks(word,arm):
 if not all('a'<=c<='z' for c in word):return [word]
 starts=[];ends=[];inside=False
 for i,c in enumerate(word):
  vowel=c in 'aeiou'
  if vowel and not inside:starts.append(i)
  if not vowel and inside:ends.append(i)
  inside=vowel
 if inside:ends.append(len(word))
 cut=ends[:-1] if arm=='AFTER' else starts[1:];out=[];start=0
 for end in cut+[len(word)]:out.append(word[start:end]);start=end
 return out

def main():
 fixture_count=fixtures()
 if '--fixtures' in sys.argv:print(json.dumps({'status':'PASS','exhaustive_pooled_partition_fixtures':fixture_count}));return
 for path,digest in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 source=json.loads((ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text());targets=json.loads((ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json').read_text())['targets'];result=json.loads((A/'RESULT.json').read_text());rt=rule_checks=alias_checks=0;survivors=[]
 for arm,entry in result['arms'].items():
  allcounters={}
  for book in BOOKS:
   groups=[];total=0
   for recipe in source[book]:
    previous='';recovered=[];pending=''
    for word in recipe['words']:
     units=chunks(word,arm)
     for i,unit in enumerate(units):
      assert unit;last=i+1==len(units);groups.append((unit,'E' if last else 'C',previous));pending+=unit;previous=unit[-1];total+=1
      if last:recovered.append(pending);pending=''
    assert recovered==recipe['words'] and not pending;rt+=1
   assert total==entry['full_fragment_counts'][book];sample=groups[:8000];assert len(sample)==8000;allcounters[book]={}
   for sty in ['NONE','VC','V6']:
    counter=Counter()
    for unit,flag,previous in sample:
     state=0 if sty=='NONE' or not previous else int(previous in 'aeiou') if sty=='VC' else ('aeiou'.index(previous)+1 if previous in 'aeiou' else 0);counter[unit,flag,state]+=1
    allcounters[book][sty]=counter;saved=entry['rules'][sty]['books'][book];types=len(counter);top=sum(sorted(counter.values())[-10:]);assert types==saved['types_upper_count'] and top==saved['top10_lower_count'];records=[[list(k),n] for k,n in sorted(counter.items())];assert hashlib.sha256(json.dumps(records,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()==saved['counter_digest']
    flags=[types/8000>=t['type_ratio']-.05 and top/8000<=t['top10_share']+.05 for t in targets.values()];assert all(flags)==saved['not_excluded'];rule_checks+=1
  for sty,row in entry['rules'].items():
   joint=all(b['not_excluded'] for b in row['books'].values());assert joint==row['all_books_not_excluded']
   if joint:survivors.append(arm+'-'+sty)
  for aliases,record in entry['alias_relaxation'].items():
   alias=int(aliases)
   for book in BOOKS:
    cells=[]
    for count in allcounters[book]['NONE'].values():
     # Independent round-robin distribution of each occurrence.
     bins=[0]*alias
     for i in range(count):bins[i%alias]+=1
     cells.extend(n for n in bins if n)
    saved=record['books'][book];assert len(cells)==saved['types_upper_count'];assert sum(sorted(cells)[-10:])==saved['top10_lower_count'];assert sum(cells)==8000;flags=[len(cells)/8000>=t['type_ratio']-.05 and sum(sorted(cells)[-10:])/8000<=t['top10_share']+.05 for t in targets.values()];assert all(flags)==saved['not_excluded'];alias_checks+=1
   assert all(z['not_excluded'] for z in record['books'].values())==record['all_books_not_excluded']
  assert entry['minimum_optimistic_aliases']==next((i for i in range(1,17) if entry['alias_relaxation'][str(i)]['all_books_not_excluded']),None)
 assert survivors==result['surviving_rules'];assert (not survivors)==(result['status']=='ALL_SIX_CHEAP_GROUPING_RULES_EXCLUDED');report={'status':'PASS','exhaustive_pooled_partition_fixtures':fixture_count,'independent_rule_book_counts':rule_checks,'independent_alias_book_counts':alias_checks,'complete_source_grouping_reconstructions':rt,'native_or_glyph_validation':False,'scientific_status':result['status']};(A/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
