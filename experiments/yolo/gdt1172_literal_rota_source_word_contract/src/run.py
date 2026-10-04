#!/usr/bin/env python3
from pathlib import Path
import json
from collections import Counter

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())


def main() -> int:
    experiment = Path(__file__).resolve().parents[1]
    data = json.loads((experiment / 'artifacts/SOURCE_WORDS.json').read_text())
    counts = Counter()
    by_line = {}
    for line in data['lines']:
        n = len(line['expanded_word_labels'])
        by_line[line['id']] = n
        counts[line['region']] += n
    index = {line['id']: line for line in data['lines']}
    for join in data['joins']:
        left, right = index[join['left_line']], index[join['right_line']]
        assert left['region'] == right['region']
        assert left['expanded_word_labels'][-1] == join['left_label']
        assert right['expanded_word_labels'][0] == join['right_label']
        counts[left['region']] -= 1
    assert not data['unresolved_word_count_alternatives']
    total = sum(counts.values())
    target = data['target_contract']['required_word_groups']
    result = {
        'experiment_id': 'GDT1172',
        'status': 'COMPLETE_LITERAL_INSTRUCTION_COUNT_CONTRADICTED' if total != target else 'COUNT_SURVIVES_ONLY',
        'physical_line_fragments': by_line,
        'cross_line_words_rejoined': len(data['joins']),
        'region_word_counts': dict(counts),
        'source_instruction_words': total,
        'fixed_ZL_projection_groups': target,
        'source_minus_target': total-target,
        'paired_alternatives': {
            'English_lyric_and_complete_instruction': 'instruction_conjunct_failed' if total != target else 'unresolved',
            'Latin_contrafactum_and_complete_instruction': 'instruction_conjunct_failed' if total != target else 'unresolved'
        },
        'whole_black_box_alone_is_not_registered_complete_source': counts['black'] == target,
        'lyric_count_and_recurrence_tested': False,
        'source_word_key_or_underlay_fitted': False,
        'confirmed_Voynich_words': 0,
        'claim_scope': 'Declared complete-copy law and ZL projection only; no music/source identity, general music refutation or independent paleographic confirmation.'
    }
    (experiment / 'artifacts/RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
