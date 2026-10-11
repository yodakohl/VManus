from pathlib import Path
import collections,csv,gzip,hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 v=p.read_bytes();return json.loads(gzip.decompress(v) if p.suffix=='.gz' else v)
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2)+'\n')
def format_stream(stream,stop):
 out=[];prefix=[]
 for unit in stream:
  prefix.append(unit)
  if stop(tuple(prefix)):out.append(prefix);prefix=[]
 if prefix:out.append(prefix)
 return out

def fixtures():
 assert format_stream([0,1,2,3],lambda p:p==(0,1))==[[0,1],[2,3]]
 assert format_stream([0,1],lambda p:p==(0,1,2,3))==[[0,1]]
 assert format_stream([0,1,2,3],lambda p:p==(0,1,2,3))==[[0,1,2,3]]
 assert format_stream([0,1,0,2],lambda p:p in [(0,1),(0,2)])==[[0,1],[0,2]]
 # Escape witness OUTSIDE the hypothesis: next-unit lookahead after prefix01.
 def ahead(x):
  out=[];word=[]
  for i,u in enumerate(x):
   word.append(u);nextunit=x[i+1] if i+1<len(x) else None
   if (word==[0,1] and nextunit!=2) or word==[0,1,2,3]:out.append(word);word=[]
  if word:out.append(word)
  return out
 assert ahead([0,1,3])==[[0,1],[3]] and ahead([0,1,2,3])==[[0,1,2,3]]
 return {'status':'PASS','final_flush_distinguished':True,'valid_prefix_free_rule':True,'lookahead_escape_is_outside_contract':True}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};result={};events={};witness={}
 for ed,rows in sorted(data.items()):
  by={(r['locus'],int(r['source_group_index'])):r for r in rows};source={}
  for ph in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    for g in line['groups']:source[g[0]]=(line['metadata'],g)
  chosen=[]
  for (loc,i),r in sorted(by.items()):
   if r['ivtff_group_raw'] not in ['ol','oldy'] or (loc,i+1) not in by:continue
   nxt=by[loc,i+1];m,g=source[r['id']]
   for row in [r,nxt]:
    mm,gg=source[row['id']];assert row['page'] in allow and not row['page'].startswith(('f84','f116v','f1r'));assert mm['kind']==row['kind']=='P' and mm['page']==row['page'] and mm['locus']==row['locus'];assert gg[2]==row['ivtff_group_raw']==''.join(row['units']) and int(gg[1])==int(row['source_group_index']);assert gg[3]==gg[4]==row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   assert nxt['page']==r['page'];chosen.append({'group':r,'following_group':nxt,'metadata':m})
  chosen.sort(key=lambda e:e['group']['id']);pages=collections.defaultdict(lambda:collections.defaultdict(list))
  for x in chosen:pages[x['group']['page']][x['group']['ivtff_group_raw']].append(x)
  matched=sorted(p for p,v in pages.items() if 'ol' in v and 'oldy' in v);status='NO_FIXED_PAIR_CAPACITY'
  if matched:
   page=matched[0];short=pages[page]['ol'][0];long=pages[page]['oldy'][0];a=short['group']['units'];z=long['group']['units'];assert a==['o','l'] and z==['o','l','d','y'] and z[:len(a)]==a and len(z)>len(a);witness[ed]={'page':page,'short':short,'long':long,'prefix_units':a,'extension_units':z[len(a):],'forced_short_stop':True,'long_group_requires_no_stop_at_same_prefix':True};status='PREFIX_STOP_CONTRADICTION'
  result[ed]={'status':status,'eligible_ol':sum(x['group']['ivtff_group_raw']=='ol' for x in chosen),'eligible_oldy':sum(x['group']['ivtff_group_raw']=='oldy' for x in chosen),'matched_pages':matched,'selected_page':matched[0] if matched else None};events[ed]=chosen;print(ed,result[ed],flush=True)
 save('EVENTS.json',events);save('WITNESSES.json',witness);save('RESULT.json',{'status':'RESET_PREFIX_GAP_RULE_EXCLUDED_ALL_READINGS' if len(witness)==3 else 'READER_SPECIFIC_PREFIX_OBSTRUCTION','readers':result,'fixtures':fx,'ceiling':'Conditional reset prefix-only formatting rule only; source stream continues within each witness line. No word meanings or general boundary inference.'})
if __name__=='__main__':main()
