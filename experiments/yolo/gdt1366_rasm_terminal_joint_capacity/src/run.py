from pathlib import Path
from collections import defaultdict,Counter
import gzip,json,re,csv,hashlib
B=Path(__file__).resolve().parents[1];R=B.parents[2]
CACHE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
def leaf(row):return int(re.match(r'f(\d+)',row['page']).group(1))
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/CACHE).read_bytes()));allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};panels={}
 for reader,rows in sorted(data.items()):
  places=defaultdict(set)
  for row in rows:
   assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   w=row['ivtff_group_raw'];u=re.findall(r'ckh|cth|cph|cfh|ch|sh|[aoeindqysrlmktpf]',w);assert ''.join(u)==w and u==row['units'];places[w].add(leaf(row))
  selected=[r for r in rows if len(places[r['ivtff_group_raw']])>=2]
  alphabet={c for r in selected for c in r['ivtff_group_raw']};middle={c for r in selected for c in r['ivtff_group_raw'][1:-1]};assert len(alphabet)==18 and len(middle)==15,'UNAPPLICABLE'
  terminals=alphabet-middle; witnesses=[];patterns=Counter();forms=Counter()
  for row in selected:
   w=row['ivtff_group_raw'];offsets=[i for i,c in enumerate(w) if c in terminals]
   if len(offsets)>1:
    witnesses.append({'source':row,'offsets':offsets,'count':len(offsets)});patterns[''.join(w[i] for i in offsets)]+=1;forms[w]+=1
  panels[reader]={'groups':len(selected),'types':len({r['ivtff_group_raw'] for r in selected}),'leaves':len({leaf(r) for r in selected}),'alphabet':sorted(alphabet),'middle':sorted(middle),'terminal_candidates':sorted(terminals),'violating_groups':len(witnesses),'violating_types':len(forms),'violating_leaves':len({leaf(z['source']) for z in witnesses}),'violation_rate':len(witnesses)/len(selected),'patterns':dict(patterns),'top_forms':[{'form':f,'occurrences':n} for f,n in sorted(forms.items(),key=lambda x:(-x[1],x[0]))[:10]],'witnesses':witnesses,'decision':'EXCLUDED' if witnesses else 'CAPACITY_ONLY'}
  print(reader,{k:v for k,v in panels[reader].items() if k not in ('witnesses','alphabet','middle')})
 (B/'artifacts/RESULT.json').write_text(json.dumps({'status':'JOINT_TERMINAL_CAPACITY','panels':panels},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
