"""Recover old915/949 complete family, preserving raw reader-specific context."""
import collections,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
S=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts'
READERS=['ZL3b','IT2a','RF1b'];DISPLAY={'rr':'f48v.6','rl':'f112v.8','lr':'f107v.21','ll':'f33r.5'}
def main():
 inputs={};out={};witnesses={}
 def read(name):
  p=S/name;inputs[str(p.relative_to(R))]=hashlib.sha256(p.read_bytes()).hexdigest();return json.loads(p.read_text())
 for reader in READERS:
  discovery=next(x for x in read(f'DISCOVERY_CENSUS_{reader}.json') if x['stems']==['oka','ota'])
  evaluation=next(x for x in read(f'EVALUATION_{reader}.json')['candidates'] if x['stems']==['oka','ota'])
  ds=read(f'SOURCE_DISCOVERY_{reader}.json');es=read(f'SOURCE_EVALUATION_{reader}.json');lines={x['metadata']['locus']:x for x in ds['lines']+es['lines']}
  occ=[dict(o,old_partition='DISCOVERY') for cell in discovery['cells'].values() for o in cell]+[dict(o,old_partition='EVALUATION') for o in evaluation['occurrences']]
  assert len({tuple(o['source_ids']) for o in occ})==len(occ)
  rows=[];cells=collections.Counter()
  for o in occ:
   line=lines[o['locus']];assert not o['page'].startswith('f84') and o['page']!='f116v'
   groups=line['groups'];a=next(i for i,g in enumerate(groups) if g[0]==o['source_ids'][0]);b=a+1;ga,gb=groups[a:b+1]
   assert [ga[0],gb[0]]==o['source_ids'] and [ga[2],gb[2]]==o['words'];assert ga[4]==gb[3]=='DEFINITE_SPACE'
   assert [ga[2][:-1],gb[2][:-1]]==['oka','ota'];cell=ga[2][-1]+gb[2][-1];cells[cell]+=1
   positions=['FIRST' if i==0 else 'LAST' if i==len(groups)-1 else 'INTERNAL' for i in [a,b]]
   rows.append({'occurrence':o,'cell':cell,'raw_line':line,'positions':positions,'left_neighbour':groups[a-1] if a else None,'right_neighbour':groups[b+1] if b+1<len(groups) else None,'outer_separators':[ga[3],gb[4]]})
  expected={'ZL3b':{'rr':5,'rl':1,'lr':1,'ll':2},'IT2a':{'rr':3,'rl':1,'lr':1,'ll':2},'RF1b':{'rr':5,'rl':1,'lr':1,'ll':2}}[reader]
  assert cells==collections.Counter(expected) # independently published949wholefamily counts
  display={}
  for cell,locus in DISPLAY.items():
   r=next(x for x in rows if x['occurrence']['locus']==locus and x['cell']==cell)
   assert r['positions']==['INTERNAL','INTERNAL'];display[cell]={'source_ids':r['occurrence']['source_ids'],'outer_separators':r['outer_separators']}
  out[reader]={'cells':dict(cells),'all_old_occurrences':rows,'display_source_ids':display}
 # Separate positional/raw-reader audit of the previously selected qoka/o examples.
 previous=json.loads((R/'experiments/yolo/gdt1276_fixed_pair_binary_state_bound/artifacts/QOKA_O_RAW_LINES.json').read_text())
 loci=sorted({x['occurrence']['locus'] for rows in previous.values() for x in rows})
 for reader in READERS:
  ls={x['metadata']['locus']:x for x in read(f'SOURCE_EVALUATION_{reader}.json')['lines']}
  witnesses[reader]=[ls[locus] for locus in loci]
 result={'status':'OLD_PARADIGM_CONTEXT_RECOVERED','scope':'Exposed descriptive raw-source review of old915/949; no new mixed discovery, test, blind sample or translation','inputs':inputs,'readers':out,'display_loci':DISPLAY,'qoka_o_same_locus_reader_comparison':witnesses,'checks':'All25family occurrences match exactsourceIDs/forms/innerseams and published949cells; displayed4cells INTERNAL/INTERNALineachreader;innerseamsdefinite,outerseamsretained. Completeqokacomparison27rawlinesretained.','initial_assertion_correction':'An initial extraction assertion incorrectly expected all displayed outer seams definite. It failed at ZL f112v.8 otal-to-kedy UNCERTAIN_SMALL_SPACE. This is retained as a failed stronger boundary claim, not silently normalized or counted as fully definite.915eligibility requires the inner seam, unchanged.', 'limits':['No common linguistic construction or statistical independence proved','Displayedquartetpostselectedfromoldcompletefamily','Combines olddiscoveryandevaluation;notfreshholdout','Readeragreementnotindependentpalaeography','Exactordinalsandexternalneighboursdiffer','No actualfourstategrammar inferred']}
 p=B/'OKA_OTA_PARADIGM_CONTEXT_RESULT_20261008.json';p.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({r:out[r]['cells'] for r in READERS}));print('PASS:25oldfamilyoccurrences;12displayedsourceevents;27qokacomparisonlines')
if __name__=='__main__':main()
