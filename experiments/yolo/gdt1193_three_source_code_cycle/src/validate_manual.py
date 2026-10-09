"""Root checks the completed blinded manual response; not used by the reader."""
from pathlib import Path
import json,importlib.util
D=Path(__file__).resolve().parents[1];A=D/'artifacts'
spec=importlib.util.spec_from_file_location('cycle',D/'src/run.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
expected=json.loads((A/'MANUAL_EXPECTED.json').read_text());reader=json.loads((A/'MANUAL_READER.json').read_text());pub=json.loads((A/'PUBLIC_TABLE.json').read_text());inverse={(row['rank'],''.join(map(str,row['tail']))):u for u,row in pub['entries'].items()};alph=pub['alphabets'];checks=0
for label,target in expected.items():
 response=reader[label];assert response['words']==target['words'];assert len(response['trace'])==len(target['groups']);state=0;previous=None;pending='';words=[]
 for n,(raw,t) in enumerate(zip(target['groups'],response['trace']),1):
  gs=x.w.m.glyphs(raw);style=1 if previous is None else 2 if previous in '.,;:!?' else 0;position=alph['initial'][style*7:style*7+7].index(gs[0]);rank=(position-state)%7;flag='E' if gs[-1] in alph['final'][:3] else 'C';last=alph['final'][:3] if flag=='E' else alph['final'][3:6];tail=''.join(str((last if i==len(gs)-1 else alph['medial'][:3]).index(g)) for i,g in enumerate(gs[1:],1));u=inverse[rank,tail];pending+=u;emitted=pending if flag=='E' else None
  assert t['group']==n and t['incoming_state']==state and t['style']==['ordinary','recipe-first','after-punctuation'][style] and t['initial']==gs[0] and t['initial_position']==position and t['rank']==rank and t['tail']==tail and t['fragment']==u and t['character_count']==len(u) and t['end_flag']==flag and t['emitted_word']==emitted
  state=(state+len(u))%6;previous=u[-1];assert t['outgoing_state']==state
  if emitted is not None:words.append(emitted);pending=''
  checks+=1
 assert words==target['words'] and response['final_state']==state and response['pending_word']==pending==''
result={'status':'PASS','blinded_blocks':len(expected),'groups_and_complete_manual_traces_verified':checks,'source_words_exact':sum(len(v['words']) for v in expected.values()),'unstated_rules_needed':reader['unstated_rules_needed'],'ceiling':'Assistant hand arithmetic with electronic table lookup and supplied glyph segmentation; not a paper usability study, native translation, or independent statistical confirmation.'};(A/'MANUAL_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
