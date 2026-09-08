# GDT876 — two later owner-map placements contradicted

Both native viewers localize f67r2.72, .73 and .74 to the three horizontal lines below the right circular composition on Yale1006194. The V71 R3 claims that .72 is written on the left outer circular band and .73 on the right outer circular band are contradicted. The written location of .74 is narrowed, while its semantic referent remains unknown.

This is a correction of a later working-map regression, not discovery of previously unknown manuscript geometry or a translation. The earlier V71 R1 code already assigns all three to the lower horizontal block. Only these three records were evaluated; no complete f67r2 remapping or restoration of all R1 claims follows.

## Native evidence

| Record | Native location agreed by A and B | Earlier R3 placement | Consequence |
|---|---|---|---|
| f67r2.72 | Upper pale brown horizontal line below right circle | Left outer circular text band, DIRECT_VISIBLE | Quarantine that definite circular-band position |
| f67r2.73 | Middle red horizontal line below right circle | Right outer circular text band, DIRECT_VISIBLE | Quarantine that definite circular-band position |
| f67r2.74 | Lower pale brown horizontal line below right circle | Unresolved paired-wheel legend | Written location known; referent/scope still unresolved |

Localization used multiple ordered shape groups. For .72, the initial short group followed by long and repeated loop/minim groups and an intervening tall form matches the packet's opening sequence. For .73, the conspicuous repeated central tall-form groups and surrounding groups identify the red line. For .74, the ordered initial long and short groups, later tall form and separate minim group identify the lower line. Both records preserve uncertainty about fine transcription alternatives. A pale final glyph, red ink or horizontal baseline is not a decoded word or function.

Root had seen the complete original in GDT875 and older orientation, the three transcription strings and the old placement claims. The protocol therefore declares retrospective source correction. Preregistration d8bcb285 was published before this audit's source crop. Root sealed its three observations before viewer B received the neutral packet. B read neither the motivating placement predictions nor root's observations. B also had earlier whole-image exposure. These are separate native observations of one manuscript, not independent manuscript witnesses or a new three-edition confirmation.

## Exact historical regression

`V71_R1_build_owner_map.py`, lines186–188, branches on 72≤n≤74 and returns `F67_RIGHT_LOWER_PROSE_LINE_01/02/03`, explicitly describing the three-line block below the right wheel. Its helper at lines217–226 distinguishes this selected owner/default from the competing circular-band rival. The later `build_v71_r3_owner_ledger.py`, lines295–308, instead assigns n=72 and n=73 to left/right `RING_TEXT_BAND`, with `DIRECT_VISIBLE` and statements that concentric writing encloses the corresponding circle. The generated `V71_R3_TECHNICAL_REPORT.md`, lines262–264, publishes those placements. These are hard-coded ordinal branches; reproducing their output does not independently validate the image location.

The older R1 placement was therefore available already. The contribution here is independent native rechecking and an explicit correction of the later contradictory claims. This does not establish that all R1 positions are right, that all R3 positions are wrong, or that a diagram below/above relationship gives semantic ownership. In particular, .72 could still refer to another diagram despite its written position. That possibility is not the R3 claim that the writing physically follows the left circle.

## Operational correction and reproducibility

`artifacts/CORRECTIONS.json` lists only the two contradicted definite positions and .74's narrowed written location. Every semantic referent remains UNRESOLVED. Historical code, reports, transcriptions and renderer outputs remain byte-preserved. Downstream use must not cite those two R3 placements as direct visual evidence. This is a source-location correction; it is not an automatic rewrite of grammar, meaning defaults, GDT791 metadata kinds or GDT874's fixed metadata-based census.

`src/SPEC.json` binds the original image SHA2560518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c and official source URL. Root viewed one new lossless crop of the already viewed original; B viewed the original and one independently chosen crop. A_VIEWS.json and B_VIEWS.json retain exact coordinates and image hashes. No new original, page admission, OCR, enhancement, generated pixels or automatic character classification was used.

Run src/run.py to reproduce the three-record packet from the GDT874 guarded projection. Run src/validate.py to check locked protocol, image/source-record integrity and the root observation seal. Run src/compare_observations.py to render the predeclared agreement rule into the compact correction table; it was written after viewing and performs no image analysis. Validation PASS concerns provenance and observation records, not truth of native vision. The source caches must be present at their declared ignored paths; official image URL and hash allow independent retrieval.

No GDT388 relation packet is scored and no word meaning, linguistic clause or picture referent is established. The three-record audit stops here. Any larger source-map audit needs its own concrete decision and budget; the stopped semantic/underlayer/rotation routes are not reopened.
