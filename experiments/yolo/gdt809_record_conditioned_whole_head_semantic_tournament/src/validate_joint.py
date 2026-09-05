#!/usr/bin/env python3
"""Independent source, alignment, repetition and boundary audit of joint reader."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'AGENTS.md').is_file())
BASE = Path(__file__).resolve().parent.parent
SRC, ART = BASE / 'src', BASE / 'artifacts'


def read(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def query(source, pages, columns):
    command = [str(ROOT / 'vmanus-exp'), 'query-tsv', source, '--selector', 'page']
    for page in pages:
        command.extend(['--allow', page])
    command += ['--columns', columns, '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    return list(csv.DictReader(io.StringIO(result.stdout), delimiter='\t'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-write', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=ART)
    args = parser.parse_args()
    artifacts = args.output_dir.resolve()
    checks = []

    def check(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    result = json.loads((artifacts / 'JOINT_RESULT.json').read_text())
    check('claim ceiling', result['confirmed_lexemes'] == result['component_exports'] == result['new_manuscript_pages'] == 0)
    check('explicit seals', result['sealed_data'] == {'f84': 'FORBIDDEN', 'f84r': 'FORBIDDEN'})
    check('artifact checksums', all(hashlib.sha256((artifacts / name).read_bytes()).hexdigest() == value
                                     for name, value in result['artifact_sha256'].items()))
    specs = read(SRC / 'JOINT_PARAGRAPH_SPECS.tsv')
    pages = sorted({r['page'] for r in specs})
    allowed = {r['page'] for r in read(ROOT / 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv')}
    check('scope', len(specs) == 4 and set(pages) <= allowed and not any(p.startswith('f84') for p in pages))
    raw = query('transcription/voynich_zl3b_lines.tsv', pages,
                'page,locus,line_number,paragraph_start,paragraph_end,section,language,hand,eva_clean')
    cross = {r['locus']: r for r in query('transcription/voynich_cross_transcription_lines.tsv', pages,
                                        'page,locus,zl3b_clean,it2a_clean,rf1b_clean')}
    selected = []
    for spec in specs:
        group = sorted((r for r in raw if r['page'] == spec['page'] and
                        int(spec['first_line']) <= int(r['line_number']) <= int(spec['last_line'])),
                       key=lambda r: int(r['line_number']))
        check('full paragraph ' + spec['paragraph_id'], group[0]['paragraph_start'] == group[-1]['paragraph_end'] == '1'
              and not any(r['paragraph_start'] == '1' for r in group[1:])
              and not any(r['paragraph_end'] == '1' for r in group[:-1])
              and len(group) == int(spec['last_line']) - int(spec['first_line']) + 1)
        for r in group:
            selected.append({**r, 'paragraph_id': spec['paragraph_id']})
    lines = read(artifacts / 'JOINT_4_PARAGRAPH_LINES.tsv')
    by_locus = {r['locus']: r for r in lines}
    check('17 source lines', len(lines) == len(selected) == 17 and len(by_locus) == 17)
    check('complete source parity', all(all(by_locus[r['locus']][k] == v for k, v in r.items()) for r in selected))
    check('alternate lines and exactness', all(r['it2a_clean'] == cross[r['locus']]['it2a_clean']
          and r['rf1b_clean'] == cross[r['locus']]['rf1b_clean']
          and int(r['whole_line_all_three_exact']) == int(r['eva_clean'] == r['it2a_clean'] == r['rf1b_clean']) for r in lines))
    lexicon = read(SRC / 'JOINT_LEXICON_SPECS.tsv')
    lex = {r['surface']: r for r in lexicon}
    check('common dictionary source parity', read(artifacts / 'JOINT_COMMON_DICTIONARY.tsv') == lexicon and len(lex) == len(lexicon) == 16)
    tokens = read(artifacts / 'JOINT_TOKEN_READINGS.tsv')
    token_count = sum(len(r['eva_clean'].split()) for r in selected)
    check('two token-complete readers', len(tokens) == token_count * 2 == result['tokens_per_model'] * 2)
    grouped = defaultdict(list)
    for r in tokens:
        grouped[r['model'], r['locus']].append(r)
    check('model line cross product', set(grouped) == {(m, r['locus']) for m in ('D', 'R') for r in selected})
    for (model, locus), rows in grouped.items():
        words = by_locus[locus]['eva_clean'].split()
        check('token conservation ' + model + ':' + locus,
              [int(r['token_index']) for r in rows] == list(range(1, len(words) + 1))
              and [r['surface'] for r in rows] == words)
        ranks = Counter()
        for r in rows:
            word = r['surface']
            ranks[word] += 1
            expected_stable = all(by_locus[locus][c].split().count(word) >= ranks[word] for c in ('it2a_clean', 'rf1b_clean'))
            if int(r['rank_stable_all_three']) != int(expected_stable):
                raise AssertionError('token rank status')
            if int(r['dictionary_covered']) != int(word in lex):
                raise AssertionError('dictionary coverage')
    render_groups = defaultdict(list)
    for r in tokens:
        render_groups[r['render_group']].append(r)
    check('every span emitted once', all(sum(int(r['group_first']) for r in group) == 1
           and group[0]['group_first'] == '1'
           and all(r['render_text_de'] == 'CONSUMED_BY_PREVIOUS' for r in group[1:]) for group in render_groups.values()))
    check('unresolved text conserved', all(g[0]['render_text_de'] == '[' + ' '.join(r['surface'] for r in g) + ']'
           for g in render_groups.values() if g[0]['render_kind'] == 'UNRESOLVED_EVA'))
    check('no lexical export in tokens', all(r['confirmed_lexeme'] == r['component_export_credit'] == '0' for r in tokens))
    covered = sum(r['surface'] in lex for r in tokens if r['model'] == 'D')
    check('coverage result', covered == result['hypothesis_covered_tokens_per_model'])
    probe_specs = read(SRC / 'JOINT_PROBE_SPECS.tsv')
    expected = []
    for spec in probe_specs:
        for r in selected:
            words = r['eva_clean'].split()
            pattern = spec['pattern'].split()
            intervals = []
            if spec['kind'] == 'CONTIGUOUS':
                intervals = [(i, i + len(pattern)) for i in range(len(words) - len(pattern) + 1)
                             if words[i:i + len(pattern)] == pattern]
            elif spec['kind'] == 'REPEATED_WITH_GAP':
                found = [i for i, w in enumerate(words) if w == pattern[0]]
                if len(found) >= 2:
                    intervals = [(found[0], found[-1] + 1)]
            else:
                for i in range(len(words) - 3):
                    a, v, b, w = words[i:i + 4]
                    if v == w == pattern[0] and len({a, b, v}) == 3:
                        intervals.append((i, i + 4))
            for lo, hi in intervals:
                span = words[lo:hi]
                support = []
                for column in ('zl3b_clean', 'it2a_clean', 'rf1b_clean'):
                    reader = cross[r['locus']][column].split()
                    if spec['kind'] == 'REPEATED_WITH_GAP':
                        support.append(int(reader.count(pattern[0]) >= 2))
                    else:
                        support.append(int(any(reader[j:j + len(span)] == span for j in range(len(reader) - len(span) + 1))))
                expected.append((spec['probe_id'], r['locus'], lo + 1, hi, ' '.join(span), *support))
    actual = read(artifacts / 'JOINT_REPEAT_AND_SCOPE_PROBES.tsv')
    check('all probe coordinates and reader support',
          [(r['probe_id'], r['locus'], int(r['start_token']), int(r['end_token']), r['written_span'],
            int(r['zl3b_support']), int(r['it2a_support']), int(r['rf1b_support'])) for r in actual] == expected)
    check('probe result census', len(actual) == result['probe_events'] and
          sum(r['readings_supporting'] == '3' for r in actual) == result['three_reading_supported_probe_events'])
    cards = read(artifacts / 'JOINT_PREDICTION_SCORECARD.tsv')
    check('no semantic winner inferred from patterns', len(cards) == len(probe_specs) * 2
          and all(r['selection_credit'] == r['distinguishes_literal_models'] == '0' for r in cards))
    counts = Counter(r['probe_id'] for r in actual)
    exact_counts = Counter(r['probe_id'] for r in actual if r['readings_supporting'] == '3')
    check('scorecard observations', all(int(r['observed_events']) == counts[r['probe_id']]
          and int(r['all_three_support_events']) == exact_counts[r['probe_id']] for r in cards))
    boundary = read(artifacts / 'JOINT_BOUNDARY_READING.tsv')
    check('local boundary comparison', len(boundary) == 3 and
          [r['inner_written'] for r in boundary] == ['ctho daiin', 'ctho daiin', 'cthodaiin']
          and all(r['inner_without_spaces'] == 'cthodaiin' and r['component_meaning_export'] == '0' for r in boundary))
    check('boundary source flanks', all(' '.join([r['left_anchor'], r['inner_written'], r['right_anchor']])
          in cross['f32v.8'][{'ZL3b': 'zl3b_clean', 'IT2a': 'it2a_clean', 'RF1b': 'rf1b_clean'}[r['reader']]]
          for r in boundary))
    packet = artifacts / 'JOINT_GDT388_RELATION_PACKET.tsv'
    intake = subprocess.run([str(ROOT / 'vmanus-exp'), 'check-edge-packet', str(packet)], cwd=ROOT, capture_output=True, text=True)
    parsed = json.loads(intake.stdout)
    check('GDT388 independent intake', intake.returncode == 1 and parsed == json.loads((artifacts / 'JOINT_GDT388_EDGE_INTAKE.json').read_text())
          and parsed['eligible_edges'] == 0 and parsed['score_ready'] is False and parsed['packet_rows'] == len(actual))
    doc = (artifacts / 'JOINT_COMPETING_PARAGRAPH_READINGS.md').read_text()
    check('all paragraph lines in reader document', all(r['eva_clean'] in doc for r in lines))
    check('all model lines in reader document', all('; '.join(r['render_text_de'] for r in group if r['group_first'] == '1') in doc
                                                  for group in grouped.values()))
    report = {'experiment_id': 'GDT809', 'status': 'PASS', 'checks_passed': len(checks), 'checks': checks,
              'paragraphs': 4, 'lines': 17, 'tokens_per_model': token_count, 'confirmed_lexemes': 0}
    if not args.no_write:
        (artifacts / 'JOINT_VALIDATION.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
