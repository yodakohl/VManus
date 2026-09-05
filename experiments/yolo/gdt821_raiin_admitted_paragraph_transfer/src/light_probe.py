#!/usr/bin/env python3
"""One post-reading physical-lightness rival on the identical GDT821 context."""
import argparse
import csv
import io
import json
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent


def build():
    spec = json.loads((EXP / 'src/LIGHT_TRIAL.json').read_text())
    assert spec['whole'] == 'raiin' and spec['gloss_de'] == 'leicht?'
    assert spec['sense'] == 'LOW_PHYSICAL_HEAVINESS_OF_A_CARRIER_NOT_SMALL_DOSE_MILDNESS_EASE_BRIGHTNESS_SPEED_OR_ASCENT'
    assert spec['sealed_data'] == ['f84', 'f84r'] and not spec['meanings_validated']
    with (EXP / spec['base_trial']).open() as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    replacements = 0
    for row in rows:
        words = json.loads(row['source_groups_json'])
        glosses = json.loads(row['literal_trial_json'])
        assert len(words) == len(glosses)
        for i, word in enumerate(words):
            if word == spec['whole']:
                assert glosses[i] == 'steigt?'
                glosses[i] = spec['gloss_de']; replacements += 1
        row['literal_trial_json'] = json.dumps(glosses, ensure_ascii=False)
        row['confidence'] = spec['confidence']
    assert len(rows) == 195 and replacements == 28
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader(); writer.writerows(rows)
    result = dict(experiment_id='GDT821', phase=spec['phase'], status='ONE_PHYSICAL_LIGHTNESS_RIVAL_NOT_TRANSLATION',
        context_loci=65, literal_rows=195, source_groups=1724, changed_exact_group_readings=replacements,
        new_admissions=0, new_image_inspections=0, dictionary_changed=False, meanings_validated=False,
        confirmed_lexemes=0, confirmed_plaintext_clauses=0, base_meanings_unchanged=True,
        forced_finite_predicate=False, referent_and_comparison_reference_unknown=True, sealed_data=['f84','f84r'])
    return {'LIGHT_TRIALS.tsv': output.getvalue(), 'LIGHT_RESULT.json': json.dumps(result, indent=2, sort_keys=True)+'\n'}


def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--check', action='store_true'); args=parser.parse_args()
    for name, content in build().items():
        path = EXP / 'artifacts' / name
        if args.check:
            assert path.read_text() == content, 'Replay differs: ' + name
        else:
            path.write_text(content)
    print('One physical-lightness rival reproduced on identical context; no meaning validated')


if __name__ == '__main__':
    main()
