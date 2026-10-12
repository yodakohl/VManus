from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(name):return json.loads((B/'artifacts'/name).read_text())
def main():
    for p,h in read('REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    for p,h in read('OBSERVATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    a=read('STAGE_A.json');b=read('STAGE_B.json');lock=read('STAGE_A_LOCK.json')
    assert hashlib.sha256((B/'artifacts/STAGE_A.json').read_bytes()).hexdigest()==lock['sha256']
    complete=a['free_k']['status']=='COMPLETE_DIFFERENTIAL_TEMPLATE' and a['free_t']['status']=='COMPLETE_DIFFERENTIAL_TEMPLATE'
    assert not complete
    cases=b['fixed_cases'];assert len(cases)==3
    assert all(c['matching_H_under_frozen_template']==c['wrong_H_under_frozen_template']=='UNRESOLVED' for c in cases)
    out={'status':'TEMPLATE_CAPACITY_STOP__INFORMED_GRAPHIC_COMPATIBILITY','fixed_crossed_test':'UNSCORABLE','reason':'Incomplete free high-body references at StageA; later reference visibility cannot repair the frozen comparison.','fixed_target_cases':len(cases),'descriptive_low_motif_compatible':sum(c['low_motif']=='LOW_LATERAL_SUPPORTS_AND_CONNECTING_BRIDGE_COMPATIBLE' for c in cases),'source_physical_leaves':1,'observer_count':1,'sound_or_word_values':0,'source_aware':True,'postview_graphic_comparison':'Exploratory only; single complex letter, multi-letter ligature and modifier constructions not distinguished.','claim_ceiling':'Manual local appearance, not confirmed graphemes, atom count, sequence order, actual pen strokes or independent palaeography.'}
    (B/'artifacts/RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
