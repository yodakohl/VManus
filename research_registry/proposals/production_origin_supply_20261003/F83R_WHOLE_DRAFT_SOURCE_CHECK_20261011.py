from pathlib import Path
import gzip,hashlib,json
from tools import word_profiles
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
m=json.loads((P/'F83R_MATERIAL_MANUAL_EXPLORATORY_DRAFT_20261011.json').read_text());k=json.loads((P/'F83R_SHARED_PROCEDURE_TYPE_VS_USE_DRAFT_20261011.json').read_text());src=R/m['source']['path'];h=hashlib.sha256(src.read_bytes()).hexdigest();assert h==m['source']['sha256']==k['source']['sha256'];rows=json.loads(gzip.decompress(src.read_bytes()))['rows'];bykey={(r['edition'],r['locus'],r['source_group_index']):r for r in rows};anchor_checks=0
for ed,lines in m['native_anchor_rows'].items():
 for locus,entries in lines.items():
  for x in entries:
   original=bykey[(ed,locus,x['group'])];assert (x['raw'],x['left'],x['right'])==(original['ivtff_group_raw'],original['left_separator'],original['right_separator']);anchor_checks+=1
seen=[]
for record in k['whole_page_records']:
 name=record['record'];a,b=m['source']['exact_record_extents'][name];expected=[{'locus':r['locus'],'group':r['source_group_index'],'raw':r['ivtff_group_raw'],'left':r['left_separator'],'right':r['right_separator']} for r in rows if r['edition']=='ZL3b' and r['locus'] in {f'f83r.{i}' for i in range(a,b+1)}];assert expected==record['raw_ZL_groups'];seen.extend((x['locus'],x['group']) for x in expected)
assert len(seen)==len(set(seen))==341
for x in k['captions']:assert bykey[('ZL3b',x['locus'],x['group'])]['ivtff_group_raw']==x['raw_ZL']
assert len(k['captions'])==4
c=word_profiles.ensure_cache()
for form,counts in m['profile_review']['counts_ZL_IT_RF'].items():
 p=word_profiles.profile(c,form);assert [p['editions'][ed]['count'] for ed in ['ZL3b','IT2a','RF1b']]==counts
assert bykey[('RF1b','f83r.28','5')]['ivtff_group_raw']=="{ch'}edy"
for ed in ['ZL3b','IT2a']:assert bykey[(ed,'f83r.28','5')]['ivtff_group_raw']=='shedy'
out={'status':'PASS_SOURCE_FIDELITY_ONLY','source_sha256':h,'draft_hashes':{n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['F83R_MATERIAL_MANUAL_EXPLORATORY_DRAFT_20261011.json','F83R_SHARED_PROCEDURE_TYPE_VS_USE_DRAFT_20261011.json']},'anchor_group_checks':anchor_checks,'complete_ZL_prose_groups':341,'ZL_captions':4,'existing_exact_profiles_checked':6,'RF_second_argument':"{ch'}edy (NOT literal shedy)",'semantic_token_coverage':0,'limit':'Preservation of existing data and profiles only. No syntax, word value, shared procedure, content interpretation or historical writer validated. Root assessment supplies the qoky-unexecuted correction.'};(P/'F83R_WHOLE_DRAFT_SOURCE_VALIDATION_20261011.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
