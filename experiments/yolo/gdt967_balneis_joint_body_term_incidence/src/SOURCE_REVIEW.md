# Independent review of the 13-family De balneis source inventory

2026-09-15. Separate source-only audit begun 10:00 UTC, 15-minute bound.
Owner: independent reviewer. No target strings, carrier counts, fits, new
admissions or source edits enter this review. Producer owns the inventory and
its corrections. Corrections described here occurred before registration or
target fitting.

**Status: PASS for corrected v2 source counts and witnesses.** The initial draft
remains rejected. Final hashes and the precise validation scope are below.

## Source and scope

Primary: the complete ALIM553 text in `balneis_cache/ALIM553.txt`, SHA-256
`397968f02fc5faf54161f2c0df9e7557f96d36e649a27a140e64c2cfe0c69ecd`.
The download is <https://alim-admin.unisi.it/download_txt?id=553>.
The raw file has 404 physical lines. Its spelling, editorial brackets,
punctuation and capitalization are preserved in occurrence witnesses.

The operative columns are AQUA, HEAD, STOMACH, OCULUS, LIVER, SPLEEN, SKIN,
LUNG, KIDNEY, BLADDER, WOMB, NERVOUS_TISSUE and HYDROPS. There is **no EAR
column**. HEAD denotes the prospectively specified clinical caput family;
the civic caput in I is excluded by sense. These are bounded source-term
families, not an exhaustive anatomy or disease ontology. Background polarity
and context-role fields are not operative for the proposed incidence test.

## Retained initial draft and deviations

The initial files inspected before correction had these hashes:

- `BALNEIS_BODY_SOURCE.json`:
  `b2db4bda3aa2abd9a2b61c631e0f303484e8cc55f6d9d92f0e4a4285cb2b2238`
- `BALNEIS_BODY_SOURCE.md`:
  `d0b3bc43df29a5de03628429292bf64010e9940872f7aeae1dce630745b9d21d`

The initial JSON claimed `SOURCE_ONLY_AUDITED`, but the independent reconstruction
found one wrong record boundary, one extra occurrence and six omitted occurrences.
It is not an approved scientific freeze.

| Change | Record | Source line | Zero-based Unicode offset | Exact token |
|---|---:|---:|---:|---|
| Remove dedication token wrongly included in AQUA | 30 assigned incorrectly; actually 31 | 370 | 16456 | aquis. |
| Add HEAD variant | 17 | 201 | 9075 | capitus |
| Add HEAD inflection | 17 | 206 | 9283 | capiti |
| Add STOMACH spelling variant | 32 | 387 | 17164 | stomacus |
| Add LIVER spelling variant | 7 | 79 | 3899 | Jecur. |
| Add LIVER inflection | 32 | 385 | 17072 | Iecoris |
| Add LIVER spelling variant | 33 | 397 | 17612 | Jecur. |

Record XXX Spelunca must span lines **353–364**, not 353–376. XXXI Dedicatio
starts at 365 and ends at 376. XXXII starts at 377. Omitting the dedication's
header before deriving intervals wrongly lets the preceding bath absorb its
body. The correct operation is to identify and bound **all 33 numbered heads
first**, and only then remove record 31 from the operative bath list.

All retained initial-draft occurrence spellings, Unicode offsets, source lines,
full physical-line witnesses and whitespace-token indices matched the independent
reconstruction. `line_column` values consistently use zero-based columns; the
schema should explicitly state this rather than leave the convention implicit.

## Independent reconstruction

The reviewer did not import the producer's parser or family matcher. The audit
enumerated all line-initial Roman-numbered bracketed headings from the original
source, asserted the sequence I through XXXIII, and bounded each heading with
the next heading before excluding XXXI. It then scanned every whitespace token
of each eligible complete interval. Lowercasing and removal of punctuation and
bracket delimiters were used only to look up the finite aliases below; original
tokens and offsets were retained separately. No source text was rewritten.

For each matched token the audit reconstructed record identity, one-based line,
zero-based character offset in the full Unicode string, zero-based column,
zero-based whitespace-token index within the full physical line, exact token
including punctuation, and exact source line. Offsets are **characters, not
UTF-8 byte offsets**. Tokens in verse beginning on a heading line retain their
indices in that entire physical line, including the printed header tokens.

Boundary cross-checks include the exceptional one-line Juncare record V at line
61, the standalone XI heading at 122 with its body through 134, the 14-line XX
record at 231–244, the XXX/XXXI separation above, and the 16-line XXXII record
at 377–392. All 32 complete baths are retained; prologue and dedication are not
silently added to adjacent records.

## Expected complete counts and aliases

The following totals were independently reconstructed from all 32 bodies.
Forms shown here are classification keys after the stated lookup projection;
the inventory must retain each original printed witness.

| Family | Complete explicit lookup forms | Tokens | Records |
|---|---|---:|---:|
| AQUA | aqua, aque, aquam, aquas, aquis, unda, undam, undis, limpha | 82 | 31 |
| HEAD | caput, capitis, capitus, capiti; exclude civic caput at I.23 | 12 | 10 |
| STOMACH | stomachi, stomachique, stomacho, stomachum, stomacus | 13 | 13 |
| OCULUS | oculis, oculorum, oculos | 9 | 7 |
| LIVER | epar, iecoris, iecur, jecur | 9 | 9 |
| SPLEEN | splem, splene, splenis, splenisque | 7 | 7 |
| SKIN | cute, cutim, cutis | 8 | 6 |
| LUNG | pulmonem, pulmoni, pulmonis | 5 | 5 |
| KIDNEY | renes, renibus | 5 | 5 |
| BLADDER | vesicam, vesicas, vesice | 3 | 3 |
| WOMB | matrice, matricem, matrices, matrix | 4 | 3 |
| NERVOUS_TISSUE | neruis, neruos | 4 | 3 |
| HYDROPS | ydropicis, ydropicos, ydropisis | 5 | 5 |
| **Total** | | **166** | **32-record scope** |

The initial totals were AQUA83, HEAD10, STOMACH12 and LIVER6; the other nine
family totals already agreed. Correcting those four columns changes the total
from 161 to 166. Counts of tokens and counts of records must remain separate:
for example WOMB has four tokens in three records, and SKIN eight in six.

The corrected 32-by-13 multiplicity matrix has **31 distinct row signatures**.
XI Sancta Anastasia and XXIV Sanctus Georgius both have AQUA=4 and zero in every
other operative column. A joint assignment therefore needs two distinct target
paragraphs with that signature, but this inventory cannot distinguish their
bath identities. No unique identity should be inferred from identical source
rows. Every other complete source row differs under the fixed 13 columns.

## Exclusions and interpretation conditions

- AQUA's declared noun family excludes `aquosas` at II.28 and `lymphato` at
  XXII.266. Water-related adjectives or a diluted drink are not silently
  equated with a counted noun token.
- OCULUS deliberately excludes the ten printed lumen-family witnesses. Some
  concern eyes or sight clinically; others concern a witness's own sight.
  Their exclusion defines the lexical family and is not evidence that the
  source contains only nine references to eyes or vision.
- HEAD excludes I.23's civic use. `capue` beside it is also retained in the
  exclusion ledger, but is not itself a caput-family match. Other nonclinical
  terms beginning with `cap` do not enter: `capit` at XIV.162, `capax` at
  XXIII.272 and `capillos` at XXXII.391. Head-related synonyms outside the
  declared caput family are not automatically added.
- A prefix-neighbor search also rejects the adverb `unde` as UNDA and
  `renouabis`/`renouabit` as KIDNEY. The final matcher must use whole declared
  forms, not stem-prefix searching.
- Editorial expansions such as `stomachiq[u]e` and `splenisq[ue]` remain exact
  printed tokens. Their declared family membership does not erase the original
  brackets or assert a global spelling/phonological normalization.
- LIVER groups the explicitly declared epar/iecur forms and variants; AQUA
  groups the declared aqua/unda/limpha forms. Consequently a blanket claim of
  "no synonym collapse" would be misleading. The correct ceiling is that only
  the specified aliases are grouped, with no additional synonym merging.
- NERVOUS_TISSUE is a family identifier with historical nerve/sinew breadth
  unresolved. It is not a recovered modern physiological category.

These choices are compatible with a prospective sense-specific carrier model.
They do not permit post-fit reclassification: all occurrences of a selected
target carrier still count under the frozen whole-group or within-group-piece
rule. Source-family exclusions and target no-homography are separate assumptions.

Polarity, relation direction, condition scope and therapeutic interpretation
are **not certified by this count audit**. The draft's per-line polarity labels
must be marked nonoperative background or reviewed separately before use. A
count-compatible carrier map would not establish which bath helps or harms a
condition, or supply a complete source paragraph translation.

## Final-file receipt

Independently replayed against these exact corrected files at 10:07 UTC:

- `BALNEIS_BODY_SOURCE.json` (schema `balneis_body_source.v2`):
  `a8d45d6226e52b1d11c271d0b61ff867218e6ad85bdfa91fe5b4b62f067f50e5`
- `BALNEIS_BODY_SOURCE.md`:
  `d9103bcfe0c9225a50b4ffbeabcedd5fd36dacd739175fe623ae15d158751511`

All 33 Roman-numbered headings and complete intervals agree with the primary;
all 32 selected bath intervals are correct. All 416 family-by-record cells,
including zeros, agree with the independent reconstruction. All 166 operative
occurrences and all 14 exclusion witnesses agree in their exact tokens, source
lines and coordinate fields. No operative occurrence is duplicated or assigned
to the dedication. All 166 Markdown occurrence rows agree with the verified
JSON. The original draft hashes and specific corrections are retained in v2.
All v2 polarity/context values are explicitly `unreviewed` and nonoperative.

The form table lists admitted inflection/spelling forms under the declared
casefold, not every capitalization variant as a separate class. Exact printed
capitalization is present in the occurrence ledger; a lowercase table form such
as `pulmoni` does not change the printed `Pulmoni` witness. This interpretation
is explicit in the JSON's matching-normalization contract.

The corrected source inventory is ready for prospective registration under the
declared 13-family scope. This approval covers source preparation and count
reconstruction only. No target eligibility, carrier match, search result,
polarity inference or manuscript meaning has been validated here.
