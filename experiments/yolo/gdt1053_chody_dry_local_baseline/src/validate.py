#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())


def main() -> int:
    base = Path(__file__).resolve().parents[1]
    lock = json.loads((base / 'PREREG_LOCK.json').read_text())
    for item in lock.values():
        assert hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256']
    paragraphs = json.loads((ROOT / lock['input']['path']).read_text())
    result = json.loads((base / 'artifacts' / 'RESULT.json').read_text())
    checks = 0
    five = re.compile(r'[a-z]{5}\Z')
    code = re.compile(r'qo(?:k|t)(ch|sh)[a-z]*\Z')
    code_capacity = {}
    for reader in ('ZL3b', 'IT2a'):
        found = []
        excluded = {'no_quality_code': 0, 'no_five_character_control': 0}
        classes = {'only_dry': 0, 'both': 0, 'only_moist': 0}
        total = 0
        for para in paragraphs[reader]:
            tokens = [(w, sid, line['locus']) for line in para['lines'] for w, sid in zip(line['words'], line['source_ids'])]
            target_positions = [i for i, (word, _, _) in enumerate(tokens) if word == 'chody']
            total += len(target_positions)
            if not target_positions:
                continue
            codes = {i: code.fullmatch(word).group(1) for i, (word, _, _) in enumerate(tokens) if code.fullmatch(word)}
            if not codes:
                excluded['no_quality_code'] += len(target_positions)
                continue
            controls = [i for i, (word, _, _) in enumerate(tokens) if five.fullmatch(word) and word != 'chody' and i not in codes]
            if not controls:
                excluded['no_five_character_control'] += len(target_positions)
                continue
            class_set = set(codes.values())
            classes['both' if len(class_set) == 2 else ('only_dry' if 'ch' in class_set else 'only_moist')] += 1
            def dry(i):
                nearest = sorted(codes, key=lambda j: (abs(j - i), j))[0]
                return int(codes[nearest] == 'ch'), nearest
            for i in target_positions:
                candidates = [j for j in controls if tokens[j][2] == tokens[i][2]]
                target_dry, q = dry(i)
                local_dry = sum(dry(j)[0] for j in controls)
                row = {'paragraph_id': para['id'], 'page': para['page'], 'locus': tokens[i][2],
                       'source_id': tokens[i][1], 'position': i + 1,
                       'nearest_code': tokens[q][0], 'nearest_code_locus': tokens[q][2],
                       'nearest_code_distance': abs(i-q), 'target_dry': target_dry,
                       'control_count': len(controls), 'control_dry_count': local_dry,
                       'control_dry_fraction': local_dry / len(controls),
                       'same_line_control_count': len(candidates),
                       'same_line_dry_fraction': sum(dry(j)[0] for j in candidates) / len(candidates) if candidates else None}
                found.append(row)
        stored = result['readers'][reader]
        assert found == stored['targets']
        checks += 1
        summary = stored['summary']
        assert summary['total_exact_targets'] == total
        assert summary['eligible_targets'] == len(found)
        assert summary['eligible_physical_paragraphs'] == len({x['paragraph_id'] for x in found})
        assert summary['exclusions'] == excluded
        checks += 1
        assert abs(summary['target_dry_rate'] - sum(x['target_dry'] for x in found) / len(found)) < 1e-12
        assert abs(summary['control_dry_rate'] - sum(x['control_dry_fraction'] for x in found) / len(found)) < 1e-12
        assert abs(summary['target_minus_control'] - (summary['target_dry_rate'] - summary['control_dry_rate'])) < 1e-12
        assert summary['decision_gate'] == (len(found) >= 20 and summary['eligible_physical_paragraphs'] >= 20 and summary['target_minus_control'] >= .10)
        checks += 1
        assert sum(classes.values()) == summary['eligible_physical_paragraphs']
        code_capacity[reader] = classes
    assert result['decision'] == 'DOWNGRADE_TO_WEAK_CONTEXTUAL'
    checks += 1
    validation = {'status': 'PASS', 'checks': checks, 'readers': ['ZL3b', 'IT2a'],
                  'code_capacity_postresult_diagnostic': code_capacity,
                  'scope': 'source/hash and exact within-paragraph calibration; code-class capacity is a labelled postresult diagnostic, not a new gate or manuscript meaning'}
    (base / 'artifacts' / 'VALIDATION.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(json.dumps(validation))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
