from pathlib import Path
from collections import Counter,defaultdict
from itertools import product
import csv,hashlib,json,sys
B=Path(__file__).resolve().parents[1];R=B.parents[2]
OLD='experiments/yolo/gdt1274_shorter_reference_doublet_bound/artifacts/RESULT.json'
def save(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def roster(frames):
 out=[];order={'DRY':0,'INTACT':1,'MASS':2,'LINK':3}
 for context in sorted(frames,key=lambda s:s.encode()):
  subjects,facts=frames[context];out.append(('FRAME',context))
  out.extend(('SUBJECT',s) for s in sorted(subjects,key=lambda s:s.encode()));heads=defaultdict(Counter)
  for (kind,sign,subject,args),count in facts.items():
   assert subject in subjects and count>0;heads[(kind,sign,args)][subject]+=count
  for h,members in sorted(heads.items(),key=lambda p:(order[p[0][0]],p[0][1]=='+',json.dumps(p[0][2],separators=(',',':')))):
   out.append(('HEAD',*h))
   out.extend(('MEMBER',s,n) for s,n in sorted(members.items(),key=lambda p:p[0].encode()))
 return out
def read_roster(groups):
 frames={};current=None;head=None;members=set();heads=set()
 for g in groups:
  tag=g[0]
  if tag=='FRAME':
   assert head is None or members;assert g[1] not in frames;current=g[1];frames[current]=(set(),Counter());head=None;members=set();heads=set()
  elif tag=='SUBJECT':
   assert current is not None and head is None and g[1] not in frames[current][0];frames[current][0].add(g[1])
  elif tag=='HEAD':
   assert current is not None and (head is None or members);head=g[1:];assert head not in heads;heads.add(head);members=set()
  elif tag=='MEMBER':
   assert head is not None and g[1] in frames[current][0] and g[1] not in members and g[2]>0;members.add(g[1]);kind,sign,args=head;frames[current][1][kind,sign,g[1],args]+=g[2]
  else:raise AssertionError(tag)
 assert head is None or members
 return frames
def contrasts():
 phase={'groups':[['PHASE',[1,1],[['DRY','+',1]]],['PHASE',[1,1],[['DRY','+',1]]]],'intervals':[[0,1],[1,2]],'native_binding':False}
 plus=[['FRAME','C'],['SUBJECT','A'],['HEAD','DRY','+',[]],['MEMBER','A',1]];minus=[['FRAME','C'],['SUBJECT','A'],['HEAD','DRY','-',[]],['MEMBER','A',1]]
 outside={'encoded_plus':[0,1,2,2],'encoded_minus':[0,1,3,2],'decoded_plus':plus,'decoded_minus':minus,'global_word_decoder':False,'native_binding':False}
 return phase,outside
def controls():
 atoms=[('DRY','+','A',()),('DRY','+','B',()),('DRY','-','A',()),('INTACT','-','A',()),('MASS','+','A',((0,1),'U')),('LINK','+','A',('A',)),('LINK','+','B',('A',)),('LINK','-','B',('X',))];cases=pairs=0;ids={};transitions=set()
 for counts in product(range(3),repeat=len(atoms)):
  frames={'C0':({'A','B','C'},Counter({a:n for a,n in zip(atoms,counts) if n})),'C1':(set(),Counter())};groups=roster(frames);assert read_roster(groups)==frames;assert all(a!=b for a,b in zip(groups,groups[1:]));cases+=1
  for a,b in zip(groups,groups[1:]):
   transitions.add((a[0],b[0]));ia=ids.setdefault(a,len(ids));ib=ids.setdefault(b,len(ids))
   for x,y in product(range(2),repeat=2):assert (ia,x)!=(ib,y);pairs+=1
 for frames in [{'C0':(set(),Counter()),'C1':(set(),Counter())},{'C0':({'A'},Counter())}]:
  groups=roster(frames);assert read_roster(groups)==frames and all(a!=b for a,b in zip(groups,groups[1:]));cases+=1;transitions.update((a[0],b[0]) for a,b in zip(groups,groups[1:]))
 invalid=[[('FRAME','C'),('FRAME','C')],[('FRAME','C'),('SUBJECT','A'),('SUBJECT','A')],[('FRAME','C'),('SUBJECT','A'),('HEAD','DRY','+',()),('HEAD','INTACT','+',()),('MEMBER','A',1)],[('FRAME','C'),('SUBJECT','A'),('HEAD','DRY','+',()),('MEMBER','A',1),('MEMBER','A',1)]]
 for groups in invalid:
  try:read_roster(groups)
  except AssertionError:pass
  else:raise AssertionError('invalid accepted')
 single=roster({'C':(set(),Counter())});assert read_roster(single)=={'C':(set(),Counter())} and (single+single)[0]==(single+single)[1]
 p,o=contrasts();assert p['groups'][0]==p['groups'][1] and p['intervals']==[[0,1],[1,2]]
 for key in ['plus','minus']:
  encoded=o['encoded_'+key];decoded=[['FRAME','C'],['SUBJECT','A'],['HEAD','DRY','+' if encoded[2]==2 else '-',[]],['MEMBER','A',1]];assert decoded==o['decoded_'+key]
 out={'status':'PASS','source_free':True,'source_documents':cases,'disjoint_alias_adjacent_checks':pairs,'invalid_documents_rejected':len(invalid),'observed_tag_transitions':sorted([list(t) for t in transitions]),'opaque_code_ids_not_native_values':True,'contrasts_checked':True,'independent_document_restart_counterexample':True};save(B/'artifacts/CONTROLS.json',out);print(out)
def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 old=json.loads((R/OLD).read_text());manifest=json.loads((R/'experiments/yolo/gdt1274_shorter_reference_doublet_bound/experiment.json').read_text());matches=[r for r in manifest['outputs'] if r['path']==OLD];assert len(matches)==1 and matches[0]['sha256']==hashlib.sha256((R/OLD).read_bytes()).hexdigest();allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};cases=[]
 for case in old['cases']:
  reader=case['reader'];line=sorted(case['complete_line'],key=lambda r:int(r['source_group_index']));at=[i for i,r in enumerate(line) if int(r['source_group_index'])==case['first_group_index']];assert len(at)==1;i=at[0];span=line[i-1:i+3];assert i>=1 and len(span)==4
  assert all(r['edition']==reader and r['locus']==case['locus'] and r['kind']=='P' and r['page'] in allowed and not r['page'].startswith('f84') and r['page'] not in ['f1r','f116v'] for r in span)
  assert all(int(b['source_group_index'])==int(a['source_group_index'])+1 and a['right_separator']==b['left_separator']=='DEFINITE_SPACE' for a,b in zip(span,span[1:]));assert span[1]['ivtff_group_raw']==span[2]['ivtff_group_raw']==case['form']=='qokeedy'
  cases.append({'reader':reader,'locus':case['locus'],'first_group_index':case['first_group_index'],'form':case['form'],'selected_rows':span,'roster_realization_possible':False})
 assert [c['reader'] for c in cases]==['ZL3b','IT2a','RF1b'];phase,outside=contrasts();save(B/'artifacts/RESULT.json',{'status':'ROSTER_WORD_REALIZATION_CONTRADICTED','cases':cases,'phase_counterexample':phase,'outside_contract':outside,'scope':'Exposed old doublet rejects canonical1038only with one word per typed record, global single-valued word decoding and the pair inside one canonical document;1039repeat compatibility is not native temporal meaning.'});print([(c['reader'],c['locus']) for c in cases])
if __name__=='__main__':controls() if '--controls' in sys.argv else main()
