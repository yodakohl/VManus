# Parisel `cho/che` source and implementation audit

## Purpose

Reconstruct the externally specified post-`ch/sh` `o/e` folio system on the
three manual IVTFF readings, while separating the published definition from
the implementation that generated the published template table. This is a
source/provenance audit and a transcription-robustness test. It is not a
lexical or phonetic interpretation.

The external source is Christophe Parisel, *A Quantitative Confirmation of
the Currier Language Distinction*, arXiv:2604.25979v2 (5 May 2026), and its
linked repository `labyrinthinesecurity/currier-models`.

## External facts frozen before local reconstruction

- The paper defines a group as `cho`-type when it contains `cho` or `sho` but
  no `che` or `she`, and conversely for `che`-type.
- It defines the folio switch by the literal threshold
  `sigma=1 iff n_cho/(n_cho+n_che) > 0.5`, with at least five classifiable
  groups.
- It reports 197 eligible folios, a 31-template retained inventory, and no
  reversal of template direction.
- The linked code actually fits a two-state binomial EM and uses posterior
  assignment, not the stated threshold, for its template table.
- Repository commit `c9bb7e5d4d19d00b2e6f63af6df0a421308be14a` produced the
  31-template report. Its parser deleted `<->` through the generic
  `<[^>]*>` substitution before splitting on periods, thereby concatenating
  the two source groups around every drawing interruption.
- Commit `74c24ee939956d44abd81d4a9895dc03894d44d1` changed only this parser
  behavior: it first replaces `<->` with `.`, then removes other angle-bracket
  markup. The current linked report at main commit
  `627ee9a1f3df76cbc61a1415399b78ad2eb50602` contains 200 eligible folios
  and 34 retained templates. This repair still removes uncertain comma spaces
  and `<~>` unaligned drawing interruptions, so it is a repository correction,
  not a complete source-separator correction.
- Even the published 31-row table contains two literal direction reversals:
  `shXo` has rates `0.000/0.034`, and `otchXy` has rates `0.000/0.032` in
  reported state-1/state-0 order. Equality rows also exist. Therefore the
  paper's exact zero-reversal statement and `2^-31` calculation do not
  describe its own table.

These are audit targets, not assumptions about manuscript meaning.

## Frozen local inputs

- `transcription/sources/ZL3b-n.txt`, SHA-256
  `bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`
- `transcription/sources/IT2a-n.txt`, SHA-256
  `7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5`
- `transcription/sources/RF1b-e.txt`, SHA-256
  `e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782`
- `results/source_separator_transcription_validation.json`, SHA-256
  `8698a2643219fd8ab00b05bba8705a1f1e8219c9b468824fbe2dc92117043deb`

## Exact reconstructions

Parse each manual reading separately. Collapse panel suffixes such as `f68r2`
to physical page `f68r`, matching the external code. Remove comments,
locator/header angle markup, braces, `@number` entities, and `!%*`. Keep only
lowercase basic-EVA letters within each resulting group.

Run three parser modes:

1. `PUBLISHED_MERGE`: remove `<->` as generic angle markup before splitting.
2. `REPOSITORY_DRAWING_SPLIT`: replace `<->` by a period before other angle
   markup is removed, exactly matching the later repository repair.
3. `SOURCE_ALL_SEPARATORS`: preserve periods, uncertain comma spaces, `<->`
   drawing interruptions, and `<~>` unaligned drawing interruptions as group
   boundaries. This is the source-valid primary mode.

For each mode and reading, compute both:

1. `THRESHOLD`: the equation printed in the paper;
2. `EM`: the exact deterministic two-state binomial EM in the linked code,
   initialized at `(p_high,p_low,pi)=(.7,.2,.5)`, tolerance `1e-8`, maximum
   200 iterations, posterior state 1 iff responsibility is greater than .5.

For every group, tokenize `ch` and `sh` as single glyphs and replace every
immediately following `o` or `e` with `X`. Retain a template only when it has
at least ten substitution events in both assigned folio states. A reversal is
defined literally as `rate_state1 < rate_state0`; equality is recorded
separately.

## Hard gates

- each reading has exactly 200 eligible physical pages in every parser mode;
- the source-all-separators EM mixture has positive two-state delta-AIC in every
  reading and separated component rates (`p_high-p_low >= .45`);
- exact state and template outputs are emitted for all 18
  reading/parser/assignment combinations;
- all common eligible physical pages are compared synchronously across
  readings, never as independent samples;
- the exact paper-definition/implementation assignment disagreement is
  reported rather than silently choosing one;
- no manual separator class is deleted in the source-valid primary result;
- a nonimporting validator reconstructs all local numerics and artifact bytes;
- zero English glosses.

## Decision and claim ceiling

The folio-level two-regime `cho/che` distribution may be retained as a robust
formal manuscript mechanism only if the source-all-separators mixture
separation and cross-reading state-agreement gates pass. The published
31-template inventory, the repository's 34-template partial correction, the
literal threshold/implementation equivalence, and the exact no-reversal claim
must not be called source-complete if the frozen audit contradicts them.

No result identifies `ch`, `sh`, `o`, or `e` as sounds, vowels, consonants,
letters, words, plaintext, a natural language, a cipher operation, or any
English meaning. `cho`, `che`, `template`, `state`, and `switch` are formal
labels only.
