"""Conserve two guarded exposed projections and apply authored P28 scope rules.
No decoder, full-table parsing, new visual ownership, or semantic validation.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

P = Path('research_registry/proposals/translation_programs_20260912/work/P28')

def read(name):
    with (P / name).open() as f:
        return list(csv.DictReader(f, delimiter='\t'))

def write(name, rows, fields):
    with (P / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(rows)

def dump(name, data):
    (P / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

for s in json.loads((P / 'SOURCE.json').read_text()):
    assert hashlib.sha256((P / s['projection']).read_bytes()).hexdigest() == s['projection_sha256']
    # Hash bytes without parsing the mixed legacy table.
    assert hashlib.sha256(Path(s['source']).read_bytes()).hexdigest() == s['sha256']
lines, labels = read('PROSE.tsv'), read('LABELS.tsv')
assert len(lines) == 72 and len(labels) == 23
assert {x['page'] for x in lines + labels} == {'f77r', 'f82r'}
for i, label in enumerate(labels, 1):
    label['local_id'] = f'L{i:02d}'
    label['identity_status'] = 'LOCAL_WRITTEN_SITE_ID_ONLY; physical complete object and meaning unconfirmed'
write('REGISTER.tsv', labels, list(labels[0]))

tokens, refs = [], []
for line in lines:
    words = line['zl3b_line'].split()
    for i, word in enumerate(words):
        token = {k: line[k] for k in ['page', 'panel_id', 'record_id', 'locus']}
        token.update(position=i+1, word=word)
        tokens.append(token)
        for label in labels:
            pattern = label['label_surface'].split()
            if words[i:i+len(pattern)] == pattern:
                refs.append({**token, 'surface': label['label_surface'], 'width': len(pattern),
                             'label_id': label['local_id'], 'label_page': label['page'],
                             'label_panel': label['panel_id'], 'label_locus': label['locus']})
assert len(tokens) == 599
assert all(r['width'] == 1 for r in refs)  # actual result, no multi-label decomposition
assert len(refs) == 5
write('REFERENCES.tsv', refs, list(refs[0]))

trace, alignments, stats = [], {}, {}
for model in ['N0', 'N1', 'N2', 'C1']:
    rows = []
    for token in tokens:
        hits = [r for r in refs if r['locus'] == token['locus'] and r['position'] == token['position']]
        if model == 'N0':
            hits = [r for r in hits if r['label_panel'] == token['panel_id']]
        elif model == 'N1':
            hits = [r for r in hits if r['label_page'] == token['page']]
        elif model == 'N2':
            local = [r for r in hits if r['label_page'] == token['page']]
            hits = local or hits
        ids = sorted({r['label_id'] for r in hits})
        known = any(r['locus'] == token['locus'] and r['position'] == token['position'] for r in refs)
        if not known:
            reading, status = '⟦'+token['word']+'⟧', 'OPEN'
        elif model == 'C1':
            reading, status = '[Klasse '+token['word']+'; Art unbekannt]', 'HYPOTHETICAL_CLASS'
        elif len(ids) == 1:
            reading, status = '['+ids[0]+': lokale Kennung '+token['word']+']', 'CONDITIONAL_LABEL_RESOLUTION'
        elif not ids:
            reading, status = '[Name '+token['word']+'; Ziel außerhalb des Bereichs]', 'UNRESOLVED_SCOPE'
        else:
            reading, status = '[Name '+token['word']+'; Alternativen '+','.join(ids)+']', 'AMBIGUOUS_LABEL'
        rows.append({**token, 'model': model, 'reading': reading, 'candidate_ids': ','.join(ids) or 'NA', 'status': status})
    alignments[model] = rows
    write('ALIGNMENT_'+model+'.tsv', rows, list(rows[0]))
    stats[model] = dict(Counter(x['status'] for x in rows))
    text = ['# P28 '+model+' — vollständige Prosa beider Arbeitsblätter', '',
            '599 Gruppen unverändert. Eckige Lesungen sind Annahmen, ⟦…⟧ ungelöste Gruppen. Bildzonen und IDs übersetzen kein Wort.', '']
    for line in lines:
        rr = [r for r in rows if r['locus'] == line['locus']]
        text += ['**'+line['locus']+' · '+line['record_id']+'**', '', '`'+line['zl3b_line']+'`', '', ' / '.join(r['reading'] for r in rr), '']
    (P / ('READING_'+model+'.md')).write_text('\n'.join(text))
    for record in dict.fromkeys(x['record_id'] for x in lines):
        ll = [x for x in lines if x['record_id'] == record]
        if model == 'N0':
            eligible = [x for x in labels if x['panel_id'] == ll[0]['panel_id']]
        elif model == 'N1':
            eligible = [x for x in labels if x['page'] == ll[0]['page']]
        else:
            eligible = labels
        rr = [x for x in rows if x['record_id'] == record and x['status'] != 'OPEN']
        trace.append({'model': model, 'record': record, 'entry_locus': ll[0]['locus'],
                      'scope': ll[0]['panel_id'] if model == 'N0' else ll[0]['page'] if model == 'N1' else 'HYPOTHETICAL_TWO_PAGE_REGISTER' if model == 'N2' else 'CLASS_NO_INDIVIDUAL_TARGET',
                      'available_labels': ','.join(x['local_id'] for x in eligible),
                      'references': ';'.join(x['locus']+':'+str(x['position'])+' '+x['word']+' '+x['status'] for x in rr) or 'NONE',
                      'unwritten_scope_assumption': 'visual boundary or register assumption; no translated qualifier'})
write('SCOPE_TRACE.tsv', trace, list(trace[0]))

# Declared qualifier candidate: a complete label at record opening, not any convenient neighbour.
qualifiers = []
for record in dict.fromkeys(x['record_id'] for x in lines):
    ts = [x for x in tokens if x['record_id'] == record]
    head = ts[0]
    hits = [x for x in labels if x['label_surface'] == head['word']]
    later = [r for r in refs if r['record_id'] == record and not (r['locus'] == head['locus'] and r['position'] == 1)]
    qualifiers.append({'record': record, 'head': head['word'], 'candidate_label_count': len(hits),
                       'selected_scope': hits[0]['panel_id'] if len(hits) == 1 else 'UNRESOLVED_NO_UNIQUE_LABEL',
                       'following_label_references': len(later),
                       'qualifier_status': 'HYPOTHETICAL_ONLY' if len(hits) == 1 else 'NO_CANDIDATE'})
write('QUALIFIERS.tsv', qualifiers, list(qualifiers[0]))
# Explicit post-exposure Q2 revision: all line heads, scope persists to next trigger/record.
q2, q2_switches = [], []
current_record, active_panel = None, None
for line in lines:
    if line['record_id'] != current_record:
        current_record, active_panel = line['record_id'], None
    head = line['zl3b_line'].split()[0]
    head_labels = [x for x in labels if x['label_surface'] == head]
    trigger = len(head_labels) == 1
    if trigger:
        active_panel = head_labels[0]['panel_id']
        q2_switches.append({'locus': line['locus'], 'head': head, 'activated_panel': active_panel})
    for r in [x for x in refs if x['locus'] == line['locus']]:
        available = r['label_panel'] == active_panel if active_panel else r['label_page'] == line['page']
        q2.append({**r, 'active_scope': active_panel or line['page'],
                   'status': 'CONDITIONAL_LABEL_RESOLUTION' if available else 'UNRESOLVED_SCOPE'})
write('Q2_REFERENCES.tsv', q2, list(q2[0]))
dump('Q2_SWITCHES.json', q2_switches)
dump('RESULT.json', {'status': 'PARTIAL_SCOPE_READINGS_NO_QUALIFIED_NAME_IDENTIFICATION',
     'prose_lines': len(lines), 'prose_groups': len(tokens), 'label_loci': len(labels),
     'label_groups': sum(len(x['label_surface'].split()) for x in labels),
     'distinct_complete_labels': len({x['label_surface'] for x in labels}),
     'same_form_labels_on_both_pages': sorted({x['label_surface'] for x in labels if x['page']=='f77r'} & {x['label_surface'] for x in labels if x['page']=='f82r'}),
     'reference_occurrences': len(refs), 'models': stats,
     'record_initial_label_candidates': sum(x['candidate_label_count'] == 1 for x in qualifiers),
     'following_references_after_unique_qualifier': sum(x['following_label_references'] for x in qualifiers if x['candidate_label_count'] == 1),
     'Q2_post_exposure_revision': {'line_heads_examined': len(lines), 'switches': len(q2_switches),
          'reference_status': dict(Counter(x['status'] for x in q2))},
     'new_textual_scope_qualifiers_identified': 0, 'resolved_complete_physical_objects': 0,
     'independent_confirmation_capacity': 0, 'confirmed_meanings': 0})

# Read output back rather than relying on count-only success.
for model in alignments:
    reread = read('ALIGNMENT_'+model+'.tsv')
    assert [(x['locus'], int(x['position']), x['word']) for x in reread] == [(x['locus'], x['position'], x['word']) for x in tokens]
assert len({x['label_surface'] for x in labels}) == len(labels)
dump('VALIDATION.json', {'status': 'PASS_SOURCE_CONSERVATION_AND_RULE_ENUMERATION_ONLY',
     'aligned_models': 4, 'groups_each': 599, 'labels_preserved_whole': 23,
     'semantic_truth_checked': False, 'held_pages_opened': 0})
print((P / 'RESULT.json').read_text())
