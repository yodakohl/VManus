# GDT1068 — no complete f67r2 title recurs on f69r

Decision: `NO_COMPLETE_LITERAL_TITLE_TRANSFER`. The positive 12+16 f69r
wind-system resemblance is unchanged. This test asked only whether one of
the twelve *unchanged, complete* f67r2 titles reappears as a consecutive
written-group sequence in an f69r outer or radial inscription.

| Reading | Outer: 16 items, 192 cells | Radial: 22 items, 264 cells | Full-title matches |
|---|---:|---:|---:|
| ZL3b | 0 constituent overlaps | 4 constituent overlaps | 0 |
| IT2a | 1 constituent overlap | 4 constituent overlaps | 0 |
| RF1b | 0 constituent overlaps | 5 constituent overlaps | 0 |

All four ZL3b/IT2a radial constituent incidences are the same structure:
`okar` occurs in f67r2 titles 3 and 10 and in f69r.30 and .33. RF1b has
those four plus `chy` from title 11 at f69r.21. IT2a has `chy` from title
11 at the outer f69r.16. These are **constituent** coincidences, not title
matches. `okar` occurs 118 times across 55 of 179 admitted ZL3b selectors;
its recurrence is not a wind-name anchor. The complete per-cell outcome is
in [RESULT.json](artifacts/RESULT.json).

The fixed input is GDT958's full `raw_title` for all 12 f67r2 sectors per
reading. Target scope is all 16 f69r.5–20 outer items and all 22 f69r.21–42
radial items, selected through the f69r-only guarded TSV query. No title
piece, uncertain spelling, alternative form, or section was chosen after the
result. [PREREGISTRATION.md](PREREGISTRATION.md) discloses that ZL3b had
already been inspected before the IT2a/RF1b check. These three are alternate
readings of one manuscript, not independent confirmations. The validator
recomputed all 1368 title-item cells and all matches: PASS.

The literal cross-page title bridge is unavailable on current readings.
This does **not** show that f67r2 and f69r concern different subjects:
historical rotae can place names and descriptions in different registers,
and f69r has no independently owned one-to-one set of twelve wind labels.
Oxford St John's College MS17 f40v gives a strong image-family comparison,
but its twelve owned wind names do not identify which, if any, of f69r's
22 radial or 16 outer text items are wind names. GDT1067's 180-degree
source/destination ambiguity also remains. The next lexical test needs an
independently fixed owner and orientation, or a different explicit relation;
another spelling relaxation of these already exposed titles would not be
prospective evidence. Confirmed translated words: **0**.

No new Voynich page or image was admitted, no sealed or reserve leaf was
opened, and no statistical significance is claimed. Sources: [Oxford MS17
facsimile metadata](https://iiif.bodleian.ox.ac.uk/iiif/manifest/66a78997-ab65-4059-a9d3-d08a0bba067c.json),
[Voynich f69r layout](https://www.voynich.nu/q10/index.html#f69r), and
[GDT958](../gdt958_wind_fixed_form_variation/REPORT.md).
