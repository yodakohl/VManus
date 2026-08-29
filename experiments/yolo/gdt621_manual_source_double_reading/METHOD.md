# GDT621 method

## Question

Can two blinded readers independently produce and reconcile a diplomatic Latin
heading-plus-twelve-token transcription before any control or Voynich target
access?

## Inputs

GDT620 acquisition code was registered publicly in commit
`61a253ce2756ad06a6c69c620e702500f5e640ef`. The resulting public acquisition
artifact was published separately in commit
`798e05f46e79c4abd2047577669d3a67d561ec51` with SHA-256
`f14976f54fd4ea0424ada9f23d19e7f02424beff739f5b4943dd3b0329ae378e`.
Ten private JPEGs are bound by exact filename, hash, and dimensions, never by
private directory.

## Method

Latin DEV01–DEV05 are read first. Readers A and B work in separate agent and
rendering sessions with distinct session IDs and receive only an opaque DEV ID
and private JPEG. Registered headwords are locator hints, not a blind discovery
endpoint. Profile, repository, catalog, edition, network, other sources, and
the other reader's material may not be consulted; each reader attests this.
Each starts with the full page and may then zoom or use an unsaved in-memory
crop. Outputs remain only in root-mailbox storage, not the shared workspace,
until both readers complete all pages.
The exact packet fields are `opaque_candidate_id`, `source_sha256`, `session_id`,
and a path-free `opaque_rendering_handle`; no additional keys are allowed.
It is canonical UTF-8 sorted-key compact JSON with final LF, and SHA-256 is
computed over that payload with no hash field. The reader attests the exact
keys and packet hash. Headword, witness/control identity, URL, crosswalk, profile/repository
locator, expected rubric, filename/path, and other submission are excluded.
The handle matches `^R[AB][0-9]{2}-[0-9A-F]{16}$` and carries no semantic text,
path, URL, or headword.

Each reader diplomatically submits the visible heading/rubric and exactly the
first twelve whitespace-delimited lexical tokens after it; these tokens are the
primary new capture. Read the main text block top-to-bottom then left-to-right;
exclude marginalia and image labels. The rubric ends at the visible transition
to main text. A token is a maximal non-whitespace codepoint run; line breaks are
whitespace, while punctuation and abbreviation signs stay attached. Codepoints, spacing,
abbreviation marks, and token boundaries are preserved; uncertainty is noted by
position using the V1 ASCII tags below; boundary doubt is separate. Nothing is
silently normalized or expanded.
Notation is `GDT621_DIPLOMATIC_V1`: preserve exact UTF-8 codepoints without
Unicode normalization. A non-keyboard sign is `<SIGN:DESCRIPTION>`, uncertainty
is `<UNCERTAIN:x>`, and unreadable is `<UNREADABLE>`; tags contain no whitespace.

Each five-page raw submission is canonical UTF-8 sorted-key compact JSON with
final LF and exact SHA-256. The hash preimage omits its own hash field. A's five
rows and commitment are verified before B's five rows and commitment; both raw
commitments then freeze before reconciliation. Only then does
reconciliation compare every codepoint, space, abbreviation mark, and token
boundary. Every disagreement receives a ledger row with both forms, type,
reconciled form, reason, adjudicator, and time. Agreement requires an explicit
zero-difference row. Reconciliation is frozen as canonical
`artifacts/LATIN_RECONCILIATION_FROZEN.json`, status
`LATIN_RECONCILIATION_FROZEN__CLM_UNOPENED`, and publicly committed before Clm
DEV01–DEV05 open as separate rubric/locator controls. Clm may not repair,
replace, normalize, or adjudicate Latin.
Each reader has exactly one ordered DEV01–DEV05 bundle, each page exactly once;
its bundle SHA excludes `bundle_sha256`, page source hashes match the registered
Latin bindings, and there is no recursive per-page submission hash.
The checkpoint cannot be empty or status-only: its exact schema contains
experiment/status, GDT620 binding, both bundle hashes, all five reconciled
rubric-plus-12-token readings, the complete ledger, reconciliation access audit,
canonicalization, claim ceiling, and a nonrecursive checkpoint hash. The final
result binds its public commit and SHA and byte-identically reuses bundle hashes,
reconciled Latin, and ledger; later Latin change is forbidden.
Before checkpoint hashing the adjudicator attests IDs/timestamps and that only
the frozen bundles and five Latin JPEGs were used for glyph resolution. Clm,
network, repo/profile, catalog, edition, other-source, Voynich, f84, and f84r
access counts are zero.
For a zero-difference page the sole ledger sentinel is row kind
`AGREEMENT_NO_DIFFERENCE`, with no invented position and null reading,
resolution, adjudicator, and timestamp fields. Other rows are `DIFFERENCE`.

All display is local: the immutable source JPEG exists and is never rewritten.
After full-page display, temporary in-memory renderer output may be scaled or
resampled for zoom. No derivative is persisted; rotation, enhancement,
annotation, or source rewrite is forbidden. OCR, automatic text recognition, and image
classification are forbidden. No Voynich target, f84, or f84r is available.

The result uses the same canonical JSON rule and SHA-256. Its single canonical
access-audit schema binds
reader, session, page and timestamps; full-page-first; every source restriction;
mutual blinding; and whether OCR or automation was used.
It contains exactly ten Latin view events (A DEV01–05, then B DEV01–05) and five
later Clm events, all bound to source hashes. All nonaccess attestations are
true, OCR/automation false, and target/Voynich/f84/f84r access counts zero. Clm
events attest that the public checkpoint commit and hash were already verified.
Each Clm event records `checkpoint_committed_utc`, and its `opened_utc` must be
strictly later.
Public artifacts reject absolute/private paths and image bytes; bare filenames
occur only in the registered profile, while reader results use IDs and hashes.

## Decision rule and claim ceiling

Registration status is
`DOUBLE_READING_PROFILE_REGISTERED__NO_SOURCE_IMAGE_OPENED`. Completion status
is `SOURCE_DOUBLE_READING_COMPLETE__TARGET_UNOPENED`; a protocol violation or
material failure yields `MANUAL_READING_STOP`. This can produce a reproducible
source transcription only, never a Voynich sign, word, language, plaintext,
plant identification, operation, or meaning.
