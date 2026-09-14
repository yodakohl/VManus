#!/usr/bin/env python3
import collections,csv,hashlib,json
from pathlib import Path
from extract import extract
E=Path(__file__).resolve().parents[1]
def dump(name,data): (E/'artifacts'/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def tsv(name,rows,cols):
 with (E/'artifacts'/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=cols,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def main():
 extract()
 lock=json.loads((E/'CANDIDATE_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((E/p).read_bytes()).hexdigest()==h,p
 model=json.loads((E/'src/CANDIDATES.json').read_text());packet=json.loads((E/'artifacts/SOURCE_PACKET.json').read_text());occ=json.loads((E/'artifacts/ALL_OCCURRENCES.json').read_text())
 census=[]
 for ed in ['ZL3b','IT2a','RF1b']:
  for fam in ['cheo/cho','oka/ota']:
   rows=[o for o in occ if o['edition']==ed and o['family']==fam];cnt=collections.Counter(o['cell'] for o in rows)
   census.append(dict(edition=ed,family=fam,rr=cnt['rr'],rl=cnt['rl'],lr=cnt['lr'],ll=cnt['ll'],total=len(rows)))
 tsv('CENSUS.tsv',census,['edition','family','rr','rl','lr','ll','total'])
 aligned=[];reader=['# Two complete candidate readings of the selected lines','','All meanings, punctuation and scopes are assumptions. Source is complete physical lines, not independently established sentences. Uncertain readings remain explicit.','']
 for ln in packet['lines']:
  md=ln['metadata'];raw=[g['ivtff_group_raw'] for g in ln['groups']];reader += [f"## {md['edition']} {md['locus']}",'','`'+' '.join(raw)+'`','']
  for cid,c in model['candidates'].items():
   vals=[c['lexicon'].get(w,'[UNGEKLÄRT: '+w+']') for w in raw]
   for g,v in zip(ln['groups'],vals):aligned.append(dict(candidate=cid,edition=md['edition'],locus=md['locus'],source_id=g['source_group_id'],raw=g['ivtff_group_raw'],gloss=v,status='OPEN_READER_VARIANT' if v.startswith('[UNGEKLÄRT:') else 'STIPULATED'))
   reader += [f"**{cid} — wortweise:** "+' | '.join(vals),'']
   unresolved=[w for w in raw if w not in c['lexicon']]
   if unresolved:reader += ['**Durchgehende Fassung:** Wegen der offenen RF-Gruppen hier keine vollständige deutsche Fassung behauptet. Die ZL-/IT-Fassung an derselben Stelle steht separat.','']
   else:reader += ['**Durchgehende Fassung:** '+c['readings'][md['locus']],'']
  reader += ['**Zusätzlich angesetzt:** Interpunktion; Listen-/Verfahrensumfang; Zugehörigkeit der benachbarten Wörter. Materialien werden durch gleiche Wörter über verschiedene Blätter nicht zu denselben Individuen.','']
 (E/'artifacts/READINGS.md').write_text('\n'.join(reader).rstrip()+'\n')
 tsv('ALIGNMENT.tsv',aligned,['candidate','edition','locus','source_id','raw','gloss','status'])
 consequence=[]
 for d in model['consequences']:
  row=dict(d)
  if d['id']=='D2':
   row['observed']=[dict(edition=x['edition'],family=x['family'],mixed=x['rl']+x['lr'],total=x['total']) for x in census]
   row['decision']='N plus universal adjacent-constituent bridge contradicted by known mixed cells; N semantic core not isolated; S not selected.'
  elif d['id']=='D5':row['observed']={ln['metadata']['edition']:[g['ivtff_group_raw'] for g in ln['groups']][-3:] for ln in packet['lines'] if ln['metadata']['locus']=='f75r.36'};row['decision']='Reader difference present; both authored renderings share consequence.'
  else:row['observed']=None;row['decision']='NO_INDEPENDENT_OBSERVABLE_BINDING_IN_PACKET'
  consequence.append(row)
 dump('CONSEQUENCES.json',consequence)
 tsv('CONSEQUENCES.tsv',[{k:(json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else str(v)) for k,v in d.items()} for d in consequence],list(consequence[0]))
 candidates=[]
 for cid,c in model['candidates'].items():
  rows=[r for r in aligned if r['candidate']==cid]
  candidates.append(dict(id=cid,glossary_forms=len(c['lexicon']),aligned_positions=len(rows),assigned_positions=sum(r['status']=='STIPULATED' for r in rows),open_positions=sum(r['status']!='STIPULATED' for r in rows),full_clear_readings=sum(all(g['ivtff_group_raw'] in c['lexicon'] for g in ln['groups']) for ln in packet['lines']),meaning_selected=False))
 zl=[ln for ln in packet['lines'] if ln['metadata']['edition']=='ZL3b'];freq=collections.Counter(g['ivtff_group_raw'] for ln in zl for g in ln['groups'])
 result=dict(status='TWO_FULL_READINGS_ADJACENCY_BRIDGE_FAILS_MEANING_UNSELECTED',selection=packet['selection'],census=census,total_pair_occurrences=len(occ),physical_selected_leaves=4,source_reader_lines=len(packet['lines']),zl_groups=sum(freq.values()),zl_types=len(freq),zl_singleton_types=sum(v==1 for v in freq.values()),candidates=candidates,semantic_confirmation_capacity=0,project_significance_claim=False,reserves_opened=False,new_manuscript_finding='none claimed; mixed cells were already present in GDT915',decision='The first countable contrast rejects an extra universal attachment rule, not the numerical meanings. State and number are not selected by available independent observations. No further extension of these drafts is justified by the census alone.')
 dump('RESULT.json',result)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
