#!/usr/bin/env python3
"""Small integrity/scope check for one historical chapter; no target data access."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
EXPECTED = {
    '31r': '0ab2913dfd217650a5b0c6ea4ddf6197dd132c645b2dc0865574a3c473106340',
    '31v': '4dab73e0d94380d0959cf608c579196cca08a7cde06fac95e72693c1681c3da1',
    '32r': 'a58306ffd7575fdec8220695268ff43a634fbdf5aa937d218d2e5c621d3cc1b4',
    '32v': '3f98b1cef5397ec6d9a8247ed9acd200e32b372c2ce05d9565e4edc043932c57',
}
rows = json.loads((BASE / 'I_IMAGE_RECEIPTS.json').read_text())
assert {x['folio'] for x in rows} == set(EXPECTED)
for row in rows:
    assert row['sha256'] == EXPECTED[row['folio']]
    assert hashlib.sha256((BASE / row['file']).read_bytes()).hexdigest() == row['sha256']
    assert row['status'] == 200 and row['dimensions'][1] == 2000
    assert row['url'].startswith('https://bl.digirati.io/images/ark:/81055/vdc_100162150552.')
selected = json.loads((BASE / 'I_SELECTED_CANVASES.json').read_text())['selected']
assert {x['label']['en'][0] for x in selected} == {'f. '+f for f in EXPECTED}
assert len(selected) == 4
meta = json.loads((BASE / 'I_SOURCE_METADATA.json').read_text())
assert meta['important_correction']['final_reading'].startswith('xxxv,35')
assert meta['important_correction']['not_a_manuscript_variant_claim']
assert 'age35' in meta['medical_instructions'] and 'age65' in meta['medical_instructions']
assert meta['four_broad_ages']['second_end_years'] == [40,45]
assert meta['new_raw_ideas'] == []
assert not meta['scope']['new_target_primary_text_opened']
assert not meta['scope']['target_image_opened']
reading = (BASE / 'I_SLOANE_COMPLETE_WORKING_READING.md').read_text()
assert list(map(int,re.findall(r'^## (\d+)\.', reading, flags=re.M))) == list(range(1,14))
assert '**.xxxv. (35)**' in reading
assert '**both bloodletting and purging unless great need requires them**' in reading
assert '**honey or sugar**' in reading
transcript = (BASE / 'I_NATIVE_TRANSCRIPT_WORKING.md').read_text()
assert 'Quant li .xxxv. an' in transcript
assert 'END OF SELECTED CHAPTER' in transcript
assert 'not diplomatic' in transcript
manifest = BASE / 'I_SOURCE_RECEIPTS.json'
if manifest.exists():
    for item in json.loads(manifest.read_text())['files']:
        assert item['file'].startswith('I_') and '/' not in item['file']
        data = (BASE / item['file']).read_bytes()
        assert len(data) == item['bytes']
        assert hashlib.sha256(data).hexdigest() == item['sha256']
for path in BASE.glob('I_*'):
    if path.suffix in ('.md','.json','.py','.txt'):
        content = path.read_text()
        assert (chr(47)+'home'+chr(47)) not in content and ('BEGIN '+'PRIVATE KEY') not in content
print(json.dumps({'status':'PASS_SOURCE_PACKET_INTEGRITY_NOT_PALEOGRAPHIC_OR_MEANING_VALIDATION',
                  'source_folios':list(EXPECTED),'sense_units':13,
                  'intervention_thresholds_checked':[35,65],
                  'new_raw_cards':0,'target_data_opened':False},indent=2))
