# YOLO experiment layout

GDT001–GDT336 remain in the repository root as a byte-frozen compatibility
island. Their scripts, validators, reports, and hash-bound artifacts have many
same-directory and cross-experiment dependencies and must not be moved casually.

Starting with GDT337, every new experiment lives at:

```text
experiments/yolo/gdtNNN_short_slug/
├── README.md
├── METHOD.md
├── src/
│   ├── run.py
│   └── validate.py
└── artifacts/
    └── README.md
```

Create the next directory with:

```bash
python3 tools/new_yolo_experiment.py short_slug
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
verifies the generated repository indexes.
