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
        path = ROOT / item['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError(f'preregistration/input hash changed: {path}')
    source = json.loads((ROOT / lock['input']['path']).read_text())
    quality = re.compile(r'^qo(?:k|t)(ch|sh)[a-z]*$')
    plain_five = re.compile(r'^[a-z]{5}$')
    result = {'experiment': 'GDT1053', 'readers': {}}
    for reader in ('ZL3b', 'IT2a'):
        records = []
        exclusions = {'no_quality_code': 0, 'no_five_character_control': 0}
        target_total = 0
        for para in source[reader]:
            flat = []
            for line in para['lines']:
                for word, source_id in zip(line['words'], line['source_ids']):
                    flat.append({'word': word, 'source_id': source_id, 'locus': line['locus']})
            targets = [i for i, x in enumerate(flat) if x['word'] == 'chody']
            if not targets:
                continue
            target_total += len(targets)
            codes = [(i, quality.fullmatch(x['word']).group(1)) for i, x in enumerate(flat) if quality.fullmatch(x['word'])]
            if not codes:
                exclusions['no_quality_code'] += len(targets)
                continue
            def nearest(index):
                return min(codes, key=lambda code: (abs(code[0] - index), code[0]))
            controls = [i for i, x in enumerate(flat) if plain_five.fullmatch(x['word']) and x['word'] != 'chody' and not quality.fullmatch(x['word'])]
            if not controls:
                exclusions['no_five_character_control'] += len(targets)
                continue
            control_dry = {i: int(nearest(i)[1] == 'ch') for i in controls}
            for i in targets:
                same_line = [j for j in controls if flat[j]['locus'] == flat[i]['locus']]
                code_index, code_class = nearest(i)
                records.append({
                    'paragraph_id': para['id'], 'page': para['page'], 'locus': flat[i]['locus'],
                    'source_id': flat[i]['source_id'], 'position': i + 1,
                    'nearest_code': flat[code_index]['word'], 'nearest_code_locus': flat[code_index]['locus'],
                    'nearest_code_distance': abs(i - code_index), 'target_dry': int(code_class == 'ch'),
                    'control_count': len(controls), 'control_dry_count': sum(control_dry.values()),
                    'control_dry_fraction': sum(control_dry.values()) / len(controls),
                    'same_line_control_count': len(same_line),
                    'same_line_dry_fraction': (sum(control_dry[j] for j in same_line) / len(same_line)) if same_line else None,
                })
        n = len(records)
        target_rate = sum(x['target_dry'] for x in records) / n if n else None
        control_rate = sum(x['control_dry_fraction'] for x in records) / n if n else None
        same = [x for x in records if x['same_line_control_count']]
        same_delta = (sum(x['target_dry'] - x['same_line_dry_fraction'] for x in same) / len(same)) if same else None
        summary = {'total_exact_targets': target_total, 'eligible_targets': n,
                   'eligible_physical_paragraphs': len(set(x['paragraph_id'] for x in records)),
                   'exclusions': exclusions, 'target_dry_rate': target_rate,
                   'control_dry_rate': control_rate,
                   'target_minus_control': target_rate - control_rate if n else None,
                   'same_line_targets_with_control': len(same), 'same_line_target_minus_control': same_delta}
        summary['decision_gate'] = bool(n >= 20 and summary['eligible_physical_paragraphs'] >= 20 and summary['target_minus_control'] >= 0.10)
        result['readers'][reader] = {'summary': summary, 'targets': records}
    result['decision'] = 'RETAIN_MEDIUM_WORKING_ONLY' if all(result['readers'][r]['summary']['decision_gate'] for r in ('ZL3b','IT2a')) else 'DOWNGRADE_TO_WEAK_CONTEXTUAL'
    out = base / 'artifacts' / 'RESULT.json'
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'decision': result['decision'], 'summaries': {r: result['readers'][r]['summary'] for r in result['readers']}}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
