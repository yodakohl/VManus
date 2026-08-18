# VManus

VManus is a provenance-preserving research workspace for structural analysis of
the Voynich manuscript. It does **not** contain a confirmed translation,
plaintext, language identification, phonetic alphabet, or English lexicon.

For a concise public account of established results and failures, start with
[`HIGH_LEVEL_RESULTS.md`](HIGH_LEVEL_RESULTS.md).

## Navigation

For scientific work, read these in order:

1. `VOYNICH_ACTIVE_STATE.md`
2. `experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv`
3. `experiments/semantic_assumptions/grammar/CONFIRMED_GRAMMAR.md`
4. `experiments/semantic_assumptions/CLOSED_ROUTE_FAMILIES.tsv`

For repository navigation, use:

- [`experiments/EXPERIMENT_INDEX.md`](experiments/EXPERIMENT_INDEX.md): human
  index of every GDT experiment, newest first.
- [`experiments/EXPERIMENT_INDEX.tsv`](experiments/EXPERIMENT_INDEX.tsv): full
  machine-readable paths, dependencies, sizes, runners, validators, and
  artifacts.
- [`experiments/yolo/README.md`](experiments/yolo/README.md): layout required
  for GDT337 and later.

The active state and ledger are authoritative but no longer short documents;
the generated index is the practical routing layer. The curated pre-reset
primary-evidence subset remains under `archive_pre_reset_2026-08-06/` with a
SHA-256 manifest.

## Repository layout

```text
transcription/                         canonical manual source material
voynich-manuscript-decoding-artifacts/ parser/formal artifacts
experiments/semantic_assumptions/      active claims, grammar, and source tables
archive_pre_reset_2026-08-06/          curated historical primary evidence
candidates/                            reproducible candidate exports
experiments/yolo/                      structured GDT337+ experiments
tools/                                 repository navigation/scaffolding tools
```

GDT001–GDT336 remain as a legacy flat compatibility island at repository root.
They are hash-bound and heavily cross-dependent; moving them piecemeal would
break published reproduction paths. New experiments must not extend that flat
layout.

Create the next experiment with:

```bash
python3 tools/new_yolo_experiment.py short_slug
python3 tools/build_experiment_index.py
python3 tools/build_experiment_index.py --check
```

## Generated and local data

The large `.gdt001/`, `.gdt176/`, and `__pycache__/` trees are ignored local
workspaces, not published repository content. They may contain recreatable
virtual environments, downloaded corpora, and external repository caches.
Do not commit them.

Large scientific outputs already committed for GDT001–GDT336 remain frozen.
For new work, publish the method, source, validator, compact result, hashes, and
only the tables needed for reproduction. Prefer a frozen seed and generator to
an exhaustive generated table when the table can be reproduced exactly.

Canonical manual transcription and parser sources remain in `transcription/`
and `voynich-manuscript-decoding-artifacts/`. Use `./vpy` for Python work.
Material findings and their reproducible experiment source are published to
the public repository after validation and a staged-tree privacy scan.
