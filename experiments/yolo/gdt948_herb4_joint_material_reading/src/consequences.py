#!/usr/bin/env python3
"""Consequences of fixed, exposed HERB4 hypotheses; no learning or truth score."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,io,json,hashlib
B=Path(__file__).resolve().parents[1]

def table(rows,fields):
 s=io.StringIO();w=csv.DictWriter(s,fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows);return s.getvalue()

def components(m):
 ans={}
 for p in ['H17','H21','H32','H29']:
  events=[e for e in m['events'] if e['paragraph']==p];neighbors={e['id']:set() for e in events}
  for a in events:
   for c in events:
    if a['id']!=c['id'] and set(a['inputs']+a['outputs'])&set(c['inputs']+c['outputs']):neighbors[a['id']].add(c['id'])
  todo=set(neighbors);parts=[]
  while todo:
   q=[min(todo)];part=set()
   while q:
    x=q.pop()
    if x in part:continue
    part.add(x);q.extend(neighbors[x]-part)
   todo-=part;parts.append(sorted(part))
  ans[p]=parts
 return ans

def evaluate(name,m):
 ent={x['id']:x for x in m['entities']};rows=[]
 # State values are explicit hypothesis assignments, including alleged output states.
 # No state is claimed observed or mechanically derivable from historical text.
 for e in m['events']:
  for q in e.get('requirements',[]):
   st=ent[q['entity']].get('initial_state',{})
   actual=st.get(q['property'],'UNSPECIFIED')
   verdict='UNKNOWN' if q['property'] not in st else 'CONDITIONAL_MATCH' if actual==q['value'] else 'CONDITIONAL_CONTRADICTION'
   rows.append({'candidate':name,'event':e['id'],'trigger':e['trigger_ref'],'entity':q['entity'],'property':q['property'],'obligation_type':'desired_end_state_not_observed' if e['id']=='29E07' else 'assumed_input_requirement','required':json.dumps(q['value']),'assigned':json.dumps(actual),'verdict':verdict,'basis':'jointly_assigned_meanings_states_and_bindings; not_independent_manuscript_observation'})
 qcases=[]
 for e in m['events']:
  if e['trigger_ref'] not in ['f32v.9#1','f29v.3#6']:continue
  written=[x for x in e['outputs'] if ent[x]['anchor_refs']]
  implicit=[x for x in e['outputs'] if not ent[x]['anchor_refs']]
  qcases.append({'candidate':name,'locus':e['trigger_ref'],'qotchy_value':m['lexicon']['qotchy']['process'],'cfhy_value':m['lexicon']['cfhy']['process'],'inputs':'|'.join(e['inputs']),'named_outputs':'|'.join(written),'unnamed_outputs':'|'.join(implicit),'physical_creation_assumed':bool(e['outputs']),'independent_output_identity_evidence':0,'decision':'UNDISTINGUISHED_BY_THE_OBSERVED_TEXT'})
 return rows,qcases,{'candidate':name,'tokens':145,'fixed_values':len(m['lexicon']),'action_occurrences':len(m['events']),'requirement_results':dict(Counter(r['verdict'] for r in rows)),'material_components':components(m),'unwritten_entities':[x['id'] for x in m['entities'] if not x['anchor_refs']],'author_check_statuses':dict(Counter(c['status'] for e in m['events'] for c in e['checks'])),'independent_meaning_confirmation_capacity':0}

def build():
 lock=json.loads((B/'CANDIDATE_LOCK.json').read_text())
 for name,digest in lock['files'].items():assert hashlib.sha256((B/'src'/name).read_bytes()).hexdigest()==digest,name
 source=json.loads((B/'src/SOURCE.json').read_text());freq=Counter(t for line in source['lines'] for t in line['tokens'])
 packet={k:json.loads((B/'src'/f).read_text()) for k,f in [('M_v01','MODEL_v01.json'),('M_v02','MODEL.json'),('I_v02','MODEL_INSPECT.json')]}
 allrows=[];qrows=[];summaries=[];outputs={}
 for name,m in packet.items():
  rows,qs,s=evaluate(name,m);allrows+=rows;qrows+=qs;summaries.append(s)
  # Publish complete aligned prose for the lexical rival as well, not excerpts only.
  if name=='I_v02':
   lines=['# GDT948 — vollständige Prüfungsgegenlesung I','', 'Hypothetisch; zwei Wortwerte und explizite Stoffrollen unterscheiden sich von M_v02. Keine bestätigte Übersetzung.','']
   for p in ['H17','H21','H32','H29']:
    lines += ['## '+p,'']
    for c in [c for c in m['clauses'] if c['paragraph']==p]:
     lines += ['**'+c['refs'][0].split('#')[0]+'**',c['process_text'],'Ergänzungen: '+' '.join(c['supplied']),'']
   outputs['READING_INSPECT.md']='\n'.join(lines)
 # Closed, exact statement of the alternative: both lexical values must be disclosed.
 changes=[{'form':w,'M_v02':packet['M_v02']['lexicon'][w]['process'],'I_v02':packet['I_v02']['lexicon'][w]['process'],'occurrences':freq[w]} for w in freq if packet['M_v02']['lexicon'][w]!=packet['I_v02']['lexicon'][w]]
 result={'experiment':'GDT948','status':'JOINT_FULL_DRAFTS_WITH_EXPLICIT_REPAIRS_MEANING_UNSELECTED','source':{'tokens':sum(freq.values()),'types':len(freq),'singleton_types':sum(v==1 for v in freq.values()),'repeated_types':sum(v>1 for v in freq.values()),'repeated_type_tokens':sum(v for v in freq.values() if v>1),'physical_leaves':4,'all_exposed':True},'candidates':summaries,'lexical_rival_changes':changes,'catalogue_rival':'Complete K_v02 uses every same nominal/property concept and converts instructions into catalogue fields. It does not assert execution. That cannot be penalized as a false prediction.','chosen_truth_candidate':None,'independently_translated_words':0,'significance_claim':False,'search_calibration':None,'meaning_confirmation_capacity':0,'interpretation':'Full coverage is authored hypothesis coverage. Singleton bridge changes remove one chosen contradiction and one missing powder origin, not establish their meanings. qotchy separation and inspection each fit the preserved lexical contexts with different assumed material roles. All graph/state compatibility is conditional.'}
 outputs['STATE_CONSEQUENCES.tsv']=table(allrows,['candidate','event','trigger','entity','property','obligation_type','required','assigned','verdict','basis'])
 outputs['QOTCHY_CANDIDATES.tsv']=table(qrows,['candidate','locus','qotchy_value','cfhy_value','inputs','named_outputs','unnamed_outputs','physical_creation_assumed','independent_output_identity_evidence','decision'])
 outputs['CONSEQUENCE_RESULT.json']=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 outputs['LEXICON.tsv']=table([{'form':w,'frequency':freq[w],**{k:packet['M_v02']['lexicon'][w][k] for k in ['process','catalogue','kind']}} for w in sorted(freq)],['form','frequency','process','catalogue','kind'])
 return outputs

def main():
 for name,text in build().items():(B/'artifacts'/name).write_text(text,encoding='utf-8')
 print((B/'artifacts/CONSEQUENCE_RESULT.json').read_text())
if __name__=='__main__':main()
