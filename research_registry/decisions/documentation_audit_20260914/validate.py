"""Bounded documentation checks; no manuscript parsing or scientific validation."""
from pathlib import Path
import hashlib
import json
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def main():
    errors = []
    preserved = json.loads((HERE / 'PRESERVATION.json').read_text())
    for source, binding in preserved.items():
        path = ROOT / binding.get('preserved_as', source)
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != binding['sha256']:
            errors.append(f'preservation mismatch: {source}')
        if len(data) != binding['bytes'] or len(data.splitlines()) != binding['lines']:
            errors.append(f'preservation size mismatch: {source}')

    route_path = ROOT / 'VOYNICH_CURRENT_ROUTE.md'
    route = route_path.read_text()
    route_size = {'lines': len(route.splitlines()), 'bytes': len(route_path.read_bytes())}
    if route_size['lines'] > 80 or route_size['bytes'] > 6000:
        errors.append('route exceeds documented compactness limit')
    for pointer in (
        'docs/VOYNICH_RESEARCH_BRIEF.md', 'docs/VOYNICH_DATA_SCOPE.md',
        'research_registry/README.md',
        'research_registry/proposals/translation_programs_20260912/work/W89/REPORT.md',
        'research_registry/proposals/translation_programs_20260912/work/W93/REPORT.md',
    ):
        if pointer not in route:
            errors.append(f'missing mandatory route pointer: {pointer}')
    if 'docs/VOYNICH_RESEARCH_BRIEF.md' not in (ROOT / 'AGENTS.md').read_text():
        errors.append('AGENTS lacks mandatory knowledge entry')

    documents = [
        'AGENTS.md', 'VOYNICH_CURRENT_ROUTE.md', 'research_registry/README.md',
        'docs/VOYNICH_RESEARCH_BRIEF.md', 'docs/VOYNICH_DATA_SCOPE.md',
        'research_registry/decisions/documentation_audit_20260914/REPORT.md',
        'research_registry/decisions/documentation_audit_20260914/PEER_AUDIT.md',
    ]
    checked_links = 0
    for name in documents:
        source = ROOT / name
        for raw_target in re.findall(r'\[[^\]\n]*\]\(([^)\n]+)\)', source.read_text()):
            target = raw_target.strip().strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            path = (source.parent / unquote(parsed.path)).resolve()
            try:
                path.relative_to(ROOT)
            except ValueError:
                errors.append(f'link outside repository: {name}: {target}')
                continue
            # This run's generated receipt is written below.
            if path != HERE / 'VALIDATION.json' and not path.exists():
                errors.append(f'missing local link: {name}: {target}')
            checked_links += 1

    work = ROOT / 'research_registry/proposals/translation_programs_20260912/work'
    program_reports = [f'P{number:02}/REPORT.md' for number in range(1, 31)]
    for name in program_reports:
        if not (work / name).is_file():
            errors.append(f'missing first-pass report: {name}')

    result = {
        'status': 'PASS' if not errors else 'FAIL',
        'scope': 'document preservation, local links, entry pointers, route size, report existence only',
        'scientific_revalidation': False,
        'manuscript_data_opened': False,
        'preserved_sources_checked': len(preserved),
        'changed_entry_documents_checked': documents,
        'local_markdown_links_checked': checked_links,
        'route': route_size,
        'first_pass_reports_present': sum((work / name).is_file() for name in program_reports),
        'errors': errors,
    }
    (HERE / 'VALIDATION.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
