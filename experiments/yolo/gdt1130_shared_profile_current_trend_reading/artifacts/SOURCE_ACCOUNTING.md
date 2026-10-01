# GDT1130 source accounting

Prepared only from the two already exposed, registered ring/body JSON packets.
All original packet objects are retained in `SOURCE.json.raw_packets`; no TSV,
target image, new query or access admission was used. All four registered inputs
are hash checked; GDT1051 supplies unchanged formal annotations only.

| Reader | f68r2.6 | f68r2.31 | f89v1.13–20 | Total |
|---|---:|---:|---:|---:|
| IT2a | 8 | 11 | 78 | 97 |
| ZL3b | 8 | 12 | 75 | 95 |
| RF1b | 8 | 11 | 77 | 96 |

There are six ring units,24 body units and288 unique native positions. Physical
leaves68/89 are exposed development material; independent confirmation leaves:0.

## Source format

`src/SOURCE.json.groups` is the canonical author input, ordered IT/ZL/RF then
ring/body/native order. Each row has `source_group_id`, `edition`, `locus`,
`part`, `index`, unchanged string `source_group_index`, `raw` and
`ivtff_group_raw`, separators, full `native_metadata`, literal uncertainty,
and an exact `source_pointer` to the original packet array/position.
IDs are derived as `EDITION|LOCUS|GNNN`; the original packets have no ID column.
`units` retains every original six ring/24 body unit plus ordered native IDs.
`raw_packets` retains every original metadata/query/flag field losslessly.
Formal annotations are labeled `formal_annotation_GDT1051` and have no meanings.

Cached ring position rows contain no native paragraph flags or group-count
field: their corresponding values are null, not invented. Prose native flags
and counts are retained verbatim. RF body has no complete native paragraph
flags and stays a comparison window. Literal entities/brackets/braces remain
raw; uncertain spaces are neither joined nor normalized.

## Bounded validator criteria

`python src/check_accounts.py --prepare-source` reproduces the source from the
registered JSONs. Final author validation runs only after root releases account
and constructor hashes. It checks exact coverage/source mapping, unchanged
constructor pins, finite declaration limits, repeated dictionary identity,
explicit constant/reference/part-effect declarations and honest barriers.
Declared non-null shared parts are bookkeeping claims, not validated meanings:
manual review must establish same semantic interface and actual effects on a
retained owner/property/basis. No automatic semantic winner or complete reading
certification is produced. Preparation/checker budget:15 active minutes;
root owns final scientific review, ledger and publication.

Final validation is recorded in `AUTHOR_VALIDATION.json` and
`AUTHOR_VALIDATION.md`:67 accounting checks pass at the root-released hashes.
It retains A's partial fragment statuses and B's distinction between operational
completion and its exact candidate's reported contradiction. B's interpreted
repeat inventory excludes three repeated unassigned raw forms; these remain
UNKNOWN/BLOCKED source obligations, not dictionary meanings.

The final checker accepts `--final-a`, `--freeze-a`, `--final-b`, `--freeze-b`
with the released SHA256 values. A's constructor file is
`artifacts/A_CONSTRUCTORS.json`; B's is `src/B_CONSTRUCTORS.json`. It replays
the frozen B materializer and reading writer in a temporary copy and checks
exact output bytes while preserving all original author artifacts. This checks
engineering reproducibility, not scientific or semantic truth.
