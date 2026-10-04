#!/usr/bin/env python3
from pathlib import Path
import json
import hashlib
import re

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())


def main() -> int:
    exp = Path(__file__).resolve().parents[1]
    a = exp / 'artifacts'
    words = json.loads((a/'SOURCE_WORDS.json').read_text())
    result = json.loads((a/'RESULT.json').read_text())
    lock = json.loads((a/'PREREG_LOCK.json').read_text())
    for relative, digest in lock['files'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == digest, relative
    assert hashlib.sha256((a/'HARLEY978_F11V.jpg').read_bytes()).hexdigest() == words['source_sha256']
    # Independently assemble written words from line fragments, not runner counts.
    assembled = {}
    for region in ('black','upper_red','lower_red'):
        text = ' '.join(' '.join(line['expanded_word_labels']) for line in words['lines'] if line['region']==region)
        text = text.replace('~ ~','')
        assert '~' not in text
        assembled[region] = text.split()
    assert assembled['black'][7] == 'paucioribus'
    assert 'Tacentibus' in assembled['black']
    # Independent old source checks complete R01-R07 coverage. Keep its
    # intra-word variants separate from the native count.
    source = (ROOT/'research_registry/work_batches/ten_hours_20260915/ROTA_SOURCE_EVENTS.md').read_text()
    rule_texts = re.findall(r'^\*\*R0[1-7] — .*?\*\* (.+)$', source, re.M)
    assert len(rule_texts)==7
    old_groups = [re.findall(r'[A-Za-z]+', t) for t in rule_texts]
    allowed = {('repetat','repetit'),('dicat','dicit')}
    flat = [t for line in old_groups for t in line]
    manual = sum(assembled.values(), [])
    assert len(flat)==len(manual)
    for original,current in zip(flat,manual):
        assert original==current or (original,current) in allowed, (original,current)
    counts={k:len(v) for k,v in assembled.items()}
    assert counts == result['region_word_counts']
    assert sum(counts.values())==result['source_instruction_words']
    assert result['fixed_ZL_projection_groups']==62
    assert result['source_minus_target']==sum(counts.values())-62
    assert result['status']=='COMPLETE_LITERAL_INSTRUCTION_COUNT_CONTRADICTED'
    assert all(v=='instruction_conjunct_failed' for v in result['paired_alternatives'].values())
    assert not result['lyric_count_and_recurrence_tested']
    out={'status':'PASS','source_image_hash':words['source_sha256'],'native_manual_counts':counts,'old_rules_word_counts':[len(w) for w in old_groups],'registration_hashes_unchanged':True,'independent_implementation':'No runner import; reassembles carried words and independently extracts all seven prior source clauses. Same author and source exposure; no independent paleographic review.','confirmed_Voynich_words':0}
    (a/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
