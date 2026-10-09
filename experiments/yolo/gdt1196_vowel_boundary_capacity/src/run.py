from pathlib import Path
import json,re,hashlib
from collections import Counter
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
SOURCE=ROOT/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json';TARGET=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/artifacts/RESULT.json';BOOKS=['b4','w1','bs1','gr1'];VOWELS='aeiou';STYLES=['NONE','VC','V6']
def save(name,data):(A/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def split(word,arm):
 if not re.fullmatch('[a-z]+',word):return [word]
 runs=list(re.finditer('[aeiou]+',word))
 cuts=[m.end() for m in runs[:-1]] if arm=='AFTER' else [m.start() for m in runs[1:]]
 points=[0]+cuts+[len(word)];return [word[a:b] for a,b in zip(points,points[1:])]
def style(previous,name):
 if name=='NONE':return 0
 if name=='VC':return int(previous in VOWELS) if previous else 0
 return VOWELS.index(previous)+1 if previous and previous in VOWELS else 0

def census(source,arm):
 counters={b:{s:Counter() for s in STYLES} for b in BOOKS};full={};roundtrips=0
 for book in BOOKS:
  sample=total=0
  for recipe in source[book]:
   previous=None;recovered=[];pending=''
   for word in recipe['words']:
    pieces=split(word,arm);assert pieces and all(pieces)
    for j,part in enumerate(pieces):
     flag='E' if j==len(pieces)-1 else 'C';total+=1
     if sample<8000:
      for name in STYLES:counters[book][name][part,flag,style(previous,name)]+=1
      sample+=1
     pending+=part
     if flag=='E':recovered.append(pending);pending=''
     previous=part[-1]
   assert recovered==recipe['words'] and pending=='';roundtrips+=1
  assert sample==8000;full[book]=total
 return counters,full,roundtrips

def bounds(counts,targets):
 values=list(counts);types=len(values);top=sum(sorted(values,reverse=True)[:10]);tests={ed:{'types_upper_count':types,'type_lower_limit':t['type_ratio']-.05,'top10_lower_count':top,'top10_upper_limit':t['top10_share']+.05,'types_not_excluded':types/8000>=t['type_ratio']-.05,'concentration_not_excluded':top/8000<=t['top10_share']+.05} for ed,t in targets.items()}
 return {'types_upper_count':types,'types_upper_ratio':types/8000,'top10_lower_count':top,'top10_lower_share':top/8000,'reader_bounds':tests,'not_excluded':all(row['types_not_excluded'] and row['concentration_not_excluded'] for row in tests.values())}
def balanced(counts,aliases):
 out=[]
 for n in counts:
  q,r=divmod(n,aliases);out.extend([q+1]*r)
  if q:out.extend([q]*(aliases-r))
 return out

def main():
 for path,digest in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 source=json.loads(SOURCE.read_text());targets=json.loads(TARGET.read_text())['targets'];assert all(t['tokens']==8000 for t in targets.values());result={'experiment':'GDT1196','arms':{},'source_recipes':sum(map(len,source.values())),'source_words':sum(len(r['words']) for rs in source.values() for r in rs),'claim_ceiling':'Necessary optimistic frequency capacity of fixed artificial source segmentation/state rules; no glyph writer, native boundaries or meanings.'}
 for arm in ['AFTER','BEFORE']:
  counters,totals,rt=census(source,arm);entry={'rules':{},'alias_relaxation':{},'full_fragment_counts':totals,'complete_grouping_reconstructions':rt}
  for name in STYLES:
   bb={b:bounds(counters[b][name].values(),targets) for b in BOOKS}
   for b in BOOKS:
    records=[[list(k),n] for k,n in sorted(counters[b][name].items())];bb[b]['counter_digest']=hashlib.sha256(json.dumps(records,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
   entry['rules'][name]={'books':bb,'all_books_not_excluded':all(v['not_excluded'] for v in bb.values())}
  for aliases in range(1,17):
   bb={b:bounds(balanced(counters[b]['NONE'].values(),aliases),targets) for b in BOOKS};entry['alias_relaxation'][str(aliases)]={'books':bb,'all_books_not_excluded':all(v['not_excluded'] for v in bb.values())}
  entry['minimum_optimistic_aliases']=next((i for i in range(1,17) if entry['alias_relaxation'][str(i)]['all_books_not_excluded']),None);result['arms'][arm]=entry
 result['surviving_rules']=[arm+'-'+style for arm,e in result['arms'].items() for style,z in e['rules'].items() if z['all_books_not_excluded']];result['status']='NECESSARY_CAPACITY_NOT_EXCLUDED' if result['surviving_rules'] else 'ALL_SIX_CHEAP_GROUPING_RULES_EXCLUDED';save('RESULT.json',result);print(json.dumps({'status':result['status'],'surviving_rules':result['surviving_rules'],'minimum_optimistic_aliases':{arm:e['minimum_optimistic_aliases'] for arm,e in result['arms'].items()}},indent=2))
if __name__=='__main__':main()
