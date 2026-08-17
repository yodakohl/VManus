#!/usr/bin/env python3
"""Rank GDT247 cross-scope forms using already-published opaque-host evidence."""
import csv,hashlib,json,math
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parent
MATCH='gdt247_exact_label_prose_member_matches.tsv';MAN='gdt165_host_manifest.tsv';EDGE='gdt165_edge_inventory.tsv';CTX='gdt166_context_inventory.tsv';DIR='gdt165_directed_relations.tsv';R165='gdt165_result.json';R166='gdt166_result.json'
OUTS=['gdt248_cross_scope_address_candidates.tsv','gdt248_address_counterexamples.tsv'];DOCS=['GDT248_CROSS_SCOPE_ADDRESS_RANKING_METHOD.md','GDT248_CROSS_SCOPE_ADDRESS_RANKING_REPORT.md']
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()
def read(p):
 with (R/p).open(encoding='utf-8') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(p,rows):
 with (R/p).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def entropy(c):
 n=sum(c.values());return -sum(v/n*math.log2(v/n) for v in c.values()) if n else 0.0
def main():
 m=read(MATCH);man={r['page_host']:r for r in read(MAN)};edge=read(EDGE);ctx=[r for r in read(CTX) if r['context_mode']=='WINDOW_PM2'];direct=read(DIR)
 assert all(not r['locus'].startswith('f84') for r in edge) and all(not r['locus'].startswith('f84') for r in ctx)
 assert {r['member_surface'] for r in m}=={'okaly','olky','okal'}
 labels={r['member_surface']:r for r in m};rows=[]
 rank_order=['okal','olky','okaly']
 states={'okal':'Q13_STARS_BRIDGE_LOW_CAPACITY_CONTENT_ADDRESS_CANDIDATE','olky':'CURRIER_B_WIDE_FORMAL_CODE_CANDIDATE','okaly':'CROSS_REGISTER_GENERAL_FORMAL_CODE_CANDIDATE'}
 for rank,h in enumerate(rank_order,1):
  z=[r for r in ctx if r['focal_host']==h];out=Counter(r['target_host'] for r in edge if r['source_host']==h);inc=Counter(r['source_host'] for r in edge if r['target_host']==h);mrow=man[h];m0=labels[h]
  sections=Counter(r['section'] for r in z);currier=Counter(r['currier'] for r in z);hands=Counter(r['hand'] for r in z)
  stable=sum(r['source_host']==h or r['target_host']==h for r in direct)
  rows.append({'rank':rank,'page_host':h,'gdt247_label_locus':m0['label_locus'],'gdt247_prose_locus':m0['prose_locus'],'global_endpoint_events':mrow['endpoint_events'],'global_physical_folios':mrow['physical_folios'],'window_occurrences':len(z),'window_physical_folios':len({r['physical_folio'] for r in z}),'sections':';'.join(f'{k}:{sections[k]}' for k in sorted(sections)),'currier':';'.join(f'{k}:{currier[k]}' for k in sorted(currier)),'hands':';'.join(f'{k}:{hands[k]}' for k in sorted(hands,key=str)),'unique_window_contexts':len({r['context_sha256'] for r in z}),'outgoing_events':sum(out.values()),'outgoing_partner_types':len(out),'outgoing_partner_entropy_bits':f'{entropy(out):.9f}','incoming_events':sum(inc.values()),'incoming_partner_types':len(inc),'incoming_partner_entropy_bits':f'{entropy(inc):.9f}','gdt165_stable_directed_relations':stable,'candidate_state':states[h],'semantic_value':'UNASSIGNED'})
 write(OUTS[0],rows)
 counter=[
 {'counterexample':'NO_STABLE_DIRECTED_RELATION','value':'0 GDT165 stable directed relations involve okaly olky or okal','consequence':'no transferable neighbor-defined function'},
 {'counterexample':'CONTEXT_DIVERSITY','value':'33/33 WINDOW_PM2 occurrences have distinct exact context hashes','consequence':'none is a fixed local formula on the published panel'},
 {'counterexample':'OKALY_BROAD_REGISTER','value':'18 focal occurrences on 15 folios across H B S T','consequence':'the f80 label/prose bridge is not visually or section specific'},
 {'counterexample':'OLKY_CURRIER_B_CONFOUND','value':'11 focal occurrences across four sections are all Currier B','consequence':'Currier/register rendering can explain recurrence'},
 {'counterexample':'OKAL_LOW_CAPACITY','value':'four global focal occurrences on four Stars folios plus the f82r local bridge','consequence':'q13-Stars bridge is abductive and not a transferable dictionary entry'},
 ]
 write(OUTS[1],counter)
 result={'experiment':'GDT248_CROSS_SCOPE_ADDRESS_RANKING','status':'OKAL_LOW_CAPACITY_Q13_STARS_ADDRESS_LEAD_OTHERS_FORMAL_OR_REGISTER_LIKE','candidates':len(rows),'ranking':rank_order,'okaly':{'window_occurrences':18,'folios':15,'sections':4},'olky':{'window_occurrences':11,'folios':9,'sections':4,'currier_b_fraction':1.0},'okal':{'window_occurrences':4,'folios':4,'sections':['S'],'plus_f82r_exact_label_prose_bridge':True},'stable_directed_relations':0,'interpretation':'okal is the narrowest opaque q13-to-Stars bridge candidate; olky is Currier-B-wide and okaly cross-register, so neither has a local visual interpretation.','active_semantic_assignments':0,'claim_ceiling':'Post-hoc ranking of opaque exact hosts only; no referent function word language plaintext or translation.','f84':{'input':False,'retained':False,'joined':False,'scored':False,'new_access':False},'inputs':{p:sha(p) for p in [MATCH,MAN,EDGE,CTX,DIR,R165,R166]},'outputs':{},'documents':{},'implementation':{}}
 for p in OUTS:result['outputs'][p]=sha(p)
 for p in DOCS:
  if (R/p).exists():result['documents'][p]=sha(p)
 result['implementation'][Path(__file__).name]=sha(Path(__file__).name);result['content_hash']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest();(R/'gdt248_result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'status':result['status'],'ranking':[(r['rank'],r['page_host'],r['candidate_state'],r['sections']) for r in rows]},sort_keys=True))
if __name__=='__main__':main()
