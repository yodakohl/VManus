# GDT156 — synthetic Voynich-style abbreviation control

Status: **ENCODER FROZEN IN GDT155 BEFORE UNBLIND CALIBRATION**.

## Question

What Voynich-like formal signals can be manufactured by applying a compact
record compiler to readable medieval German, and which signals still depend on
the source text after the compiler is fixed?

This is a constructive positive control.  It does not model Voynich letters,
sounds, words, or meanings.  The literal strings `q`, `d`, `s`, `o`, `ot`,
`al`, `ar`, `ain`, `aiin`, `dy`, and `m` are anonymous output symbols.

## Encoder `VMS_HPR2_ABBR_V1`

Input is the committed expanded diplomatic line stream from GDT155.  Unicode
alphabetic/digit runs are source groups.  Long s and dotless i/j are folded as
in the blind control.  The PAGE_HOST projection is:

1. the first alphabetic character;
2. the next at most two consonantal characters anywhere to its right;
3. the final alphabetic character, even if that duplicates an earlier choice.

The vowel set is frozen as `a e i o u y ä ö ü`; other alphabetic characters
are consonantal for this mechanical projection.  A numeric-only group uses
its first and final character.

The emitted group is `[OUTER][FRAME][PAGE_HOST][RIGHT][CLOSURE]`:

- OUTER `q` on the first group of a record, `s` on the first group of every
  continuation line, and `d` on other punctuation-field starts.  Conflict
  precedence is `q > s > d`.
- FRAME `o` on the first occurrence of a PAGE_HOST at or before the record
  midpoint, `ot` on its first occurrence after the midpoint, otherwise empty.
- RIGHT is `al`, `ar`, `ain`, or `aiin` for expanded group lengths 1–3, 4–5,
  6–7, or 8+.
- CLOSURE includes `dy` when punctuation `. / ; : ? !` follows before the
  next group and includes `m` on the final record group.  Both may occur.

Line breaks do not themselves close fields.  No parameter is fitted to
content, expansion recovery, or retrieval performance.

## Evaluation

Four held-book dictionaries predict the known expanded source group from:

- global frequency;
- PAGE_HOST;
- compiler signature;
- PAGE_HOST plus right family;
- the complete synthetic token/factorization.

Record retrieval repeats the GDT155 same-book, non-co-page, full-pool target
selection using known regularized content/addressee overlap.  Expanded-source
character trigrams are an explicitly unblinded reference, not an encoded
predictor.

Exact wrapper×closure rectangles and wrapper×right-family compatibility are
counted.  Each property is marked `IMPOSED_BY_ENCODER`,
`EMERGENT_AFTER_ENCODING`, or
`MIXED_IMPOSED_OPERATOR_PLUS_EMERGENT_HOST_REUSE`.

Economy is measured two ways: literal output codepoints, and abstract glyph
atoms where each multiletter compiler marker counts as one atom.  If compiler
overhead outweighs PAGE_HOST shortening, V1 is reported as a structural code
rather than an efficient abbreviation; no post-hoc fusion or escape rule is
introduced to rescue it.

## Claim ceiling

The experiment can show that a specified record compiler is sufficient to
create Voynich-like surface regularities from ordinary abbreviated natural
language.  It cannot show that Voynich uses this encoder, identify a language,
assign a morpheme or sound, recover plaintext, meaning, or translation.  No
Voynich corpus or image is an input and no f84 material is accessed.
