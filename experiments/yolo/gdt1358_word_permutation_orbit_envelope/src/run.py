from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,itertools,json,re,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def save(path,data):
 raw=(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode();path.write_bytes(gzip.compress(raw,mtime=0) if path.suffix=='.gz' else raw)
def signature(word,family):
 return tuple(sorted(word)) if family=='BAG' else min(word[i:]+word[:i] for i in range(len(word)))
def envelope(source,native):
 s=sorted(source,reverse=True);b=sorted(native,reverse=True);assert sum(s)==sum(b);ss=bb=best=at=at_s=at_b=0
 for k in range(1,max(len(s),len(b))+1):
  if k<=len(s):ss+=s[k-1]
  if k<=len(b):bb+=b[k-1]
  if ss-bb>best:best=ss-bb;at=k;at_s=ss;at_b=bb
 t=max(0,len(b)-len(s));d=max(t,best);return {'N':sum(s),'type_lower':t,'prefix_lower':best,'k_witness':at,'source_prefix_sum':at_s,'native_prefix_sum':at_b,'replacement_lower':d,'fraction':[d,sum(s)],'status':'EXCLUDED_BY_NECESSARY_COUNTS' if d else 'NOT_EXCLUDED'}
def controls():
 coarsen=edits=words=0
 for m in range(1,5):
  for counts in itertools.product(range(1,4),repeat=m):
   for labels in itertools.product(range(m),repeat=m):
    groups=Counter()
    for label,n in zip(labels,counts):groups[label]+=n
    coarse=list(groups.values());assert envelope(counts,coarse)['replacement_lower']==0;coarsen+=1
    for i in range(len(coarse)):
     for j in range(len(coarse)+1):
      if i==j:continue
      modified=coarse+[0];modified[i]-=1;modified[j]+=1;modified=[n for n in modified if n];assert envelope(counts,modified)['replacement_lower']<=1;edits+=1
 for length in range(1,7):
  for word in itertools.product('abc',repeat=length):
   cyclic=signature(word,'CYCLIC');bag=signature(word,'BAG')
   for i in range(length):assert signature(word[i:]+word[:i],'CYCLIC')==cyclic
   assert signature(word[::-1],'BAG')==bag;words+=1
 out={'status':'PASS','source_free':True,'coarsenings':coarsen,'single_group_replacements':edits,'short_word_orbits':words};save(B/'artifacts/CONTROLS.json',out);print(out)
def main():
 for path,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
 data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};native={};tables={}
 for reader,rows in sorted(data.items()):
  for row in rows:
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert row['units'] and re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',row['ivtff_group_raw'])==row['units'] and ''.join(row['units'])==row['ivtff_group_raw']
  assert len(rows)>=8000
  for panel,selected in [('FULL',rows),('FIRST8000',rows[:8000])]:
   wordrows=defaultdict(list)
   for row in selected:wordrows[tuple(row['units'])].append(row)
   for family in ['CYCLIC','BAG']:
    orbit=defaultdict(list)
    for word,rr in sorted(wordrows.items()):orbit[signature(word,family)].append({'word':list(word),'count':len(rr),'source_ids':[r['id'] for r in rr]})
    table=[{'signature':list(key),'count':sum(x['count'] for x in members),'members':members} for key,members in sorted(orbit.items())];counts=sorted([x['count'] for x in table],reverse=True);name=reader+'_'+panel+'_'+family;tables[name]=table;native[name]={'groups':len(selected),'raw_types':len(wordrows),'orbit_types':len(table),'sorted_counts':counts,'largest_orbit_count':counts[0],'top10_orbit_count':sum(counts[:10])};print(name,len(wordrows),len(table),sum(counts[:10]),flush=True)
 source=json.loads((R/'experiments/yolo/gdt1177_preposition_binding_transfer/artifacts/SOURCE_TEXTS.json').read_text());sources={};profiles={};comparisons={}
 for book in ['b4','w1','bs1','gr1']:
  allwords=[word for recipe in source[book] for word in recipe['words']];assert len(allwords)>=8000;sample=allwords[:8000];assert all(isinstance(w,str) and w for w in sample);freq=Counter(sample);digest=hashlib.sha256(json.dumps(sample,ensure_ascii=False,separators=(',',':')).encode()).hexdigest();counts=sorted(freq.values(),reverse=True);sources[book]={'groups':8000,'source_types':len(freq),'sorted_counts':counts,'ordered_sample_sha256':digest};profiles[book]={'word_counts':[[w,n] for w,n in sorted(freq.items())],'ordered_sample_sha256':digest}
  for reader in sorted(data):
   for family in ['CYCLIC','BAG']:
    name=reader+'_'+family+'_'+book;comparisons[name]=envelope(counts,native[reader+'_FIRST8000_'+family]['sorted_counts']);print(name,comparisons[name]['replacement_lower'],comparisons[name]['k_witness'],flush=True)
 save(B/'artifacts/RESULT.json',{'status':'ORBIT_COARSENING_ENVELOPES','native':native,'sources':sources,'comparisons':comparisons,'scope':'Fixed-source global base-spelling/reordering necessary counts and replacement lower bounds; no language identity, actual error rate or sufficient fit.'});save(B/'artifacts/ORBIT_TABLES.json.gz',tables);save(B/'artifacts/SOURCE_PROFILES.json',profiles)
if __name__=='__main__':controls() if '--controls' in sys.argv else main()
