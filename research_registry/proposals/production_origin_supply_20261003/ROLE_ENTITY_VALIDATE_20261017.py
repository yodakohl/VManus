#!/usr/bin/env python3
"""Static source/accounting and four-form table check; no meaning test."""
import collections,hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 paths={k:HERE/f'ROLE_ENTITY_{k}_20261017.json' for k in ['PLAN','SOURCE','PROFILES','REPORT']};x={k:read(p) for k,p in paths.items()};s=x['SOURCE'];r=x['REPORT'];oldpath=ROOT/s['source'];assert sha(oldpath)==s['source_sha256'];old=read(oldpath)
 assert s['original_packet']==old['source_pin'];assert sha(ROOT/s['original_packet']['path'])==s['original_packet']['sha256']
 for p,h in x['PLAN']['primary_sha256'].items():assert sha(ROOT/p)==h
 for p,h in r['pins'].items():assert sha(ROOT/p)==h
 forms=['qokal','qokar','ol','or'];tables={}
 for mode in ['E','C']:
  tab={}
  for f in forms:
   root=f[:-1];end=f[-1]
   tab[f]={'slot':(0 if root=='qoka' else 1) if mode=='E' else (0 if end=='l' else 1),'opaque_referent':('A' if end=='l' else 'B') if mode=='E' else ('Q' if root=='qoka' else 'O')}
  assert r['models'][mode]['table']==tab;tables[mode]=tab
 source_rows=old['all_native_groups'];assert len(s['groups'])==len(source_rows)==176
 totals=collections.Counter();tagged=collections.Counter();lines=collections.OrderedDict()
 for g,orig in zip(s['groups'],source_rows):
  for k,v in orig.items():
   if k=='inherited_capacity_status':continue
   assert g['group' if k=='native_group' else k]==v,(k,g['group']['source_group_id'])
  f=g['group']['ivtff_group_raw'];ed=g['edition'];totals[ed]+=1;assert g['meaning']=='UNASSIGNED'
  for m in ['E','C']:assert g[m]==tables[m].get(f)
  assert g['status']==('HYPOTHETICAL_STRUCTURAL_TAG_ONLY' if f in forms else 'UNKNOWN_UNINTERPRETED')
  tagged[ed]+=f in forms;lines.setdefault((ed,g['locus']),[]).append(g)
 assert dict(totals)==s['total_groups_by_reader']=={'IT2a':59,'ZL3b':59,'RF1b':58}
 assert dict(tagged)==s['tagged_occurrences_by_reader']=={'IT2a':11,'ZL3b':10,'RF1b':10}
 assert s['literal_text_by_line']==[{'edition':ed,'locus':loc,'text':' '.join(g['group']['ivtff_group_raw'] for g in gs)} for (ed,loc),gs in lines.items()]
 def evaluate(pair,mode):
  vals=[tables[mode][f] for f in pair]
  if vals[0]['slot']==vals[1]['slot']:return None
  return [next(v['opaque_referent'] for v in vals if v['slot']==i) for i in [0,1]]
 pair_rows=r['all_16_formal_pairs'];assert len(pair_rows)==16 and {tuple(z['written_pair']) for z in pair_rows}==set(itertools.product(forms,repeat=2));split=collections.Counter()
 for z in pair_rows:
  flags=[]
  for m in ['E','C']:
   want=evaluate(z['written_pair'],m);assert z[m]['closed_binary']==(want is not None)
   if want is not None:assert z[m]['tuple']==want
   else:assert 'tuple' not in z[m]
   flags.append(want is not None)
  split[tuple(flags)]+=1
 assert dict(split)=={(False,False):4,(False,True):4,(True,False):4,(True,True):4}
 pairs=[]
 for (ed,loc),gs in lines.items():
  if ed!='IT2a':continue
  for a,b in zip(gs,gs[1:]):
   aa,bb=a['group'],b['group'];fs=[aa['ivtff_group_raw'],bb['ivtff_group_raw']]
   if all(f in forms for f in fs):
    assert int(bb['source_group_index'])==int(aa['source_group_index'])+1
    assert aa['right_separator']==bb['left_separator']=='DEFINITE_SPACE'
    pairs.append((loc,[aa['source_group_id'],bb['source_group_id']],fs))
 actual=r['actual_adjacent_four_form_pairs_in_old_IT_scope'];assert len(pairs)==len(actual)==2
 for (loc,ids,fs),z in zip(pairs,actual):
  assert z['locus']==loc and z['group_ids']==ids and z['written_pair']==fs and z['argument_frame_owned'] is False and z['seam']=='DEFINITE_SPACE'
  for mode in ['E','C']:assert z[mode]=={'closed_binary':True,'tuple':evaluate(fs,mode)}
 for label in ['qokal or','qokar ol']:
  for mode in ['E','C']:assert r['known_reversal'][label][mode]==evaluate(label.split(),mode)
 ps=x['PROFILES'];pm={p['form']:p for p in ps['profiles']};assert set(pm)==set(forms) and len(ps['profiles'])==4
 for f,p in pm.items():
  assert p['matching']=='exact_raw_group' and set(p['editions'])=={'IT2a','ZL3b','RF1b'}
  for ed,v in p['editions'].items():
   assert sum(v['positions'].values())==v['count']
   for rows in v['strata'].values():assert sum(z['count'] for z in rows)==v['count']
  it=p['editions']['IT2a'];z=r['profiles_and_prior_account']['IT2a_exact_form_counts'][f]
  assert z=={'count':it['count'],'pages':it['pages_with_form'],'positions':it['positions'],'repetition':it['repetition']}
 receipt=ps['source_receipt']['inputs']
 for k in ['source','code','allowlist']:assert sha(ROOT/receipt[k])==receipt[k+'_sha256']
 ct=r['counts'];assert ct['IT_groups']==59 and ct['IT_tagged_occurrences']==11 and ct['IT_unknown_occurrences']==48 and ct['formal_pair_cases']==16
 assert all(ct[k]==0 for k in ['new_native_cases','new_word_meanings','confirmed_words'])
 out={'status':'PASS_STATIC_SOURCE_AND_STRUCTURAL_TABLE_ACCOUNTING','validator_sha256':sha(Path(__file__)),'artifact_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths.values()},'source_rows':176,'per_reader_groups':dict(totals),'per_reader_tagged_occurrences':dict(tagged),'formal_pairs':16,'pair_partition':{'both':4,'E_only':4,'C_only':4,'neither':4},'actual_IT_pairs':pairs,'unknown_IT_groups':48,'checks':['All raw source groups, line/paragraph metadata and retained source flags match1129 exactly; old native_group key is renamed group; inherited_capacity_status is not duplicated in projection','Only four exact whole forms tagged; all remaining groups unknown','Both factorisations independently reconstructed from stated two-by-two axes','All ordered pairs and actual two adjacency cases reconstructed; no ownership inferred','Profile receipt/source/report pins and stored per-reader/profile arithmetic checked'],'limits':['A/B and Q/O are unbound structural variables, not observed entities. Complete binary expression ownership is an assumption.','Static profile integrity is not an independent corpus recount.','The two actual adjacent pairs are previously known same-leaf source material; no semantic score, new relation or independent replication.','No new meaning, source query, solver, image, or empirical experiment.'],'validator_schema_note':'Initial validator expected identical key names; corrected source mapping native_group to group and acknowledged omitted inherited_capacity_status before successful validation. No root artifact changed.','overclaim_review':'No material overclaim found: report distinguishes full source display from partial hypothetical tagging and does not select a factorisation.'}
 (HERE/'ROLE_ENTITY_VALIDATION_20261017.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':out['status'],'groups':176,'tagged':dict(tagged),'formal_pairs':16}))
if __name__=='__main__':main()
