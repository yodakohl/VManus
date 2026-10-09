import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
BASE=R/'research_registry/proposals/production_origin_supply_20261003'
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 prior=json.loads((BASE/'OKA_OTA_PARADIGM_CONTEXT_RESULT_20261008.json').read_text());nom={};cases={}
 for reader,block in prior['readers'].items():
  rows=[]
  for row in block['all_old_occurrences']:
   prev=row['left_neighbour'];target=row['occurrence']['words'][0]
   assert prev and prev[4]=='DEFINITE_SPACE' and row['outer_separators'][0]=='DEFINITE_SPACE'
   prediction='okal' if prev[2] in ['aiin','kaiin'] else 'okar'
   rows.append({'target_id':row['occurrence']['source_ids'][0],'previous':prev[2],'observed':target,'predicted':prediction,'correct':target==prediction})
  nom[reader]={'events':rows,'correct':sum(x['correct'] for x in rows),'total':len(rows)}
  source=R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_EVALUATION_{reader}.json';data=json.loads(source.read_text());line=next(x for x in data['lines'] if x['metadata']['locus']=='f58v.26');gs=line['groups'];indices=[i for i,g in enumerate(gs) if g[2]=='qokeos'];assert len(indices)==1
  i=indices[0];prev,target=gs[i:i+2];assert int(target[1])==int(prev[1])+1 and prev[4]==target[3]=='DEFINITE_SPACE'
  eligible=target[2] in ['okar','okal'];prediction='okal' if prev[2] in ['aiin','kaiin'] else 'okar'
  cases[reader]={'raw_line':line,'previous_id':prev[0],'target_id':target[0],'previous':prev[2],'observed':target[2],'eligible':eligible,'predicted':prediction if eligible else None,'decision':'CONTRADICTION' if eligible and target[2]!=prediction else ('COMPATIBLE' if eligible else 'INELIGIBLE_WHOLE_FORM')}
 out={'status':'KNOWN_COUNTERCASE_STOP_BEFORE_BROAD_TRANSFER','rule':'Exact precedingaiin orkaiin =>okal;elseokar;Pproseanddefiniteleftseam','nomination_fit':nom,'fixed_case':cases,'full_transfer_census_executed':False,'limits':'Known exposed countercase; no global accuracy, one-way rescue, words meaning or image confirmation. ITokalar unsplit.'}
 assert cases['ZL3b']['decision']=='CONTRADICTION'
 (B/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'fit':{r:[v['correct'],v['total']] for r,v in nom.items()},'case':{r:{k:v[k] for k in ['previous','observed','predicted','decision']} for r,v in cases.items()}},indent=2))
if __name__=='__main__':main()
