# GDT155 — medieval abbreviation positive-control calibration

Status: **SOURCE AND BLIND ANALYSIS FAMILY FROZEN BEFORE FULL-CORPUS
UNBLINDING**.

## Question

Which Voynich-style formal signals are produced by genuine early-fifteenth-
century abbreviated natural language, and where does a form-only HPR2-like
decomposition place information that is known after unblinding?

This is a positive-control calibration, not evidence that Voynichese is
German, an abbreviation system, or readable by the control parser.  It stops
single-`PAGE_HOST` visual-gloss mining.

## Sources and access chronology

The controls are:

1. CoReMA `Ste1`, the Sterzing miscellany, first quarter of the fifteenth
   century.  Its hyperdiplomatic TEI contains two short culinary/technical
   records and embedded editorial expansion characters.
2. The Nuremberg Letterbooks v1, books 2–5 (1408–1423), whose public label
   archive contains PAGE-XML records with diplomatic transcription and
   embedded abbreviation expansions plus a regularized document view.

The source audit exposed a few examples printed by the public interfaces and
used them only to verify the encoding.  No full-corpus expansion inventory,
expanded-word frequency, regularized vocabulary, addressee, or content field
is used to choose the blind models.  The complete expansion truth is committed
by hash before analysis and is exported only by a later unblind program.

## Blinded input

For each source line the freeze exports:

- exact record, book/manuscript, page, line, and writer identifiers;
- `diplomatic_bare`, obtained by omitting every editorial `ex` node;
- `diplomatic_marked`, the same visible string with one anonymous `¤` marker
  per TEI `expan`/`abbr` span;
- counts and physical order only.

The blind tables contain no omitted letters, expanded words, normalized
plaintext, modern meaning, `addressee`/`content` division, or recipe gloss.
Unicode is NFC-normalized.  A fixed analysis fold maps long s to `s`, dotless
`ı` to `i`, dotless `ȷ` to `j`, lowercases, and retains letters, digits, `¤`,
and source whitespace.  This is a display normalization, not linguistic
lemmatization.

The Nuremberg XML file is the record.  PAGE/TextLine XML order supplies line
order.  CoReMA `seg` elements supply its two records and `lb` supplies lines.
No images, OCR, or automatic recognition are used.

## Blind transformation discovery

Nuremberg is evaluated in four outer book-held folds.  All operations are
rediscovered from the other three books only.  For every training vocabulary
form, exact prefix and suffix deletion pairs of one to three codepoints are
enumerated.  An operation is licensed only with at least eight distinct base
hosts and five training records.  The twelve left and twelve right operations
with the most distinct hosts are retained, with pair count and lexical order
as fixed tie-breaks.

A token is parsed by at most two left and two right deletions.  Every deletion
must leave either a training surface form or a residual observed under at
least two distinct envelopes.  Candidate parses are ranked by training-only
residual recurrence, then fewer operations, longer residual, and lexical
order.  The residual is called `PAGE_HOST` solely to make the control directly
comparable with HPR2.  The stripped material, anonymous abbreviation marker,
line/record position, and punctuation boundary are compiler/record features.

The following representations are fixed:

- `RAW_GROUP_IDENTITY`;
- `RAW_CHAR3`;
- `PAGE_HOST_IDENTITY`;
- `PAGE_HOST_CHAR3`;
- `COMPILER_SIGNATURE` (ordered stripped left/right operations and marker);
- `MARKER_AND_POSITION`;
- `HOST_PLUS_COMPILER`.

## Blind analyses

Before unblinding the program records:

1. transformation spectra, left/right asymmetry, productive host counts, and
   compact rectangle/compatibility counts;
2. line and record architecture: group count, marker density, boundary
   position, reuse, and line-reset diagnostics;
3. an all-record GDT148-style retrieval ranking under every representation;
4. held-book dictionaries mapping each representation to an opaque target
   class placeholder.  No target class value is inspected before unblinding.

The Ste1 slice is too small for an independent fold.  It is a high-relevance
descriptive transfer: Nuremberg-trained operations are applied unchanged, and
its two record and 33 abbreviation-site capacities are reported separately.

## Unblind evaluation

The later unblind exports omitted characters and expanded/regularized text,
then evaluates the already frozen objects:

- exact and top-k expanded-word recovery at abbreviation sites;
- whether `PAGE_HOST`, raw surface, or compiler features best retain expanded
  word identity;
- whether blind record retrieval ranks the record with the most similar
  expanded content, expanded addressee, or regularized content highly;
- concentration of wrapper/right/marker features in known `addressee` versus
  `content` divisions where alignment is secure;
- effect sizes by held book, writer, record length, and abbreviation density.

The truth targets and scoring rules are fixed for all records; attractive
letters or words are not selected individually.  Retrieval reports mean
reciprocal rank, top-1, top-decile, normalized rank, and matched within-book
permutations.  Abbreviation recovery reports accuracy, macro accuracy over
expansion classes, coverage, and bootstrap intervals by record.

## Synthetic Voynich-style abbreviation control

After unblinding, `VMS_HPR2_ABBR_V1` is applied deterministically to the known
expanded control text:

- `PAGE_HOST`: first alphabetic character, up to two following consonantal
  characters, and the final alphabetic character (duplicates preserved);
- `q`: record-first group; `d`: punctuation-delimited field first group;
  `s`: continuation-line first group; otherwise no outer wrapper;
- `o`: first host mention in a record; `ot`: first host mention after the
  record midpoint; otherwise no local frame;
- right family `al/ar/ain/aiin`: expanded length bins 1–3/4–5/6–7/8+;
- `dy`: punctuation-delimited field closure; `m`: record closure.

These literal strings are anonymous encoder symbols, not sounds or meanings.
The encoder is evaluated for compression, recurrence, transformation
rectangles, line reset, record retrieval, and recoverability by the same
frozen analysis.  Every reported property is tagged `IMPOSED_BY_ENCODER` or
`EMERGENT_AFTER_ENCODING`; imposed behavior is not evidence for Voynich.

## Controls and claim ceiling

Raw-character, whole-group frequency, character-KT/cross-entropy, nearest-
neighbor edit distance, and compiler-only representations are mandatory.
Nuremberg alternate transcription layers are aligned views, not replications.
Ste1 and Nuremberg are separate manuscripts but not language-independent
controls.

No result may assign a Voynich word, morpheme, sound, part of speech, language,
plaintext, or translation.  At most GDT155 can calibrate that a specified
formal effect is common, weak, or unexpectedly absent in real abbreviated
medieval German, and show what the analogous control layer corresponds to
after expansion.

All scripts must reject any identifier beginning `f84` before retention.  No
Voynich corpus is an input to the control analysis.
