"""Replay the bounded public primary-text extraction; never reads Voynich data."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
packet = json.loads((BASE / 'E_COMPLETE_PASSAGES.json').read_text())
source_bytes = (BASE / 'E_SOURCE_QUINTE_ESSENCE.html').read_bytes()
assert hashlib.sha256(source_bytes).hexdigest() == packet['source_sha256']
raw = source_bytes.decode('utf-8').replace('\r\n', '\n')

class Plain(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
    def handle_data(self, value):
        self.parts.append(value)

def flatten(value):
    parser = Plain()
    parser.feed(re.sub(r'<span class="pagenum">.*?</span>', '', value, flags=re.S))
    return re.sub(r'\s+', ' ', ''.join(parser.parts)).strip()

rows = [
    {'html': match.group(1), 'text': flatten(match.group(1)),
     'source_line': raw.count('\n', 0, match.start()) + 1}
    for match in re.finditer(r'<td class="maintext">(.*?)</td>', raw, re.S)
]
expected = [('Q1_SOL_SENSES', 14, 20), ('Q2_REAL_SUN_HEAT', 37, 40),
            ('Q3_FLORIN_MEDIATED_TRANSFER', 41, 47),
            ('Q4_GOLD_SILVER_SEPARATION', 63, 65)]
assert len(packet['passages']) == len(expected)
for passage, (identifier, first, last) in zip(packet['passages'], expected):
    assert passage['id'] == identifier
    assert (passage['block_start'], passage['block_end']) == (first, last)
    assert passage['paragraphs'] == rows[first:last + 1]
    assert passage['complete_local_span'] is True
proposal_bytes = (BASE / 'E_RAW_SOL_INTERMEDIATE_CARRIER.json').read_bytes()
proposal = json.loads(proposal_bytes)
assert proposal['source']['packet_sha256'] == hashlib.sha256(
    (BASE / 'E_COMPLETE_PASSAGES.json').read_bytes()).hexdigest()
review = json.loads((BASE / 'E_SCOPE_CORRECTION_REVIEW.json').read_text())
assert review['record_id'] == 'IDEA000762'
assert review['verdict'] == 'untested'
assert 'ONLY AFTER selecting the florin recipe' in review['design']['prediction']
print(json.dumps({'status': 'PASS', 'primary_spans': 4, 'primary_paragraphs': 21,
                  'independent_witnesses': 1, 'new_complete_luna_witnesses': 0,
                  'claim_ceiling': 'SOURCE_EXTRACTION_AND_SCOPE_ONLY',
                  'raw_target_texts_or_images_read_by_validator': 0}, indent=2))
