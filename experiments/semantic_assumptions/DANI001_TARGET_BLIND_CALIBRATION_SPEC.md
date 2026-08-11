# DANI001 target-blind calibration specification

Status: **REGISTERED_CALIBRATION_DESIGN_UNRUN**
Date: 2026-08-10

## Authority, purpose, and ceiling

This contract implements only the calibration and score-blind capacity stage
required by `DANI001_FIXED_MAPPING_DIAGNOSTIC_SPEC.md` as registered at commit
`1faa87f`.  The registered science-specification bytes have SHA-256
`cc73479b3c35eaa87a3f56184fc3472fe6232b67c13deb3bf30ef8555a6c8426`.
If those bytes, that commit, or this calibration specification do not match a
later freeze manifest, execution hard-stops without an output.

Calibration tests deterministic synthetic mechanisms and then asks only
whether the real source panels have enough nonidentity variation to support the
registered one-shot diagnostic.  It never computes, requests, stores, returns,
or reconstructs the real released-map (rank-0) score.  It supplies no evidence
for Syriac, Aramaic, Semitic language, sound, wordhood, pharmaceutical content,
plaintext, or translation.  Synthetic strings and lexicons are engineering
fixtures, not proposed Voynich readings.

This file does not authorize the observed run.  A separate target freeze may
be constructed only after the calibration result has passed independent
validation under the decision rules below.

## Exact names and paths

The future implementation has these exact repository-relative source paths:

- `experiments/semantic_assumptions/dani001_panel.py`
- `experiments/semantic_assumptions/dani001_calibration_generator.py`
- `experiments/semantic_assumptions/dani001_core.py`
- `experiments/semantic_assumptions/dani001_core.h`
- `experiments/semantic_assumptions/dani001_core.cpp`
- `experiments/semantic_assumptions/run_dani001_target_blind_calibration.py`
- `experiments/semantic_assumptions/validate_dani001_target_blind_calibration.py`
- `experiments/semantic_assumptions/DANI001_SYNTHETIC_MANIFEST.json`
- `experiments/semantic_assumptions/DANI001_CALIBRATION_FREEZE.json`

The producer creates only:

- `experiments/semantic_assumptions/results/dani001_target_blind_calibration.json`
- `experiments/semantic_assumptions/results/dani001_target_blind_calibration.md`

The independent validator creates only:

- `experiments/semantic_assumptions/results/dani001_target_blind_calibration_validation.json`
- `experiments/semantic_assumptions/results/dani001_target_blind_calibration_validation.md`

All four outputs must be absent when the calibration freeze is created and
again immediately before producer execution.  Each phase writes temporary
files in a fresh directory outside the repository, fsyncs them, then installs
its two files with `os.link` no-clobber operations after confirming that both
destinations are absent.  A collision or partial installation is a hard stop;
the one installed member, if any, is removed only after its inode and bytes are
proved to be the just-created temporary file.  Existing files are never
altered.

## Exact local source-atlas reconstruction contract

The five actual local inputs and their hashes are inherited unchanged from the
science specification.  The atlas is not accepted merely because its stored
hash matches: after the synthetic gate, both producer and clean validator must
independently reconstruct its complete TSV bytes from the three raw manual
sources and compare the reconstructed bytes to
`results/source_separator_transcription.tsv`.  The validation JSON is opened
only as a hash-bound provenance input; neither implementation imports or
executes the historical atlas producer or validator.

Read the editions in exact order `ZL3b,IT2a,RF1b`, using UTF-8 with strict
decoding and Python `str.splitlines()`.  A page header is recognized by
`^<([^>.]+)>\s+<!(.*)>`; set the active page to capture 1 lower-cased and
replace the complete active metadata dictionary by all nonoverlapping
`\$([A-Z])=([^\s>]+)` matches in capture 2.  A source row is recognized by
`^<([^,]+),([^>]*)>\s*(?:<!([^>]*)>)?\s*(.*)$`; its captures are respectively
`locus,code,comment,text`, and the comment is discarded.  Nonmatching lines
are ignored.  The active page and metadata persist until the next page header.
Within each edition, `source_row_index` starts at zero and is incremented once
before emitting that row's group records, so the first recognized row stores
`1`.  Duplicate `(edition,locus)` keys, a source
row before any page header, invalid topology, or a TSV-unsafe tab/CR/LF in a
source group hard-stops.

Split each `text` left to right as follows.  Recognize `<->` and `<~>` before
single characters.  On `<`, consume through the next `>`; `<%>` and `<$>` are
row controls and are omitted from group content, while every other complete
angle form remains verbatim in the current group.  On `[` or `{`, consume the
complete form through the next matching `]` or `}` and retain it verbatim in
the current group.  Outside those forms, `.` and `,` are separators; every
other character is group content.  At a separator, strip surrounding
whitespace from the accumulated group.  Empty groups, more than one pending
separator between retained groups, a trailing separator, an unterminated
form, zero retained groups, or a boundary count other than group-count minus
one hard-stops.  The four stored separator names are exactly, in marker order,
`DEFINITE_SPACE,UNCERTAIN_SMALL_SPACE,DRAWING_INTERRUPTION,
DRAWING_INTERRUPTION_UNALIGNED`.  Group indices are one-based in source order.

For each source group independently reproduce the legacy cleaner only for the
atlas audit.  Replace every complete square form matching
`\[([^:\]]+)(?::[^\]]*)?\]` by capture 1; delete `\{[^}]*\}`; replace
`<[^>]*>` by one ASCII space; delete literal `? ! * '` characters; split by
`[\s.,;:=/\\|+\-]+`; within every nonempty piece delete all non-ASCII-letter
characters and lower-case; discard a piece that then becomes empty.  The
one-based legacy positions for a group are the next contiguous positions in
the flattened cleaned source row.  Mapping status is exactly
`ZERO_ASCII_FRAGMENT`, `ONE_ASCII_FRAGMENT`, or `MULTI_ASCII_FRAGMENT` from
that group's cleaned-fragment count.  No pre-grounding parser, root, role, or
formal feature is consulted.

The reconstructed TSV has exactly these 23 columns in this order:

```
source_group_id,edition,locus,page,section,currier,hand,code,kind,
grammar_scope,source_row_index,source_group_index,source_group_count,
paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw,
clean_ascii_fragments,clean_ascii_fragment_count,
legacy_surface_positions_1based,legacy_interlinear_row_present,
legacy_mapping_status
```

`source_group_id` is `EDITION|LOCUS|G` plus the group index zero-padded to
three decimal digits.  `section,currier,hand` are active metadata `$I,$L,$H`
or the empty string.  `kind` is `code[1]` when present, else empty.
`grammar_scope` is `CONFIRMED_PROSE` iff `len(code)>1`, `code[1]=="P"`, and
Currier is `A` or `B`; otherwise it is `DIAGNOSTIC_NONPROSE`.
`paragraph_start` and `paragraph_end` are integer `1` iff literal `<%>` or
`<$>` occurs anywhere in the row text, else `0`.  The first/last exterior
separator names are `LINE_START`/`LINE_END`.  Clean fragments are joined by
one ASCII space and legacy positions by one comma.
`legacy_interlinear_row_present` is integer `1` iff the flattened cleaned row
is nonempty, else `0`; it describes the historical cleaner outcome and does
not authorize opening the old interlinear file.

Serialize with CPython 3.12.3 `csv.DictWriter`, UTF-8 without BOM,
`delimiter="\t"`, `lineterminator="\n"`, the exact header above, default
minimal CSV quoting, and one row per source group in edition/source-row/group
order.  The result must have exactly 15,985 source rows, 115,470 group rows,
99,485 manual boundaries, the four-state vocabulary above, and SHA-256
`4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0`.
Any byte or count discrepancy is an output-free input-contract stop.

## Exact external JSON projections

All three downloaded responses use strict UTF-8.  JSON is parsed with CPython
3.12.3 `json.loads` and an `object_pairs_hook` applied recursively to every
object; any duplicate member name at any depth, malformed JSON, invalid UTF-8,
or wrong required container type hard-stops.  No raw response body, forbidden
lexicon value, or diagnostic excerpt is persisted.

The concept endpoint must be one top-level JSON object.  Its stable projection
is exactly the object below; bracketed expressions name direct lookups in the
downloaded object, and the source `files` array order is retained without
sorting:

```
{
  "id": source["id"],
  "conceptrecid": source["conceptrecid"],
  "revision": source["revision"],
  "doi": source["doi"],
  "created": source["created"],
  "updated": source["updated"],
  "metadata": {
    "title": source["metadata"]["title"],
    "publication_date": source["metadata"]["publication_date"],
    "description": source["metadata"]["description"]
  },
  "files": [
    {"key": item["key"], "size": item["size"],
     "checksum": item["checksum"], "url": item["links"]["self"]}
    for item in source["files"]
  ]
}
```

`source["metadata"]` must be an object and `source["files"]` a JSON array;
every named member and nested container must exist and support the lookup
above.  Extra members and live statistics are ignored.  Canonicalize this
projection with `json.dumps(sort_keys=True,separators=(",",":"),
ensure_ascii=True,allow_nan=False)` plus one LF, encode UTF-8, and require
SHA-256 `780301fd3c4b2c3c328c1f69a1eab65d0b0600f2d491ea9578f81699d36ddfa7`.
The raw concept bytes and parsed object are then discarded.

The deposited lexicon must be one top-level JSON object.  Its member names are
the exact lexicon keys; each must be a nonempty string and each value a
nonempty JSON array of entry objects.  Process keys in ascending UTF-8 byte
order.  For every entry project only:

- `source_present = bool(source)` where a missing or JSON-null `source` is
  null, a present value must be a string, the empty string is false, and a
  nonempty string is true;
- `domain = "missing"` when `domain` is absent, null, or the empty string;
  otherwise it must be a string in exact vocabulary
  `astro,botanical,function,general,medical,pharma`.

Any other source/domain type or domain value hard-stops.  Every other entry
member, including meaning, Syriac spelling, and vowel hint, is ignored and
discarded with the raw entry.  For one key, aggregate `source_present` by
logical OR over its entries and retain the ordered tuple of canonical domain
tags.  `entries` is the total number of entry objects, not the number of keys.

The exact key-set views are:

- `FULL`: every key;
- `REACHABLE`: every nonempty key whose every Unicode code point is in the
  registered 14-symbol nibble codebook;
- `SOURCE_PRESENT`: keys whose aggregated source-present boolean is true;
- `STRICT_NO_FUNCTION`: keys for which every entry domain is not `function`;
- for each exact domain `D`, `LEAVE_OUT_D`: keys having at least one entry
  whose domain is not `D` (equivalently, delete `D` entries and retain a key
  only when another entry remains).

For each view, reachability filtering precedes nibble encoding.  Direct codes
are the sorted unique codes of reachable keys.  Deposited-affix codes are the
sorted unique codes of the exact registered preimage union for those keys;
any accepted preimage longer than ten Unicode code points hard-stops.  The
projected raw dictionaries and all forbidden values are cleared before the
bundle is returned.  Exact registered totals are 1,389 keys / 1,441 entries,
819 reachable / 570 unreachable keys, 104 source-present / 55 reachable
source-present keys, and 1,243 strict-no-function / 738 reachable strict-no-
function keys.  The complete per-view count array is independently rebuilt
and later serialized only in the aggregate schema below; no key, spelling,
meaning, source string, or gloss is output.

## Counter-hash primitive

There is no PRNG state and no implementation-selected seed.  All synthetic
choices use SHA-256 with root domain
`DANI001-TARGET-BLIND-CALIBRATION-V1`.

For an ASCII label `L` and a sequence of nonnegative integer fields `x`, define

```
H(L,x...) = SHA256(
  ASCII("DANI001-TARGET-BLIND-CALIBRATION-V1") || 0x00 ||
  uint16_le(len(ASCII(L))) || ASCII(L) ||
  uint16_le(number_of_fields) ||
  uint64_le(x[0]) || ... || uint64_le(x[-1])
)
```

Labels must be among the literal labels named below, fields must fit unsigned
64-bit, and the digest is interpreted as one unsigned little-endian 256-bit
integer.  For `B(L,m,x...)`, where `1<=m<=2**64`, append rejection attempt
`a=0,1,...` to the fields, set `q=floor(2**256/m)*m`, take the first
`H(L,x...,a)<q`, and return `H mod m`.  This removes modulo bias.

`PERM(L,m,x...)` applies descending Fisher--Yates to `[0,...,m-1]`; at step
`i=m-1,...,1`, with zero-based completed-step index `c=m-1-i`, swap positions
`i` and `B(L,i+1,x...,c)`.  Thus a recorded Fisher--Yates draw is exactly
`[L,[i+1,x...,c],result]`.  Permutation ranks and unranking always use the
registered lexicographic order.  Let `N=m!`.  Where a sequence of unique
nonidentity ranks is required, for zero-based sequence index `s` and
zero-based collision attempt `j`, candidate rank is
`1+B(L,N-1,s,j)`; take the first candidate not used by an earlier `s` in that
same named sequence.  Its recorded draw is exactly
`[L,[N-1,s,j],result_before_adding_one]`.  Internal SHA rejection attempts are
not recorded.  No output or test statistic participates in selection.

The complete domain-label allowlist is:

- `plant-map-rank`
- `null-probe-rank`
- `null-key-tail`
- `adversary-candidate-rank`
- `adversary-decoy-tail`
- `toy-map-rank`
- `conjugacy-permutation`

An unknown label hard-stops.  The synthetic manifest records every label and
integer field used.  An implementation may cache a draw but may not replace or
extend this primitive.
`counter_protocol.sha256` is the SHA-256 of canonical JSON containing exactly
`{"labels":[the allowlist above in order],"root":the root-domain string}`.

## Canonical synthetic objects

The core input-index order is `(k,d,r,s,l,n,q,y,m,g)` and output-index order is
`(k,d,r,s,l,n,w,y,m,g)`.  Fixed marker index order is `(sh,t,p,f)`, emitting
the four output code points `(š,ṭ,p,ṣ)`.  These marker outputs cannot be emitted
by a permuted core input.

For marker width `h` and integer `j`, `TAG(h,j)` is the `h` base-4 digits of
`j`, most-significant digit first, with leading zeroes; each digit is rendered
by the corresponding fixed marker spelling above.  `KEYTAG(h,j)` uses the
corresponding emitted marker code points.  `VTAG(h,j)` uses the same base-4
digits but spellings `(a,o,e,i)`.  Those vowels are consumed by the registered
scanner and emit nothing.  They therefore distinguish normalized source types
without lengthening a lexicon key or emitted template.  A core tail is rendered
by the one-character input spellings and is mapped to output code points by the
map under test.

The ordinary 256-type construction defines `marker(j)=floor(j/16)` and
`vowel(j)=j mod 16`.  Raw type `j` starts
`VTAG(2,vowel(j)) || TAG(2,marker(j))`.  Its emitted/key marker is only
`KEYTAG(2,marker(j))`.  In ten-variable worlds its tail is exactly
`(0,1,2,3,4,5)` when `j` is even and `(4,5,6,7,8,9)` when `j` is odd.  In a
toy with `m=4` or `m=6`, its tail is `(0,...,m-1)`.  All 256 normalized raw
types are distinct, while every reachable key is at most eight emitted code
points.  In the ten-variable construction any remaining set containing at
least one even and one odd type fixes all ten map assignments.  Every generator
must assert before manifest construction that every reachable key has length
at most eight; because the longest registered deposited-affix preimage adds two
code points, every accepted preimage is then at most ten code points.

A synthetic projected lexicon is a UTF-8 canonical JSON array sorted by key
bytes.  A reachable record is

```
{"key":KEY,"entries":[
  {"domain":"astro","source_present":true},
  {"domain":"botanical","source_present":true},
  {"domain":"general","source_present":true},
  {"domain":"medical","source_present":true},
  {"domain":"pharma","source_present":true}
]}
```

in that exact entry order.  Consequently all reachable plant keys survive
`SOURCE_PRESENT`, `STRICT_NO_FUNCTION`, and every leave-one-domain-out view,
including deletion of the absent `function` tag.  Exactly 570 unreachable
records are included in every ten-variable synthetic world.  Unreachable key
`j` is `u` followed by the three most-significant-first base-14 digits of `j`,
using the registered nibble symbols in codebook order.  It has the same five
entries.  The leading `u` makes it unreachable; it is counted but never
encoded.  The reachable/unreachable union is sorted once by key bytes; toy
worlds contain no unreachable records.  For every world, the pre-score manifest
binds full/reachable counts, the full lexicon digest, and its invariant assertion
ID.  The `PLANT_000` remove/restore mutation additionally binds full, without-
unreachable, and removed-record payload digests.  Producer and validator
calibration aggregates bind post-score full/without-unreachable score-vector
digests for every applicable world.

A canonical synthetic row has exactly these fields:

```
{"edition":EDITION,"page":"f"+decimal(FOLIO)+"r",
 "locus":"P."+decimal(FOLIO),"groups":[RAW_GROUP...],
 "separators":[SEPARATOR...]}
```

Edition order is `ZL3b,IT2a,RF1b`; folios are ascending integers without zero
padding; group order is generator order.  There is one fewer separator than
groups.  The decimal suffix of `locus` must equal the page-derived physical
folio.  Ordinary worlds use only `.`.  Therefore
`DOT_ONLY_EMULATION` and `MANUAL_GROUP` contain the same tokens, while still
being constructed independently.  Duplicate `(edition,page,locus)` keys,
empty rows, an unknown edition, a nonnumeric page, a group/separator arity
mismatch, or a nonallowlisted separator hard-stops.

Canonical synthetic JSON uses CPython 3.12.3 `json.dumps` with
`sort_keys=True,separators=(",",":"),ensure_ascii=True,allow_nan=False` and
one LF.  Arrays retain the order defined here.  Each canonical row is hashed
separately; the concatenation of its 32-byte row digests in row order is the
world-row digest.  Lexicon, panel, and complete-world canonical bytes also
receive separate SHA-256 digests.  These digests bind every generated row
without persisting strings in calibration result artifacts.

The complete-world payload whose digest is `world_sha256` has exactly
`world_id,variable_count,candidate_rank,secret_rank,alternate_rank,rows,lexicon`
in one canonical JSON object; digest fields are not part of their own preimage.
Panel digest preimages are the panel builder's canonical array of objects with
exactly `edition,page,locus,folio,normalized_eva,emitted_template,
strict_literal_eligible`, in canonical row/group order.  `emitted_template` is
an array of fixed codebook integers or negative core-variable indices
`-(i+1)`; it never contains a mapped output or score.

## Distributed planted worlds

There are exactly 100 ten-variable worlds with trial indices `0..99`.  Their
secret ranks are the first 100 unique nonidentity ranks from
`plant-map-rank`, using the trial index as the sequence index.  World ID is
`PLANT_` plus the zero-padded three-digit trial index.  The scored candidate
rank of each plant is exactly its secret rank.

For every `j=0..255`, the raw type is
`VTAG(2,vowel(j)) || TAG(2,marker(j))` followed by its frozen core tail.  Its
reachable lexicon key is `KEYTAG(2,marker(j))` followed by that tail mapped
under the trial's secret map.  Every one of physical folios `1..32` contains
each of the 256 types exactly once, in increasing `j`, in all three editions.
All separators are dots.  No annotation or unregistered character occurs.

The secret map therefore matches all 256 types, the construction is spread
identically across 32 folios, and any map matching one even and one odd type in
full equals the secret.  After deterministic top-20 deletion, at least 108
even and 108 odd types remain.  This is a structural invariant checked before
scoring, not a score-selected world filter.

A plant trial succeeds only if all of the following are true:

1. the secret rank is the unique maximum of the joint `T` vector;
2. all registered primary gates 1--7 pass;
3. `DIRECT_ONLY`, `STRICT_NO_FUNCTION`, `SOURCE_PRESENT`, and all six
   leave-one-domain-out views are powered and pass their applicable gates;
4. every mandatory capacity count and SD condition passes;
5. direct-decision and pre-expanded-affix vectors are byte-identical;
6. deleting the 570 unreachable records leaves every score vector
   byte-identical.

The aggregate plant control passes when at least 95 of 100 trials succeed.  No
failed trial may be replaced, regenerated, or omitted.

## Map-independent null worlds

There are exactly 128 ten-variable worlds with trial indices `0..127` and IDs
`NULL_000` through `NULL_127`.  Probe ranks are the first 128 unique
nonidentity ranks selected by `null-probe-rank`.  Probe ranks are not supplied
to any row or lexicon generator.

Rows and tails equal the distributed plant construction.  For type `j`, its
six output tail symbols are the first six elements of
`PERM("null-key-tail",10,trial,j)`; its key is
`KEYTAG(2,marker(j))` followed by those symbols.  Null-key fields never include
the probe rank and the SHA domains are
disjoint.  Each type is therefore permutation-variable, but the 256 key-tail
constraints do not arise from the probe or from one shared map.

A null trial is counted as a false pass only when its probe takes the registered
all-required-gates pass decision.  The null control passes when at most one of
128 probes is a false pass.  Individual null outcomes are not used to replace
or select worlds.

## Toy scalar equivalence

Four toy worlds are frozen: `TOY4_PLANT`, `TOY4_NULL`, `TOY6_PLANT`, and
`TOY6_NULL`.  They use respectively the first four or six core input/output
indices, the same 256 `VTAG(2,vowel(j)) || TAG(2,marker(j))` normalized types,
32 folios, three editions, and both panels.  For each plant, take the first
nonidentity `PERM("toy-map-rank",m,m,0,a)` over attempts `a=0,1,...`; its
candidate and secret are that map.  For each null, take the first nonidentity
`PERM("toy-map-rank",m,m,1,a)` as its probe.  Plant and null keys start
`KEYTAG(2,marker(j))`; null key `j` then uses the complete output order
`PERM("null-key-tail",m,1000+m,j)`.

For every rank in the complete `4!` or `6!` orbit, an independent scalar
implementation and the optimized integer core must agree on every raw integer
vector, folio vector, distribution scalar, standardized vector, `T`, strict-
better/tie/inclusive count, gate, and decision.  `<u4` and `<f8` vector bytes
must be identical.  This is an equality control; toy plants need not meet the
ten-factorial tail threshold.

## Named adversarial worlds

All adversarial candidate ranks are unique nonidentity ranks selected by
`adversary-candidate-rank` in the order below.  When an alternate is needed,
it is the map obtained by replacing every candidate output index `i` with
`(i+1) mod 10`; it therefore differs from the candidate at every input.
All use 32 folios, three editions, and both panels unless stated otherwise.
Every named five-input tail is `(0,1,2,3,4)` for an even type index and
`(5,6,7,8,9)` for an odd type index.  Except for the specially defined
one-type world, define for `j=0..511`
`block(j)=floor(j/256)`, `local(j)=j mod 256`,
`marker5(j)=32*block(j)+2*floor(local(j)/16)+(local(j) mod 2)`, and
`vowel5(j)=floor((local(j) mod 16)/2)`.  Its raw prefix is
`VTAG(2,vowel5(j)) || TAG(3,marker5(j))` and its key prefix is
`KEYTAG(3,marker5(j))`.  The marker therefore fixes tail parity; all 256 raw
types in either block remain distinct; blocks 0 and 1 have disjoint markers;
and every five-tail key has length eight.
Random decoy output tails use `adversary-decoy-tail` with fields
`(adversary_index,type_index,attempt)`, taking the first five symbols of the
permutation.  Reject and increment `attempt` only when that tail equals the
candidate map's output on the type's five-input tail.  This rejection uses no
score.

Adversary order and exact expected outcomes are:

1. `FIXED_HEAVY_HIGH_COVERAGE`.  Use the 256 block-0 five-input variable types
   just defined, tied to the fixed alternate map.  Add 64 fixed types.  Fixed
   type `j` has raw spelling
   `cth` followed by its three marker spellings with literal vowels `a,o,e`
   inserted after marker positions 0, 1, and 2; its key is emitted `k` followed
   by `KEYTAG(3,j)`.  The emitted `ṭ` from `cth` is removed by the deposited
   gallows-prefix path.  Put every variable type once and every fixed type 100
   times on every folio.  Candidate eligible-token coverage must be at least
   `0.90` in all six edition/panels, all nonidentity component SDs must be
   positive, and primary rank gate 1 or 2 must be false.
2. `ONE_TYPE_CONCENTRATION`.  Types `j=0..8` have raw prefix
   `VTAG(2,0) || TAG(3,j)` and candidate-map keys with prefix `KEYTAG(3,j)`.
   For `j=9..255`, let `u=j-9`; the raw prefix is
   `VTAG(2,u mod 16) || TAG(3,9+floor(u/16))`, and the key prefix is the
   corresponding `KEYTAG(3,...)`; those types have decoy keys.  Signal markers
   `0..8` and decoy markers `9..24` are disjoint.  On every folio type 0 occurs
   100 times, types 1--8 twice, and all others once.  A decoy tail is rejected
   if it equals the candidate output on either registered five-input tail, so
   no candidate-mapped decoy raw type can match through another type's key.
   The primary core and folio-concentration gates 1--5 must pass.
   Frequency deletion must remove tags 0--8 plus eleven decoys, leave the
   candidate matching no retained type, and make gate 6 false.  This is the
   exact operational meaning of the named one-type plant; eight low-frequency
   supports satisfy the registered type-capacity and absolute-type gates.
3. `ONE_FOLIO_CONCENTRATION`.  Use the 512 five-input types defined above.
   Types `0..255` use candidate-map keys; types `256..511` use decoy keys.  Folio
   1 contains the first block once each; folios 2--32 contain the second block
   once each.  All folios have variable types.  Primary core gates 1--3 must
   pass; exactly one folio has positive candidate advantage, so gates 4 and 5
   must both be false.
4. `PREFIX_ONLY`.  Every type is raw fixed `t` followed by the block-0 raw
   prefix and five-input tail, for exactly `j=0..255`.  Its lexicon key omits
   the emitted leading `ṭ` and contains only the three-code-point key prefix
   plus the candidate-mapped tail.  The lexicon key has length eight, the
   direct emitted token length nine, and the longest generated deposited-affix
   preimage length is ten.
   The deposited-affix primary must pass.  `DIRECT_ONLY` must have zero matches
   at every rank, fail positive-SD capacity, and set its mandatory robustness
   gate false.
5. `UNKNOWN_SKIP`.  Start with the distributed plant and append unregistered
   ASCII `b` to every raw type.  Default scanner and primary vectors must equal
   the corresponding clean plant byte for byte.  `STRICT_LITERAL` must exclude
   every token, fail capacity, and set gate 7 false.
6. `ONE_READING_WRONG`.  Use the 512 five-input types; ZL3b and IT2a use types
   `0..255` with candidate-map keys, while RF1b uses types `256..511`
   with alternate-map keys.  Each included block occurs once on every folio.
   The candidate's RF1b raw absolute advantage is zero and primary core gate 3
   and the joint-minimum decision must be false.

Every world must meet its stated outcome exactly.  An unstated gate is
descriptive and cannot substitute for the named expected failure.  Failure of
an adversary to exhibit its frozen signature fails calibration; the generator
may not search for a replacement.

## Parser, mutation, and invariance fixtures

`PARSER_CANONICAL` consists in every edition of one `f1r` / `P.1` row with raw groups
`k[dr:sy]`, `l[ny]`, `q{abc}y`, and `m<note>g`, separated respectively by
comma, `<->`, and `<~>`, followed by a dot and the raw group `kd`.  Square
primary selection, no-colon square selection, brace deletion, nonseparator
angle deletion, all four separator states, joining without inserted bytes,
normalization, and strict-literal propagation must match an independently
computed manifest expectation.  No counter-hash choice occurs in this fixture.
Its manifest `expected` is exactly
`{"assertion_count":4,"assertions":[...]}` with, in order, IDs
`PARSER_PRIMARY_SELECTION`, `PARSER_SEPARATOR_STATES`,
`PARSER_PANEL_INDEPENDENCE`, and `PARSER_STRICT_PROPAGATION`; each assertion has
operator `PARSER_FIXTURE` and value `true`.

Apply these exact mutations to frozen clean copies, one at a time.  Unless a
bullet names `PARSER_CANONICAL`, the base is `PLANT_000`.  "First row" means
the first row in canonical edition/folio order, and "append" means append to
that row:

- `EMPTY_PANEL`: replace rows by an empty array; hard-stop.
- `DUPLICATE_ROW`: append the first row unchanged; hard-stop on duplicate key.
- `DUPLICATE_JSON_KEY`: preserve the complete canonical `PLANT_000` lexicon
  array, every record, every entry, and their order.  In raw JSON only, replace
  the first object's canonical encoding by exactly
  `{"entries":ENTRIES,"key":KEY,"key":KEY}`, where `ENTRIES` and `KEY` are
  that first record's ordinary canonical member encodings; every later object
  retains its ordinary canonical encoding.  The array uses comma separators
  with no whitespace and one terminal LF.  Duplicate-key-aware parsing must
  hard-stop; the fixture may not reduce the payload to the first object.
- `TOKEN_REVERSE`: reverse groups within every row and reverse separators with
  them; aggregate score vectors must remain byte-identical, while row and panel
  digests must differ.
- `ROW_REVERSE`: reverse complete row order; the scorer must canonicalize by
  edition, integer folio, page bytes, and locus bytes, giving byte-identical
  score vectors while the input-row digest differs.
- `LEXICON_REVERSE`: reverse key order and every entry order; projected sets
  and every score vector must be byte-identical.
- `UNMATCHED_SQUARE`, `NESTED_SQUARE`, `UNMATCHED_BRACE`, `NESTED_BRACE`,
  `UNMATCHED_ANGLE`, and `NESTED_ANGLE`: replace the first raw group of
  `PARSER_CANONICAL` respectively by `[k`, `[[k]]`, `{k`, `{{k}}`, `<k`, or
  `<<k>>`; each hard-stops before a panel digest.
- `OVERLENGTH_PREIMAGE`: append the reachable key `kkkkkkkkkkk`; hard-stop
  before any source panel is opened.
- `OVERLENGTH_TOKEN`: append raw `kdrslnqymgk`, a consumed
  11-output-code-point token not in any accepted preimage; keep it in every
  denominator and unmatched at every rank.
- `UNKNOWN_INSERT`: append `b` to every clean plant group; default vectors are
  invariant and strict-literal eligible counts fall by exactly all inserted
  instances.
- `MISSING_EDITION`: delete RF1b; hard-stop before scoring.
- `PAGE_DOMAIN`: change the first row's page to `fRos`; synthetic numeric-page
  validation hard-stops.  The separate actual parser still excludes its bound
  `fRos` rows and verifies the registered exclusion counts.
- `FOLIO_DRIFT`: change the first row's page from `f1r` to `f2r` while retaining
  locus `P.1`; the page/locus folio disagreement hard-stops.
- `UNREACHABLE_REMOVE`: from the canonical full `PLANT_000` lexicon remove
  exactly the 570 records whose keys begin with literal `u`; the mutation
  payload binds the removed-state lexicon and the ordered canonical bytes of
  the 570 removed records.  Every raw and standardized score-vector byte must
  remain invariant.
- `UNREACHABLE_RESTORE_ADD_FROM_REMOVED`: its base state is named
  `PLANT_000_WITHOUT_UNREACHABLE`, exactly the prior removed-state payload.
  Add each of the saved 570 records exactly once, reject any duplicate key,
  sort canonically, and require byte identity with the original full lexicon.
  Every raw and standardized score-vector byte must remain invariant.  It is
  forbidden to implement this as an add to the already-full lexicon.

The ordered mutation `expected_status` and `expected_equalities` values are
exactly the following; JSON member order is immaterial because serialization
sorts keys:

```
EMPTY_PANEL                     EXPECTED_HARD_STOP       {"empty_panel_rejected":true}
DUPLICATE_ROW                   EXPECTED_HARD_STOP       {"duplicate_row_rejected":true}
DUPLICATE_JSON_KEY              EXPECTED_HARD_STOP       {"duplicate_json_key_rejected":true}
TOKEN_REVERSE                   EXPECTED_BYTE_INVARIANCE {"input_rows_equal":false,"score_vectors_equal":true}
ROW_REVERSE                     EXPECTED_BYTE_INVARIANCE {"input_rows_equal":false,"score_vectors_equal":true}
LEXICON_REVERSE                 EXPECTED_BYTE_INVARIANCE {"projected_sets_equal":true,"score_vectors_equal":true}
UNMATCHED_SQUARE                EXPECTED_HARD_STOP       {"panel_digest_created":false}
NESTED_SQUARE                   EXPECTED_HARD_STOP       {"panel_digest_created":false}
UNMATCHED_BRACE                 EXPECTED_HARD_STOP       {"panel_digest_created":false}
NESTED_BRACE                    EXPECTED_HARD_STOP       {"panel_digest_created":false}
UNMATCHED_ANGLE                 EXPECTED_HARD_STOP       {"panel_digest_created":false}
NESTED_ANGLE                    EXPECTED_HARD_STOP       {"panel_digest_created":false}
OVERLENGTH_PREIMAGE             EXPECTED_HARD_STOP       {"source_panel_opened":false}
OVERLENGTH_TOKEN                EXPECTED_DECLARED_CHANGE {"always_unmatched":true,"denominator_delta":1}
UNKNOWN_INSERT                  EXPECTED_DECLARED_CHANGE {"default_vectors_equal":true,"strict_instances_removed":24576}
MISSING_EDITION                 EXPECTED_HARD_STOP       {"missing_rf_rejected":true}
PAGE_DOMAIN                     EXPECTED_HARD_STOP       {"nonnumeric_page_rejected":true}
FOLIO_DRIFT                     EXPECTED_HARD_STOP       {"page_locus_disagreement_rejected":true}
UNREACHABLE_REMOVE              EXPECTED_BYTE_INVARIANCE {"raw_vectors_equal":true,"standardized_vectors_equal":true}
UNREACHABLE_RESTORE_ADD_FROM_REMOVED EXPECTED_BYTE_INVARIANCE {"full_lexicon_bytes_equal":true,"raw_vectors_equal":true,"standardized_vectors_equal":true}
```

Malformed fixtures execute inside isolated pure-function calls whose expected
exception is caught by the calibration harness and counted as a passing
control.  They perform no filesystem write.  An equivalent malformed or
hash/schema stop in the calibration's own bound inputs is output-free.
Expected invariances compare raw vectors before distribution summaries as well
as every derived digest and decision.

## Conjugacy, affix, and worker controls

Use `PLANT_000`.  Let `rho` be the first nonidentity
`PERM("conjugacy-permutation",10,a)` over attempts `a=0,1,...`.  Rename core
input and output indices by
`rho`, leave fixed markers unchanged, and transform each candidate map to
`rho o map o inverse(rho)`.  Reindex the renamed orbit back to original
lexicographic map rank.  Every raw vector, standardized vector, gate, and
decision must then be byte-identical to the original.

For every toy, plant, null, and named adversarial world, evaluate deposited
affix matching both by the literal first-match decision procedure and by the
deduplicated preimage set.  Every binary match and all score vectors over every
rank must be byte-identical.  For the actual panels this comparison is made
only at nonidentity ranks `1..3,628,799`.

The equality evidence is hash-bound without publishing a favorable form,
type, key, rank, or vector.  For one synthetic evaluation path form an ordered
array over scoring view, edition, panel, and weighting in their registered
orders.  Each entry has exactly `view,edition,panel,weighting,raw_dtype,
raw_sha256,standardized_sha256`; raw dtype is `<u4` for token/type and `<f8`
for folio, and `standardized_sha256` hashes the contiguous `<f8` standardized
vector or is JSON `null` when that component's SD is not positive.  All array
digests use the complete synthetic orbit including synthetic rank 0.  The
affix evidence object is exactly
`{"schema":"dani001-affix-evidence-v1","world_id":ID,
"literal_decision_function_sha256":HEX,
"expanded_decision_function_sha256":HEX,
"literal":[...],"expanded":[...]}`.  The two decision-function digests bind
independently compiled exact Boolean functions under the encoding below;
byte equality is the registered analytic proof that every binary decision
agrees at every rank, without materializing a type-by-rank bitmap.  The
unreachable evidence object is
exactly `{"schema":"dani001-unreachable-evidence-v1","world_id":ID,
"full":[...],"without":[...],"restored":[...]}`.  Hash each canonical object
with one terminal LF.  An affix assertion passes only when literal first-match
and expanded-preimage decision-function bytes are identical, both ordered
evidence arrays agree, and every derived distribution digest, gate, and world
decision agrees.  An unreachable assertion passes only when the `without`
lexicon is constructed by deleting and saving the exact unreachable records,
`restored` is constructed only by adding those saved records back, all three
evidence arrays agree, and every derived digest, gate, and decision agrees.
Constructing restoration from the already-full lexicon is forbidden.

The canonical decision-function byte stream begins with ASCII
`DANI001-DECISION-FUNCTION-V1`, one `0x00`, and one unsigned byte containing
the core width.  Then, in scoring-view, edition, panel order, append
`uint32_le(type_count)`.  Eligible normalized types are ordered by ascending
UTF-8 bytes but their identities are not serialized.  For each type append
`uint32_le(constraint_count)`, followed by its deduplicated partial-bijection
constraints sorted by `(mask,required_tuple)`.  One constraint is
`uint16_le(mask)` followed by exactly `core_width` unsigned required-output
bytes, using `0xff` for unbound and `0..core_width-1` for bound outputs.  No
template, type identity, delimiter, rank result, or terminal byte is present.
The literal path must obtain its constraints by executing the frozen deposited
first-match decision order; the expanded path must independently obtain them
from the deduplicated preimage set.  Equality of these complete canonical
streams proves equality of the Boolean match function on the entire
permutation universe.  Each path is nevertheless scored separately to produce
the raw/standardized vector arrays above.

The optimized full ten-factorial evaluation of `PLANT_000` is run once with
one worker and once with exactly 32 workers.  Raw integer vectors and derived
`<u4`/`<f8` vector digests must be byte-identical.  Threads may fill disjoint
fixed rank intervals only; all binary64 reductions use the registered serial
order after integer blocks have joined.

## Synthetic manifest schema

`DANI001_SYNTHETIC_MANIFEST.json` is canonical JSON with exactly these
top-level keys:

```
schema                 string, exactly "dani001-synthetic-manifest-v1"
science_spec           {commit,path,sha256}
calibration_spec       {path,sha256}
counter_protocol       {root,labels,sha256}
worlds                 array in toy, plant, null, adversary order
parser_fixture         object
mutations              array in the order above
aggregate_expectations object
```

Each world object has exactly:

```
world_id, family, trial_index, variable_count, permutation_count,
candidate_rank, secret_rank, alternate_rank, generator_fields,
row_count, row_sha256s, rows_sha256, lexicon_record_count,
reachable_key_count, lexicon_sha256, dot_panel_sha256,
manual_panel_sha256, world_sha256, expected
```

Unavailable ranks are JSON `null`; no field is omitted.  Family/trial values
are exhaustive and fixed: `TOY4_PLANT` and `TOY6_PLANT` have family
`TOY_PLANT`, trial index 0; `TOY4_NULL` and `TOY6_NULL` have family `TOY_NULL`,
trial index 0; `PLANT_000..099` have family `PLANT` and trial indices `0..99`;
`NULL_000..127` have family `NULL` and trial indices `0..127`; and the six
adversaries have family `ADVERSARY` and trial indices `0..5` in their listed
order.

`generator_fields` is the ordered array of every recorded bounded draw in
actual construction order, each exactly `[label,[modulus,*call_fields],result]`.
It includes failed unique-rank collision candidates, failed first-nonidentity
permutations, and rejected decoy attempts; it excludes only internal SHA
rejection attempts.  The field domains are exact: unique rank draws use
`[N-1,sequence_index,collision_attempt]`; null-key-tail draws use Fisher--Yates
fields `[i+1,trial_index,type_index,completed_step]`; toy-map draws use
`[i+1,m,plant_null_index,nonidentity_attempt,completed_step]` where
`plant_null_index` is 0 or 1; toy-null tails use
`[i+1,1000+m,type_index,completed_step]`; adversary decoys use
`[i+1,adversary_index,type_index,decoy_attempt,completed_step]`; and conjugacy
uses `[i+1,nonidentity_attempt,completed_step]`.

Every world's `expected` is exactly
`{"assertion_count":1,"assertions":[{"id":ID,"operator":"WORLD_SIGNATURE","value":true}]}`.
IDs are `TOY4_PLANT_COMPLETE_EQUALITY`, `TOY4_NULL_COMPLETE_EQUALITY`,
`TOY6_PLANT_COMPLETE_EQUALITY`, `TOY6_NULL_COMPLETE_EQUALITY`;
`PLANT_ddd_SUCCESS`; `NULL_ddd_PROBE_INDEPENDENCE`; and
`ADVERSARY_` plus the adversary world ID plus `_SIGNATURE`, respectively.
These signature assertions mean every clause in that world's named section,
not a selectable subset.

Each mutation object has exactly `mutation_id,assertion_id,base_world_id,
operation,mutated_input_sha256,payload_sha256s,expected_status,
expected_equalities`.  `assertion_id` is `MUTATION_` plus `mutation_id`.
`payload_sha256s` is an object whose sorted keys name every distinct byte body
used by the mutation.  It is `{"mutated":mutated_input_sha256}` except for
`UNREACHABLE_REMOVE`, where it has exactly `full,removed_records,without`, and
`UNREACHABLE_RESTORE_ADD_FROM_REMOVED`, where it has exactly
`removed_records,restored,without`; `mutated_input_sha256` is respectively the
`without` and `restored` digest.  The manifest
contains no actual source group, normalized type, folio ID, key, spelling, or
meaning.  The clean validator regenerates every row/key from this specification
and checks all manifest digests; it never trusts manifest expected values as
computed outcomes.

There are exactly 238 world objects.  `parser_fixture` has exactly
`fixture_id,row_count,row_sha256s,rows_sha256,dot_panel_sha256,
manual_panel_sha256,strict_literal_counts,expected`; its fixture ID is
`PARSER_CANONICAL` and it is not counted among the 238 scored worlds.

`aggregate_expectations` has exactly `control_order,assertion_ids,totals,
generator_fields,plant_success_min,null_false_pass_max,world_count,
atomic_assertion_count`.  `generator_fields` is exactly
`{"conjugacy":[...]}` and contains every bounded draw, including rejected
identity attempts, used to select the registered conjugacy permutation in the
same triple encoding as world generator fields; no other control uses a draw.
`control_order` is exactly `toys,plants,nulls,adversaries,parser,mutations,
conjugacy,workers,affix_equivalence,unreachable_invariance`.  For each name,
`assertion_ids` is the following ordered expansion and `totals` is its length:

- toys: the four toy IDs above, 4;
- plants: `PLANT_ddd_SUCCESS` for `000..099`, 100;
- nulls: `NULL_ddd_PROBE_INDEPENDENCE` for `000..127`, followed by
  `NULL_FALSE_PASS_COUNT_LE_1`, 129;
- adversaries: the six adversary signature IDs in world order, 6;
- parser: `PARSER_PRIMARY_SELECTION`, `PARSER_SEPARATOR_STATES`,
  `PARSER_PANEL_INDEPENDENCE`, `PARSER_STRICT_PROPAGATION`, 4;
- mutations: `MUTATION_` plus each of the 20 mutation IDs in listed order, 20;
- conjugacy: `CONJUGACY_VECTOR_EQUALITY`, 1;
- workers: `WORKER_1_32_VECTOR_EQUALITY`, 1;
- affix equivalence: `AFFIX_` plus each of the 238 world IDs plus
  `_EQUIVALENCE`, in world order, 238;
- unreachable invariance: `UNREACHABLE_` plus each ten-variable world ID plus
  `_INVARIANCE`, in plant, null, adversary order, 234.

The exact totals object in control order is therefore
`{"toys":4,"plants":100,"nulls":129,"adversaries":6,"parser":4,
"mutations":20,"conjugacy":1,"workers":1,"affix_equivalence":238,
"unreachable_invariance":234}`.  `plant_success_min` is 95,
`null_false_pass_max` is 1, `world_count` is 238, and
`atomic_assertion_count` is exactly 737.  Any duplicate, absent, extra, or
reordered assertion ID hard-stops before scoring.

## Actual score-blind capacity stage

The synthetic stage completes before the producer opens any of the three real
transcription sources, separator atlas, separator validation, or external
lexicon body for parsing.  Hashing downloaded external bodies during the
acquisition stage is not parsing or scoring.  The producer completes all
synthetic worlds and controls even after one synthetic failure, so the fixed
aggregate denominator cannot depend on the first failure.  If any synthetic
aggregate fails, it records a synthetic failure and exits without opening real
panel inputs.

After a complete synthetic pass, reconstruct both real panels and all lexicon
views exactly as the science specification requires.  The scoring API for an
object tagged `ACTUAL` accepts only the closed-open rank range
`[1,3,628,800)`.  A start rank of zero, a full-orbit request, subtraction from
a known all-rank total, a request for the released mapping, or an attempt to
serialize a rank-indexed actual vector hard-stops.  No generic default rank
range exists.  The optimized core records monotonically increasing counters
for actual rank intervals, logical map/view evaluations, match calls, and
output writes.  All 12 views and all six edition/panel surfaces are completed
even when an earlier view already implies a capacity stop.  The only permitted
actual rank interval is `[1,3,628,800)`.  The primary capacity has exactly 72
logical view/surfaces and `72*3,628,799 = 261,273,528` logical map/view
evaluations.  The independently scored implementation evidence adds exactly
18 logical surfaces--six literal-affix, six without-unreachable, and six
restored-unreachable--and `18*3,628,799 = 65,318,382` logical evaluations.
Thus every valid actual run has exactly 90 logical surfaces and 326,591,910
logical evaluations.  An implementation may batch views in one physical
traversal but may not change, omit, or double-count those logical totals.

Every actual constraint compiler applies the lexicographic rank-interval lower
bound before evaluating a completed assignment.  It may traverse only
permutation-tree branches whose rank interval intersects `[1,3,628,800)` and
may never construct the identity leaf, test whether a constraint is compatible
with identity, compute then discard rank 0, subtract an identity contribution,
or use a full-orbit complement.  Rank-audit counters are incremented by the
same compiler/evaluator calls that produce the vectors; they may not be filled
with expected constants afterward.  This is the operative meaning of rank 0
being neither evaluated nor inferred.

For each registered view, edition, and panel, capacity independently computes:

- permutation-variable normalized-type count using nonidentity ranks only;
- capacity-folio count using nonidentity-variable types only;
- positive-finite-population-SD booleans for token, type, and equal-folio raw
  vectors over nonidentity ranks;
- nonidentity raw-vector SHA-256 digests;
- literal-decision versus pre-expanded-affix equality where applicable.

Views are ordered exactly:

1. `FULL_DEPOSITED_AFFIX`
2. `DIRECT_ONLY`
3. `STRICT_NO_FUNCTION`
4. `STRICT_LITERAL`
5. `TOP20_DELETED`
6. `SOURCE_PRESENT`
7. `LEAVE_ASTRO_OUT`
8. `LEAVE_BOTANICAL_OUT`
9. `LEAVE_FUNCTION_OUT`
10. `LEAVE_GENERAL_OUT`
11. `LEAVE_MEDICAL_OUT`
12. `LEAVE_PHARMA_OUT`

Within a view the order is edition `ZL3b,IT2a,RF1b`, panel
`DOT_ONLY_EMULATION,MANUAL_GROUP`, weighting `TOKEN,TYPE,FOLIO`.  Top-20 lists,
variable type identities, capacity-folio identities, normalized forms, keys,
and match examples remain private transient memory; not even their digests are
serialized.  Only their counts and aggregate score-vector digests may leave
the process.

Primary, direct-only, strict-no-function, and strict-literal capacity require
at least 100 variable types and 20 capacity folios in each edition/panel plus
all 18 SD booleans.  Top-20 deletion requires 80/20 plus all SD booleans.
`SOURCE_PRESENT` is powered at 30/10; leave-one-domain views at 100/20.  A
conditional view below its threshold is `INSUFFICIENT` and nonblocking.  A
mandatory view below threshold fails capacity.  All actual affix comparisons
and unreachable-key invariances must pass.

Failure of either actual implementation invariant--literal deposited-affix
decisions versus pre-expanded affix sets at any registered nonidentity rank, or
score-vector equality after removing/restoring the bound unreachable keys--is
exactly `OUTPUT_FREE_IMPLEMENTATION_INVARIANT_STOP`.  The process immediately
cleans every temporary directory and in-memory acquisition, installs neither
result nor report, creates no target freeze, and does not map the failure onto a
scientific status below.  Capacity decisions continue only when both
implementation invariants pass.

No mean, median, z score, `T`, tail, identity match, identity numerator, or
identity-relative direction is computed in this stage.  Nonidentity means and
SDs may be transiently computed only to decide finite positive SD; only the
boolean is output.  The validator repeats this same nonidentity-only procedure
independently.

## Calibration freeze and access isolation

`DANI001_CALIBRATION_FREEZE.json` is canonical JSON and has exactly:

```
schema, registered_commit, science_spec, calibration_spec,
local_inputs, external_inputs, code, synthetic_manifest,
runtime, core_build, read_allowlist, network_allowlist, temporary_allowlist,
producer_outputs_absent, validator_outputs_absent,
producer_write_allowlist, validator_write_allowlist,
static_audit
```

`schema` is exactly `dani001-target-blind-calibration-freeze-v1`.

Every path-bearing member is repository-relative and has `path,sha256,size`.
`code` is an array in exact order: panel, calibration generator, core Python,
core header, core C++, producer, validator, using the seven exact paths named
above.  The read and write allowlists are canonical arrays of exact path
strings; the network allowlist is the three exact science-specification URLs.
`science_spec`, `calibration_spec`, and `synthetic_manifest` are single exact
`path,sha256,size` objects.  `local_inputs` is an array of five such objects in
exact order ZL3b, IT2a, RF1b, source-separator TSV, source-separator validation
JSON.  Their paths and hashes are the exact science-specification values and
their sizes are recomputed from the bound bytes when the freeze is created.

`external_inputs` is an array of exactly these three objects in this order and
with no extra members:

```
{"name":"stable_metadata_projection",
 "url":"https://zenodo.org/api/records/19583305",
 "sha256":"780301fd3c4b2c3c328c1f69a1eab65d0b0600f2d491ea9578f81699d36ddfa7",
 "storage":"MEMORY_ONLY_CANONICAL_PROJECTION"}
{"name":"pipeline_body",
 "url":"https://zenodo.org/api/records/19609475/files/pipeline_v31_1.py/content",
 "sha256":"079b6de7b8d2082303a0789fb3904105aecaa491e35600a557090e7981255d6f",
 "storage":"EXTERNAL_TEMPORARY_ONLY_INERT"}
{"name":"lexicon_body",
 "url":"https://zenodo.org/api/records/19609475/files/lexicon_v31_session31_final.json/content",
 "sha256":"348992fa2bf555f1454a5a5485dd1ca9842acc143059f257f2fcdcf237821589",
 "storage":"EXTERNAL_TEMPORARY_ONLY_PROJECT_AFTER_SYNTHETICS"}
```

`registered_commit` is `1faa87f`.  `runtime` fixes CPython 3.12.3,
little-endian IEEE-754 x86-64, compiler identity/flags, OpenMP runtime, one and
32 workers, locale `C`, timezone `UTC`, and every imported package version.
It has exactly `python,implementation,machine,system,byteorder,binary64,numpy,
locale,timezone,workers,openmp_library_name,openmp_library_sha256,
runtime_image_sha256`.  Their registered values are respectively `3.12.3,
CPython,x86_64,Linux,little,IEEE754_ROUND_TO_NEAREST,1.26.4,C,UTC,[1,32]`;
the two OpenMP members are the basename and SHA-256 of the unique
`libgomp.so` target reported by `/usr/bin/ldd` on the just-built bound core
library.  Form `runtime_image_sha256` by first canonical-JSON hashing the
runtime object containing the first twelve members but not
`runtime_image_sha256`, then insert the lower-case digest as the thirteenth
member.  Canonical key sorting, not prose member order, fixes its bytes.

`core_build` fixes executable path
`/usr/bin/x86_64-linux-gnu-g++-12`, executable SHA-256
`1cfb9704049655d08accca3b1aeefd6fc749ef2cfb992ec95a81f39091d7b3ce`,
and exact `--version` stdout bytes (including exactly two terminal LF bytes):

```
x86_64-linux-gnu-g++-12 (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0
Copyright (C) 2022 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

```

It also binds the runtime-image digest and exact argv array
`["/usr/bin/x86_64-linux-gnu-g++-12","-std=c++20","-O3","-DNDEBUG",
"-fPIC","-shared","-fopenmp","-fno-fast-math","-ffp-contract=off",
"dani001_core.cpp","-o","libdani001_core.so"]`, plus the expected
shared-library SHA-256 and ABI version 1.  No PATH lookup or compiler alias is
permitted.
`core_build` has exactly `compiler_path,compiler_sha256,
compiler_version_stdout_hex,argv,shared_library_sha256,abi_version,
runtime_image_sha256`.  The version member is the lower-case hexadecimal
encoding of the exact stdout bytes above, with no stderr; `argv` is the exact
array above; `runtime_image_sha256` equals the runtime object's member; and
`shared_library_sha256` is recomputed from the fresh exact build rather than
copied from an earlier file.
The producer copies the already hash-verified `.cpp` and `.h` bytes into its
fresh temporary directory under those basenames, uses that directory as the
compiler working directory, rebuilds the library, verifies the bound digest,
and only then loads it.  Compiler-created files and execution/loading of that
one verified library are part of `temporary_allowlist`.  The clean validator
may compile a separately written implementation embedded literally in its own
source; `core_build` separately binds its exact argv and expected binary hash,
and its symbols/data layout may not be copied from or linked to producer core.
`static_audit` has exactly `status,review_id,auditor_source_sha256`; status must
be `GO`, review ID must be `DANI001_CALIBRATION_FREEZE_STATIC_AUDIT_V1`, and the
hash must be 64 lowercase hexadecimal characters before execution.

The freeze arrays are exact and ordered.  `read_allowlist` is science spec,
calibration spec, calibration freeze, synthetic manifest, panel, generator,
core Python, core header, core C++, producer, followed by the five
`local_inputs` paths in their order above.  It deliberately omits the clean
validator.  `network_allowlist` is the three `external_inputs` URLs in their
array order.  `temporary_allowlist` is exactly
`EXTERNAL_ACQUISITION_EXACT_THREE_FILES,CORE_BUILD_CPP_HEADER_LIBRARY,
OUTPUT_STAGING_TWO_FILES`.  `producer_outputs_absent` and
`producer_write_allowlist` are result JSON then result Markdown;
`validator_outputs_absent` and `validator_write_allowlist` are validation JSON
then validation Markdown, using the exact paths named at the start of this
contract.  Every listed absent path must return `ENOENT` under `lstat` at
freeze creation; these are path strings, not path/hash objects.

Producer application-level reads before the synthetic gate are limited to the
two specs, calibration freeze, synthetic manifest, panel builder, generator,
three integer-core sources, and producer.  It may acquire only the three HTTPS
endpoints in the science spec.  `dani001_panel.py` must expose and the producer
must use the exact acquisition-only context-manager API
`acquire_registered_external_files()`.  Entry
downloads and hash-checks all three responses.  It may JSON-parse the concept
response only to apply the already registered `stable_metadata_projection`
field projection, canonicalize that projection, and verify its bound digest;
it does not parse the lexicon and does not import, compile, or execute the
pipeline.  The raw concept response exists only as an in-memory `bytes` object,
is never written to a filesystem, and is released immediately
after the verified projection bytes have been produced.

The acquisition context owns one fresh `mkdtemp` directory outside the
repository.  Immediately before, throughout, and immediately after the entire
synthetic gate, its inventory is exactly three regular files and no directory
or symlink: `pipeline.py.txt` containing the exact pipeline response body,
`lexicon.json` containing the exact lexicon response body, and
`stable_metadata_projection.json` containing exact canonical stable-projection
bytes.  Thus the temporary inventory is exactly two external bodies plus one
projection.  No concept body, parsed lexicon, compiled core, result staging
file, or other object may share this directory.  The compiler uses a separate
fresh build directory and output staging uses a third fresh directory.

The context exposes no parsed lexicon before the gate.  Only after every
synthetic assertion passes may the producer call exactly once
`project_acquired_lexicon(acquisition,synthetic_gate_passed=True)`.  The
call re-hashes all three retained files, byte-compares the retained stable
projection to the exact pre-gate canonical projection bytes, and verifies its
bound digest.  It JSON-parses only `lexicon.json` and constructs the real
lexicon views.  It does not JSON-parse `stable_metadata_projection.json`
post-gate; that projection was constructed and validated before the synthetic
gate.  After the call returns, the producer may open the five local
transcription/atlas inputs.
The producer freezes a projection-call counter at zero before synthetics,
increments it to one immediately before this call, and hard-stops before any
attempted second call.  The pipeline body
remains inert and is never imported or executed.  On synthetic failure the
one-shot method is never called, all three files are deleted, and no actual
local input is opened.  Temporary
creation, write, fsync, read, and deletion are the complete
`temporary_allowlist`; no other external path is allowed.  The producer may
not read its destinations or validator source.  Acquisition and body hashing
precede installation of repository read isolation; parsing remains behind the
completed synthetic gate.

The validator initially may read only the two specs, both manifests, the six
other implementation sources as opaque hash-bound bytes, producer result and
report, and its own source as executable validator code.  It may not import or
execute the panel builder, generator, integer core, or producer.  It first
independently regenerates every synthetic object from this prose contract.  If
its synthetic reconstruction fails, or if the byte-validated producer decision
is `STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED`, it must validate
`actual_capacity:null`, the unopened counters, and output bytes without any
network access and without opening any of the five actual local inputs.  A
producer/validator disagreement on synthetic pass status fails validation
output-free and likewise grants no actual access.

Only when both producer bytes and the independent reconstruction establish a
complete synthetic pass may the validator independently reacquire the three
allowlisted HTTPS endpoints under the same memory-only-concept/exact-three-file
inventory rule and open the five local inputs.  It then independently parses
and reconstructs actual capacity.
Its only writes are its two no-clobber outputs and its temporary acquisition
files.  Application-level filesystem and network calls outside these lists
hard-stop and are counted by syscall-audit hooks.  Dynamic-loader and standard-
library reads are frozen by the runtime image digest and cannot expose a
repository file.

The freeze records exact absence (`lstat` returns `ENOENT`) of all four output
paths.  Freeze mismatch, forbidden access, network/hash mismatch, or an output
collision is an output-free stop.  Scientific control or capacity failure,
after valid inputs and isolation are established, is instead a valid negative
calibration result.

## Producer result schema and decisions

The producer result is canonical JSON with exactly these top-level keys:

```
schema, experiment, status, claim_ceiling, registered_science,
calibration_spec, calibration_freeze_sha256, synthetic_manifest_sha256,
runtime, isolation, input_checks, synthetic_controls, actual_capacity,
identity_access, decision
```

`schema` is `dani001-target-blind-calibration-result-v1`; `experiment` is
`DANI001`; `claim_ceiling` is exactly `Target-blind engineering calibration
only; no language, lexeme, plaintext, or translation.`
Hash/path objects contain only `path,sha256,size`.  `runtime` contains the
frozen string fields and worker counts.  `isolation` has exactly these fields:

```
read_allowlist_pass, write_allowlist_pass, network_allowlist_pass,
temporary_allowlist_pass, output_destinations_absent_pass,
acquisition_inventory_pass, synthetic_gate_actual_access_pass,
forbidden_read_count, forbidden_write_count, forbidden_network_count,
temporary_inventory_violation_count, output_collision_count,
pre_synthetic_actual_local_read_count,
pre_synthetic_lexicon_projection_call_count,
post_synthetic_lexicon_projection_call_count
```

The seven `_pass` members are JSON booleans and must all be true in any
installed result.  All five violation/collision counts and both pre-synthetic
counts are integer zero.  `post_synthetic_lexicon_projection_call_count` is
integer zero for a synthetic-failure result and integer one otherwise.

`input_checks` has exactly `registered_commit_pass,science_spec_pass,
calibration_spec_pass,calibration_freeze_pass,synthetic_manifest_pass,
code_hashes_pass,runtime_pass,compiler_binary_pass,core_build_pass,
external_pipeline_body_pass,external_lexicon_body_pass,
stable_projection_pass,local_inputs_pass`.  The first twelve are JSON `true`
in any installed result.  `local_inputs_pass` is `null` when synthetics fail
and actual local inputs remain unopened, and `true` otherwise.  A false value
is an output-free input-contract stop.  Neither object may contain a path,
source value, source group, normalized type, lexicon key, template, or digest
of any such identity.

`synthetic_controls` has exactly `toys,plants,nulls,adversaries,parser,
mutations,conjugacy,workers,affix_equivalence,unreachable_invariance`.  Every
member contains `total,passed,failed,aggregate_sha256,gate`; plants additionally
contain integer `successful` and threshold 95; nulls contain integer
`false_passes` and threshold 1.  No individual favorable string or row is
included.

For control name `C`, take its exact manifest `assertion_ids[C]` order and form
one in-memory assertion object per ID.  Ordinarily it has exactly `id,passed`,
where `passed` is a JSON boolean.  For `affix_equivalence` and
`unreachable_invariance` only, it has exactly `id,passed,evidence_sha256`; the
evidence member is the corresponding canonical evidence-object digest defined
above and must be lower-case 64-hex.  Let `BASE(C)` be the object with exactly
`control,assertions,total,passed,failed,gate`; `control` is `C`, `assertions`
is that ordered object array, `total` is its length, `passed` is the sum of its
true values, `failed=total-passed`, and `gate` is the registered aggregate
boolean.  For plants, `BASE` additionally has `successful` and `threshold`
with threshold 95; for nulls it additionally has `false_passes` and `threshold`
with threshold 1.  No other member is present.  Each
`synthetic_controls[C].aggregate_sha256` is SHA-256 of `BASE(C)` encoded with
the registered canonical-JSON settings and exactly one terminal LF.  The
public control member is `BASE(C)` with `control` and `assertions` removed and
`aggregate_sha256` inserted; its integer/boolean members must equal the
preimage.  This fixes all ten aggregate hash preimages without exposing an
individual string or outcome in the result.

`PASSED/TOTAL` in Markdown is the sum of the `passed` and `total` integer fields
across those ten members in their listed order.  It is not the number of world
trials.  The manifest freezes every atomic assertion contributing to each
member's total, so no implementation may combine or split checks after seeing
an outcome.

When synthetics pass, `actual_capacity` contains exactly `panel_counts,
lexicon_counts,views,mandatory_capacity_pass,conditional_view_statuses,
actual_nonidentity_vector_digest_sha256,
implementation_invariant_digest_sha256`.  It contains no panel-template field
or digest.

`panel_counts` is an array of exactly six objects in edition
`ZL3b,IT2a,RF1b`, then panel `DOT_ONLY_EMULATION,MANUAL_GROUP` order.  Each
object has exactly `edition,panel,token_count,normalized_type_count,
folio_count,strict_literal_token_count`; the last four fields are nonnegative
JSON integers.  It contains no type identity or template digest.

`lexicon_counts` has exactly `keys,entries,reachable_keys,unreachable_keys,
source_present_keys,source_present_reachable_keys,strict_no_function_keys,
strict_no_function_reachable_keys,views`.  Its first eight fields are
nonnegative JSON integers.  `views` is an array in exact order `FULL,
REACHABLE,SOURCE_PRESENT,STRICT_NO_FUNCTION,LEAVE_OUT_ASTRO,
LEAVE_OUT_BOTANICAL,LEAVE_OUT_FUNCTION,LEAVE_OUT_GENERAL,LEAVE_OUT_MEDICAL,
LEAVE_OUT_PHARMA`; each object has exactly `view,total_key_count,
reachable_key_count,direct_code_count,deposited_affix_code_count`, with four
nonnegative integer counts.  No key, code, preimage, or identity digest is
serialized.

`views` is an array in the fixed 12 scoring-view order.  Each element has
exactly `view,surfaces`; `surfaces` has six objects in the same edition/panel
order as `panel_counts`.  Each surface has exactly `edition,panel,
variable_type_count,capacity_folio_count,token_sd_positive,type_sd_positive,
folio_sd_positive,token_nonidentity_vector_sha256,
type_nonidentity_vector_sha256,folio_nonidentity_vector_sha256,
affix_equivalence`.  Counts are nonnegative integers; SD members are booleans;
the three SHA members are lowercase 64-hex digests; and `affix_equivalence` is
a boolean exactly for `FULL_DEPOSITED_AFFIX` and JSON `null` for every other
view.  Component digests hash ranks `1..3,628,799` in ascending rank order as
contiguous little-endian `<u4` for token/type integer numerators and `<f8` for
folio binary64 values, with no header or terminal bytes.

`mandatory_capacity_pass` is one JSON boolean.  `conditional_view_statuses`
is an array in exact order `SOURCE_PRESENT,LEAVE_ASTRO_OUT,
LEAVE_BOTANICAL_OUT,LEAVE_FUNCTION_OUT,LEAVE_GENERAL_OUT,LEAVE_MEDICAL_OUT,
LEAVE_PHARMA_OUT`; each object has exactly `view,status`, where status is
`POWERED` iff all six surfaces meet that view's frozen count thresholds and
all three SD booleans, and is otherwise `INSUFFICIENT`.

To form `actual_nonidentity_vector_digest_sha256`, traverse scoring view,
edition, panel, and weighting `TOKEN,TYPE,FOLIO` in those exact nested orders.
For each of the 216 components append one object with exactly
`view,edition,panel,weighting,dtype,rank_start,rank_stop,sha256`; `dtype` is
`<u4` for token/type and `<f8` for folio, `rank_start` is integer 1,
`rank_stop` is integer 3628800, and `sha256` is the corresponding component
digest stored in `views`.  Hash the canonical JSON object
`{"schema":"dani001-actual-nonidentity-vector-digest-v1","entries":[...]}`
with the registered canonical encoding and one terminal LF.  No rank-0 value,
type/template identity, or panel digest enters this preimage.

The actual implementation-invariant digest binds private equivalence evidence
without serializing it.  In surface then weighting order, transiently form one
affix entry with exactly `edition,panel,weighting,dtype,
literal_decision_function_sha256,literal_raw_sha256,
expanded_decision_function_sha256,
expanded_raw_sha256`, and one unreachable entry with exactly
`edition,panel,weighting,dtype,full_raw_sha256,without_raw_sha256,
restored_raw_sha256`.  Decision-function digests hash the complete private
Boolean functions using the canonical constraint encoding above, restricted
to this entry's surface/view; raw digests use the component byte rules above.
Hash canonical JSON object
`{"schema":"dani001-actual-implementation-invariants-v1",
"rank_start":1,"rank_stop":3628800,"affix":[...],"unreachable":[...],
"affix_pass":true,"unreachable_pass":true}` with one LF.  Store only that
lower-case digest as `implementation_invariant_digest_sha256`; the entry
arrays, decision-function digests, and private ordering never leave either process.  The
two pass members must be true or the output-free implementation-invariant stop
applies.

When synthetics fail, `actual_capacity` is JSON `null`.

When synthetics pass, `identity_access` is exactly

```
{"rank0_requests":0,"rank0_maps_evaluated":0,"rank0_match_calls":0,
 "rank0_values_stored":0,"rank0_values_inferred":0,
 "actual_rank_interval_start":1,"actual_rank_interval_stop":3628800,
 "actual_primary_logical_view_surfaces":72,
 "actual_evidence_logical_view_surfaces":18,
 "actual_logical_view_surfaces":90,
 "actual_primary_logical_map_view_evaluations":261273528,
 "actual_evidence_logical_map_view_evaluations":65318382,
 "actual_logical_map_view_evaluations":326591910}
```

All five rank-0 fields remain zero.
The primary and evidence counters are incremented at entry to the exact
scoring calls that create the corresponding vectors; the total fields are
checked sums, not separately assigned constants.  Every one of the 90 calls
passes the same live core audit object.  That object must report zero completed
rank-0 leaves and no rank interval other than `[1,3,628,800)` before the public
zero fields may be emitted.

When synthetics fail, the five rank-0 fields remain zero and the remaining
fields are exactly

```
{"actual_rank_interval_start":null,"actual_rank_interval_stop":null,
 "actual_primary_logical_view_surfaces":0,
 "actual_evidence_logical_view_surfaces":0,
 "actual_logical_view_surfaces":0,
 "actual_primary_logical_map_view_evaluations":0,
 "actual_evidence_logical_map_view_evaluations":0,
 "actual_logical_map_view_evaluations":0}
```

Status and decision are identical strings chosen in this order:

1. `STOP_SYNTHETIC_CALIBRATION_FAILURE_IDENTITY_UNOPENED` if any required
   synthetic aggregate fails; no actual panel was opened.
2. `STOP_UNPOWERED_BEFORE_RELEASED_MAP_SCORE` if the real primary capacity is
   below 100/20 or has a nonpositive/nonfinite component SD.
3. `STOP_MANDATORY_ROBUSTNESS_CAPACITY_BEFORE_RELEASED_MAP_SCORE` if primary
   capacity passes but direct-only, strict-no-function, strict-literal, or
   top-20 mandatory capacity fails.
4. `PASS_TARGET_BLIND_CALIBRATION_AND_CAPACITY_IDENTITY_UNOPENED` otherwise;
   conditional insufficient views are recorded but do not block.

There is no generic `ERROR` result: schema, hash, isolation, malformed input,
or numeric-contract errors are output-free hard stops.

Integer fields remain JSON integers, including zero.  The science spec's
positive-zero rule applies to binary64 fields only: either sign of binary64
zero serializes as `0.0`.  Other floats use CPython 3.12.3 JSON rendering;
nonfinite values hard-stop.  All JSON uses the canonical settings already
defined and ends with one LF.

The producer Markdown is exactly these lines, with one terminal LF and no
extra whitespace:

```
# DANI001 target-blind calibration

- Status: `STATUS`
- Synthetic controls: `PASSED/TOTAL`
- Distributed plants: `SUCCESSFUL/100` (required >=95)
- Map-independent null false passes: `FALSE_PASSES/128` (required <=1)
- Actual mandatory capacity: `PASS|FAIL|NOT_OPENED`
- Real rank-0 evaluations: `0`
- Real rank-0 inferences: `0`
- Decision: `DECISION`
- Claim ceiling: conditional engineering calibration only; no language, lexeme, plaintext, or translation.
- Result JSON SHA-256: `HEX`
```

String placeholders are inserted without JSON quote characters; integers are
unsigned base-10 with no leading zero; ratios use those integer renderings
separated by `/`; and `HEX` is the 64-character lowercase producer-JSON digest.

## Independent validation schema

The nonimporting validator reconstructs every manifest object, all 238 scored
synthetic worlds (4 toy + 100 plant + 128 null + 6 adversary), all
mutations, all complete toy and ten-factorial vectors, and the actual
nonidentity capacity from raw inputs.  It verifies producer JSON and Markdown
byte for byte, but never calls any producer function or examines actual rank 0.

Validation JSON has exactly:

```
schema, experiment, status, independent, imported_producer,
executed_producer, registered_science_sha256, calibration_spec_sha256,
calibration_freeze_sha256, synthetic_manifest_sha256,
producer_result_sha256, producer_report_sha256,
checks_total,checks_passed,checks_failed,reconstructed,
identity_access,decision
```

`schema` is `dani001-target-blind-calibration-validation-v1`;
`independent` is true; both import/execute fields are false.  `reconstructed`
contains integer world, row, permutation, vector, parser, mutation, and
capacity-view counts plus aggregate digests.  `identity_access` repeats the
five exact zero fields.  `status` is `PASS` only when `checks_failed==0`, every
producer byte and decision is reproduced, and both implementations record zero
real rank-0 access; otherwise no validation artifact is installed.

Validation Markdown is exactly:

```
# DANI001 target-blind calibration validation

- Status: `PASS`
- Checks: `CHECKS_PASSED/CHECKS_TOTAL`
- Reconstructed synthetic worlds: `238`
- Real rank-0 evaluations: `0`
- Real rank-0 inferences: `0`
- Producer decision: `DECISION`
- Producer result SHA-256: `HEX`
- Independent implementation: `true`
```

It ends with one LF.  A failed validation installs neither validation file.

## Transition to the second freeze

Only a byte-valid producer decision
`PASS_TARGET_BLIND_CALIBRATION_AND_CAPACITY_IDENTITY_UNOPENED` plus a clean
validation `PASS` permits construction of `DANI001_TARGET_FREEZE.json`.  That
freeze must bind the registered commit, both specifications, calibration and
synthetic manifests, all implementation sources, all four calibration
artifacts, exact runtime, external acquisitions/projection, and absence of the
four observed-result paths named in the science spec.  It may not alter a
mapping, panel, view, generator, threshold, gate, numeric rule, output schema,
or claim ceiling.  Any other calibration outcome leaves the real released map
unopened and closes this registered run without retuning.
