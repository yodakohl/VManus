"""Small reproducibility check of bounded historical extraction, not meaning."""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
spec = importlib.util.spec_from_file_location('ae_extract', HERE / 'AE_EXTRACT.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
packet = json.loads((HERE / 'AE_COMPLETE_SOURCES.json').read_text())
checks = {}
checks['reproducible_complete_packet'] = module.build() == packet
expected = {
    'pliny': 'fa8df17459830172d8f7551033db38e78bc99b38079d49ee2e280d5919e14505',
    'dioscorides': 'e2a2175c5ca1c1a2313c5816bc79c7fa1c9103766fcad193356d0c13ce6746bc',
    'isidore': '9c4bc02054177fb5e2a68a0e1f69f7a9739754af85cafe88405d3245e2d5672b',
}
for key, digest in expected.items():
    source = packet[key]['source']
    checks[key + '_input_hash'] = hashlib.sha256(
        (ROOT / source['path']).read_bytes()).hexdigest() == source['sha256'] == digest
checks['pliny_whole_unit_and_apparatus'] = (
    len(packet['pliny']['paragraphs']) == 3 and
    set(packet['pliny']['editorial_notes']) == {str(n) for n in range(2596, 2613)})
chapters = packet['dioscorides']['chapters']
checks['two_complete_greek_units'] = set(chapters) == {'190', '191'} and all(
    len(c['paragraphs']) == 2 and c['original_xml'] for c in chapters.values())
checks['greek_after_apparatus_not_lost'] = chapters['190']['paragraphs'][1].endswith(
    'κινεῖ δὲ καὶ ἔμμηνα καὶ ἔμβρυα λεῖα προστεθέντα.')
checks['distinct_leaf_and_flower_clauses'] = all(s in chapters['190']['paragraphs'][0]
    for s in ('συμπεριτρέπεσθαι τὰ φύλλα', 'ἄνθος λευκόν, ὑποπόρφυρον'))
checks['latin_ending_and_editorial_marker'] = (
    packet['isidore']['latin'].endswith('vel in cataplasmate posita abstergat.') and
    packet['isidore']['editorial_poor_reading'] == ['eo'])
checks['latin_naming_alternation_preserved'] = 'floreat, vel quod' in packet['isidore']['latin']
checks['latin_subject_not_rewritten_as_flower'] = 'idem se reclaudit' in packet['isidore']['latin']
checks['greek_attribution_and_sharealike_retained'] = 'CC BY-SA4.0' in packet['dioscorides']['source']['license_note']
out = dict(status='PASS' if all(checks.values()) else 'FAIL', checks=checks,
           claim_ceiling='Historical input/extraction integrity only; no target test or semantic confirmation.')
(HERE / 'AE_VALIDATION.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(dict(status=out['status'], passed=sum(checks.values()), total=len(checks))))
raise SystemExit(0 if all(checks.values()) else 1)
