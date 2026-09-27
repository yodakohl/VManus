# Independent replay of IDEA000583 whole packet

## Scope and freeze

I replayed the frozen whole draft against the already-owned GDT1042 `native_groups.tsv`, the unchanged first-contract JSON, and the author’s draft/report. I did not import the producer, inspect new target/source data, inspect images, or use a semantic executor. This was an informed review: I had already read the first contract and my own bounded whole-audit plan and erratum. It is not blinded evidence or independent confirmation of any word meaning.

The replay script is `DEFAULT_CONTEXT_WHOLE_REPLAY_B.py`; its machine-readable result is `DEFAULT_CONTEXT_WHOLE_REPLAY_B.json`. The three frozen author-input hashes recorded by the replay are: draft JSON `ed612bf7c690b0b93e19ba9bda2cd0961fcdab7bb21a3fbd07291502c53fc34c`, draft Markdown `5ba992a710bdbf0cc27567cb929d70844ecb171c2515ea9daee8c9e4086d8d8c`, and report `9dfdec2a8fedc86028fa545cfb5f08e7f37e1b2d42c87fd7f3c853a070e1416e`.

## Literal replay

The replay passed its exact checks: all 473 source rows and IDs, all 12 stored native fields, all 41 family occurrences and values, the 66 unchanged first-contract bindings, the seven added bindings, every row-to-lexicon binding, reader status totals, all listed derivation token sequences and nonoverlapping spans, and the stated binding/payload totals. It recomputed 82 locally derived/conditional groups. The exact per-reader status totals are:

| Reader | Complete local derivations | Conditional local derivations | Assigned, unparsed | Unknown, unparsed |
|---|---:|---:|---:|---:|
| ZL3b | 72 | 10 | 24 | 50 |
| IT2a | 0 | 0 | 96 | 61 |
| RF1b | 0 | 0 | 88 | 72 |

The ZL count is a partial account: 72 complete groups cover A1 `.1`, N `.2–.3`, and E `.7–.11`; the ten conditional groups are `.13` and `.15`. The remaining 74 ZL groups are not parsed. The 156 ZL statuses therefore do not constitute a whole-page reading. All IT and RF groups remain unparsed in this packet.

The seven new bindings are exactly `sain`, `opchdy`, `qotor`, `sheedy`, `shodaiin`, `olfar`, and `ary`. The packet has 73 total bound entries, 68 marked independent, five derived forms, and 78 payload items. These are bookkeeping and authored-grammar results, not evidence that the proposed values are correct.

## Manual semantic and source-duty review

The N.2 derivation is type-complete under the authored contract, but its content is an identity tautology. `sain` compares `DEREF(x)` with itself under the existing `.1 ar` binding; no intervening input binder changes `x`. The result is compared with `opchdy = TRUE`. This does not test context variation or establish an empirical distinction. Instantiating generic `Scalar` as `BooleanScalar` is an explicit packet assumption; if the frozen contract instead treats `Scalar` as closed, this is a typing gap rather than an implicit cast.

N.3 is more than the earlier comparison plan: its typed positive proposition asserts nonempty, unequal OLD and YOUNG thermal-disposition profile sets, without choosing a direction. But those values are sets of internal dispositions `{COLD, TEMPERATE, HOT}`. They are not the response to external cold versus heat, and no identity links OLD/YOUNG to contexts `c0`/`c1` or to the conduct plans. It therefore addresses O4 only under a narrowed reading in which unequal thermal profiles plus generic context-specific adjustment suffice. It does not establish an age-indexed cold/heat response relation.

The packet expressly leaves O2 and O3 incomplete. The same ingredient/input is given harmful and good outcomes in a different demonstrated location, but no time field or relation to `YEAR` is asserted (O2). Nor are distinct recipients or health conditions bound to the contexts (O3). O1 has an explicit `CHANGES_WITH(BODILY_NATURES, YEAR)` assertion in A1. Generic conduct-adjustment plans do not fill the missing O2/O3 bindings.

The prior no-update and fixed-register limitations remain explicit. Bare and prefixed `dar/odar`, and `tchedy/otchedy`, are used as reported; the author does not claim that all family members receive a coherent account. IT/RF remain unparsed. Fixed-register argument/type debts constrain direct transfer of the ZL template but do not prove that every conceivable grammar is impossible. The earliest `.4 G001 dair` case is left as an unknown-left-argument gap. The `.15–.16` and `.24` issues are likewise direct-template constraints, not a global impossibility result.

## Result and limits

I found no literal bookkeeping or span-replay discrepancy. The packet supports a reproducible, partial ZL derivation, with unresolved source duties and alternate-reader coverage. Its complete N.2 syntax is vacuous, while N.3 is a real authored profile assertion whose connection to the stated source duty remains underspecified. No result here confirms meanings, proves a complete coherent parse, or establishes global UNSAT.
