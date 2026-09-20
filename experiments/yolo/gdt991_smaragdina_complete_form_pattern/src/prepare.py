#!/usr/bin/env python3
"""Source-only complete predictions, before new target pattern matching."""
import collections
import hashlib
import json
from pathlib import Path
import validate

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
P = 'experiments/yolo/gdt990_smaragdina_complete_role_frames/'

source = json.loads((ROOT / P / 'src/SOURCE.json').read_text())
rows = []
classes = {}
for variant, spec in source['variants'].items():
    for writer in source['writers']:
        stream = sum((validate.tree(c['tree'], writer, c['id']) for c in spec['clauses']), [])
        assert stream == spec['streams'][writer]
        names = {}
        signature = []
        for e in stream:
            k = (e['root'], e['role'])
            if k not in names:
                names[k] = len(names)
            signature.append(names[k])
        raw = json.dumps(signature, separators=(',', ':')).encode()
        digest = hashlib.sha256(raw).hexdigest()
        counts = collections.Counter(signature)
        row = dict(variant=variant, writer=writer, forms=len(stream), role_form_types=len(names),
                   repeated_role_form_types=sum(n > 1 for n in counts.values()),
                   singleton_role_form_types=sum(n == 1 for n in counts.values()),
                   equality_signature=signature, signature_sha256=digest,
                   full_prediction=[dict(root=e['root'], role=e['role'], clause=e['clause']) for e in stream])
        rows.append(row)
        classes.setdefault(digest, []).append(dict(variant=variant, writer=writer))
assert len(rows) == 24
pred = dict(source_patterns=rows, indistinguishable_equality_classes=classes,
            gloss_rivals_not_distinguished=['THELESM as secret versus treasure', 'semantic renamings with the same role-form equality pattern'])
(E / 'artifacts/SOURCE_PREDICTIONS.json').write_text(json.dumps(pred, indent=2) + '\n')
own = dict(original_source=P + 'src/SOURCE.json', original_cases=P + 'artifacts/INTERRUPTED_CASES.json.gz',
           paragraphs=source['input_paragraphs'], fixed_case_count=32376, new_pattern_cases=1980,
           source_variants=list(source['variants']), writers=source['writers'],
           limits=dict(pattern_seconds=5, factor_seconds=2, factor_nodes=100000,
                       external_pattern_seconds=10, reverse_seconds=10, shared_target_seconds=900, workers=24),
           stop_remaining_fraction=.9, preexisting_exposure=True,
           independent_meaning_confirmation_capacity=0, confirmed_translated_words=0,
           meaning_note='Full original-code factorization is required even for a conditional source reading; no fixed lexical values or unique inverse parsing claimed.')
(E / 'src/SOURCE.json').write_text(json.dumps(own, indent=2) + '\n')
print(json.dumps(dict(source_patterns=len(rows), equality_classes=len(classes), new_target_fits=0)))
