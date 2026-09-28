# f85r2: exploratory East-versus-three overlap sensitivity

29 September 2026. This is a derivative audit of the already published complete
GDT1042 four-block inventory, prompted by GDT1043's source-side possibility
that the East vessel figure differs in topic from three age/season figures.
All four blocks and all three alternate transcriptions were included. No new
Voynich access, word segmentation, source identity, or formal test is claimed.

For ZL3b, the six exact whole-form intersections are N–E 2, N–S 2, N–W 3,
E–S 2, E–W 2, S–W 6. IT2a/RF1b have the same counts. With each pair scored
by set Jaccard and a proposed exceptional block scored as mean similarity of
the other three pairs minus mean similarity of its three edges, East has the
largest contrast: 0.0405 ZL, 0.0393 IT, 0.0371 RF. This is descriptive and
post-exposure; the readings are one manuscript, not three replications.

The result is fragile. Removing only the shared `aiin` leaves East highest
(0.0391/0.0381/0.0362). Removing both `aiin` and `or` makes North highest:
North 0.0271/0.0265/0.0254 versus East 0.0159/0.0152/0.0139. `or` occurs
312/298/298 times in 112/106/105 admitted selectors and ranks 7/8/8 by
reader, so its contribution cannot be treated as a season-specific lexical
marker. The remaining strong S–W overlap is five forms after both common
forms are removed; it is one pair, not an identified three-season construction.

Decision: do **not** use the four-block overlap as independent support for
“three seasons plus doctor,” and assign no season, doctor, humour or vessel
meaning to a Voynich whole. The source analogy remains possible on its
visual evidence; this text statistic does not sharpen it. No significance
claim, independent meaning confirmation, or reserve use. f84/f84r remain
closed. Reopening needs a source-owned relation with a word-level target rule,
not reweighting these same four known blocks.

Source: [GDT1042 report](../../experiments/yolo/gdt1042_f85r2_source_program_surface_census/REPORT.md),
its `artifacts/native_groups.tsv`, [GDT1043 report](../../experiments/yolo/gdt1043_f85r2_native_attribute_binding/REPORT.md),
and `./vmanus-work words profile or` on the admitted 179-selector corpus.
