"""Apply two preregistered local scope assignments without adding word values."""
from pathlib import Path
from collections import defaultdict, Counter
import csv
import hashlib
import io
import json

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
EDS = ['ZL3b', 'IT2a', 'RF1b']


def dump(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def tsv(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, list(rows[0]), delimiter='\t', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def join(rows, render):
    separators = {'DEFINITE_SPACE': ' ', 'UNCERTAIN_SMALL_SPACE': ' / ', 'DRAWING_INTERRUPTION': ' // '}
    return ''.join(('' if i == 0 else separators[r['left_separator']]) + render(r)
                   for i, r in enumerate(rows))


def build():
    lock = json.loads((EXP / 'PREREG_LOCK.json').read_text())
    for name, digest in lock['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    model = json.loads((EXP / 'src/MODEL.json').read_text())
    source = json.loads((ROOT / model['source']).read_text())['groups']
    base = json.loads((ROOT / model['base_model']).read_text())['models']['M']['lexicon']
    lex = {mid: dict(base) for mid in model['models']}
    for name in model['extensions']:
        extension = json.loads((ROOT / name).read_text())['models']
        for mid in lex:
            assert not (lex[mid].keys() & extension[mid]['lexicon'].keys())
            lex[mid].update(extension[mid]['lexicon'])
    assert model['new_word_values'] == {} and all(len(v) == 21 for v in lex.values())
    page, lo, hi = model['working_frame']
    frame = sorted([r for r in source if r['page'] == page and lo <= int(r['locus'].split('.')[1]) <= hi],
                   key=lambda r: (EDS.index(r['edition']), int(r['locus'].split('.')[1]), int(r['source_group_index'])))
    lines = defaultdict(list)
    for row in frame:
        lines[row['edition'], row['locus']].append(row)
    focus = [r for r in frame if r['locus'] in model['focus_loci']]
    for ed in EDS:
        assert [r['ivtff_group_raw'] for r in lines[ed, 'f77r.20']] == model['partitions']['A'] + model['partitions']['B']
        assert len(lines[ed, 'f77r.19']) == 9
        assert lines[ed, 'f77r.19'][-1]['ivtff_group_raw'] == 'chey'

    roles = []
    for mid in model['models']:
        for direction, scopes in model['directions'].items():
            for row in focus:
                locus, index = row['locus'], int(row['source_group_index'])
                part = 'PRE' if locus == 'f77r.18' else ('M' if index == 9 else 'K') if locus == 'f77r.19' else ('A' if index <= 3 else 'B')
                gloss, role = lex[mid].get(row['ivtff_group_raw'], ['⟦' + row['ivtff_group_raw'] + '⟧', 'UNREAD'])
                roles.append(dict(candidate=mid + '_' + direction, **row, gloss=gloss, lexical_role=role,
                                  partition=part, local_scope=scopes[part], participant_binding='UNRESOLVED', factual_assertion=False))
    summaries = []
    for mid in model['models']:
        for direction in model['directions']:
            for ed in EDS:
                rr = [r for r in roles if r['candidate'] == mid + '_' + direction and r['edition'] == ed]
                def ids(scope, role=None):
                    return '|'.join(r['source_group_id'] for r in rr if r['local_scope'] == scope and (role is None or r['lexical_role'] == role))
                summaries.append(dict(candidate=mid + '_' + direction, edition=ed, source_groups=len(rr),
                    known_groups=sum(r['lexical_role'] != 'UNREAD' for r in rr),
                    unknown_groups=sum(r['lexical_role'] == 'UNREAD' for r in rr),
                    antecedent_ids=ids('ANTECEDENT'), consequent_ids=ids('CONSEQUENT'),
                    antecedent_flow_ids=ids('ANTECEDENT', 'FLOW'), consequent_flow_ids=ids('CONSEQUENT', 'FLOW'),
                    consequent_copula_ids=ids('CONSEQUENT', 'COPULA'),
                    unknown_ids='|'.join(r['source_group_id'] for r in rr if r['lexical_role'] == 'UNREAD'),
                    unresolved_participants='K,A,B; PRE motion/rest participants also unread',
                    contradiction_assessment='NO_DEMONSTRATED_CONTENT_CONTRADICTION; INSUFFICIENT_CONTENT',
                    complete_content_reading=False, selected=False, independent_meaning_tests=0))
    documents = {}
    for ed in EDS:
        doc = [f'# GDT937 — vollständiger bestehender P1-Rahmen {ed}', '',
               'f77r.9–24; unveränderte R/T-Wortannahmen. ? markiert angenommene Wortwerte, ⟦…⟧ ungelesene Rohgruppen.',
               '/ = unsicherer kleiner Abstand; // = Zeichnungsunterbrechung. Keine bestätigte Übersetzung.', '']
        for (edition, locus), rr in lines.items():
            if edition != ed:
                continue
            doc += [f'## {locus}', '', '`' + join(rr, lambda r: r['ivtff_group_raw']) + '`', '']
            for mid in lex:
                doc += [mid + ': ' + join(rr, lambda r: lex[mid][r['ivtff_group_raw']][0] + '?' if r['ivtff_group_raw'] in lex[mid] else '⟦' + r['ivtff_group_raw'] + '⟧'), '']
        documents[f'P1_{ed}.md'] = '\n'.join(doc).rstrip() + '\n'
    draft = ['# GDT937 — alle vier vollständigen lokalen Gliederungen', '',
             'Jede Rohgruppe .18–20 ist enthalten. Die Tabelle folgt der Quellreihenfolge; A/B sind angenommene Grenzen.',
             'OUTSIDE_THIS_CONDITION ist keine unbedingte Tatsachenbehauptung. Alle Bedeutungen bleiben Hypothesen.', '']
    for summary in summaries:
        cid, ed = summary['candidate'], summary['edition']
        rr = [r for r in roles if r['candidate'] == cid and r['edition'] == ed]
        draft += [f'## {cid} / {ed}', '', '| Block | Lokaler Bereich | Ganze Rohfolge | Wortannahmen mit allen Lücken |', '|---|---|---|---|']
        for part in ['PRE', 'K', 'M', 'A', 'B']:
            block = [r for r in rr if r['partition'] == part]
            raw = join(block, lambda r: r['ivtff_group_raw'])
            gloss = join(block, lambda r: r['gloss'] + ('?' if r['lexical_role'] != 'UNREAD' else ''))
            draft.append(f"| {part} | {block[0]['local_scope']} | `{raw}` | {gloss} |")
        draft += ['', 'Beteiligte und die unbekannten Inhalte bleiben ungebunden; keine vollständige Satzübersetzung.', '']
    result = dict(experiment='GDT937', status='FIXED_LOCAL_SCOPE_RIVALS_CONTENT_INCOMPLETE',
        bound_source_groups=len(source), bound_prior_alignment_rows=2 * len(source), frame_groups=len(frame),
        focus_groups=len(focus), candidate_role_rows=len(roles), candidate_summary_rows=len(summaries),
        frame_counts=dict(Counter(r['edition'] for r in frame)), focus_counts=dict(Counter(r['edition'] for r in focus)),
        known_groups_by_reader={e: sum(r['ivtff_group_raw'] in lex['R'] for r in focus if r['edition'] == e) for e in EDS},
        fixed_lexicon_sizes={k: len(v) for k, v in lex.items()}, new_word_values=0,
        local_candidates=['R_F', 'R_P', 'T_F', 'T_P'], selected_candidate=None,
        complete_content_readings=0, confirmed_words=0, independent_meaning_tests=0,
        unexposed_confirmation_folios=0, new_admissions=0, significance_claimed=False,
        empirical_scope_discriminator=False, semantics_validated=False, factual_events_inferred=False,
        scope_consequence='F conditions B copula; P conditions all three K FLOW positions. A FLOW is antecedent in both. PRE motion/rest stays outside this specified condition.',
        next_content_target='Whole B: qoteey qokain sheey qotedy dalchedy; A qotain sheal qokeedy remains unresolved. No additional generic scope parser.')
    return {'CANDIDATE_ROLES.tsv': tsv(roles), 'CANDIDATE_SUMMARY.tsv': tsv(summaries),
            'LOCAL_DRAFTS.md': '\n'.join(draft).rstrip() + '\n', 'RESULT.json': dump(result), **documents}


if __name__ == '__main__':
    for name, content in build().items():
        (EXP / 'artifacts' / name).write_text(content)
    print((EXP / 'artifacts/RESULT.json').read_text())
