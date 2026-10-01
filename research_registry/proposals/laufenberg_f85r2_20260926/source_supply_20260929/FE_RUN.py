"""All frozen FD N6/N7 literal candidate windows; no semantic decoder."""
import json,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from tools import word_profiles
P=Path(__file__).resolve().parent;R=P.parents[3]
PAR='experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'
BOUND={'LINE_START','LINE_END','DEFINITE_SPACE'}
def build():
 d=json.loads((P/'FE_DECISION.json').read_text())
 for f,h in d['inputhashes'].items():assert hashlib.sha256((R/f).read_bytes()).hexdigest()==h
 a=json.loads((P/'FD_AUTHOR.json').read_text());maps={b:{**a['frozen73'][b],**{k:v['value'] for k,v in a['new_atomic_values'].items()}} for b in ['G','I']}
 c=word_profiles.ensure_cache(root=R);receipt=word_profiles.receipt(c);allow=set(receipt['inputs']['selectors']);assert len(allow)==179
 paras=json.loads((R/PAR).read_text());covered=set();cases=[];contexts=[]
 patterns={tuple(v):rule for rule,values in d['candidates'].items() for v in values}
 prefix=('tshedy','qokaiin','shedar','sheocphy','okchdy','pcheody','opchear','opchedy','lfchedy','otal')
 def visit(ed,pid,rows,kind):
  raw=[x['ivtff_group_raw'] for x in rows];local=[]
  for i in range(len(rows)):
   for pat,rule in patterns.items():
    if tuple(raw[i:i+len(pat)])!=pat:continue
    wr=rows[i:i+len(pat)];definite=all(x['left_separator'] in BOUND and x['right_separator'] in BOUND for x in wr)
    start=i-10 if rule=='N6_STORAGE' else i-13
    packet=rows[start:start+17] if start>=0 else [];pw=[x['ivtff_group_raw'] for x in packet]
    full=len(pw)==17 and tuple(pw[:10])==prefix and pw[10]=='daiin' and pw[11] in ('sheor','okchedy') and pw[12]=='qoteey' and pw[13]=='daiin' and pw[14] in ('sheor','okchedy') and pw[15:]==['sheos','aiin'] and all(x['left_separator'] in BOUND and x['right_separator'] in BOUND for x in packet)
    eligible=full and ed=='IT2a' and kind=='OWN_NATIVE_PARAGRAPH'
    declared='dry' if rule=='N6_STORAGE' else 'moist';written=maps['G'][pat[1]];leaf=int(rows[i]['page'][1:].split('r')[0].split('v')[0])
    item={'edition':ed,'paragraph_id':pid,'scope_kind':kind,'source_ids':[x['source_group_id'] for x in wr],'raw_words':list(pat),'rule':rule,'definite_surface':definite,'written_property':written,'frozen_rule_property':declared,'conditional_atom_output_mismatch':written!=declared,'full_sufficient_N5_packet':full,'N8_primary_invocation_eligible':eligible,'actual_fixed_graph_conflict':eligible and written!=declared,'physical_leaf':leaf,'split':'FD_CONSTRUCTION_LEAF' if leaf==113 else 'OTHER_EXPOSED_LEAF','no_independent_meaning':True}
    local.append(item);cases.append(item)
  if local:
   contexts.append({'edition':ed,'paragraph_id':pid,'scope_kind':kind,'groups':[dict(x,G_value=maps['G'].get(x['ivtff_group_raw'],'UNKNOWN'),I_value=maps['I'].get(x['ivtff_group_raw'],'UNKNOWN')) for x in rows]})
 for ed in word_profiles.EDITIONS:
  for p in paras.get(ed,[]):
   assert p['page'] in allow
   words=sum([l['words'] for l in p['lines']],[])
   for l in p['lines']:covered.add((ed,l['locus']))
   if not any(tuple(words[i:i+len(pat)])==pat for i in range(len(words)) for pat in patterns):continue
   rows=[]
   for line in p['lines']:
    rr=[dict(x) for x in c.execute('SELECT * FROM groups WHERE edition=? AND locus=? ORDER BY source_group_index',(ed,line['locus']))]
    assert [x['source_group_id'] for x in rr]==line['source_ids'];assert [x['ivtff_group_raw'] for x in rr]==line['words'];rows.extend(rr)
   visit(ed,p['id'],rows,'OWN_NATIVE_PARAGRAPH')
 lines=defaultdict(list)
 for x in c.execute('SELECT * FROM groups ORDER BY edition,page,locus,source_group_index'):
  x=dict(x);assert x['page'] in allow
  if (x['edition'],x['locus']) not in covered:lines[x['edition'],x['locus']].append(x)
 for (ed,locus),rows in lines.items():visit(ed,locus,rows,'OWN_LOCUS_NO_NATIVE_PARAGRAPH')
 c.close()
 result={'unit':'FE','counts':dict(Counter(x['edition']+'|'+x['rule'] for x in cases)),'candidates':len(cases),'whole_contexts':len(contexts),'outside_construction_candidates':sum(x['physical_leaf']!=113 for x in cases),'eligible_primary_candidates':sum(x['N8_primary_invocation_eligible'] for x in cases),'conditional_reverse_candidates':sum(x['conditional_atom_output_mismatch'] for x in cases),'actual_fixed_graph_conflicts':sum(x['actual_fixed_graph_conflict'] for x in cases),'confirmed_words':0,'independent_meaning_leaves':0,'search_significance':False,'source_receipt':receipt,'paragraph_source':PAR,'paragraph_source_sha256':hashlib.sha256((R/PAR).read_bytes()).hexdigest(),'limits':'Strictpacket only sufficient, not exhaustive semanticparse; zero outside doesnotrefutewords orprovewholemodelimpossible.'}
 return result,cases,contexts
if __name__=='__main__':
 result,cases,contexts=build()
 for name,obj in [('FE_RESULT.json',result),('FE_CASES.json',cases),('FE_CONTEXTS.json',contexts)]: (P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='source_receipt'},ensure_ascii=False))
