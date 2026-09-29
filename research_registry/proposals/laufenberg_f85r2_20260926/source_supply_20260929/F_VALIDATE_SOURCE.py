"""Verify the bounded historical-source packet without reading target data."""
from pathlib import Path
import hashlib
import json
from PIL import Image

BASE = Path(__file__).resolve().parent
packet = json.loads((BASE/'F_COMPLETE_ENTRIES.json').read_text())
source = BASE/packet['source_file']
raw = source.read_text(encoding='utf-8')
assert hashlib.sha256(source.read_bytes()).hexdigest() == packet['source_sha256']
expected = {'DIPSACUS': ('CHAMAELEON', ['066B','067A']),
            'ATRACTYLIS': ('ACANTHIUM', ['068A','068B']),
            'CARDUUS': ('ANONIS', ['071A','071B','072A'])}
assert set(e['id'] for e in packet['entries']) == set(expected)
for entry in packet['entries']:
    next_name, pages = expected[entry['id']]
    first = raw.index('<h2>'+entry['id']+'.</h2>')
    last = raw.index('<h2>'+next_name+'.</h2>', first)
    assert entry['source_html'] == raw[first:last]
    assert entry['complete_local_entry'] is True
    assert entry['following_entry_boundary'] == next_name
    assert entry['native_full_page_images'] == ['F_LONITZER_'+n+'.jpg' for n in pages]
    for filename in entry['native_full_page_images']:
        with Image.open(BASE/filename) as image:
            assert image.width >= 1000 and image.height >= 1600
            image.verify()
collation = json.loads((BASE/'F_NATIVE_COLLATION.json').read_text())
assert len(collation['lonitzer']) == 7
assert set(x['file'] for x in collation['lonitzer']) == {
    f for e in packet['entries'] for f in e['native_full_page_images']}
medieval = collation['medieval_supplement']
assert hashlib.sha256((BASE/medieval['image_file']).read_bytes()).hexdigest() == medieval['image_sha256']
assert 'not completely' in medieval['limits']
texts = {e['id']:e['typed_plain_text'] for e in packet['entries']}
assert 'In singu lis caulibus, in cacumine capitulum unum' in texts['DIPSACUS']
assert 'ACANTHIUM, lower image on 68v; following entry' in texts['ATRACTYLIS']
assert 'radicem tenuem et inutilem' in texts['ATRACTYLIS']
assert 'nisi quod aculeis caret' in texts['CARDUUS']
assert 'Ibit et in numeros sic Venus apta suos.' in texts['CARDUUS']
print(json.dumps({'status':'PASS','complete_entries':3,'early_printed_work':1,
                  'native_full_print_pages':7,'medieval_labelled_image_supplements':1,
                  'fully_collated_medieval_text_entries':0,'new_raw_cards':0,
                  'retained_idea_ids':['IDEA000737','IDEA000324'],
                  'scope':'source bytes, complete boundaries and observation receipts; not target meaning or modern taxonomy'},indent=2))
