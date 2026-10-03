#!/usr/bin/env python3
"""GDT1158 deterministic accounting only; does not establish visual truth."""
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
ENTRIES={f'DEV{i:02}' for i in range(1,6)}
WITNESSES={'CLM28531','LAT6823'}
KEYS={(entry,witness) for entry in ENTRIES for witness in WITNESSES}
REGIONS={'root','stem','leaf','reproductive','accessory'}
EXCEPTIONAL={'built_enclosure','vessel_container','attached_animal_human','artificial_support_tie_ring','cut_truncated_stem_treatment','intertwined_closed_root_branch_loop'}
def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def contract_and_receipt():
    lock=read(E/'artifacts/REGISTRATION_LOCK.json')
    assert set(lock['files'])=={'METHOD.md','PREREGISTRATION.md'}
    for path,digest in lock['files'].items():assert sha(E/path)==digest,path
    receipt=read(E/'artifacts/SOURCE_RECEIPT.json')
    assert sha(ROOT/receipt['source_receipt'])==receipt['source_receipt_sha256']
    old=read(ROOT/receipt['source_receipt'])
    assert len(old['pages'])==len(receipt['pages'])==10
    original={(p['candidate_id'],p['witness']):p for p in old['pages']}
    current={(p['candidate_id'],p['witness']):p for p in receipt['pages']}
    assert set(original)==set(current)==KEYS
    for key,page in current.items():
        prior=original[key]
        assert page['request_url']==prior['request_url']
        assert page['expected_sha256']==page['observed_sha256']==prior['raw_sha256']
        assert page['expected_bytes']==page['observed_bytes']==prior['observed_bytes']
        assert page['http_status']==200 and page['status']=='EXACT_BODY_VERIFIED'
        assert page['content_type']=='image/jpeg'
    assert receipt['status']=='ALL_TEN_EXACT_BODIES_VERIFIED' and receipt['voynich_access'] is False
    return current
STATES={'YES','NO','UNCERTAIN','UNKNOWN','CLIPPED','NOT_RECORDED'}
EXCEPTION_FAMILIES={'BUILT_ENCLOSURE','VESSEL_CONTAINER','ATTACHED_ANIMAL_HUMAN','ARTIFICIAL_SUPPORT_TIE_RING','TREATED_CUT_STEM','INTERTWINED_CLOSED_LOOP'}

def support_valid(support):
    assert set(support)=={'A','B'}
    for reviewer in support:
        assert set(support[reviewer])=={'LATIN','CLM'}
        assert set(support[reviewer].values())<=STATES
    return all(value=='YES' for witness in support.values() for value in witness.values())

def entry_decision(entry):
    signature=entry['signature']
    assert entry['entry'] in ENTRIES and isinstance(entry['discovery_rejection_reasons'],list)
    if signature is None:
        assert entry['discovery_rejection_reasons']
        return False,{'signature_present':False}
    descriptors=signature['descriptors'];ids=[d['id'] for d in descriptors]
    assert len(ids)==len(set(ids)) and all(isinstance(s,str) and s for s in ids)
    for descriptor in descriptors:
        assert descriptor['region'] in REGIONS and isinstance(descriptor['concrete'],bool)
        assert descriptor['description'] and descriptor['exception_family'] in EXCEPTION_FAMILIES|{None}
        assert isinstance(descriptor['evidence_refs'],list) and all(isinstance(s,str) and s for s in descriptor['evidence_refs'])
    supported=[support_valid(d['support']) for d in descriptors]
    joint=support_valid(signature['joint_attachment_support'])
    comparisons=entry['comparisons']
    expected={(other,witness) for other in ENTRIES-{entry['entry']} for witness in ['LATIN','CLM']}
    assert len(comparisons)==8 and {(c['other_entry'],c['witness']) for c in comparisons}==expected
    excluded=[]
    for comparison in comparisons:
        assert set(comparison['descriptor_states'])==set(ids)
        assert set(comparison['descriptor_states'].values())<=STATES
        assert isinstance(comparison['evidence_refs'],list) and all(isinstance(s,str) and s for s in comparison['evidence_refs'])
        excluded.append('NO' in comparison['descriptor_states'].values())
    gates={'signature_present':True,'no_recorded_rejection':not entry['discovery_rejection_reasons'],'three_descriptors':len(descriptors)>=3,'three_regions':len({d['region'] for d in descriptors})>=3,'all_concrete':all(d['concrete'] for d in descriptors),'exceptional_detail':any(d['exception_family'] is not None for d in descriptors),'all_four_support_each_descriptor':all(supported),'all_four_joint_attachment_support':joint,'all_eight_controls_exclude_signature':all(excluded)}
    return all(gates.values()),gates
def main():
    receipt=contract_and_receipt()
    rec=read(E/'artifacts/RECONCILIATION.json');support=read(E/'artifacts/RECONCILIATION_SUPPORT.json');result=read(E/'artifacts/RESULT.json')
    assert rec['reviewers']==['A','B'] and set(rec['witnesses'])=={'LATIN','CLM'}
    assert set(rec['observation_sources'])=={'A','B'}
    observations={}
    for reviewer,pointer in rec['observation_sources'].items():
        path=ROOT/pointer['path'];assert sha(path)==pointer['sha256']
        doc=read(path)
        rows=doc['images'] if reviewer=='A' else doc['observations']
        assert len(rows)==10 and {r['sequence'] for r in rows}==set(range(1,11))
        keyname='entry_id' if reviewer=='A' else 'candidate_id'
        mapped={(r[keyname],r['witness']):r for r in rows};assert set(mapped)==KEYS
        for key,row in mapped.items():
            assert row['source_sha256']==receipt[key]['observed_sha256'] and row['sequence']==receipt[key]['sequence']
            if reviewer=='B':assert row['source_url']==receipt[key]['request_url'] and row['native_full_page_viewed'] is True
            required=['localization','completeness','root','stem_branch','leaf','reproductive','exceptional_details','uncertain_or_clipped'] if reviewer=='A' else ['localization','completeness','root_architecture','stem_branch_attachment','leaf_insertion_outline','reproductive_arrangement','extra_botanical_artificial_details','uncertain_clipped_regions','exceptional_families']
            assert all(k in row and row[k] is not None for k in required)
        if reviewer=='A':assert doc['method_sha256']==sha(E/'METHOD.md')
        observations[reviewer]=mapped
    checks=['frozen_METHOD_and_PREREGISTRATION_hashes','ten_original_source_receipt_hash_URL_size_matches','two_reviewers_ten_unique_source_images_each','all_required_observation_regions_and_uncertainties_recorded','frozen_reviewer_source_hashes']
    assert len(rec['entries'])==5 and {e['entry'] for e in rec['entries']}==ENTRIES
    assert len(result['entries'])==5 and {e['entry'] for e in result['entries']}==ENTRIES
    output={e['entry']:e for e in result['entries']};decisions={}
    for entry in rec['entries']:
        qualified,gates=entry_decision(entry);decisions[entry['entry']]=qualified
        actual=output[entry['entry']]
        assert actual['qualifies']==qualified and actual['signature']==entry['signature'] and actual['label']==entry['label']
        assert actual['discovery_rejection_reasons']==entry['discovery_rejection_reasons']
        assert actual['status']==('SOURCE_SIGNATURE_CANDIDATE' if qualified else 'NOT_QUALIFIED')
        if entry['signature'] is None:
            assert actual['descriptor_count']==0 and actual['regions']==[] and actual['exceptional_families']==[] and actual['competitor_checks']==[]
            assert actual['rejection_reasons']==['NO_DISCOVERY_SIGNATURE']+['DISCOVERY_REJECTION:'+s for s in entry['discovery_rejection_reasons']]
        else:
            ds=entry['signature']['descriptors'];ids={d['id'] for d in ds}
            assert actual['descriptor_count']==len(ds) and actual['regions']==sorted({d['region'] for d in ds})
            assert actual['exceptional_families']==sorted({d['exception_family'] for d in ds if d['exception_family']})
            original={(c['other_entry'],c['witness']):c for c in entry['comparisons']}
            assert len(actual['competitor_checks'])==8 and {(c['other_entry'],c['witness']) for c in actual['competitor_checks']}==set(original)
            for row in actual['competitor_checks']:
                c=original[row['other_entry'],row['witness']];states=c['descriptor_states'];nos=sorted(k for k,v in states.items() if v=='NO')
                assert row['descriptor_states']==states and row['observed_no_descriptors']==nos
                assert row['status']=='EXCLUDED_BY_OBSERVED_NO' if nos else row['status']!='EXCLUDED_BY_OBSERVED_NO'
            if qualified:assert not actual['rejection_reasons']
            # This is a cross-reference to post-annotation agreement, not visual verification.
            for reviewer in ['A','B']:
                assert support[reviewer]['each_descriptor']==[d['id'] for d in ds]
                assert support[reviewer][entry['entry']]=={'LATIN':'YES','CLM':'YES'} and support[reviewer]['joint']=='YES'
    checks+=['all_five_entries_and_null_signature_reasons_preserved','three_concrete_descriptors_three_regions_exceptional_family','four_way_descriptor_and_joint_support','all_eight_within_panel_controls_preserve_unknowns','runner_decisions_independently_recomputed']
    # Existing DEV01 has the only proposed signature; enclosure annotations ground
    # its one exceptional family and the sufficient D1 negative controls.
    for reviewer in ['A','B']:
        for witness in WITNESSES:
            row=observations[reviewer]['DEV01',witness]
            obj=row['exceptional_details'] if reviewer=='A' else row['exceptional_families']
            state=obj['built_enclosure']['status' if reviewer=='A' else 'state'];assert state=='YES'
            for other in ENTRIES-{'DEV01'}:
                row=observations[reviewer][other,witness]
                obj=row['exceptional_details'] if reviewer=='A' else row['exceptional_families']
                assert obj['built_enclosure']['status' if reviewer=='A' else 'state']=='NO'
    checks.append('enclosure_support_and_sufficient_D1_control_states_match_original_annotations')
    total=sum(decisions.values());status='SOURCE_SIGNATURE_CANDIDATES' if total>=2 else 'NO_MULTI_ENTRY_SIGNATURE_CAPACITY'
    assert result['entry_count']==5 and result['qualifying_entries']==total and result['required_qualifying_entries']==2 and result['status']==status
    assert result['reconciliation_sha256']==sha(E/'artifacts/RECONCILIATION.json')
    assert result['observation_sources']==[dict(reviewer=r,**rec['observation_sources'][r]) for r in ['A','B']]
    assert result['accounting_only'] is True and result['meanings']==0
    assert all(result[k] is False for k in ['visual_truth_validated','voynich_access','direct_copying_claim','independent_botanical_identification','significance_claim'])
    checks+=['two_entry_threshold_and_overall_capacity_decision','no_visual_truth_copying_Voynich_or_meaning_claim']
    report={'status':'PASS','checks_passed':len(checks),'checks':checks,'scientific_decision':status,'qualifying_entries':[e for e,v in sorted(decisions.items()) if v],'accounting_only':True,'visual_truth_validated':False,'limitations':['The validator checks declared annotation support and accounting, not images or botanical truth.','Reviewer independence and post-annotation support are process records; timestamps and accounting cannot establish epistemic independence.','Containment inside the enclosure is a depicted spatial relation, not physical bonding of tree to wall.','Unknown controls remain unknown; D1 enclosure absence suffices to reject the full signature within this small panel.','Four missing qualifying signatures are capacity failures, not proof that clipped or hidden regions lack features.']}
    print(json.dumps(report,indent=2))
    return report

if __name__=='__main__':main()
