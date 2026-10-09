#!/usr/bin/env python3
"""Finite primitive check supporting the all-group terminal-sign proof."""
from pathlib import Path
import hashlib
import json

D = Path(__file__).resolve().parent
P = D / 'HUMAN_SOURCE_MARKED_FUNCTION_PREFIXES_RAW_20261005.json'
raw = json.loads(P.read_text())
c = raw['teaching_carrier']
g = raw['design']
ordinary = c['ordinary_signs']
rare = c['rare_selectors']
prefix = g['prefix_selectors']
assert len(ordinary) == 19 and len(rare) == 8
assert len(prefix) == len(g['prefix_words_in_order']) == 12
codes = [[s] for s in ordinary] + [['q', s] for s in ordinary[:7]]
codes += [['y', rare[j // 8], rare[j % 8]] for j in range(len(c['rare_characters_in_order']))]
prefix_codes = [['r', s] for s in prefix]
all_codes = codes + prefix_codes
assert len(codes) == 26 + len(c['rare_characters_in_order'])
assert all(set(code) <= set(c['existing_shape_labels']) for code in all_codes)
ends = sorted({code[-1] for code in all_codes})
assert 'y' not in ends
result = {
    'status': 'LITERAL_CARRIER_END_Y_IMPOSSIBLE__GROUPING_UNTESTED',
    'raw_card_sha256': hashlib.sha256(P.read_bytes()).hexdigest(),
    'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'source_character_codes': len(codes), 'prefix_codes': len(prefix_codes),
    'possible_primitive_terminal_signs': ends,
    'proof': 'Every legal nonempty group is a concatenation of complete marked-prefix codes and/or complete character codes. Its last sign is the last sign of its last code. All those terminal signs exclude y. A y escape has two required following selectors. The final marker-only run also ends in a non-y selector. Physical wraps occur only between complete groups.',
    'consequence': 'The literal unchanged teaching carrier cannot emit a complete y-final group, including the retained definite daldy group at f45r.10. This uses the specified working drawing labels, not a discovered native alphabet.',
    'native_primary': 'experiments/yolo/gdt1198_daldy_exact_contexts/REPORT.md',
    'limits': ['No source encoding, frequency test, new manuscript count/image or meaning.',
               'The exact twelve-word grouping has not been executed by GDT1176/1177; their lists differ.',
               'Different carriers and prefix grouping as a family are not refuted.',
               'No automatic carrier, grouping-list, source or threshold repair.'],
    'review': 'Root proof; bounded producer independently read the raw rule and confirmed the terminal argument without data queries. Same-author code is a finite primitive check, not an independent manuscript reading.',
}
(D / 'HAND_WRITER_IDEA936_TERMINAL_RESULT_20261005.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ('status', 'source_character_codes', 'prefix_codes', 'possible_primitive_terminal_signs')}))
