# GDT836 — W priority integrated; fresh source lacks literal support

Status: **SOURCE_CAPACITY_STOP**.

The decoder now enforces GDT835's mandatory-wholeword precedence during search,
including global effects from inactive W entries and atomic rollback. The
fresh historical control cannot run: two literal rules occur in its held part
but never in discovery. No key, ciphertext or historical fit was generated.
Software verification is reported separately from that stopped source test.

The Questio split was fixed at citation runs1–44/45–88 in GDT835 before new
support counts. It has44runs/2318words in discovery and44runs/2064words held.
All other gates pass: active S/W discovery minima85/27;746novel composed held
form occurrences;471unambiguous novel composed lemma occurrences; no exact
20-word reference overlap, excluded run, reused citation or missing W candidate.
Its original first STOP remains byte-identical; no split, deck or threshold
change follows. PARAGRAPHS.json preserves88 metadata records only.

The engine's STRICT path checks every cached decoded word against every current
candidate W entry after tentative package/word updates and before score, edge
or best-state commit. RELAXED retains the old key legality. Both accept the same
first W-compatible initialization from a capped candidate stream, then reset a
separate search RNG. No invalid initialization can become bestkey; neither
forced nor greedy moves bypass the constraint. METHOD.md gives exact behavior.

Nine independent invented-fixture tests pass. They exercise active/inactive W
changes, collisions created by literal/suffix changes, W ownership and cross-role
swaps, atomic multi-package updates, exact rollback, greedy/annealed/forced
rejections, common compatible initialization and separate search RNG, capped
initialization without any score/best update, strict final-state validity and
the Que source filter. The canonical GDT835 oracle and frozen Python language
model independently check emitted states. No real historical data enter those
tests.

Independent source reconstruction verifies all88paragraphs,133sentences and
4382words and reproduces the original capacity snapshot exactly. Full validation
and exact replay bind all tested code and exercise the historical --fit guard:
status2, zero generated keys/ciphertexts/fits. A build compiles successfully.
These are software/source checks, not a passing recovery experiment. No fresh
recovery percentage or improvement over RELAXED exists.
A future control requires independently declared usable source data. GDT834's
failure and GDT835's retrospective diagnosis remain unchanged; no mandatory
abbreviation rule or translation is inferred for Voynich.

The first capacity snapshot SHA-256 is
`f92960e81c7d00df316ad55c2f8c27c9579e88f8d79e556924a5e4d4da61f213`.
Source preparation, metadata, encoder specification, implementation, tests and
validator are published for reproduction. Exact staged privacy/scope and GDT836
bindings pass; the separate full repository audit retains unrelated GDT600
binding and index debt.
