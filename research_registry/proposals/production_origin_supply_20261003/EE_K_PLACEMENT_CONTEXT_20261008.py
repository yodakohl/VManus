"""Complete existing four-form context capsule; no learned rule or gloss."""
import collections,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
FORMS=['cheekey','chekeey','sheekey','shekeey'];READERS=['ZL3b','IT2a','RF1b']
def main():
 paths={};allrows={};loci=set();events={}
 for reader in READERS:
  lines={}
  for phase in ['DISCOVERY','EVALUATION']:
   p=R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json';paths[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest()
   for line in json.loads(p.read_text())['lines']:lines[line['metadata']['locus']]=line
  out=[]
  for locus,line in lines.items():
   if line['metadata']['kind']!='P':continue
   for i,g in enumerate(line['groups']):
    if g[2] not in FORMS:continue
    assert not line['metadata']['page'].startswith('f84') and line['metadata']['page']!='f116v';assert g[3:5]==['DEFINITE_SPACE','DEFINITE_SPACE'];assert i>0 and i+1<len(line['groups'])
    out.append({'source_id':g[0],'form':g[2],'locus':locus,'index':int(g[1]),'previous':line['groups'][i-1][2],'next':line['groups'][i+1][2],'metadata':line['metadata']});loci.add(locus)
  events[reader]=sorted(out,key=lambda e:e['source_id']);allrows[reader]=lines
 combined=[];shared=[];different=[]
 for locus in sorted(loci):
  comparison={r:allrows[r][locus] for r in READERS};targets={r:[g[2] for g in comparison[r]['groups'] if g[2] in FORMS] for r in READERS};assert all(len(v)<=1 for v in targets.values())
  identical=all(targets[r] and targets[r]==targets[READERS[0]] for r in READERS)
  (shared if identical else different).append(locus);combined.append({'locus':locus,'target_forms':targets,'same_target_all_readers':identical,'raw_lines':comparison})
 counts={r:{f:sum(e['form']==f for e in es) for f in FORMS} for r,es in events.items()};assert counts=={'ZL3b':dict(zip(FORMS,[5,3,1,5])),'IT2a':dict(zip(FORMS,[5,4,1,4])),'RF1b':dict(zip(FORMS,[5,3,1,3]))}
 context={}
 for reader,es in events.items():
  by=collections.defaultdict(list)
  for e in es:by[(e['previous'],e['next'])].append(e)
  context[reader]={'repeated_full_flank_frames':[{'previous':k[0],'next':k[1],'events':v} for k,v in sorted(by.items()) if len(v)>1], 'right_chol_examples':[e for e in es if e['next']=='chol']}
 out={'status':'COMPLETE_EXPOSED_CONTEXT_REVIEW_NO_RULE_SELECTED','source_hashes':paths,'counts':counts,'union_loci':len(loci),'all_reader_same_target_loci':shared,'reader_variant_loci':different,'events':events,'complete_same_locus_readings':combined,'context_comparison':context,'limits':['Selectedrarefourformfamilynotgeneralwordgrammar','Allrawsourcealreadyexposed','Readeragreementnotindependentpalaeography','No arbitrarymeaning,numbervalue,moving-eoperatororallographidentity','Lackofrepeatedfullframeisnotsemanticdifferenceorungrammaticality']}
 (B/'EE_K_PLACEMENT_CONTEXT_RESULT_20261008.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'counts':counts,'union_loci':len(loci),'all_reader_same_target':len(shared),'reader_variants':different,'repeated_full_frames':{r:len(x['repeated_full_flank_frames']) for r,x in context.items()}},indent=2))
if __name__=='__main__':main()
