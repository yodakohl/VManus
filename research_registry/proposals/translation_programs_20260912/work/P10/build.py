"""Render authored P10 hypotheses, conserve exposed source, enumerate consequences.
No decoder, fitting, segmentation search, or held-page access.
Run from repository root. Semantic truth is not validated by this script.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path('research_registry/proposals/translation_programs_20260912/work')
OUT = BASE / 'P10'

def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def table(name, rows, fields):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

source = json.loads((BASE / 'P09/INPUT.json').read_text())
assert hashlib.sha256(Path(source['source']).read_bytes()).hexdigest() == source['sha256']
lines = [x for x in source['lines'] if x['locus'].split('.')[0] in {'f32v', 'f29v'}]
assert len(lines) == 9
assert all(x['raw_line'].split() == x['groups'] for x in lines)
dump('INPUT.json', {**source, 'lines': lines, 'scope': 'Previously exposed f32v.7–11 and f29v.1–4 only; displayed ZL-framed groups'})

# Authored exact whole-form conjectures. No changes to legacy lexicons.
old = json.loads((BASE / 'P09/MODELS.json').read_text())['models']['D1']['lexicon']
keep = 'cthy chor shor chol daiin dain okaiin otshy oltchy s ar kooiin ol sho chy'.split()
base = {w: dict(old[w]) for w in keep}
for w, meaning in {
    'shy': 'feucht', 'cho': 'Inneres', 'otchol': 'trockener Anteil',
    'ctho': 'Pflanzenstoff', 'otchy': 'kalt', 'keol': 'Öl',
    'qotaiin': 'warum', 'shey': 'warum', 'qotchy': 'Antwort',
}.items():
    base[w] = {'meaning': meaning, 'origin': 'P10_authored_hypothesis_not_identified', 'certainty': 'HYPOTHESIS_ONLY'}

expanded = {w: dict(v) for w, v in base.items()}
for w, meaning in {
    'cfhy': 'Eigenart', 'skey': 'bestimmt', 'chocthy': 'innerer Pflanzenanteil',
    'cthaiin': 'äußerer Pflanzenanteil', 'odaiin': 'abweichender Grad',
    'taiin': 'Mischung', 'she': 'Eigenart', 'otey': 'bestimmt', 'sy': 'Wirkung',
}.items():
    expanded[w] = {'meaning': meaning, 'origin': 'P10_v02_added_semantic_assumption_not_evidence', 'certainty': 'HYPOTHESIS_ONLY'}
rival = {w: dict(v) for w, v in expanded.items()}
for w, meaning in {'qotaiin': 'hinsichtlich', 'shey': 'hinsichtlich', 'qotchy': 'hierzu'}.items():
    rival[w] = {'meaning': meaning, 'origin': 'P10_nominal_rival_marker_only_change', 'certainty': 'HYPOTHESIS_ONLY'}
models = {'D0': base, 'D1': expanded, 'R1': rival}
dump('MODELS.json', {'hypothetical_only': True, 'confirmed_meanings': 0, 'models': models,
    'roles': {'initial': 'Lehrer', 'qotaiin': 'Fragender', 'shey': 'Fragender', 'qotchy': 'Lehrer'},
    'rule': 'Each marker starts a segment through the next marker or paragraph end. No other speaker switches. R1 retains segments as exposition/topic/addendum, without speakers.'})

tokens = []
segments = []
for page in ['f32v', 'f29v']:
    role, sid = 'Lehrer', 0
    for line in [x for x in lines if x['locus'].startswith(page + '.')]:
        for i, word in enumerate(line['groups'], 1):
            if word in {'qotaiin', 'shey', 'qotchy'}:
                sid += 1
                role = 'Lehrer' if word == 'qotchy' else 'Fragender'
            tokens.append({'locus': line['locus'], 'position': i, 'word': word,
                           'segment': f'{page}:S{sid}', 'role': role})
assert len(tokens) == 79 and len({x['word'] for x in tokens}) == 57
for sid in dict.fromkeys(x['segment'] for x in tokens):
    ts = [t for t in tokens if t['segment'] == sid]
    segments.append({'id': sid, 'role': ts[0]['role'], 'start': f"{ts[0]['locus']}:{ts[0]['position']}",
                     'end': f"{ts[-1]['locus']}:{ts[-1]['position']}", 'words': [t['word'] for t in ts]})
dump('SEGMENTS.json', segments)

stats = {}
for model, lex in models.items():
    suffix = {'D0': 'v01', 'D1': 'v02', 'R1': 'rival_v01'}[model]
    rows = [{**t, 'role': t['role'] if model != 'R1' else 'Beschreibung',
             'meaning': lex[t['word']]['meaning'] if t['word'] in lex else f"⟦{t['word']}⟧",
             'status': 'HYPOTHESIS_ONLY' if t['word'] in lex else 'OPEN'} for t in tokens]
    table(f'ALIGNMENT_{suffix}.tsv', rows, ['locus', 'position', 'word', 'segment', 'role', 'meaning', 'status'])
    table(f'LEXICON_{suffix}.tsv', [dict(word=w, meaning=v['meaning'], origin=v['origin'],
          loci=','.join(f"{t['locus']}:{t['position']}" for t in tokens if t['word'] == w),
          status='HYPOTHESIS_ONLY') for w, v in sorted(lex.items())], ['word', 'meaning', 'origin', 'loci', 'status'])
    text = [f'# P10 {model}: vollständige positionsgetreue Arbeitslesung', '',
        'Jeder deutsche Inhaltswert ist angenommen. ⟦Wort⟧ bleibt ungelöst. Trennstriche sind Ausrichtung, keine beobachtete Interpunktion.',
        'Die Gliederung folgt allein den drei angegebenen ganzen Markern; physische Zeilen sind keine Sätze.', '']
    for s in segments:
        text += [f"## {s['id']} — {s['role'] if model != 'R1' else 'Beschreibung'} ({s['start']} bis {s['end']})", '',
                 '`' + ' '.join(s['words']) + '`', '',
                 ' / '.join(lex[w]['meaning'] if w in lex else f'⟦{w}⟧' for w in s['words']), '']
    text += ['Die zusammenhängende, ausdrücklich ergänzte Inhaltsfassung und ihre offenen Schlussfolgerungen stehen in [READING.md](READING.md).', '']
    (OUT / f'RENDERED_{suffix}.md').write_text('\n'.join(text))
    stats[model] = {'groups': len(rows), 'hypothesis_positions': sum(r['status'] == 'HYPOTHESIS_ONLY' for r in rows),
                    'open_positions': sum(r['status'] == 'OPEN' for r in rows), 'whole_form_assumptions': len(lex)}

markers = [t for t in tokens if t['word'] in {'qotaiin', 'shey', 'qotchy'}]
table('MARKERS.tsv', markers, ['locus', 'position', 'word', 'segment', 'role'])
repeated = []
for page in ['f32v', 'f29v']:
    byword = defaultdict(list)
    for t in tokens:
        if t['locus'].startswith(page + '.'):
            byword[t['word']].append(t)
    for word, ts in sorted(byword.items()):
        if len(ts) > 1:
            repeated.append({'page': page, 'word': word, 'count': len(ts),
                'loci': ','.join(f"{t['locus']}:{t['position']}" for t in ts),
                'segments': ','.join(dict.fromkeys(t['segment'] for t in ts)),
                'cross_speaker': len({t['role'] for t in ts}) > 1,
                'same_proposition': 'UNESTABLISHED; repetition is not identity of referent or proposition'})
table('REPETITIONS.tsv', repeated, ['page', 'word', 'count', 'loci', 'segments', 'cross_speaker', 'same_proposition'])

# Exhaustive exact-token uptake between each selected question and its context.
uptake = []
for page in ['f32v', 'f29v']:
    ss = [s for s in segments if s['id'].startswith(page + ':')]
    assert len(ss) == 3 and [s['role'] for s in ss] == ['Lehrer', 'Fragender', 'Lehrer']
    a, q, r = [set(s['words']) - {'qotaiin', 'shey', 'qotchy'} for s in ss]
    uptake.append({'page': page, 'question': ss[1]['id'], 'answer': ss[2]['id'],
                   'question_prior_exact_overlap': sorted(q & a), 'question_answer_exact_overlap': sorted(q & r),
                   'answer_prior_exact_overlap': sorted(r & a),
                   'sequence_paired': True, 'semantic_answer_established': False})
dump('UPTAKE.json', uptake)

assert {w for w in expanded if expanded[w] != rival[w]} == {'qotaiin', 'shey', 'qotchy'}
assert all(not x['question_prior_exact_overlap'] and not x['question_answer_exact_overlap'] for x in uptake)
dump('VALIDATION.json', {'status': 'PASS_SOURCE_ALIGNMENT_AND_ENUMERATION_ONLY', 'source_sha256': source['sha256'],
    'models': stats, 'segments': len(segments), 'markers': len(markers),
    'literal_cross_speaker_repetitions': sum(x['cross_speaker'] for x in repeated),
    'paired_questions_by_marker_order': len(uptake), 'orphan_answers_by_order': 0, 'unanswered_by_order': 0,
    'answers_with_established_semantic_reason': 0, 'independent_confirmation_capacity': 0,
    'confirmed_meanings': 0, 'held_pages_opened': 0,
    'limitations': 'Authored model renderer and assertions, not an independent semantic validator or test of the whole search.'})
print(json.dumps(stats, ensure_ascii=False))
