#!/usr/bin/env python3
"""Render explicitly authored hypotheses; no inference, decoder, fitting or new data."""
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]

def write_tsv(name, fields, rows):
    with (HERE / name).open('w') as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

def main():
    inp = json.loads((HERE / 'INPUT.json').read_text())
    source = ROOT / inp['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == inp['sha256']
    reread = []
    for block in re.findall(r'```text\n(.*?)```', source.read_text(), re.S):
        for line in block.strip().splitlines():
            locus, raw = line.split(None, 1)
            reread.append({'locus': locus, 'raw_line': raw, 'groups': raw.split()})
    assert reread == inp['lines']
    assert len(reread) == 17 and sum(len(x['groups']) for x in reread) == 145
    models = json.loads((HERE / 'MODELS.json').read_text())['models']
    inventory = defaultdict(list)
    for line in reread:
        for i, word in enumerate(line['groups'], 1):
            inventory[word].append(f"{line['locus']}:{i}")
    inv_rows = [{'form': w, 'count': len(loci), 'loci': ';'.join(loci)}
                for w, loci in sorted(inventory.items(), key=lambda z: (-len(z[1]), z[0]))]
    write_tsv('INVENTORY.tsv', ['form', 'count', 'loci'], inv_rows)
    scores = {}
    output_names = {'D0': ('READING_v01.md', 'ALIGNMENT_v01.tsv', 'LEXICON_v01.tsv'),
                    'D1': ('READING_v02.md', 'ALIGNMENT_v02.tsv', 'LEXICON_v02.tsv'),
                    'R1': ('RIVAL_v01.md', 'RIVAL_ALIGNMENT_v01.tsv', 'RIVAL_LEXICON_v01.tsv')}
    for name, model in models.items():
        lex = model['lexicon']
        md = [f'# {name}: vollständiger Rohumfang, partielle Hypothesenlesung\n',
              'Alle ausgeschriebenen Bedeutungen sind Annahmen. Keine bestätigte Übersetzung. '
              'Unaufgelöste Formen bleiben sichtbar; die Satzgliederung ist noch offen. '
              'Die zusammenhängenden Inhaltsfassungen und deren Grenzen stehen in REPORT.md.\n',
              '## Gemeinsame Regeln\n']
        md += [f'{i}. {r}' for i, r in enumerate(model['rules'], 1)]
        rows = []
        for line in reread:
            md += [f"\n## {line['locus']}\n", '`' + line['raw_line'] + '`\n',
                   '| Nr. | Ganze Gruppe | Hypothetische Lesung |\n|---:|---|---|']
            rendered = []
            for i, word in enumerate(line['groups'], 1):
                item = lex.get(word)
                meaning = item['meaning'] if item else f'[unaufgelöst: {word}]'
                rendered.append(meaning)
                md.append(f'| {i} | `{word}` | {meaning} |')
                rows.append({'locus': line['locus'], 'group_index': i, 'raw_group': word,
                             'hypothesis_meaning': meaning,
                             'rule_id': word if item else 'UNRESOLVED',
                             'supplied_words': 'Keine syntaktische Glättung in dieser Tabelle',
                             'uncertainty': item['origin'] if item else 'NO_MEANING_ASSIGNED'})
            md.append('\nWortfolge: ' + ' · '.join(rendered) + '\n')
        md_name, align_name, lex_name = output_names[name]
        (HERE / md_name).write_text('\n'.join(md))
        write_tsv(align_name, list(rows[0]), rows)
        lr = [{'form': w, 'reading_variant': 'ZL3b as displayed in GDT809',
               'meaning_hypothesis': lex[w]['meaning'], 'sense_trigger': 'same whole-form value everywhere',
               'grammar_rule': lex[w]['kind'], 'all_working_loci': ';'.join(inventory[w]),
               'counterexamples': 'See REPORT.md and CONSEQUENCES_v01.tsv; no independent validation'} for w in sorted(lex)]
        write_tsv(lex_name, list(lr[0]), lr)
        scores[name] = {'positions': len(rows), 'hypothesis_positions': sum(x['raw_group'] in lex for x in rows),
                        'unresolved_positions': sum(x['raw_group'] not in lex for x in rows),
                        'hypothesis_types': len(lex), 'interpretation_accuracy': None}
    result = {'status': 'PASS_SOURCE_AND_ALIGNMENT_ONLY', 'models': scores,
              'input_positions': 145, 'input_types': len(inventory),
              'repeated_types': sum(len(v) > 1 for v in inventory.values()),
              'confirmed_meanings': 0, 'held_pages_opened': False,
              'scientific_interpretation_validated': False}
    (HERE / 'VALIDATION.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
