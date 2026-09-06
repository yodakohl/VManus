"""Small companion CLI for navigation and explicitly task-scoped preflight."""
from __future__ import annotations

import argparse
import sys

from tools.experiment_lookup import lookup_experiments, render_lookup


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] == 'ideas':
        from tools.research_registry import main as ideas_main
        return ideas_main(arguments[1:])
    parser = argparse.ArgumentParser(prog='vmanus-work')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('ideas', help='scalable research memory: search, duplicates, reconsider, show')
    lookup = commands.add_parser('lookup', help='compact metadata pointers; opens no manuscript data')
    lookup.add_argument('identifiers', nargs='+')
    lookup.add_argument('--json', action='store_true', dest='json_output')
    locate = commands.add_parser('locate', help='exact-ID tracked Markdown filenames only; reads no report contents')
    locate.add_argument('identifier')
    staged = commands.add_parser('check-staged', help='explicit task scope, not a full global check',
                                 description='Check exact staged privacy/scope and selected experiment bindings. '
                                 'Does not run validators or replace ./vmanus-exp check --all.')
    staged.add_argument('--experiment', action='append', default=[], metavar='GDTNNN',
                        help='select a structured experiment (GDT337+); repeat as needed')
    staged.add_argument('--include', action='append', default=[], metavar='PATH',
                        help='allow an exact repository-relative non-experiment path; repeat as needed')
    args = parser.parse_args(argv)
    if args.command == 'lookup':
        try:
            sys.stdout.write(render_lookup(lookup_experiments(args.identifiers), json_output=args.json_output))
            return 0
        except ValueError as exc:
            parser.error(str(exc))
    if args.command == 'locate':
        from tools.report_locator import locate_report_paths, render_locations
        try:
            sys.stdout.write(render_locations(args.identifier, locate_report_paths(args.identifier)))
            return 0
        except ValueError as exc:
            parser.error(str(exc))
    from tools.work_preflight import main as check_staged
    forwarded = []
    for option in ('experiment', 'include'):
        for value in getattr(args, option):
            forwarded.extend(['--' + option, value])
    return check_staged(forwarded)


if __name__ == '__main__':
    raise SystemExit(main())
