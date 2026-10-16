#!/usr/bin/env python3
"""Independent arithmetic menu, stable-stop fixtures and existing-source check."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
A = E / 'artifacts'
P = ROOT / 'research_registry/proposals/production_origin_supply_20261003'


def load(path):
    return json.loads(Path(path).read_bytes())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def transition(state, rank):
    occupied = [i for i, count in enumerate(state) if count]
    k = len(occupied)
    row = dict(state=list(state), rank=rank, legal=rank < 4*k+2,
               action=None, next_state=None, terminal=False, k=k,
               next_k=None, stable=None)
    if not row['legal']:
        return row
    changed = list(state)
    if rank < 4*k:
        source = occupied[rank // 4]
        destination_position = rank % 4
        destination = destination_position if destination_position < source else destination_position + 1
        changed[source] -= 1
        changed[destination] += 1
        row['action'] = chr(65+source) + '->' + chr(65+destination)
    else:
        row['terminal'] = True
        row['action'] = 'WAIT' if rank == 4*k else 'ROTATE'
        if rank == 4*k+1:
            changed = [state[4]] + list(state[:4])
    row['next_state'] = changed
    row['next_k'] = sum(x > 0 for x in changed)
    if row['terminal']:
        row['stable'] = rank in (4*row['next_k'], 4*row['next_k']+1)
    assert sum(changed) == 5 and all(x >= 0 for x in changed)
    return row


def greedy(machine, terminal, initial, stream, reset=None):
    state = initial
    words, current = [], []
    for symbol in stream:
        ends = terminal[2*state+symbol]
        state = machine[2*state+symbol]
        current.append(symbol)
        if ends:
            words.append(tuple(current))
            current = []
            if reset is not None:
                state = reset
    return words, tuple(current)


def controls():
    machine_count = stable_count = stop_checks = stream_checks = 0
    for machine in itertools.product(range(2), repeat=4):
        for terminal in itertools.product((False, True), repeat=4):
            machine_count += 1
            stable = all(not terminal[2*s+x] or terminal[2*machine[2*s+x]+x]
                         for s in range(2) for x in range(2))
            if not stable:
                continue
            stable_count += 1
            for s in range(2):
                for x in range(2):
                    if terminal[2*s+x]:
                        assert terminal[2*machine[2*s+x]+x]
                        stop_checks += 1
                for length in range(1, 6):
                    for stream in itertools.product(range(2), repeat=length):
                        words, remainder = greedy(machine, terminal, s, stream)
                        for left, right in zip(words, words[1:]):
                            assert left[-1] != right[0] or len(right) == 1
                        if words and remainder:
                            assert words[-1][-1] != remainder[0]
                        stream_checks += 1
    # Nonstable termination: x ends in state0, changes to1; next x does not stop.
    nonstable = greedy((1, 0, 0, 1), (True, True, False, True), 0, (0, 0, 1))
    assert nonstable == ([(0,), (0, 1)], ())
    # Stable termination with a REAL boundary reset to1; continuity is dropped.
    reset_machine = (0, 0, 0, 1)
    stops = (True, True, False, True)
    assert all(not stops[2*s+x] or stops[2*reset_machine[2*s+x]+x] for s in range(2) for x in range(2))
    reset = greedy(reset_machine, stops, 0, (0, 0, 1), reset=1)
    assert reset == ([(0,), (0, 1)], ())
    return dict(status='PASS_INDEPENDENT_SOURCE_FREE_FIXTURES', machines=machine_count,
                stable_machines=stable_count, stable_stop_checks=stop_checks,
                greedy_stream_checks=stream_checks,
                escapes={'nonstable':'x | xy with terminal-condition-changing update',
                         'boundary_reset':'x | xy with stable stop but real post-boundary reset'},
                ceiling='Finite fixtures supplement the arbitrary-state proof; no manuscript semantics.')


def unique_parse(raw, signs):
    suffixes = {len(raw): [()]}
    for i in range(len(raw)-1, -1, -1):
        suffixes[i] = [(sign,) + tail for sign in signs if raw.startswith(sign, i)
                       for tail in suffixes.get(i+len(sign), [])][:2]
    assert len(suffixes[0]) == 1
    return list(suffixes[0][0])


def check_locked_inputs(lock_path):
    lock = load(lock_path)
    rows = lock.get('files', lock.get('hashes'))
    if isinstance(rows, dict):
        rows = [{'path': p, 'sha256': h} for p, h in rows.items()]
    assert rows
    for row in rows:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    assert any(row['path'] == str(Path(__file__).resolve().relative_to(ROOT)) for row in rows)
    return sha(lock_path)


def verify(lock_path):
    lock_hash = check_locked_inputs(lock_path)
    own_controls = controls()
    primary_controls = load(A/'CONTROLS.json')
    assert primary_controls['status'] == 'PASS'
    for key in ('machines', 'stable_machines', 'stable_stop_checks'):
        assert primary_controls[key] == own_controls[key]
    for name in ('nonstable', 'boundary_reset'):
        fixture = primary_controls['escapes'][name]
        transition_table, stop_table = fixture['F'], fixture['T']
        assert len(transition_table) == len(stop_table) == 4
        stable = all(not stop_table[2*state+sign] or stop_table[2*transition_table[2*state+sign]+sign]
                     for state in range(2) for sign in range(2))
        assert stable == (name == 'boundary_reset')
        assert (fixture['boundary_reset'] is None) == (name == 'nonstable')
        stream = [sign for word in fixture['word_signs'] for sign in word]
        parsed, remainder = greedy(transition_table, stop_table, fixture['initial_state'], stream,
                                   reset=fixture['boundary_reset'])
        assert remainder == ()
        assert parsed == [tuple(word) for word in fixture['word_signs']] == [(0,), (0,1)]
    states = [s for s in itertools.product(range(6), repeat=5) if sum(s) == 5]
    expected = [transition(s, rank) for s in states for rank in range(22)]
    primary = load(A/'TRANSITIONS.json')
    assert primary['states'] == [list(s) for s in states]
    assert primary['transitions'] == expected
    terminal = sorted({r['rank'] for r in expected if r['terminal']})
    moves = {r['rank'] for r in expected if r['legal'] and not r['terminal']}
    dual = sorted(set(terminal) & moves)
    assert terminal == [4,5,8,9,12,13,16,17,20,21]
    assert dual == [4,5,8,9,12,13,16,17]
    assert primary['terminal_ranks'] == terminal and primary['dual_ranks'] == dual
    assert all(r['stable'] and r['k'] == r['next_k'] for r in expected if r['terminal'])
    source_path = ROOT/'research_registry/proposals/laufenberg_f85r2_20260926/source_supply_20260929/R_COMPLETE_UNITS.json'
    derivation_path = P/'C1064_DERIVATION_20261016.json'
    original, derivation = load(source_path), load(derivation_path)
    witness = load(A/'WITNESS.json')
    assert set(witness['readers']) == {'IT2a','ZL3b','RF1b'}
    assert witness['source']['sha256'] == sha(source_path)
    assert witness['derivation']['sha256'] == sha(derivation_path)
    for edition in ('IT2a','ZL3b','RF1b'):
        unit = next(u for u in original['units'] if u['edition'] == edition)
        line = next(l for l in unit['lines'] if l['metadata']['locus'] == 'f75v.48')
        assert line['metadata']['kind'] == 'P' and line['metadata']['page'] == 'f75v'
        assert line['metadata']['edition'] == edition
        assert line['metadata']['paragraph_start'] == line['metadata']['paragraph_end'] == '0'
        selected = [g for g in line['groups'] if int(g[1]) in (6,7)]
        assert [g[0] for g in selected] == [f'{edition}|f75v.48|G006', f'{edition}|f75v.48|G007']
        assert [g[2] for g in selected] == ['saino','ol']
        assert all(g[3] == g[4] == 'DEFINITE_SPACE' for g in selected)
        parses = [unique_parse(g[2], derivation['signs']) for g in selected]
        assert parses == [['s','a','i','n','o'],['o','l']]
        assert parses[0][-1] == parses[1][0] and len(parses[1]) > 1
        du = next(u for u in derivation['units'] if u['unit_id'] == 'f75v_'+edition)
        prior_rows = [r for r in du['rows'] if r['source_group_id'] in {g[0] for g in selected}]
        assert [r['units'] for r in prior_rows] == parses
        for row, group in zip(prior_rows, selected):
            assert row['raw'] == group[2] and row['parse_status'] == 'UNIQUE'
            assert row['source_group'] == dict(zip(unit['group_columns'], group))
        saved = witness['readers'][edition]
        assert saved['boundary_status'] == unit['boundary_status']
        assert saved['metadata'] == line['metadata'] and saved['groups'] == selected
        assert saved['parses'] == parses and saved['derivation_rows'] == prior_rows
        assert saved['violates_stable_stop'] is True
    old_path = ROOT/'experiments/yolo/gdt1319_cross_word_endpoint_state/artifacts/RESULT.json'
    old = load(old_path)
    endpoints = {ed: sum(node.startswith('O:') for node in row['active_nodes']) for ed,row in old['readers'].items()}
    assert endpoints == {'IT2a':19, 'RF1b':19, 'ZL3b':18}
    result = load(A/'RESULT.json')
    summary = dict(states=len(states), state_rank_cases=len(expected),
                   legal_cases=sum(r['legal'] for r in expected),
                   illegal_cases=sum(not r['legal'] for r in expected),
                   terminal_cases=sum(r['terminal'] for r in expected),
                   stable_terminal_cases=sum(r['stable'] is True for r in expected),
                   terminal_ranks=terminal, dual_ranks=dual,
                   inherited_active_end_counts=endpoints,
                   witness_readers=sorted(witness['readers']))
    for key,value in summary.items():
        assert result[key] == value, key
    assert result['status'] == 'STABLE_STOP_CONTRACT_EXCLUDED'
    return dict(status='PASS_INDEPENDENT_SOURCE_AND_CONDITIONAL_PROOF', summary=summary,
                controls=own_controls, primary_controls_verified=True, source_sha256=sha(source_path),
                derivation_sha256=sha(derivation_path), inherited_result_sha256=sha(old_path),
                result_sha256=sha(A/'RESULT.json'), lock_sha256=lock_hash,
                validator_sha256=sha(Path(__file__)),
                limits=['Post-observation verification of a new conditional deduction from existing data, not blind discovery.',
                        '126 material-count states do not enumerate elapsed WAIT count; stop decision depends only on occupied count, so arbitrary elapsed counts do not affect this stability consequence.',
                        'Same physical source pair in three alternative readings; no independent confirmation or meaning.',
                        'Excludes mandatory first-stop plus stability plus gap-continuity conjunction, not original1054 externally framed phases or every stateful writer.'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--lock', type=Path, default=E/'CODE_LOCK.json')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = controls() if args.controls else verify(args.lock)
    path = args.output or A/('VALIDATOR_CONTROLS.json' if args.controls else 'VALIDATION.json')
    path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
