# GDT192 — compiler-stripped one/two-letter expansion

## Question

GDT189 rejects an injective letter alphabet and GDT190–191 reject fixed
frequent-host word dictionaries. Does the stripped PAGE_HOST character stream
instead behave like a historical abbreviation channel in which one source sign
expands to one or two plaintext letters?

## Frozen model

- Use the same 2,430 non-f84 physical lines and frozen PAGE_HOST parser as
  GDT189; exclude `f102v2.33` and reject every `f84*` row before parsing.
- Preserve source separators as target SPACE and reset an order-2 language
  model on each physical line.
- Each of the 20 active source signs chooses one of 702 one- or two-letter
  strings over a 26-letter target alphabet.
- Score all six frozen historical-language packs. Initialize each language's
  three runs from its three retained GDT189 injective mappings, so the expanded
  model is nested around the exact prior model.
- Perform deterministic exhaustive coordinate descent: for every active sign,
  test all 702 emissions; retain only a mapping that is locally optimal over
  every one-coordinate alternative.
- Pay `20 log2(702)` mapping bits and `log2(6)` language bits.
- Pay a Dirichlet-1/2 binary channel for the one/two-letter boundary sequence
  and a separate Dirichlet-1/2 reverse-ambiguity channel whenever multiple
  source signs emit the same target string. These make the source event stream
  reconstructible from target output plus the frozen line/separator scaffold.
- Compare against the same line-reset anonymous order-2 KT identity channel as
  GDT189.

Pass requires a negative paid gap and an identical complete expansion map in
all three starts. A winning language-pack score is not a language
identification. The test does not cover longer expansions, deletions,
page-specific expansion keys, phrase codes, or a separately transmitted
dictionary.
