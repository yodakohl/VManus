# GDT604 portable reproduction bundle

This bundle reproduces the frozen 36-key target attack and its held-folio
decision without machine-specific paths or scratch-module imports.  It does
not claim a Voynich reading: the frozen result is
`LM_DRIVEN_PSEUDOTEXT_NO_READING`.

## Requirements

- A VManus checkout containing both `AGENTS.md` and `.git`; the root is found
  dynamically from the script location and then the current directory.
- The guarded `vmanus-exp query-tsv` command, the pinned GDT327 allow-list,
  and the repository transcription available in that checkout.
- CPython 3.12.3 and NumPy 1.26.4 for byte-for-byte numeric reproduction.
  Python 3.11+ with a compatible NumPy should reproduce the logic, but exact
  float JSON hashes are certified only on the pinned environment.
- Network access once to fetch the seven hash-pinned public reference files,
  or an existing reference directory containing those exact bytes.
- Nine workers are the certified command; one through 32 are accepted.

## Exact execution order

Run from anywhere inside the VManus checkout, with this directory as the
current directory:

```sh
python3 src/fetch_references.py --output-dir references
python3 src/validate_bundle.py --bundle-root . --live-target-check
python3 src/run_all.py \
  --reference-dir references \
  --frozen-segmentation-dir artifacts \
  --output-dir reproduced \
  --workers 9
python3 src/validate_bundle.py \
  --bundle-root . \
  --artifact-dir reproduced \
  --live-target-check \
  --output reproduced/gdt604_validation.json
```

`run_all.py` creates an auto-cleaned temporary working directory.  Only the
frozen outputs are written to `--output-dir`.  A diagnostic directory can be
retained explicitly with `--keep-work-dir`, but it is not part of the binding
inventory and must not be published.

## Certified run time

On the certification host with nine workers, the full guarded-query,
36-key-fit, 36-held-evaluation, calibration, and appendix run took 111.55 s
wall time, 849.22 s CPU time, and 93,952 KiB peak resident memory.  Reference
fetching took 4.6 s on the available network.  Static validation is below one
second; live guarded-query validation adds roughly one second.  Hardware and
network variation can change these figures.

## Why segmentation is a frozen input

The original segmentation runner used Python set iteration before
insertion-sensitive `Counter.most_common()` tie resolution.  Its already
published U=115/132/138 files are therefore stable byte-bound experimental
freezes, but a fresh legacy refit is not guaranteed to choose the same tied
components under a different hash seed.  The complete 36-key attack is
reproducible from the pre-key U=138 freeze, and the runner re-queries and
revalidates the target and 68/23 split before fitting keys.

`portable_factorizer.py` preserves the method for audit.  A future canonical
tie-break refit would be a new experiment and must not silently replace these
freezes.

## Validator scope and remaining limits

The validator checks file hashes; the 180-page, 91-folio, 68/23 split; guarded
target/train/held bindings; segmentation capacities and coverage fields;
absence of held fields in the train-only freeze; all 36 unique key jobs; 414
codes; the six-homophone capacity; reference bindings; all held decision gates;
all 60 top-line rows; calibration sign; relative paths; selector safety; and
absence of private absolute paths, scratch keylib imports, or bytecode caches.

With `--live-target-check`, it reruns the guarded query and split.  It does not
open sealed rows, validate an oracle alignment, establish corpus historical
representativeness, or repair the legacy segmentation tie-order defect.  It
also cannot prove numerical byte identity on unpinned Python/NumPy platforms.

