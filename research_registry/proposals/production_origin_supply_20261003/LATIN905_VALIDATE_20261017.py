#!/usr/bin/env python3
"""Static integrity replay only: no corpus query, solver, or network."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 names=['SOURCE','REVIEW_PLAN','WORD_PROFILES','BLIND_READER','REPORT'];paths={n:HERE/f'LATIN905_{n}_20261017.json' for n in names};a={n:read(p) for n,p in paths.items()};s=a['SOURCE'];oldpath=ROOT/s['source'];assert sha(oldpath)==s['source_sha256'];old=read(oldpath)
 assert old['cases']==old['keys']==2 and len(s['cases'])==2
 for label,c,r in zip(['A','B'],s['cases'],old['records']):
  assert c['case']==label and len(r['keys'])==1;k=r['keys'][0]
  for field in ['edition','page','paragraph_id','loci']:assert c[field]==r[field]
  assert c['native_groups']==r['written_groups'];assert c['plaintext']==k['plaintext'];assert c['plaintext_string']==' '.join(k['plaintext'])
  assert c['mask']==k['mask'] and c['inherent']==k['inherent'] and k['grammar_accepted'] is False
  assert len(c['native_groups'])==len(c['plaintext'])==len(c['loci'])
  assert c['status']=='FROZEN_PRIOR_UNASSESSED_LEXICAL_OUTPUT_NOT_A_TRANSLATION'
 assert s['cases'][0]['mask']!=s['cases'][1]['mask'] and s['cases'][0]['inherent']!=s['cases'][1]['inherent']
 plan=a['REVIEW_PLAN'];assert plan['data']==str(paths['SOURCE'].relative_to(ROOT)) and plan['data_sha256']==sha(paths['SOURCE'])
 for p,h in plan['prior_sha256'].items():assert sha(ROOT/p)==h
 report=a['REPORT']
 for p,h in report['artifacts'].items():assert sha(ROOT/p)==h,p
 profiles=a['WORD_PROFILES'];forms=set(w for c in s['cases'] for w in c['native_groups']);pm={p['form']:p for p in profiles['profiles']}
 assert len(forms)==len(pm)==len(profiles['profiles'])==27 and set(pm)==forms
 receipt=profiles['source_receipt'];inputs=receipt['inputs']
 for k in ['source','allowlist','code']:assert sha(ROOT/inputs[k])==inputs[k+'_sha256']
 assert inputs['matching']=='exact_raw_group' and inputs['selector_count']==179
 checked=0
 for f,p in pm.items():
  assert p['matching']=='exact_raw_group' and set(p['editions'])=={'IT2a','ZL3b','RF1b'}
  for ed,v in p['editions'].items():
   n=v['count'];assert sum(v['positions'].values())==n
   for field,rows in v['strata'].items():assert sum(z['count'] for z in rows)==n,(f,ed,field)
   assert 0<=v['pages_with_form']<=v['pages_total']==179 and n<=v['total_groups']
   assert abs(v['fraction']-n/v['total_groups'])<1e-14
   for ex in v['examples']:
    assert ex['edition']==ed and ex['ivtff_group_raw']==f
    assert ex['source_group_id']==f"{ed}|{ex['locus']}|G{int(ex['source_group_index']):03d}"
    i=int(ex['source_group_index']);size=int(ex['source_group_count']);assert 1<=i<=size
    pos='single' if size==1 else 'start' if i==1 else 'end' if i==size else 'middle';assert ex['position']==pos
   checked+=1
 for f,claims in report['profile_account']['examples_IT2a'].items():
  v=pm[f]['editions']['IT2a']
  for k,z in claims.items():
   if k=='pages':assert z==v['pages_with_form']
   elif k=='positions':
    for pos,num in z.items():assert v['positions'][pos]==num
   elif k=='adjacent_pairs':assert z==v['repetition']['adjacent_pairs']
   else:assert z==v[k]
 for e in profiles['prior_evidence']:
  for source in e.get('sources',[]):assert sha(ROOT/source['path'])==source['sha256'],source['path']
 counts=report['counts'];assert counts['frozen_outputs_reviewed']==2 and all(counts[k]==0 for k in ['new_native_cases','new_keys','new_word_meanings','confirmed_translated_words'])
 text905=(ROOT/'experiments/yolo/gdt905_joint_cv_complete_passage_candidates/REPORT.md').read_text();text906=(ROOT/'experiments/yolo/gdt906_complete_cv_key_enumeration/REPORT.md').read_text()
 assert 'CONSTRUCTIVE_CV_SEARCH_UNRESOLVED' in text905 and 'UNKNOWN' in text905
 assert 'COMPLETE_NO_GRAMMAR_KEY' in text906 and '439.399' in text906
 assert 'UNKNOWN' in report['prior_decisions_preserved']['GDT905'] and '439399' in report['prior_decisions_preserved']['GDT906']
 out={'status':'PASS_STATIC_SOURCE_PROFILE_AND_REPORT_BINDINGS','validator_sha256':sha(Path(__file__)),'artifact_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths.values()},'old_lexical_source_sha256':sha(oldpath),'frozen_cases':2,'native_positions':sum(len(c['native_groups']) for c in s['cases']),'exact_forms':27,'separate_reader_profile_records_checked':checked,'checks':['Exact A/B extraction, original loci and distinct keys/inherent vowels preserved','Every review/report input hash and pinned old report matches','All27 source-form names represented separately in all three editions','Stored profile marginal arithmetic, example identities/positions and quoted IT report counts agree','Curated source-card hashes verified without importing their historical glosses','905 original UNKNOWN and906 later fixed-contract exhaustion distinguished; zero new meanings retained'],'limits':['Static replay does not independently reconstruct corpus profile counts; it validates stored profile consistency and bound receipts without any new raw/native query.','Does not validate the claimed external blinding chronology or linguistic expertise, and does not independently verify linked web sources.','No full-Latin impossibility proof; partial parses do not become native word assignments.','Separate keys and alternate readers are not combined or treated as independent manuscript evidence.'],'overclaim_review':'No material source/decision overclaim identified in the bounded report. The report expressly limits the linguistic judgment and preserves model-specific prior decisions.'}
 (HERE/'LATIN905_VALIDATION_20261017.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'status':out['status'],'cases':2,'positions':out['native_positions'],'profiles':checked,'validator_sha256':out['validator_sha256']}))
if __name__=='__main__':main()
