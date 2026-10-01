#!/usr/bin/env python3
"""Replay existing frozen transforms on the owned, already guarded SOURCE only.

No learner, mixed TSV, image, alternative author account, or semantic assignment
is read. The unchanged GDT1051 functions are the transformation implementation.
"""
import collections
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parent
REPLAY = ROOT / 'experiments/yolo/gdt1051_frozen_grammar_local_application/src/run.py'
spec = importlib.util.spec_from_file_location('gdt1051_frozen_replay', REPLAY)
fixed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixed)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_markdown(output):
    forms = output['exact_forms']
    def nodes(value):
        return '(' + ' + '.join(nodes(item) for item in value) + ')' if isinstance(value, list) else value
    def counts(form):
        occurrences = forms[form]['occurrences']
        return '/'.join(str(sum(o['source_group_id'].startswith(ed + '|') for o in occurrences)) for ed in ['IT2a', 'ZL3b', 'RF1b'])
    lines = [
        '# GDT1131 shared structural and frequency priors', '',
        'Shared before semantic constructor freezes where dispatch timing permits. This independent audit read no A/B/C author output. It assigns no meanings or parts of speech.', '',
        'Source: owned `SOURCE.json`, exactly473 previously exposed f85r2 groups: IT157/ZL156/RF160. N19 and E27 in each alternate reader. Physical leaf f85; zero independent confirmation leaves. f84/f84r sealed, f116v unadmitted, reserves closed; no new image, corpus, or target access.', '',
        'Execution: unchanged GDT1051 pure functions and its64 ordered GDT605 merges. No learner or local O/OT license refit was called. 441 pure lowercase groups;32 marked groups remain unresolved. Existing uncertain spaces produce459 hard chunks,428 eligible. JSON retains every source ID and actual primary/uncertain chunk trees without duplicating the473 native context rows; the authoritative native fields remain in `SOURCE.json`.', '',
        '## Actual licensed trees', '',
        '`C=ch`, `S=sh`, `N=iin`, `I=in`, `E=ee`, `K=ckh`, `T=cth` are fixed collapsed transcription states, not sounds. A dot below separates final BPE units; plus is an actual ordered merge edge. Visible lowercase s is distinct from S. The collapsed representation is reconstructable; it is not a proven linguistic segmentation.', '',
        '| Exact form | Final units | Ordered licensed trees | Exact counts IT/ZL/RF in473 |',
        '|---|---|---|---|',
    ]
    for form in output['focus_forms']:
        entry = forms[form]
        lines.append(f"| `{form}` | `{' · '.join(entry['isolated_group_units'])}` | `{' · '.join(nodes(t) for t in entry['ordered_unit_trees'])}` | {counts(form)} |")
    lines += [
        '',
        'Bare aiin is the aN root (merge4 a+N), not an invented d/qok/ok child. daN is merge13 d+aN. So is merge43 S+o; shodaiin is two units So·daN, with no licensed whole-form merge between them. Se is merge11 S+e, so shedaiin retains Se·daN. A hypothetical shared aN operation must still show actual arguments, execution and consumers for at least two supported exact forms; nesting aN in daN alone does not execute a meaning.', '',
        'GDT012/062 preserves a different formal cut: aiin has wrapper NONE, host aiin, right-family NONE; daiin has wrapper d, host aiin, right-family NONE; shodaiin has wrapper sh, residual odaiin, host od, right aiin; shedaiin has wrapper sh, residual edaiin, host ed, right aiin. These disagree in where the visible d belongs. Preserve both model outputs; do not synthesize one universal parser or silently discard od/ed/So/Se.', '',
        '## All observed N/E exact forms', '',
        'This table includes reader variants and marked forms. Unit cuts shown for isolated groups are diagnostic when their source boundary is uncertain; JSON records the actual hard-chunk replay separately. All whole-form residuals, including otherwise unused characters, stay present.', '',
        '| Exact raw form | Frozen final units | Ordered trees |',
        '|---|---|---|',
    ]
    for form in output['observed_ne_exact_forms']:
        entry = forms[form]
        if entry['isolated_group_units'] is None:
            lines.append(f'| `{form}` | UNRESOLVED | Preserve exact marked raw form |')
        else:
            lines.append(f"| `{form}` | `{' · '.join(entry['isolated_group_units'])}` | `{' · '.join(nodes(t) for t in entry['ordered_unit_trees'])}` |")
    lines += [
        '', '## Same473 recurrence and countercase constraints', '',
        '- daiin occurs at .1 G026, .4 G005, .9 G001 in all readers: OUTSIDE, N, E. Its assigned entry must replay at all three positions, including the outside paragraph.',
        '- Bare aiin occurs in N .2 G004, E .11 G002, S .14 G003, W .20 G002 in all readers. IT/ZL add .1 G030; ZL adds .22 G007 and RF .22 G008. Differences belong to the same manuscript. The .22 ZL aiin shares an uncertain chunk with og (combined aiinog); IT reads the whole aiinog as one group, while RF has definite aiin/og spacing. Do not discard og or treat every bare group as an isolated BPE word.',
        '- shodaiin occurs once per reader at N .3 G003. shedaiin occurs at OUTSIDE .1 G023 and E .11 G003 in every reader. The shared daN subtree does not erase So versus Se or transfer a semantic signature automatically.',
        '- N .4 G001 dair is d·air with air=((a+i)+r), preserving i and r. It is not daiin, and a shared d rule alone cannot pay its residual.',
        '- The retained S .13 sequence is IT/ZL `or shedy tedy sodaiiin chy`; RF reads `or {ch\'}edy tedy sodaiiin chy`. sodaiiin is s·od·ai·N, not So·daN. RF marked `{ch\'}edy` stays unresolved and is not an alias for shedy. Every chosen operator/type must confront this whole sequence, not just isolated or/shedy.',
        '- sheedy is S·Edy; shedy is Sedy=((S+e)+(d+y)). ee versus e remains visible. sheo=Se·o and sheos=Se·os also retain their complete endings. Closure profiles do not justify equal predicates.',
        '- The N endings differ: IT/RF sosees versus ZL roseer. N .5 IT ockhdor/olkor contrasts with ZL ockhdar/olkar and RF ockhdar/ol@176;ar. E .8 IT oloeorain differs from ZL/RF oloqorain; E .10 IT qtchedy differs from ZL/RF ytchedy; E .11 IT chokcod differs from ZL chok{co}m and RF chot{co}g. No transcription repair or phonetic equivalence is licensed.',
        '- Exact or and ol recur outside N/E (see JSON source IDs). A participant/relator/type assignment must survive those contexts. Two adjacent or in N .2 do not themselves establish two physical participants or distinct compass names.',
        '',
        'ZL primary uncertain-space pairs are .2 or+aiin, .3 olfar+ary, .4 chol+daiin, .10 ytchedy+qodar, .11 soiis+aiin. Preserve alternate boundaries and report the full combined residual. IT primary boundaries are definite; RF primary marked groups remain unresolved.', '',
        '## Existing frequency and dispersion prior', '',
        'Copied from GDT1130 `artifacts/FREQUENCY_PRIORS.json`: exact raw matching across179 already exposed selectors, with paired f68r2 rings excluded. Readings remain separate; these counts are descriptive development priors, not independent confirmation. Column order is IT/ZL/RF.', '',
        '| Form | Count IT/ZL/RF | Rank IT/ZL/RF | Selectors with form IT/ZL/RF |',
        '|---|---|---|---|',
    ]
    for profile in output['existing_frequency_prior']['profiles']:
        values = profile['readers']
        parts = ['/'.join(str(values[ed][field]) for ed in ['IT2a', 'ZL3b', 'RF1b']) for field in ['count', 'rank', 'pages_with_form']]
        lines.append(f"| `{profile['form']}` | {' | '.join(parts)} |")
    lines += [
        '',
        'daiin is rank1 and widespread: IT740 instances on169/179 selectors, including134 line starts,488 middles,118 ends;80 IT lines repeat it,14 adjacent pairs, maximum3 per line. ZL717 on169 selectors; RF618 on163. This contradicts a claim that the form is rare or unique to this wind text. A narrow proper-name interpretation owes an explanation for broad recurrence; a general lexical, grammatical, or mixed hypothesis still requires written arguments and context. Frequency alone proves neither a part of speech nor a translation.', '',
        'The existing artifact supplies no broad profile for bare aiin, shodaiin, shedaiin, or most N/E forms; no claim of absent research or manuscript-wide rarity follows. okaiin/qokaiin/chokaiin/okoaiin counts illustrate substantial host/wrapper frequency differences, but none occurs exactly in this N/E packet and no donated meaning follows. okoaiin has one179-selector occurrence plus its separately owned ring occurrence; it is not a manuscript singleton. dalg has one179-selector occurrence; rarity cannot prove a general negation operation.', '',
        '## Directed composition and claim ceiling', '',
        'GDT608 DIRECT beats GLOBAL and reversed components on all23 held folios, while exact ATOMIC identity beats DIRECT on all23. Its primary bits are ATOMIC0.865886, DIRECT1.059225, GLOBAL1.237040, SWAPPED2.019941. a+N is the cleanest two-sided backoff; right aN/dy/y carry near-closure profiles0.989/0.972/0.952 across their direct children. These are outer-context tendencies, not semantic return types, sentence boundaries, or deterministic stripping rules. Component standalone composition fails. The o family fails its strict stability gate (p0.0859); ol/or retain pair-specific boundary profiles, and ok/ot have pair-specific entry profiles. Retain complete form, direction and entry context together.', '',
        'GDT1051 demonstrates fixed replay, not one unified morpheme parser. GDT326 did not establish free unseen host/coordinate recombination; GDT915/916 do not grant arbitrary new stem-pair transfers. No semantic POS, name, compass direction, source language or translation is selected. All three readers represent one previously exposed physical leaf. Confirmed translated words remain0.', '',
        'Reproduce with `python experiments/yolo/gdt1131_opposed_wind_survivor_succession/src/STRUCTURAL_PRIORS_REPLAY.py`; it reads only the owned source packet, frozen grammar code/merges and existing frequency artifact. Input hashes and executable reconstruction assertions are in `STRUCTURAL_PRIORS.json`.', '',
    ]
    (BASE / 'STRUCTURAL_PRIORS.md').write_text('\n'.join(lines))


def run():
    source = json.loads((BASE / 'SOURCE.json').read_text())
    rows = source['rows']
    assert len(rows) == 473
    assert {r['locus'] for r in rows} == {f'f85r2.{i}' for i in range(1, 25)}
    assert not source['independent_confirmation_leaves']
    assert collections.Counter(r['edition'] for r in rows) == {'IT2a': 157, 'ZL3b': 156, 'RF1b': 160}
    merges = fixed.load_merges()
    tree = fixed.merge_trees(merges)
    groups = [fixed.parse_group(row['block'], row) for row in rows]
    chunks = fixed.make_chunks(groups, merges)
    assert sum(len(chunk['group_indices']) for chunk in chunks) == len(rows)
    chunk_by_id = {}
    for chunk in chunks:
        for index in chunk['group_indices']:
            chunk_by_id[chunk['edition'], chunk['locus'], index] = chunk
    forms = {}
    byline = collections.defaultdict(list)
    for row in rows:
        byline[row['edition'], row['locus']].append(row)
    for line in byline.values():
        line.sort(key=lambda row: int(row['source_group_index']))
    for row, group in zip(rows, groups):
        raw = row['ivtff_group_raw']
        chunk = chunk_by_id[row['edition'], row['locus'], int(row['source_group_index'])]
        if raw not in forms:
            eligible = bool(fixed.PURE.fullmatch(raw))
            units = list(fixed.apply_bpe(fixed.collapse(raw), merges)) if eligible else None
            forms[raw] = {
                'raw_exact': raw,
                'status': 'UNCHANGED_FROZEN_FUNCTION_REPLAY' if eligible else 'MARKED_UNRESOLVED',
                'collapsed': fixed.collapse(raw) if eligible else None,
                'isolated_group_units': units,
                'ordered_unit_trees': [tree(unit) for unit in units] if eligible else None,
                'wrapper_host': group['wrapper_host'],
                'segmentation_ceiling': 'MODEL_SPECIFIC_NOT_A_UNIQUE_MORPHEME_PARSER',
                'occurrences': [],
            }
            if eligible:
                assert ''.join(units) == fixed.collapse(raw)
        line = byline[row['edition'], row['locus']]
        idx = int(row['source_group_index'])
        forms[raw]['occurrences'].append({
            'source_group_id': row['source_group_id'],
            'block': row['block'],
            'hard_chunk_indices': chunk['group_indices'],
            'isolated_group_is_hard_chunk': len(chunk['group_indices']) == 1,
        })
    prior_path = ROOT / 'experiments/yolo/gdt1130_shared_profile_current_trend_reading/artifacts/FREQUENCY_PRIORS.json'
    prior = json.loads(prior_path.read_text())
    ne_forms = sorted({row['ivtff_group_raw'] for row in rows if row['block'] in {'N', 'E'}})
    focus = ['aiin', 'daiin', 'shodaiin', 'shedaiin', 'oraiin', 'qotaiin', 'dair', 'sodaiiin', 'or', 'ol', 'sheedy', 'shedy']
    inputs = [REPLAY, Path(__file__), BASE / 'SOURCE.json', BASE / 'AUTHOR_PLAN.json',
              BASE.parent / 'PREREGISTRATION.md', fixed.MERGES,
              ROOT / 'run_gdt012_core_semantic_atlas.py',
              ROOT / 'run_gdt062_right_family_register_renderer.py',
              ROOT / 'experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py',
              ROOT / 'experiments/yolo/gdt608_compositional_stem_orientation/REPORT.md',
              ROOT / 'experiments/yolo/gdt1051_frozen_grammar_local_application/REPORT.md', prior_path]
    output = {
        'schema': 'gdt1131-shared-structural-priors-v1',
        'status': 'FORMAL_REPLAY_AND_EXISTING_DESCRIPTIVE_PRIORS_ONLY',
        'inputs': {str(path.relative_to(ROOT)): sha(path) for path in inputs},
        'raw_counts_by_reader': dict(collections.Counter(row['edition'] for row in rows)),
        'raw_count': len(rows),
        'eligible_group_count': sum(group['wrapper_host'] is not None for group in groups),
        'hard_chunk_count': len(chunks),
        'eligible_hard_chunk_count': sum(chunk['units'] is not None for chunk in chunks),
        'primary_native_counts': {ed: {block: sum(row['edition'] == ed and row['block'] == block for row in rows) for block in ['N', 'E']} for ed in ['IT2a', 'ZL3b', 'RF1b']},
        'focus_forms': focus,
        'observed_ne_exact_forms': ne_forms,
        'exact_forms': {form: forms[form] for form in sorted(forms)},
        'primary_and_uncertain_hard_chunks': [chunk for chunk in chunks
            if 2 <= int(chunk['locus'].split('.')[1]) <= 11 or len(chunk['group_indices']) > 1],
        'existing_frequency_prior': {
            'source': str(prior_path.relative_to(ROOT)), 'sha256': sha(prior_path),
            'status': prior['status'], 'scope': prior['scope'],
            'profiles': prior['profiles'], 'limits': prior['limits'],
            'availability_for_ne': {form: ('PROFILE_PRESENT' if form in {p['form'] for p in prior['profiles']} else 'NOT_IN_THIS_EXISTING_PROFILE_ARTIFACT_NO_ABSENCE_CLAIM') for form in ne_forms},
            'use': 'SHARED_PREAUTHOR_DESCRIPTIVE_PRIOR; DOES_NOT_SELECT_OR_VALIDATE_MEANING',
        },
        'constraints': [
            'Use exact whole residual, ordered trees, source entry and consumers together.',
            'Bare aiin is aN, not an invented d/qok/ok child.',
            'daN=[d,[a,N]]; shodaiin=[S,o] followed by [d,[a,N]], not an attested single merged Shodaiin unit.',
            'GDT012/062 and GDT605 cuts are different model outputs; do not merge them into one proven parser.',
            'Only definite hard chunks receive their actual complete BPE replay; isolated groups at uncertain spaces are diagnostic views.',
            'Marked raw alternatives remain unresolved; never remove entities, braces or uncertain letters.',
            'GDT608 DIRECT beats GLOBAL and SWAPPED on23/23 held folios; ATOMIC beats DIRECT on23/23. Preserve pair-specific residuals.',
            'GDT608 right aN/dy/y near-closure profiles describe formal outer context, not semantic return types.',
            'Shared o alone is not a stable family role; ol/or retain pair-specific profiles.',
            'All exact occurrences in all473 groups remain mandatory; an outside-N/E context is not a removable exception.',
            'Frequency and dispersion permit constraints on rarity and specificity, not translations or automatic function-word assignments.',
        ],
        'validation': {
            'all_473_native_occurrence_ids_retained': sum(len(form['occurrences']) for form in forms.values()) == 473,
            'isolated_and_hard_chunk_collapsed_reconstruction': True,
            'only_frozen_pure_functions_executed': True,
            'new_corpus_or_images_or_targets': False,
            'author_accounts_accessed': False,
        },
        'scope': {'physical_leaf': 'f85', 'prior_exposure': True, 'independent_confirmation_leaves': [],
                  'f84': 'SEALED_UNREAD', 'f84r': 'SEALED_UNREAD', 'f116v': 'UNADMITTED_UNREAD', 'reserves': 'CLOSED'},
        'confirmed_translated_words': 0,
        'semantic_validation': False,
    }
    assert output['validation']['all_473_native_occurrence_ids_retained']
    path = BASE / 'STRUCTURAL_PRIORS.json'
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    write_markdown(output)
    print(json.dumps({key: output[key] for key in ['raw_count', 'eligible_group_count', 'hard_chunk_count', 'eligible_hard_chunk_count', 'primary_native_counts', 'validation']}, indent=2))


if __name__ == '__main__':
    run()
