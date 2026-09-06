# GDT860 — literal entity mentions beyond f56r.1

**ADDITIONAL_TEXT_LOCATORS_ONLY.** The fixed safe179 census finds two additional
loci: `@168;` at f100r.12 in ZL/RF, and `@167;` at f114r.1 in RF. Only the
already known f56r.1 has both entity strings mentioned in the same line.
These are text locators, not demonstrated physical glyphs or upper links.

| Reading | @167; | @168; | Distinct loci / physical leaves | Outside-known mentions | Outside loci |
|---|---:|---:|---:|---:|---|
| ZL3b | 1 | 2 | 2 / 2 | 1 | f100r.12 |
| RF1b | 2 | 2 | 3 / 3 | 2 | f100r.12, f114r.1 |
| IT2a | 0 | 0 | 0 / 0 | 0 | none |

All seven literal mentions, with zero-based raw character offsets:

| Reading | Locus / source group index | Entity / offset | Complete raw group | Left / right separator |
|---|---|---|---|---|
| RF | f100r.12 / 5 | @168; / 11 | `{c@132;h}da@168;oto` | DEFINITE_SPACE / DEFINITE_SPACE |
| RF | f114r.1 / 8 | @167; / 1 | `o@167;aiin` | DEFINITE_SPACE / DEFINITE_SPACE |
| RF | f56r.1 / 1 | @167; / 1 | `o@167;chal` | LINE_START / DEFINITE_SPACE |
| RF | f56r.1 / 2 | @168; / 5 | `chchs@168;y` | DEFINITE_SPACE / DEFINITE_SPACE |
| ZL | f100r.12 / 6 | @168; / 0 | `@168;oto` | UNCERTAIN_SMALL_SPACE / DEFINITE_SPACE |
| ZL | f56r.1 / 1 | @167; / 1 | `o@167;chal` | LINE_START / DEFINITE_SPACE |
| ZL | f56r.1 / 2 | @168; / 5 | `chchs@168;y` | DEFINITE_SPACE / DEFINITE_SPACE |

Source IDs are the literal reading/locus/Gnnn identifiers preserved in
HITS.json. Physical leaf keys are f56/f100 in ZL and f56/f100/f114 in RF.
Both known f56r.1 lines have ordered mentions @167; then @168;. Each other
hit-bearing line has one mention. IT contributes no hit-bearing line.
The complete five reader-lines and every ordered mention are retained in
SOURCE_LINES.json, with all metadata and separators. All observed mentions
have kind P; selection itself covered all kinds without a prose-only filter.

RF f100r.12's hit group contains brace notation around a different substring;
that is the one raw-group annotation flag. RF f114r.1's hit group has no such
flag. ZL f100r.12 instead has an uncertain small space before its entity group.
These differences remain unnormalized. The scanner's annotation-character
flag does not adjudicate the notation or assert ambiguity of the entity itself.
More generally, mentions inside alternatives need not represent two physical
glyphs. IT's zero literal mentions can reflect notation convention and do not
establish physical absence. Alternate readings are not independent copies.

Independent literal-find validator checked all seven occurrence offsets,
source records, full-line parity, frozen source hashes, scope and counts;
PASS. Regex runner replay is byte-identical. Exact-prefix rejection,
multiple/unmatched/alternative mention fixtures passed before data. No image
was opened, no visual admission granted, no entity replaced with p/f/t, and
no paired physical relation or meaning inferred. Additional imaging or tests
require their own decision; this census ends here.

Public preregistration64a428f1 was pushed08:06:06UTC on2026-09-06. Run,
independent validation and replay completed immediately afterward. Report and
handoff completed before the08:10:31 deadline of the10-minute total budget
(start08:00:31UTC).
