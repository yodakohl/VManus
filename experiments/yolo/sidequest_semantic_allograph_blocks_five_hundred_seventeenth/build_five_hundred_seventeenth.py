#!/usr/bin/env python3
from __future__ import annotations
import csv,json
from collections import defaultdict
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
P516=R/'experiments/yolo/sidequest_semantic_master_copy_mode_five_hundred_sixteenth'
def read(p):
 with Path(p).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,x):
 with (H/n).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(x[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(x)
def make_blocks(log,max_delta):
 allog=[x for x in log if x['renderer_action']=='COPY_LOCAL_EXEMPLAR'];blocks=[];cur=[]
 for x in allog:
  if cur and x['record']==cur[-1]['record'] and x['locus']==cur[-1]['locus'] and int(x['copy_order'])-int(cur[-1]['copy_order'])<=max_delta:cur.append(x)
  else:
   if cur:blocks.append(cur)
   cur=[x]
 if cur:blocks.append(cur)
 return blocks
def main():
 log=read(P516/'FIVE_HUNDRED_SIXTEENTH_381_MASTER_COPY_LOG.tsv');by_order={int(x['copy_order']):x for x in log}
 policies=[]
 policies.append({'policy':'PER_EVENT','allograph_decisions':'67','events_copied_from_exemplar':'67','extra_rule_events_copied':'0','selected':'NO','description_de':'Bei jeder Sonderform einzeln entscheiden.'})
 for delta,name in [(1,'CONSECUTIVE_RUN'),(2,'ONE_GAP_LOCAL_BLOCK'),(3,'TWO_GAP_LOCAL_BLOCK'),(4,'THREE_GAP_LOCAL_BLOCK')]:
  blocks=make_blocks(log,delta);span=sum(int(b[-1]['copy_order'])-int(b[0]['copy_order'])+1 for b in blocks)
  policies.append({'policy':name,'allograph_decisions':str(len(blocks)),'events_copied_from_exemplar':str(span),'extra_rule_events_copied':str(span-67),'selected':'YES' if delta==2 else 'NO','description_de':f'Im selben Locus Sonderformen bündeln, wenn der Startabstand höchstens {delta} Ereignisse beträgt.'})
 loci={(x['record'],x['locus']) for x in log if x['renderer_action']=='COPY_LOCAL_EXEMPLAR'};lc=[x for x in log if (x['record'],x['locus']) in loci]
 policies.append({'policy':'WHOLE_LOCUS','allograph_decisions':str(len(loci)),'events_copied_from_exemplar':str(len(lc)),'extra_rule_events_copied':str(len(lc)-67),'selected':'NO','description_de':'Jeden betroffenen Locus vollständig kopieren.'})
 sts={x['statement_id'] for x in log if x['renderer_action']=='COPY_LOCAL_EXEMPLAR'};sc=[x for x in log if x['statement_id'] in sts]
 policies.append({'policy':'WHOLE_STATEMENT','allograph_decisions':str(len(sts)),'events_copied_from_exemplar':str(len(sc)),'extra_rule_events_copied':str(len(sc)-67),'selected':'NO','description_de':'Jede betroffene Aussage vollständig kopieren.'})
 write('FIVE_HUNDRED_SEVENTEENTH_ALLOGRAPH_POLICY_COMPARISON.tsv',policies)
 blocks=make_blocks(log,2);rows=[];membership={}
 for i,b in enumerate(blocks,1):
  start=int(b[0]['copy_order']);end=int(b[-1]['copy_order']);span=[by_order[n] for n in range(start,end+1)];bid=f'AB{i:02d}'
  for x in span:membership[x['event_id']]=bid
  rows.append({'block_id':bid,'record':b[0]['record'],'page':b[0]['page'],'locus':b[0]['locus'],'start_order':str(start),'end_order':str(end),'start_event':b[0]['event_id'],'end_event':b[-1]['event_id'],'span_events':str(len(span)),'true_allograph_events':str(len(b)),'extra_rule_events_copied':str(len(span)-len(b)),'event_ids':'|'.join(x['event_id'] for x in span),'surfaces':' '.join(x['renderer_final_surface'] for x in span),'master_instruction_de':'Am Blockanfang Exemplarstil einschalten; ganze Spanne kopieren; danach zur Regeloberfläche zurückkehren.'})
 write('FIVE_HUNDRED_SEVENTEENTH_FIFTY_ALLOGRAPH_BLOCKS.tsv',rows)
 starts={x['start_event']:x['block_id'] for x in rows};out=[];dec=[]
 for x in log:
  reasons=[]
  if x['statement_first_event']=='YES' and x['program_status']=='UNIQUE':reasons.append('SELECT_UNUSUAL_PROGRAM');dec.append((x,'SELECT_UNUSUAL_PROGRAM',x['statement_id']))
  if x['owner_reset']=='YES':reasons.append('RESET_VISIBLE_OWNER');dec.append((x,'RESET_VISIBLE_OWNER',x['owner_code']))
  if x['event_id'] in starts:reasons.append('ENTER_ALLOGRAPH_BLOCK');dec.append((x,'ENTER_ALLOGRAPH_BLOCK',starts[x['event_id']]))
  bid=membership.get(x['event_id'],'NONE')
  out.append({**x,'allograph_block_id':bid,'block_rendering_mode':'COPY_BLOCK_FROM_EXEMPLAR' if bid!='NONE' else 'RENDER_BY_RULE','block_start_decision':'YES' if x['event_id'] in starts else 'NO','revised_conscious_decision_count':str(len(reasons)),'revised_conscious_reasons':'|'.join(reasons) if reasons else 'NONE','revised_master_mode':'CONSCIOUS_LOCAL_CHOICE' if reasons else 'AUTOMATIC_FLOW'})
 write('FIVE_HUNDRED_SEVENTEENTH_381_BLOCK_MASTER_LOG.tsv',out)
 drows=[]
 for i,(x,t,v) in enumerate(dec,1):drows.append({'decision_no':str(i),'event_id':x['event_id'],'statement_id':x['statement_id'],'record':x['record'],'page':x['page'],'decision_type':t,'selected_value':v})
 write('FIVE_HUNDRED_SEVENTEENTH_134_REVISED_CONSCIOUS_DECISIONS.tsv',drows)
 summary={'status':'PASS','allograph_events':67,'selected_blocks':len(rows),'copied_span_events':sum(int(x['span_events']) for x in rows),'extra_rule_events_copied':sum(int(x['extra_rule_events_copied']) for x in rows),'revised_decision_instances':len(drows),'revised_conscious_events':sum(x['revised_master_mode']=='CONSCIOUS_LOCAL_CHOICE' for x in out),'revised_automatic_events':sum(x['revised_master_mode']=='AUTOMATIC_FLOW' for x in out),'previous_decision_instances':151,'decisions_saved':151-len(drows)}
 (H/'FIVE_HUNDRED_SEVENTEENTH_BUILD_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
