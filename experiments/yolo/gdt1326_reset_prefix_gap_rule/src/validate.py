from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 v=p.read_bytes();return json.loads(gzip.decompress(v) if p.suffix=='.gz' else v)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 # Exhaust all stop assignments on the four relevant long-word prefixes.
 prefixes=[(0,),(0,1),(0,1,2),(0,1,2,3)];checked=0
 def split(x,accept):
  start=0;out=[]
  for end in range(1,len(x)+1):
   if tuple(x[start:end]) in accept:out.append(x[start:end]);start=end
  if start<len(x):out.append(x[start:])
  return out
 for labels in itertools.product([False,True],repeat=4):
  accepted={p for p,v in zip(prefixes,labels) if v};short=split([0,1,3],accepted);long=split([0,1,2,3],accepted);assert not(short[0]==[0,1] and long==[[0,1,2,3]]);checked+=1
 assert split([0,1],{(0,1,2,3)})==[[0,1]] and split([0,1,2,3],{(0,1,2,3)})==[[0,1,2,3]]
 assert split([0,1,0,2],{(0,1),(0,2)})==[[0,1],[0,2]]
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};events=read(B/'artifacts/EVENTS.json');witness=read(B/'artifacts/WITNESSES.json');result=read(B/'artifacts/RESULT.json');verified=0;contradictions=0
 for ed,rows in sorted(data.items()):
  keep={r['id']:r for r in rows};actual=[]
  for ph in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata'];groups=line['groups']
    for g,nxt in zip(groups,groups[1:]):
     if g[2] not in ['ol','oldy'] or g[0] not in keep or nxt[0] not in keep or int(nxt[1])!=int(g[1])+1:continue
     r=keep[g[0]];following=keep[nxt[0]]
     for raw,row in [(g,r),(nxt,following)]:
      assert row['page'] in allowed and not row['page'].startswith(('f84','f116v','f1r'));assert row['page']==m['page'] and row['locus']==m['locus'] and row['kind']==m['kind']=='P';assert raw[2]==row['ivtff_group_raw']==''.join(row['units']);assert int(raw[1])==int(row['source_group_index']);assert raw[3]==raw[4]==row['left_separator']==row['right_separator']=='DEFINITE_SPACE';verified+=1
     actual.append({'group':r,'following_group':following,'metadata':m})
  actual.sort(key=lambda x:x['group']['id']);assert actual==events[ed];forms=collections.defaultdict(set)
  for x in actual:forms[x['group']['page']].add(x['group']['ivtff_group_raw'])
  pages=sorted(p for p,s in forms.items() if s=={'ol','oldy'});summary=result['readers'][ed];assert summary['matched_pages']==pages;assert summary['eligible_ol']==sum(x['group']['ivtff_group_raw']=='ol' for x in actual);assert summary['eligible_oldy']==sum(x['group']['ivtff_group_raw']=='oldy' for x in actual)
  if pages:
   selected=witness[ed];assert selected['page']==summary['selected_page']==pages[0]
   for role,form in [('short','ol'),('long','oldy')]:
    options=[x for x in actual if x['group']['page']==pages[0] and x['group']['ivtff_group_raw']==form];assert selected[role]==options[0]
   u=selected['short']['group'];v=selected['long']['group'];assert u['units']==['o','l'] and v['units']==['o','l','d','y'];assert v['ivtff_group_raw'].startswith(u['ivtff_group_raw']) and v['ivtff_group_raw']!=u['ivtff_group_raw'];assert selected['short']['following_group']['locus']==u['locus'];assert summary['status']=='PREFIX_STOP_CONTRADICTION';contradictions+=1
  else:assert summary['status']=='NO_FIXED_PAIR_CAPACITY' and ed not in witness
 assert result['status']==('RESET_PREFIX_GAP_RULE_EXCLUDED_ALL_READINGS' if contradictions==3 else 'READER_SPECIFIC_PREFIX_OBSTRUCTION')
 out={'status':'PASS','selected_readers_with_counterpair':contradictions,'nominated_occurrence_and_follower_joins':verified,'exhaustive_prefix_stop_assignments':checked,'scope':'Independent original-source window extraction and prefix obstruction; no image adjudication or universal spacing/meaning claim.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
