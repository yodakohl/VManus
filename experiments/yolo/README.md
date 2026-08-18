# YOLO experiment layout

GDT001–GDT336 remain in the repository root as a byte-frozen compatibility
island. Their scripts, validators, reports, and hash-bound artifacts have many
same-directory and cross-experiment dependencies and must not be moved casually.

Starting with GDT337, every new experiment lives at:

```text
experiments/yolo/gdtNNN_short_slug/
├── README.md
├── METHOD.md
├── experiment.json
├── src/
│   ├── run.py
│   └── validate.py
└── artifacts/
    └── README.md
```

Create the next directory with:

```bash
./vmanus-exp new short_slug
```

Use `--dry-run` to preview the paths. New scripts must discover the repository
root explicitly; they must not treat their own experiment directory as the
workspace root. Cross-experiment inputs should be named and hash-bound in the
method/result rather than reached through copied files.

Keep the committed artifact set compact: method, runner, validator, result,
validation, and the smallest tables needed to reconstruct the finding. Store a
seed, generator version, summary, and digest instead of an exhaustive null table
when exact regeneration is practical. This is a layout rule, not permission to
remove any already published artifact.

`tools/build_experiment_index.py --check` enforces the GDT337+ path rule and
verifies the generated repository indexes. `./vmanus-exp check` additionally
validates every manifest, bound hash, sealed-data declaration, staged path, and
privacy rule.

## Manifest lifecycle

`experiment.json` is the machine-readable contract. Fill its question, claim
ceiling, dependencies, commands, and input bindings before scoring. Every
scientific input/output with a non-null digest is checked byte-for-byte. A
manifest marked `validation.status: PASS` must bind every input/output and name
its validation artifact.

Use:

```bash
./vmanus-exp manifest experiments/yolo/gdtNNN_short_slug
./vmanus-exp run experiments/yolo/gdtNNN_short_slug
./vmanus-exp validate experiments/yolo/gdtNNN_short_slug
./vmanus-exp publish experiments/yolo/gdtNNN_short_slug
```

`publish` is deliberately non-mutating: it validates the exact staged tree and
prints a pass/failure; it does not commit or push.

## Sealed-source loading

New experiments that read global TSV sources must use `GuardedTSV` from
`tools.vmanus_experiment`. It extracts the frozen selector field by tab offsets,
rejects/skips forbidden or non-whitelisted rows, and only then parses the rest
of an admitted row. This prevents a global table from transiently materializing
sealed formal payload merely because the final joined output is filtered.
