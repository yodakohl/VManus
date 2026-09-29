#!/usr/bin/env python3
"""Join frozen visual notes and fixed source names; no image decoding."""
import csv
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / 'experiments/yolo/gdt1087_botanical_blind_name_audit'
SOURCE = ROOT / 'experiments/yolo/gdt1062_schechter_plant_label_source_alignment/src/claims.tsv'


def read_tsv(path):
    with path.open(newline='') as file:
        return list(csv.DictReader(file, delimiter='\t'))


def index(rows, key):
    result = {}
    for row in rows:
        value = row[key]
        if value in result:
            raise ValueError(f'duplicate {key}: {value}')
        result[value] = row
    return result


def main() -> int:
    claims = index(read_tsv(SOURCE), 'page')
    admissions = index(read_tsv(BASE / 'src/PAGE_ADMISSIONS.tsv'), 'folio')
    visuals = index(read_tsv(BASE / 'artifacts/BLIND_VISUAL.tsv'), 'folio')
    decisions = index(read_tsv(BASE / 'src/ASSESSMENTS.tsv'), 'folio')
    sources = index(read_tsv(BASE / 'artifacts/SOURCE.tsv'), 'folio')
    pages = set(claims)
    if len(pages) != 23 or any(set(x) != pages for x in (admissions, visuals, decisions, sources)):
        raise ValueError('full 23-page scope mismatch')
    fields = ['folio', 'first_group_it2a', 'public_plant', 'prior_exposure',
              'observed_traits', 'blind_candidate_taxa', 'blind_alternatives',
              'blind_confidence', 'decision', 'supporting_traits',
              'contrary_traits', 'reason', 'alternative', 'canvas_id', 'image_sha256']
    output = BASE / 'artifacts/RESULTS.tsv'
    with output.open('w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        for folio in sorted(pages, key=lambda s: (int(s[1:-1]), s[-1])):
            c, a, v, d, src = claims[folio], admissions[folio], visuals[folio], decisions[folio], sources[folio]
            if d['decision'] not in {'SUPPORT', 'CONFLICT', 'UNDECIDABLE'}:
                raise ValueError(f'bad decision: {folio}')
            if d['decision'] == 'SUPPORT' and len([x for x in d['supporting_traits'].split(';') if x.strip()]) < 2:
                raise ValueError(f'support needs two traits: {folio}')
            writer.writerow(dict(folio=folio, first_group_it2a=c['eva_label'],
                public_plant=c['claimed_plant'], prior_exposure=a['prior_exposure'],
                observed_traits=v['observed_traits'], blind_candidate_taxa=v['candidate_taxa'],
                blind_alternatives=v['alternatives'], blind_confidence=v['confidence'],
                decision=d['decision'], supporting_traits=d['supporting_traits'],
                contrary_traits=d['contrary_traits'], reason=d['reason'],
                alternative=d['alternative'], canvas_id=src['canvas_id'],
                image_sha256=src['sha256']))
    print(output.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
