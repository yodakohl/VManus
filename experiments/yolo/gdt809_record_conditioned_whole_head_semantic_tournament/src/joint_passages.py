#!/usr/bin/env python3
"""Two explicit, token-preserving working readings of four admitted paragraphs.

No learned gloss is evidence for another gloss. All raw transcription access
goes through the repository's selector-before-materialization command.
"""
from __future__ import annotations

import argparse
from collections import Counter
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
SRC = BASE / 'src'
MODELS = {'D': 'Pflanzenteile mit Eigenschaften und Graden',
          'R': 'Zutaten mit Zuständen und Mengen'}
OUTPUTS = ('JOINT_4_PARAGRAPH_LINES.tsv', 'JOINT_TOKEN_READINGS.tsv',
           'JOINT_COMMON_DICTIONARY.tsv', 'JOINT_REPEAT_AND_SCOPE_PROBES.tsv',
           'JOINT_PREDICTION_SCORECARD.tsv', 'JOINT_BOUNDARY_READING.tsv',
           'JOINT_GUARDED_QUERY_STATS.json', 'JOINT_COMPETING_PARAGRAPH_READINGS.md',
           'JOINT_GDT388_RELATION_PACKET.tsv', 'JOINT_GDT388_EDGE_INTAKE.json')


def read(path):
    with path.open(encoding='utf-8', newline='') as handle:
        return list(csv.DictReader(handle, delimiter='\t'))


def write(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0])
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def query(path, pages, columns):
    command = [str(ROOT / 'vmanus-exp'), 'query-tsv', path, '--selector', 'page']
    for page in pages:
        command += ['--allow', page]
    command += ['--columns', ','.join(columns), '--forbid-prefix', 'f84', '--forbid-prefix', 'f84r']
    done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    stats = [json.loads(s[len('GUARD_STATS '):]) for s in done.stderr.splitlines() if s.startswith('GUARD_STATS ')]
    if len(stats) != 1:
        raise RuntimeError('Missing guarded query audit')
    return list(csv.DictReader(io.StringIO(done.stdout), delimiter='\t')), {
        'source': path, 'allow': pages, 'columns': columns, 'stats': stats[0]}


def positions(tokens, pattern):
    return [i for i in range(len(tokens) - len(pattern) + 1) if tokens[i:i + len(pattern)] == pattern]


def load():
    specs = read(SRC / 'JOINT_PARAGRAPH_SPECS.tsv')
    pages = sorted({s['page'] for s in specs})
    allowed = {r['page'] for r in read(ROOT / 'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv')}
    if not set(pages) <= allowed or any(p.startswith('f84') for p in pages):
        raise RuntimeError('Paragraph scope exceeds inherited allow-list')
    raw, ls = query('transcription/voynich_zl3b_lines.tsv', pages,
                    ['page', 'locus', 'line_number', 'paragraph_start', 'paragraph_end', 'section', 'language', 'hand', 'eva_clean'])
    cross, cs = query('transcription/voynich_cross_transcription_lines.tsv', pages,
                      ['page', 'locus', 'zl3b_clean', 'it2a_clean', 'rf1b_clean'])
    cross = {(r['page'], r['locus']): r for r in cross}
    result = []
    for spec in specs:
        selected = sorted((r for r in raw if r['page'] == spec['page'] and
                           int(spec['first_line']) <= int(r['line_number']) <= int(spec['last_line'])),
                          key=lambda r: int(r['line_number']))
        if not selected or selected[0]['paragraph_start'] != '1' or selected[-1]['paragraph_end'] != '1':
            raise RuntimeError('Selection is not a complete paragraph')
        if any(r['paragraph_start'] == '1' for r in selected[1:]) or any(r['paragraph_end'] == '1' for r in selected[:-1]):
            raise RuntimeError('Nested paragraph boundary')
        if len(selected) != int(spec['last_line']) - int(spec['first_line']) + 1:
            raise RuntimeError('Paragraph line gap')
        for r in selected:
            c = cross[r['page'], r['locus']]
            if c['zl3b_clean'] != r['eva_clean']:
                raise RuntimeError('ZL line/cross mismatch')
            result.append({'paragraph_id': spec['paragraph_id'], **r,
                           'it2a_clean': c['it2a_clean'], 'rf1b_clean': c['rf1b_clean'],
                           'whole_line_all_three_exact': int(r['eva_clean'] == c['it2a_clean'] == c['rf1b_clean']),
                           'token_count': len(r['eva_clean'].split()), 'confirmed_plaintext': 0})
    if len(result) != 17:
        raise RuntimeError('Selected paragraph census drift')
    return specs, result, [ls, cs]


def render(lines, lexicon):
    lex = {r['surface']: r for r in lexicon}
    rows, readings = [], {}
    phrases = {
        'D': {('chor', 'chol', 'daiin'): 'Blütenstand: trocken im dritten Grad?',
              ('cthy', 'oltchy'): 'Blattgut: kalt und trocken?',
              ('otshy', 'okaiin'): 'kalt-feuchte Zubereitung?'},
        'R': {('chor', 'chol', 'daiin'): 'getrocknete Blüten, drei Portionen?',
              ('cthy', 'oltchy'): 'Blattzutat: kalt und trocken?',
              ('otshy', 'okaiin'): 'kalt-feuchte Zubereitung?'}}
    for model in MODELS:
        for line in lines:
            words = line['eva_clean'].split()
            other = [line[k].split() for k in ('it2a_clean', 'rf1b_clean')]
            ranks, rendered = Counter(), []
            i = 0
            while i < len(words):
                selected = next((p for p in phrases[model] if tuple(words[i:i + len(p)]) == p), None)
                if selected:
                    count = len(selected)
                    display = phrases[model][selected]
                    kind = 'CONDITIONAL_WORKING_SPAN'
                elif words[i] in lex:
                    count = 1
                    display = lex[words[i]]['descriptive_de' if model == 'D' else 'recipe_de']
                    kind = 'EXPLORATORY_EXACT_WHOLE'
                else:
                    count = 1
                    while i + count < len(words) and words[i + count] not in lex:
                        count += 1
                    display = '[' + ' '.join(words[i:i + count]) + ']'
                    kind = 'UNRESOLVED_EVA'
                rendered.append(display)
                group_id = f"{model}:{line['locus']}:{i + 1}"
                for j in range(i, i + count):
                    word = words[j]
                    ranks[word] += 1
                    item = lex.get(word)
                    rows.append({'model': model, 'paragraph_id': line['paragraph_id'], 'page': line['page'],
                                 'locus': line['locus'], 'token_index': j + 1, 'surface': word,
                                 'rank_stable_all_three': int(all(reader.count(word) >= ranks[word] for reader in other)),
                                 'dictionary_covered': int(item is not None),
                                 'confidence': item['confidence'] if item else 'UNKNOWN',
                                 'provenance': item['provenance'] if item else 'NONE',
                                 'render_group': group_id, 'group_first': int(j == i),
                                 'render_text_de': display if j == i else 'CONSUMED_BY_PREVIOUS',
                                 'render_kind': kind, 'hypothesis_not_translation': 1,
                                 'confirmed_lexeme': 0, 'component_export_credit': 0})
                i += count
            readings[model, line['locus']] = '; '.join(rendered)
    return rows, readings


def probes(lines, specs):
    rows = []
    for spec in specs:
        for line in lines:
            words = line['eva_clean'].split()
            readers = [line[k].split() for k in ('eva_clean', 'it2a_clean', 'rf1b_clean')]
            pattern = spec['pattern'].split()
            hits = []
            if spec['kind'] == 'CONTIGUOUS':
                hits = [(i, i + len(pattern), 'EXACT_CONTIGUOUS_WORDS') for i in positions(words, pattern)]
            elif spec['kind'] == 'REPEATED_WITH_GAP':
                found = positions(words, pattern)
                if len(found) >= 2:
                    hits = [(found[0], found[-1] + 1, 'SAME_WHOLE_REPEATS_NOT_SAME_REFERENT')]
            elif spec['kind'] == 'ALTERNATING_VALUE':
                value = pattern[0]
                hits = [(i, i + 4, 'TWO_HEAD_VALUE_WINDOWS') for i in range(len(words) - 3)
                        if words[i + 1] == words[i + 3] == value
                        and words[i] != words[i + 2] and words[i] != value and words[i + 2] != value]
            else:
                raise RuntimeError('Unimplemented joint probe')
            for start, stop, basis in hits:
                span = words[start:stop]
                if spec['kind'] == 'REPEATED_WITH_GAP':
                    support = [int(reader.count(pattern[0]) >= 2) for reader in readers]
                else:
                    support = [int(bool(positions(reader, span))) for reader in readers]
                rows.append({'probe_event_id': f'JPE{len(rows) + 1:03d}', 'probe_id': spec['probe_id'],
                             'paragraph_id': line['paragraph_id'], 'page': line['page'], 'locus': line['locus'],
                             'start_token': start + 1, 'end_token': stop, 'written_span': ' '.join(span),
                             'support_basis': basis, 'zl3b_support': support[0], 'it2a_support': support[1],
                             'rf1b_support': support[2], 'readings_supporting': sum(support),
                             'baseline_status': spec['baseline_status'], 'inference_limit': spec['inference_limit'],
                             'independent_manuscripts': 1, 'semantic_discriminator_credit': 0})
    return rows


def boundary_reading(lines):
    line = next(r for r in lines if r['locus'] == 'f32v.8')
    rows = []
    for reader, col in [('ZL3b', 'eva_clean'), ('IT2a', 'it2a_clean'), ('RF1b', 'rf1b_clean')]:
        tokens = line[col].split()
        matches = []
        for pattern in [('daiin', 'ctho', 'daiin', 'qotaiin'), ('daiin', 'cthodaiin', 'qotaiin')]:
            for i in positions(tokens, list(pattern)):
                matches.append((i, pattern))
        if len(matches) != 1:
            raise RuntimeError('Ambiguous local boundary witness')
        i, pattern = matches[0]
        inner = pattern[1:-1]
        rows.append({'page': 'f32v', 'locus': 'f32v.8', 'reader': reader,
                     'left_anchor': pattern[0], 'inner_written': ' '.join(inner), 'right_anchor': pattern[-1],
                     'inner_without_spaces': ''.join(inner), 'word_count': len(inner),
                     'interpretation': 'ALTERNATE_READER_BOUNDARY_OF_ONE_MANUSCRIPT_SPAN',
                     'component_meaning_export': 0})
    if len({r['inner_without_spaces'] for r in rows}) != 1:
        raise RuntimeError('Boundary forms differ beyond whitespace')
    return rows


def scorecard(events, specs):
    consequences = {
        'J01': ('supports trying a coordinated organ list', 'supports trying a coordinated ingredient list'),
        'J02': ('dry quality plus third degree remains compatible', 'dried ingredient plus three portions remains compatible; unit unspecified'),
        'J03': ('needs repeated fields or another repetition/scope rule', 'needs repeated fields or another repetition/scope rule; not two proven operations'),
        'J04': ('needs two value-bearing fields or a writing convention', 'needs two value-bearing fields or a writing convention; values cannot be summed'),
        'J05': ('repeat can name two entries or refer back', 'repeat can name two ingredients or resume one preparation; identity unresolved'),
        'J06': ('two head-degree fields are compatible if heads are quality-bearing', 'two ingredient-amount fields are compatible if heads name ingredients'),
        'J07': ('ordered property fields or repeated entries remain possible', 'alternating states do not establish a sequence of operations')}
    result = []
    for spec in specs:
        matches = [r for r in events if r['probe_id'] == spec['probe_id']]
        for idx, model in enumerate(MODELS):
            result.append({'probe_id': spec['probe_id'], 'model': model, 'observed_events': len(matches),
                           'all_three_support_events': sum(r['readings_supporting'] == 3 for r in matches),
                           'interpretive_consequence': consequences[spec['probe_id']][idx],
                           'observational_decision': 'COMPATIBLE_OR_ADDITIONAL_SCOPE_NEEDED' if matches else 'NO_SELECTED_EVENT',
                           'distinguishes_literal_models': 0, 'selection_credit': 0,
                           'reason': 'Written-pattern observations alone do not identify organs, degree, quantity or operations'})
    return result


def relation_intake(events, output):
    # GDT388 is an image-relation acquisition gate. These are deliberately
    # declared as already observed text relations and receive no image credit.
    fields = ('edge_id batch_id page physical_folio diagram_unit_id pivot_visual_id pivot_locus target_visual_id '
              'target_locus relation_type direction_basis ownership_basis geometry_only_selection source_manifest_id '
              'page_crop_sha256 pivot_crop_sha256 target_crop_sha256 source_aware_localizer relation_reviewer '
              'relation_confidence ambiguity_state formal_access_state fold_assignment eligibility_status').split()
    rows = []
    for event in events:
        page = event['page']
        rows.append(dict(zip(fields, [event['probe_event_id'], 'GDT809_PARAGRAPH_TEXT', page, page[:-1],
                    event['paragraph_id'], 'TEXT_START', f"{event['locus']}@{event['start_token']}",
                    'TEXT_END', f"{event['locus']}@{event['end_token']}", 'FORMAL_WRITTEN_SPAN',
                    'OBSERVED_TRANSCRIPTION_ORDER', 'TEXT_NOT_IMAGE_OWNERSHIP', 'FALSE', 'GDT809',
                    'NONE', 'NONE', 'NONE', 'GUARDED_TEXT_READER', 'ROOT_REVIEW', 'TEXT_ONLY',
                    'NOT_VISUAL_RELATION', 'FORMAL_ACCESSED', 'FOUR_EXISTING_PARAGRAPHS', 'INELIGIBLE_TEXT_RELATION'])))
    packet = output / 'JOINT_GDT388_RELATION_PACKET.tsv'
    write(packet, rows, fields)
    done = subprocess.run([str(ROOT / 'vmanus-exp'), 'check-edge-packet', str(packet)], cwd=ROOT,
                          text=True, capture_output=True)
    result = json.loads(done.stdout)
    if done.returncode != 1 or result['score_ready'] or result['eligible_edges'] != 0:
        raise RuntimeError('Joint text relations unexpectedly received visual-edge credit')
    expected = [f'edge row {i + 2}: formal access is not sealed' for i in range(len(rows))]
    if result['errors'] != expected:
        raise RuntimeError('Unexpected relation intake error: ' + str(result['errors']))
    (output / 'JOINT_GDT388_EDGE_INTAKE.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result


def reader_document(specs, lines, lexicon, readings, events, tokens):
    text = ['# GDT809 – vier vollständige Absätze, zwei Arbeitslesarten', '',
            'Die EVA-Absätze sind vollständig. Die deutschen Fassungen sind ausdrücklich hypothetische Teilübersetzungen. '
            'Unaufgelöste Wörter bleiben in eckigen Klammern sichtbar; keine Lücke wird durch eine erfundene Handlung verdeckt. '
            'Auch ausgeschriebene deutsche Wörter sind Arbeitsannahmen. Die beiden Modelle erklären die Schrift noch nicht.', '',
            'D: Pflanzenteile mit Eigenschaften und Graden. R: Zutaten mit Zuständen und Mengen. '
            '„Trocken“ als humoral gedachte Eigenschaft und „getrocknet“ als Zustand sind verschiedene Annahmen. '
            'Keines davon bedeutet automatisch „trockne“. Blatt/Kraut sowie Blüte/Frucht bleiben austauschbare Identitätsrivalen.', '',
            'Die Ankerzeilen stammen aus GDT625/GDT629/GDT759/GDT768. Die neue Arbeit stellt ihre vollständigen Absätze, '
            'offenen Nachbarn, Leserunterschiede und gemeinsamen Annahmen nebeneinander; bekannte Muster werden nicht erneut als Entdeckung gezählt.', '']
    for spec in specs:
        selected = [r for r in lines if r['paragraph_id'] == spec['paragraph_id']]
        text += [f"## {spec['paragraph_id']} – {spec['page']}.{spec['first_line']}–{spec['last_line']}", '', '```text']
        text += [r['locus'] + '  ' + r['eva_clean'] for r in selected]
        text += ['```', '']
        for model, title in MODELS.items():
            text += [f'### {model}: {title}', '']
            text += [r['locus'] + ': ' + readings[model, r['locus']] + '\n' for r in selected]
        relevant = [r for r in events if r['paragraph_id'] == spec['paragraph_id']]
        text += ['### Schriftliche Befunde und offene Bindungen', '']
        for e in relevant:
            text += [f"- `{e['locus']} {e['written_span']}`: {e['readings_supporting']}/3 alternative Lesungen tragen das angegebene Muster. {e['inference_limit']}"]
        text += ['', 'Die Alternativlesungen betreffen dasselbe Manuskript. Wortzählung, Wortgrenze und ganze Zeile werden getrennt geprüft.', '']
    text += ['## Gemeinsames kleines Wörterbuch', '',
             'Alle Bedeutungen haben niedrige oder sehr niedrige, nicht numerisch kalibrierte Sicherheit. '
             'Die vollständige Evidenz, Gegenlesart und Herkunft stehen in JOINT_COMMON_DICTIONARY.tsv.', '',
             '| Ganzform | Arbeitsbedeutung | D | R |', '|---|---|---|---|']
    for r in lexicon:
        text += [f"| `{r['surface']}` | {r['working_default_de']} | {r['descriptive_de']} | {r['recipe_de']} |"]
    first = [r for r in tokens if r['model'] == 'D']
    covered = sum(r['dictionary_covered'] for r in first)
    text += ['', f'Das kleine Wörterbuch belegt {covered}/{len(first)} Tokenpositionen mit einer Hypothese. '
             'Diese Abdeckung misst weder Richtigkeit noch Übersetzungsqualität.', '',
             '## Konkrete Kompositionsfrage', '',
             'An f32v.8 steht im gleichen örtlichen Rahmen bei ZL3b/IT2a `daiin [ctho daiin] qotaiin`, '
             'bei RF1b `daiin [cthodaiin] qotaiin`. Die innere Zeichenfolge bleibt nach Weglassen der Leerzeichen gleich. '
             'Das stützt die Prüfung einer gemeinsamen Ausdrucksgrenze. Es identifiziert weder `ctho` noch eine Blattwurzel `cth`.', '',
             'An f32v.9 folgt dagegen `chocthy daiin cthaiin daiin`. Ein Modell muss erklären, weshalb die beiden '
             'unterschiedlichen Ganzformen jeweils dieselbe folgende Form tragen. Zutaten mit Mengen und Eigenschaften '
             'mit Graden bleiben dafür beide mögliche Arbeitslesarten; die innere Form `cthaiin` wird nicht stillschweigend zerlegt.', '',
             '## Was diese Runde verändert', '',
             'Die Arbeitslesung führt konkrete Nomen und Zustände weiter, legt jedoch die bisher überglätteten '
             'Bindungen offen. Wiederholte Wörter bleiben wiederholt; gleiches Wort bedeutet nicht zwangsläufig gleicher '
             'Gegenstand. Die Bedeutung von Grad, Menge, Eigenschaft und Arbeitsvorgang bleibt lokal eine ausdrückliche '
             'Modellentscheidung. Kein Modell gewinnt aus den hier beobachteten Schriftmustern allein eine Organ- oder Einheitenidentität.', '']
    return '\n'.join(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, default=BASE / 'artifacts')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if not output.is_relative_to(ROOT):
        raise RuntimeError('Outputs must stay inside repository')
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((BASE / 'experiment.json').read_text())
    bindings = {r['path']: r['sha256'] for collection in ('inputs', 'outputs') for r in manifest[collection]}
    required = [SRC / name for name in ('joint_passages.py', 'JOINT_PARAGRAPH_SPECS.tsv',
                                       'JOINT_LEXICON_SPECS.tsv', 'JOINT_PROBE_SPECS.tsv')]
    for path in required:
        if bindings.get(path.relative_to(ROOT).as_posix()) != digest(path):
            raise RuntimeError('Unbound joint source: ' + path.name)
    specs, lines, query_stats = load()
    lexicon = read(SRC / 'JOINT_LEXICON_SPECS.tsv')
    probe_specs = read(SRC / 'JOINT_PROBE_SPECS.tsv')
    tokens, readings = render(lines, lexicon)
    events = probes(lines, probe_specs)
    boundary = boundary_reading(lines)
    write(output / 'JOINT_4_PARAGRAPH_LINES.tsv', lines)
    write(output / 'JOINT_TOKEN_READINGS.tsv', tokens)
    write(output / 'JOINT_COMMON_DICTIONARY.tsv', lexicon)
    write(output / 'JOINT_REPEAT_AND_SCOPE_PROBES.tsv', events)
    write(output / 'JOINT_PREDICTION_SCORECARD.tsv', scorecard(events, probe_specs))
    write(output / 'JOINT_BOUNDARY_READING.tsv', boundary)
    (output / 'JOINT_GUARDED_QUERY_STATS.json').write_text(json.dumps(query_stats, indent=2, sort_keys=True) + '\n')
    (output / 'JOINT_COMPETING_PARAGRAPH_READINGS.md').write_text(
        reader_document(specs, lines, lexicon, readings, events, tokens), encoding='utf-8')
    intake = relation_intake(events, output)
    result = {'experiment_id': 'GDT809', 'joint_status': 'TWO_WORKING_READINGS__IDENTITIES_UNRESOLVED',
              'paragraphs': len(specs), 'lines': len(lines), 'tokens_per_model': len(tokens) // len(MODELS),
              'models': MODELS, 'dictionary_entries': len(lexicon), 'probe_events': len(events),
              'three_reading_supported_probe_events': sum(e['readings_supporting'] == 3 for e in events),
              'hypothesis_covered_tokens_per_model': sum(r['dictionary_covered'] for r in tokens if r['model'] == 'D'),
              'boundary_readings': len(boundary), 'confirmed_lexemes': 0, 'component_exports': 0,
              'new_manuscript_pages': 0, 'edge_score_ready': intake['score_ready'],
              'sealed_data': {'f84': 'FORBIDDEN', 'f84r': 'FORBIDDEN'},
              'artifact_sha256': {name: digest(output / name) for name in OUTPUTS}}
    (output / 'JOINT_RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'artifact_sha256'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
