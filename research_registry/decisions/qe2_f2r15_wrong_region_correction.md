# f2r.15: old visual correction used the wrong detail region

2026-09-08. Direct user-requested native inspection; no semantic experiment.

The 2026-08-11 correction is not a valid location correction for f2r.15.
Its registered and hash-verified detail is Yale1006078 region
`1750,900,900,900`, enlarged to1800pixels. Root viewed that exact detail again:
it shows the isolated upper-right f2r.14 caption `ytoail` at a leaf-tip boundary.
It does not include the faint lower-right entry identified as f2r.15.
The report also lists the correct whole original, but that does not repair the
wrong detail or its description of an upper leaf-tip inscription as f2r.15.

For the user's question, root viewed the whole original and regions
`1650,1850,1000,650` at native size, then `1800,2120,650,280` enlarged2x.
The latter excludes the prose beneath the leaf. Root observes a faint short
written sequence in the broader green blade, with the visible signs inside the
leaf and no continuation onto bare parchment. `ios an on` remains the existing
manual ZL/RF transcription, not a fresh independently validated glyph reading.
This restores the plausibility of a leaf-contained annotation; its meaning,
authorial purpose, exact segmentation and ink/paint chronology remain unknown.
Magnification adds no physical image information. No OCR, generative image,
contrast reconstruction, painting removal or layer analysis was used.

Observer qualification: B's first frozen response located the ordinary prose
below the leaf. After explicit target-rectangle guidance, B could not confidently
distinguish the faint target sequence from pigment/leaf detail. Preserve both
responses. This is therefore root's native placement observation, not agreement
between two independently localized readings. The wrong old detail identity is
separately reproducible from the public IIIF source coordinates.

Withdraw root's recent application of the Aug11 boundary-overlap claim in
qb0 follow-up qc3/qc4 and the user-facing answer. qb0's original paint chronology
claim remains unsupported: rejecting the wrong location correction does not
establish that the ink predates the green paint. Original reports, ledger events
and reviews are retained; the current route and new review carry this correction.

Sources/observations:
- `experiments/semantic_assumptions/results/f2r15_native_visual_ownership_correction.json`
- `docs/visual_overview/F2R_USER_QUESTION_ADMISSION.md`
- `qe1_f2r15_native_ROOT.json`
- `qe0_f2r15_native_B_public.json` and `qe0_f2r15_native_B_v2.json`

Official source recipe: prepend
`https://collections.library.yale.edu/iiif/2/1006078/` to a listed region and
append `/full/0/default.jpg` for native region size. The old registered crop uses
`/1800,/0/default.jpg`; root's narrow detail uses `/1300,/0/default.jpg`.
Source hashes are in the packets. A valid image hash establishes file identity,
not correct localization or a true visual interpretation.

Reproduce source/coordinate checks with
`python tools/validate_f2r_question_sources.py --fetch`.
This validates official JPEG hashes and disjoint detail regions, not the native
interpretation, the manual transcription or ink/paint chronology.
