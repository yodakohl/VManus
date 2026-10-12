from pathlib import Path
from collections import Counter
import hashlib,itertools,json,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def tail(word):
 n=0
 for a in word[::-1]:
  if a!=word[-1]:break
  n+=1
 return n
def split(f,a):
 q,r=divmod(f,a);return [n for n in [q+1]*r+[q]*(a-r) if n]
def allocations(n,a):
 if a==1:yield [n];return
 for first in range(n+1):
  for rest in allocations(n-first,a-1):yield [first]+rest
def controls():
 count=merge=0
 for n in range(1,11):
  for a in range(1,6):
   best=split(n,a)
   for alt in allocations(n,a):
    assert len(best)>=sum(v>0 for v in alt)
    x=sorted(best+[7,3,1],reverse=True);y=sorted(alt+[7,3,1],reverse=True)
    for k in range(1,max(len(x),len(y))+1):assert sum(x[:k])<=sum(y[:k])
    count+=1
    if len(alt)>=2:
     merged=sorted([alt[0]+alt[1]]+alt[2:],reverse=True);before=sorted(alt,reverse=True)
     assert sum(v>0 for v in merged)<=sum(v>0 for v in before)
     for k in range(1,len(before)+1):assert sum(merged[:k])>=sum(before[:k])
     merge+=1
 for w in ['a','aaa','baaa','abab','xyy','ßß']:
  t=tail(w);a=1+min(t,len(w)-1);assert len({w[:len(w)-d] for d in range(min(t,len(w)-1)+1)})==a
 assert 1+min(tail('a'),0)==1 and 1+min(tail('aaa'),2)==3
 out={'status':'PASS','source_free':True,'allocation_with_background_cases':count,'merging_cases':merge,'run_budget_fixtures':6};save(B/'artifacts/CONTROLS.json',out);print(out)
def main():
 for path,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
 source=json.loads((R/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text());old=json.loads((R/'experiments/yolo/gdt1202_whole_word_two_alias_capacity/artifacts/RESULT.json').read_text());target=json.loads((R/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json').read_text())['targets'];limits={}
 for ed,t in target.items():
  assert t['tokens']==8000;types=round(8000*t['type_ratio']);top=round(8000*t['top10_share']);assert abs(types/8000-t['type_ratio'])<1e-12 and abs(top/8000-t['top10_share'])<1e-12;limits[ed]={'native_types':types,'native_top10_count':top,'types_lower_count':types-400,'top10_upper_count':top+400}
 assert limits==old['native_limits'];books={};tables={}
 for book in ['b4','w1','bs1','gr1']:
  words=[w for rec in source[book] for w in rec['words']];assert len(words)>=8000;sample=words[:8000];assert all(isinstance(w,str) and w for w in sample);freq=Counter(sample);table=[];allcells=[];gains=losses=gaining=losing=0;budgets=Counter()
  for w,f in sorted(freq.items()):
   length=len(w);t=tail(w);a=1+min(t,length-1);cells=split(f,a);budgets[a]+=1;gain=min(f,a)-min(f,2);gains+=max(0,gain);losses+=max(0,-gain);gaining+=gain>0;losing+=gain<0;allcells+=cells;table.append({'word':w,'count':f,'length':length,'terminal_run':t,'alias_budget':a,'balanced_counts':cells})
  oldtypes=sum(min(f,2) for f in freq.values());oldtop=sum(sorted([n for f in freq.values() for n in split(f,2)],reverse=True)[:10]);assert oldtypes==old['books'][book]['two_alias_types_upper_count'] and oldtop==old['books'][book]['two_alias_top10_lower_count'] and len(freq)==old['books'][book]['source_types'];maximum=len(allcells);minimum=sum(sorted(allcells,reverse=True)[:10]);assert sum(allcells)==8000 and maximum==oldtypes+gains-losses;conditions={}
  for ed,lim in limits.items():
   a=maximum>=lim['types_lower_count'];b=minimum<=lim['top10_upper_count'];conditions[ed]={'types_not_excluded':a,'concentration_not_excluded':b,'not_excluded':a and b}
  books[book]={'source_types':len(freq),'budget_type_counts':{str(k):v for k,v in sorted(budgets.items())},'types_upper':maximum,'top10_lower':minimum,'type_gains_vs_two':gains,'type_losses_vs_two':losses,'gaining_words':gaining,'losing_words':losing,'top10_delta_vs_two':minimum-oldtop,'ordered_sample_sha256':hashlib.sha256(json.dumps(sample,ensure_ascii=False,separators=(',',':')).encode()).hexdigest(),'reader_conditions':conditions};tables[book]=table;print(book,json.dumps(books[book],sort_keys=True),flush=True)
 save(B/'artifacts/RESULT.json',{'status':'TERMINAL_RUN_VARIANT_ENVELOPE','native_limits':limits,'books':books});save(B/'artifacts/FREQUENCIES.json',tables)
if __name__=='__main__':controls() if '--controls' in sys.argv else main()
