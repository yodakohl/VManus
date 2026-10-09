# GDT1177 — narrower binding passes design books, fails transfer books

The single frozen P4 list passes both necessary word-frequency conditions on
b4 and w1, but fails on the predeclared transfer collections bs1 and gr1.
**The joint result is a failure.** This is not a selected working writer.

|Collection|Role|Top10 fraction|Type fraction|
|---|---|---:|---:|
|b4|known design|16.913%|32.025%|
|w1|known design|14.363%|32.850%|
|bs1|fixed transfer|19.663%|30.638%|
|gr1|fixed transfer|21.888%|31.500%|

All values use8000 groups and all three inherited reader-specific bands.
The transfer failures concern concentration of frequent words. No transfer
source was substituted, no spelling variant or pronoun was added after scoring.
1054 complete projected recipes retain all normalized source words in order;
three recipes were excluded by the inherited whole-recipe uncertainty rule.
The two transfer collections were not counted in this work block before the
list was frozen, but all sources were historically exposed.

This was an explicitly informed refinement of1176, not an independent initial
hypothesis. Its development success does not transfer across books. Exact short
word lists remain sensitive to source vocabulary and spelling; that is a
mechanism limitation to investigate, not permission to patch this list.
No glyph-code construction was started for this failed rule. Eight other
statistical conditions, alphabet costs and native structures stay untested.

[Contract](PREREGISTRATION.md), [specification](src/SPEC.json),
[result](artifacts/RESULT.json), [complete source](artifacts/SOURCE_TEXTS.json),
[validator](src/validate.py). No native word meanings or new target data.
Local construction result; not published.
