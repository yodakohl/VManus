#!/usr/bin/env python3
"""Frozen FR source/accounting checks, not a grammar or meaning validator."""
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
EXPECTED = {
    'FR_TARGET.json': 'd7b25cfdf0a54071abf688e97932ab83653c779a9b5a9134b741d0817a73194f',
    'FR_AUTHOR.json': 'e34408bcbf4633d301957e6fbaabd0de03cab9d96981046e9ff86079054b00d0',
    'FO_AUTHOR.json': '0a28d6f096b560fe7d70302ff8bfc55e0e78c31ee77529a386f3ed630de58b09',
    'FP_WHOLE_AUTHOR.json': '5750753c45f8de14ac8ac13a31ff4beeb5deb98a652a8342f1f2fb0ce295f393',
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = datetime.now(timezone.utc)
    checks = []
    def check(name, passed):
        checks.append({'check': name, 'passed': bool(passed)})
    observed = {name: digest(BASE / name) for name in EXPECTED}
    for name, expected in EXPECTED.items():
        check('immutable_hash:' + name, observed[name] == expected)
    author = json.loads((BASE / 'FR_AUTHOR.json').read_text())
    target = json.loads((BASE / 'FR_TARGET.json').read_text())
    native = [dict(g, context=c['context']) for c in target['contexts'] for g in c['groups']]
    primary = author['rows']
    alternatives = author['alternatives']
    candidates = primary + alternatives
    check('101_primary_rows', len(primary) == 101)
    check('65_alternative_rows', len(alternatives) == 65)
    check('166_native_groups', len(native) == 166)
    check('unique_native_IDs', len({g['source_group_id'] for g in native}) == 166)
    check('unique_candidate_IDs', len({r['ID'] for r in candidates}) == 166)
    source = {g['source_group_id']: g for g in native}
    by_id = {r['ID']: r for r in candidates}
    check('same_complete_ID_set', set(source) == set(by_id))
    check('primary_native_order', [r['ID'] for r in primary] == [g['source_group_id'] for g in native if g['edition'] == 'IT2a'])
    check('alternatives_native_order', [r['ID'] for r in alternatives] == [g['source_group_id'] for g in native if g['edition'] != 'IT2a'])
    for row in candidates:
        group = source.get(row['ID'])
        check('raw_identity:' + row['ID'], group is not None and row['raw'] == group['ivtff_group_raw'])
    for row in primary:
        check('segment_reconstruction:' + row['ID'], ''.join(row['segments']) == row['raw'])
    unbound = sum(r['status'].startswith(('UNBOUND', 'FIRST_UNPAID')) for r in primary)
    check('36_primary_unbound', unbound == 36)
    check('zero_complete_contexts', author['complete'] is False and author['accounting']['whole_contexts_completed'] == 0)
    check('target_hash_declared_by_author', author['target_sha256'] == EXPECTED['FR_TARGET.json'])
    for name in ['FO_AUTHOR.json', 'FP_WHOLE_AUTHOR.json', 'FR_TARGET.json']:
        check('author_base_hash:' + name, author['immutable_base_hashes'][name] == EXPECTED[name])
    # These compare authored fields, not derived execution or material composition.
    f80 = {r['position']: r for r in primary if r['context'] == 'f80v.30-37'}
    r27, r31, r32 = [f80[n] for n in (27, 31, 32)]
    check('authored27_fresh_no_input', r27['typed_input'] == 'none' and r27['typed_output'] == 'Paint:M27; parent=None; no inheritance')
    check('authored27_state', r27['state']['activePaint'] == 'M27' and r27['state']['IngredientQueue'] == ['I26'] and r27['state']['currentRecipient'] == 'R19' and r27['state']['Layers'] == ['L22'])
    check('authored31_application_arguments', r31['typed_input'] == 'M27,R19' and r31['typed_output'] == 'Layer:L31 recipient=R19')
    check('authored31_pending_queue_and_Layers', r31['state']['activePaint'] == 'M27' and r31['state']['IngredientQueue'] == ['I26'] and r31['state']['currentRecipient'] == 'R19' and r31['state']['Layers'] == ['L22', 'L31'])
    check('authored32_Paint_consumes_queue', r32['expression'] == 'Homogenize(M27,[I26])' and r32['typed_input'] == 'M27:Paint,I26:Ingredient' and r32['typed_output'] == 'same M27:Paint; I26 consumed' and r32['state']['IngredientQueue'] == [])
    check('authored32_identity_preserved', r32['state']['activePaint'] == 'M27' and r32['state']['currentRecipient'] == 'R19' and r32['state']['Layers'] == ['L22', 'L31'] and r32['latestPhysicalResult'] == 'M27:Paint')
    native_fields = list(target['contexts'][0]['groups'][0])
    candidate_fields = ['context', 'candidate_position', 'candidate_segments', 'candidate_contribution', 'candidate_expression', 'candidate_input', 'candidate_output', 'candidate_state', 'candidate_status', 'meaning_status', 'independent_confirmation_credit']
    table_path = BASE / 'FR_CANDIDATE_TABLE.tsv'
    with table_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=native_fields + candidate_fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for group in native:
            row = by_id.get(group['source_group_id'], {})
            output = {k: group.get(k, '') for k in native_fields}
            output.update(context=group['context'], candidate_position=row.get('position', ''), candidate_segments=json.dumps(row.get('segments', []), ensure_ascii=False), candidate_contribution=row.get('contribution', ''), candidate_expression=row.get('expression', ''), candidate_input=row.get('typed_input', ''), candidate_output=row.get('typed_output', ''), candidate_state=json.dumps(row.get('state'), ensure_ascii=False, sort_keys=True), candidate_status=row.get('status', 'MISSING_CANDIDATE'), meaning_status='UNCONFIRMED_C0', independent_confirmation_credit=0)
            writer.writerow(output)
    check('LF_table', b'\r' not in table_path.read_bytes())
    finished = datetime.now(timezone.utc)
    task_first = datetime.fromisoformat('2026-10-01T06:49:33+00:00')
    elapsed = (finished - task_first).total_seconds()
    result = {
        'status': 'PASS_SOURCE_AND_AUTHORED_ACCOUNTING_ONLY' if all(x['passed'] for x in checks) else 'FAIL_ACCOUNTING',
        'meaning_validation': False, 'generic_grammar_validation': False,
        'source_hashes': observed, 'script_sha256': digest(Path(__file__)), 'table_sha256': digest(table_path),
        'counts': {'primary': len(primary), 'alternatives': len(alternatives), 'native': len(native), 'primary_unbound': unbound, 'complete_contexts': author['accounting']['whole_contexts_completed']},
        'checks': checks, 'errors': [x['check'] for x in checks if not x['passed']],
        'timing': {'task_first_clock_utc': task_first.isoformat(), 'task_cap_seconds': 150, 'actual_finish_utc': finished.isoformat(), 'task_elapsed_seconds': round(elapsed, 3), 'task_overrun_seconds': round(max(0, elapsed - 150), 3), 'run_start_utc': started.isoformat(), 'run_seconds': round((finished-started).total_seconds(), 6)},
        'limits': 'Rows27/31/32 checks inspect authored assertions only. Table conserves native raw groups/boundaries/flags, not meanings. No sequential parser, source-image validation, complete grammar or independent word confirmation. Unsupported spreading prose and prior partial critique remain unchanged.'
    }
    (BASE / 'FR_ACCOUNTING.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'status': result['status'], 'counts': result['counts'], 'errors': result['errors'], 'timing': result['timing'], 'output_hashes': {n: digest(BASE / n) for n in ['FR_VALIDATE_ACCOUNTING.py', 'FR_ACCOUNTING.json', 'FR_CANDIDATE_TABLE.tsv']}}))
    return 0 if not result['errors'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
