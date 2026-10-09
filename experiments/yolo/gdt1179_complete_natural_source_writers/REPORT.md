# GDT1179 — complete natural-source writers fail the basic screen

All three fixed writing systems preserve all1054 complete normalized recipe projections, but none passes the inherited ten-metric screen across the four declared books and three alternate readers. No full writer is retained. This is source-control construction, not manuscript decipherment.

A uses literal orthographic shortcuts and paid inner boundaries. B uses503 whole-word entries trained only on b4/w1 with literal fallback. C uses nearest prior exact-word references up to503 source tokens with the same fallback. The short-word pairing rule and all codes were fixed before the measurements. See PREREGISTRATION.md and METHOD.md for the complete contract.

| System | Book | Mean glyphs | SD | Top10 share | Type share | Conditional entropy | Passed gates /10 |
|---|---|---:|---:|---:|---:|---:|---:|
| A | b4 | 8.1769 | 3.0791 | 0.0856 | 0.3554 | 2.8146 | 3 |
| A | w1 | 8.1892 | 2.8903 | 0.0725 | 0.3974 | 2.8534 | 1 |
| A | bs1 | 7.9313 | 3.1597 | 0.1245 | 0.3422 | 2.8154 | 3 |
| A | gr1 | 8.2650 | 2.8732 | 0.1000 | 0.3761 | 2.8484 | 2 |
| B | b4 | 4.8461 | 3.4407 | 0.0856 | 0.3554 | 3.5638 | 5 |
| B | w1 | 5.0101 | 3.2480 | 0.0725 | 0.3974 | 3.5871 | 3 |
| B | bs1 | 6.1809 | 3.9335 | 0.1245 | 0.3422 | 3.2643 | 3 |
| B | gr1 | 6.7375 | 3.8083 | 0.1000 | 0.3761 | 3.2189 | 2 |
| C | b4 | 6.4742 | 3.9046 | 0.0323 | 0.6551 | 3.4032 | 2 |
| C | w1 | 6.5469 | 3.7213 | 0.0270 | 0.6909 | 3.4339 | 2 |
| C | bs1 | 6.2271 | 3.8835 | 0.0480 | 0.6161 | 3.4292 | 2 |
| C | gr1 | 6.6029 | 3.7350 | 0.0234 | 0.6947 | 3.4079 | 2 |

A is too long. B obtains a superficially suitable mean in the training books but excessive length spread and entropy; literal fallback lengthens the other books. C creates far too many distinct written forms and insufficient frequent-word concentration. Partial gate counts are diagnostics, not model selection or significance estimates. All numerical tolerances are unchanged from1174; none has been widened.

The validator decodes all12 persisted full encoded books, compares the recovered words against every source recipe, and re-encodes from decoded words without original grouping metadata. All3162 recipe roundtrips pass. It also checks the alphabet, dictionary training, counts, frozen dependency hashes and an unused-rank guard. A first validator comparison exposed only floating-point set-iteration differences around1e-16 in JS divergence; numeric comparison now allows1e-12 without changing any result, threshold or writer.

Learning/operation costs are material: B requires503 word correspondences; C requires recovering and searching/counting up to503 prior words. Exact reversibility does not establish historical practicality. Complete source means the frozen expanded-edition projection, not independent diplomatic collation. All four collections are exposed construction data. Original1175–1178 failures remain; no native word, language or meaning is assigned. No sealed or reserved data were used.

Decision: stop these exact systems. The outstanding question is whether a smaller forward contextual alphabet can alter word-form diversity without pairing words or maintaining a large dictionary. That requires its own fixed proposal; it is not a repair or success of this comparison. Local construction checkpoint under the4October user exception; no publication is claimed.
