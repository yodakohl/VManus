"""Independent reconstruction from frozen sources; no semantic validation."""
import hashlib,json,csv,io
from pathlib import Path
H=Path(__file__).resolve().parents[1];R=H.parents[2]
def load(p):return json.loads((H/p).read_text())
def main():
 m=load('src/MODEL.json')
 for p,d in m['input_hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==d
 data=json.loads((R/m['source']).read_text());assert data['RF1b']==[]
 expected=[]; events=[]; alignment=[]; wantgraphs=[]
 for edition in m['editions']:
  for u in data[edition]:
   words=[];ids=[];locs=[]
   for l in u['lines']:words+=l['words'];ids+=l['source_ids'];locs.append(l['locus'])
   targets=[]
   for i,w in enumerate(words):
    if w=='dalchedy':targets.append((i,i,'JOINED'))
    if w=='dal' and words[i+1:i+2]==['chedy']:targets.append((i,i+1,'SPLIT'))
   if not targets and m['include_counter_locus'] not in locs:continue
   expected.append({'edition':edition,**u}); ends={b for a,b,t in targets if t=='SPLIT'}; starts={a for a,b,t in targets if t=='SPLIT'}
   for c,v in m['candidates'].items():
    for a,b,t in targets:
     positives=[ids[i] for i in range(b+1,len(words)) if words[i]=='chedy' and i not in ends]
     events.append({'candidate':c,'edition':edition,'paragraph':u['id'],'leaf':u['leaf'],'kind':t,'negative_ids':ids[a:b+1],'negative_raw':words[a:b+1],'later_positive_ids':positives,'prediction':'later exact bare positive in same native paragraph','result':'RAW_CAPACITY_ONLY' if positives else 'CONDITIONAL_CONSTRUCTION_CONTRADICTION','independent_carrier_binding':False,'negative_value':v['joint_negative'],'positive_value':v['joint_positive']})
   offset=0
   for l in u['lines']:
    for c,v in m['candidates'].items():
     for i,(w,sid) in enumerate(zip(l['words'],l['source_ids'])):
      ctor=offset+i in starts; lexical=w in v['dictionary']
      alignment.append({'candidate':c,'edition':edition,'paragraph':u['id'],'locus':l['locus'],'position':i+1,'source_id':sid,'raw':w,'value':'NOT(scope-next-chedy)_C0' if ctor else v['dictionary'].get(w,'⟦'+w+'⟧'),'lexical':lexical,'construction_only':ctor})
    offset+=len(l['words'])
   if 'f115v.10' in locs:
    q=next(l for l in u['lines'] if l['locus']=='f115v.9')['source_ids'];z=next(l for l in u['lines'] if l['locus']=='f115v.10')['source_ids']
    for c in m['candidates']:wantgraphs.append({'candidate':c,'edition':edition,'patient_identity_assumed':[q[8],z[3]],'preparation_identity_assumed':[q[6],z[1]],'removal':{'agent':q[6],'predicate':q[7],'patient':q[8],'removed':q[9]},'transition':{'patient':z[3],'initial_state':z[4],'predicate':z[5],'final_state':z[6]},'status':'ASSUMED_NOT_MEANING_BOUND'})
 assert expected==load('src/SOURCE.json')['units'];assert events==load('artifacts/CANDIDATE_TABLE.json');assert alignment==load('artifacts/ALIGNMENT.json');assert wantgraphs==load('artifacts/GRAPHS.json')
 tab=list(csv.DictReader(io.StringIO((H/'artifacts/CANDIDATE_TABLE.tsv').read_text()),delimiter='\t'));assert len(tab)==len(events)
 for actual,want in zip(tab,events):
  for k,value in actual.items():assert value==(json.dumps(want[k],ensure_ascii=False) if isinstance(want[k],list) else str(want[k]))
 reader=(H/'artifacts/FULL_READER.md').read_text()
 for u in expected:
  assert u['edition']+' '+u['id'] in reader
  for l in u['lines']: assert l['locus']+' RAW: `'+ ' '.join(l['words'])+'`' in reader
 result=load('artifacts/RESULT.json');assert result['native_paragraphs']==len(expected) and result['source_groups']==sum(u['groups'] for u in expected) and result['alignment_rows']==len(alignment) and result['candidate_cases']==len(events)
 assert result['extension_contradiction_physical_loci']==sorted({v['negative_ids'][0].split('|')[1] for v in events if v['result']=='CONDITIONAL_CONSTRUCTION_CONTRADICTION'})
 for c in m['candidates']:
  for e in m['editions']:
   vs=[v for v in events if v['candidate']==c and v['edition']==e];rs=[v for v in alignment if v['candidate']==c and v['edition']==e]
   assert result['summaries'][c][e]=={'negative_cases':len(vs),'contradictions':sum(v['result']=='CONDITIONAL_CONSTRUCTION_CONTRADICTION' for v in vs),'raw_capacity_only':sum(v['result']=='RAW_CAPACITY_ONLY' for v in vs),'groups':len(rs),'lexical_assigned':sum(v['lexical'] for v in rs),'construction_only':sum(v['construction_only'] for v in rs),'unread':sum(not v['lexical'] and not v['construction_only'] for v in rs)}
   focal=[r for r in rs if r['paragraph']=='f115v|f115v.8-f115v.10'];assert len(focal)==27 and sum(r['lexical'] for r in focal)==13
 assert result['decision']==('JOINT_HEALTH_PURITY_C0_UNRANKED_EXPLICIT_PROGRESS_CONTRADICTED' if any(v['result']=='CONDITIONAL_CONSTRUCTION_CONTRADICTION' for v in events) else 'JOINT_HEALTH_PURITY_C0_UNRANKED_PROGRESS_CAPACITY_ONLY')
 assert result['confirmed_words']==0 and result['semantic_selection'] is None
 out={'status':'PASS','native_paragraphs':len(expected),'raw_groups':result['source_groups'],'alignments':len(alignment),'cases':len(events),'scope':'source selection, raw identities, constant finite-family hypotheses, every registered consequence, assumed graphs, complete reader and counts','semantic_validation':False};(H/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
