from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):return json.loads(p.read_text())
def main():
    for p,h in read(B/'artifacts/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    lock=read(B/'artifacts/OBSERVATION_LOCK.json');assert hashlib.sha256((R/lock['path']).read_bytes()).hexdigest()==lock['sha256'];o=read(B/'artifacts/OBSERVATION.json');receipt=read(B/'artifacts/SOURCE_RECEIPT.json');assert hashlib.sha256((B/'source/F57V_ORIGINAL.jpg').read_bytes()).hexdigest()==receipt['sha256']
    assert o['whole_band_coverage'] and o['view_count']==1 and o['exact_item_count'] is None and not o['explicit_global_entry_delimitation']
    result={'status':o['status'],'source_identity':'EXACT_HISTORICAL_JPEG','observations':{'localized':o['localization'],'boundary_device':o['boundary_device'],'repeat_limits':o['repeat_limits'],'graphic_forms':o['multi_part_shapes'],'coverage_notes':o['coverage_notes']},'exact_item_count':None,'exact_type_inventory':None,'claimed_new_phonemes':0,'claimed_new_meanings':0,'scope':'One informed image-only observation. Recorded boundaries unresolved; no alphabet count, transcript repair or old semantic claim. Accounting is not perceptual validation.'};(B/'artifacts/RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({'status':result['status'],'exact_item_count':None,'new_phonemes':0}))
if __name__=='__main__':main()
