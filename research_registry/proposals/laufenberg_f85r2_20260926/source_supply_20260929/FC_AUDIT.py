"""FC frozen whole-value outside-duty audit; not a reference decoder."""
import csv, hashlib, io, json, re
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime, timezone
from tools import word_profiles
R=Path(__file__).resolve().parents[4]
P=Path(__file__).resolve().parent
PARA='experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'
BOUND={'LINE_START','LINE_END','DEFINITE_SPACE'}
COLS=['source_group_id','edition','page','locus','source_group_index','ivtff_group_raw','left_separator','right_separator','G_value','I_value']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dumps(a):return json.dumps(a,ensure_ascii=False,indent=2)+'\n'
def build():
 d=json.loads((P/'FC_DECISION.json').read_text())
 for rel,h in d['inputhashes'].items():assert sha(R/rel)==h,(rel,'frozen input changed')
 a=json.loads((P/'FB_AUTHOR.json').read_text())
 maps={b:dict(a['retained61'][b]) for b in ['G','I']}
 for b in maps:maps[b].update({k:v['value'] for k,v in a['new_whole_values'].items()});assert len(maps[b])==73
 c=word_profiles.ensure_cache(root=R)
 cache_receipt=word_profiles.receipt(c)
 receipt=cache_receipt['inputs']
 assert receipt['selector_count']==179 and not any(x.startswith('f84') or x=='f116v' for x in receipt['selectors'])
 # All bodies are admitted cached groups; no mixed TSV is directly parsed.
 occurrences=[dict(x) for x in c.execute("SELECT * FROM groups WHERE ivtff_group_raw IN (?,?) ORDER BY edition,page,locus,source_group_index",('dain','lfchedy'))]
 assert all(x['page'] in receipt['selectors'] for x in occurrences)
 targets={(x['edition'],x['locus']) for x in occurrences}
 paradata=json.loads((R/PARA).read_text())
 contexts=[];byline={};native_counts=Counter()
 def rows_for(ed,locus):return [dict(x) for x in c.execute('SELECT * FROM groups WHERE edition=? AND locus=? ORDER BY source_group_index',(ed,locus))]
 def overlay(row):return [row.get(k) if k not in ('G_value','I_value') else maps[k[0]].get(row['ivtff_group_raw'],'UNKNOWN') for k in COLS]
 for ed in word_profiles.EDITIONS:
  for p in paradata.get(ed,[]):
   if not any((ed,l['locus']) in targets for l in p['lines']):continue
   assert p['page'] in receipt['selectors']
   seq=[]
   for l in p['lines']:
    rr=rows_for(ed,l['locus']);assert [x['source_group_id'] for x in rr]==l['source_ids'];assert [x['ivtff_group_raw'] for x in rr]==l['words']
    seq.extend(rr)
   context={'edition':ed,'paragraph_id':p['id'],'page':p['page'],'physical_leaf':int(re.match(r'f(\d+)',p['page'])[1]),'columns':COLS,'groups':[overlay(x) for x in seq]}
   contexts.append(context);native_counts[ed]+=1
   for l in p['lines']:assert (ed,l['locus']) not in byline;byline[ed,l['locus']]=(context,seq)
 cases=[];missing_lines={}
 for o in occurrences:
  ed,locus=o['edition'],o['locus'];raw=o['ivtff_group_raw'];leaf=int(re.match(r'f(\d+)',o['page'])[1])
  typ=a['new_whole_values'][raw]['type'];eligible=set(d['candidate_mention_policy'][typ])
  ctx,seq=byline.get((ed,locus),(None,[]));idx=next((i for i,x in enumerate(seq) if x['source_group_id']==o['source_group_id']),None)
  target_def=o['left_separator'] in BOUND and o['right_separator'] in BOUND
  prior=[];barrier=None;candidate=[]
  if idx is not None:
   prior=seq[:idx]
   for row in reversed(prior):
    if row['ivtff_group_raw'] not in maps['G'] or row['left_separator'] not in BOUND or row['right_separator'] not in BOUND:
     barrier={'source_group_id':row['source_group_id'],'raw':row['ivtff_group_raw'],'G_value':maps['G'].get(row['ivtff_group_raw'],'UNKNOWN'),'reason':'UNKNOWN' if row['ivtff_group_raw'] not in maps['G'] else 'UNCERTAIN_BOUNDARY'};break
    if row['ivtff_group_raw'] in eligible:candidate.append({'source_group_id':row['source_group_id'],'raw':row['ivtff_group_raw'],'value':maps['G'][row['ivtff_group_raw']],'identity':'UNRESOLVED_NOMINAL_LABEL'})
  if ctx is None:
   missing_lines[ed,locus]={'edition':ed,'locus':locus,'columns':COLS,'groups':[overlay(x) for x in rows_for(ed,locus)]}
  nextrow=seq[idx+1] if idx is not None and idx+1<len(seq) else None
  # R9 checks the complete exact contiguous pair; identity still needs R6.
  r9=raw=='dain' and nextrow is not None and nextrow['ivtff_group_raw']=='chol' and target_def and nextrow['left_separator'] in BOUND and nextrow['right_separator'] in BOUND
  origin=leaf==111 and locus in [f'f111r.{n}' for n in range(36,44)]
  status='NO_PARAGRAPH_CAPACITY' if ctx is None else 'TARGET_BOUNDARY_UNCERTAIN' if not target_def else 'CANDIDATE_LABEL_ONLY' if candidate else 'UNKNOWN_OR_BOUNDARY_BLOCKED' if barrier else 'NO_CANDIDATE_IN_AVAILABLE_FRAME'
  cases.append({'source_group_id':o['source_group_id'],'edition':ed,'page':o['page'],'locus':locus,'physical_leaf':leaf,'split':'ORIGINAL_CONSTRUCTION' if origin else 'OTHER_PARAGRAPH_SAME_SELECTION_LEAF' if leaf==111 else 'OTHER_EXPOSED_LEAF','form':raw,'value':maps['G'][raw],'type':typ,'paragraph_id':ctx['paragraph_id'] if ctx else None,'status':status,'latest_candidate':candidate[0] if candidate else None,'all_candidate_mentions':candidate,'last_barrier':barrier,'R9_exact_pair':r9,'R9_next_id':nextrow['source_group_id'] if r9 else None,'resolved_outside_entity':False,'semantic_contradiction':False,'diagnostic_limit':'Nominal labels are not resolved identities; available paragraph/run is no universal reference-scope law.'})
 counts=defaultdict(Counter)
 for x in cases:counts[x['edition']+'|'+x['form']][x['status']]+=1
 out={'unit':'FC','registered_input_sha256':sha(P/'FC_DECISION.json'),'inputhashes':{PARA:sha(R/PARA),str((P/'FB_AUTHOR.json').relative_to(R)):sha(P/'FB_AUTHOR.json')},'corpus_receipt':cache_receipt,'target_count':len(cases),'native_paragraph_count':dict(native_counts),'group_count':sum(len(x['groups']) for x in contexts),'line_only_count':len(missing_lines),'counts':{k:dict(v) for k,v in counts.items()},'outside_resolved_reference_claims':0,'confirmed_words':0,'independent_meaning_leaves':0,'search_significance':False,'R9_pair_ids':[x['source_group_id'] for x in cases if x['R9_exact_pair']]}
 c.close()
 return {'FC_RESULT.json':dumps(out),'FC_CASES.json':dumps(cases),'FC_WHOLE_CONTEXTS.json':dumps({'paragraphs':contexts,'line_only':list(missing_lines.values())})}
def main():
 started=datetime.now(timezone.utc).isoformat()
 outputs=build()
 for k,v in outputs.items():(P/k).write_text(v)
 print(dumps({'first_new_body_audit_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'result':json.loads(outputs['FC_RESULT.json'])}))
if __name__=='__main__':main()
