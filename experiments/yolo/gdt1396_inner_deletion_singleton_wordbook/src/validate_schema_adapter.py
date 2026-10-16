#!/usr/bin/env python3
"""Explicit post-failure metadata-type correction; original validator stays frozen."""
import hashlib
import json
from pathlib import Path

E=Path(__file__).resolve().parents[1]
ROOT=E.parents[2]
A=E/'artifacts'
OLD="'source_group_index':group['source_group_index']"
NEW="'source_group_index':int(group['source_group_index'])"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    lock_path=E/'ADAPTER_LOCK.json'
    lock=json.loads(lock_path.read_text())
    for pin in lock['files']:
        assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']
    original=E/'src/validate.py'
    text=original.read_text()
    assert text.count(OLD)==1
    transformed=text.replace(OLD,NEW)
    transformed_hash=hashlib.sha256(transformed.encode('utf-8')).hexdigest()
    assert transformed_hash==lock['transformed_validator_sha256']
    assert not (A/'VALIDATION.json').exists()
    assert not (A/'VALIDATION_DIAGNOSTIC.json').exists()
    namespace={'__file__':str(original),'__name__':'frozen_validator_schema_diagnostic'}
    exec(compile(transformed,str(original),'exec'),namespace)

    def diagnostic_save(path,receipt):
        assert path==A/'VALIDATION.json'
        assert receipt['status']=='PASS_INDEPENDENT_VALIDATION'
        receipt['status']='PASS_DIAGNOSTIC_SCHEMA_NORMALIZATION'
        pins=receipt['pins']
        pins['original_frozen_validator_sha256']=pins.pop('validator_sha256')
        assert pins['original_frozen_validator_sha256']==sha(original)
        pins['executed_adapter_sha256']=sha(Path(__file__))
        pins['executed_transformed_validator_sha256']=transformed_hash
        pins['adapter_lock_sha256']=sha(lock_path)
        pins['original_validation_failure_sha256']=sha(A/'ORIGINAL_VALIDATION_FAILURE.json')
        receipt['diagnostic_correction']={
            'original_status':'ORIGINAL_FROZEN_VALIDATOR_FAILED',
            'field':'source_group_index',
            'change':'Convert the old1233 decimal-string index to int solely in the expected old1227 witness dictionary.',
            'replacement_from':OLD,'replacement_to':NEW,
            'original_code_inputs_result_unchanged':True,
            'scientific_criteria_unchanged':True,
            'claim':'Diagnostic correctness after explicit schema normalization; not a PASS for the original frozen validator.'}
        (A/'VALIDATION_DIAGNOSTIC.json').write_text(json.dumps(receipt,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
    namespace['save']=diagnostic_save
    namespace['validate']()
    assert not (A/'VALIDATION.json').exists()
    for pin in lock['files']:
        assert sha(ROOT/pin['path'])==pin['sha256'],pin['path']

if __name__=='__main__':
    main()
