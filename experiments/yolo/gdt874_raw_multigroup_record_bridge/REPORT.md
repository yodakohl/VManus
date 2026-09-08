# GDT874 — complete raw multigroup local-record bridges

The fixed thirty-page census yields two reading-specific cross-leaf matches and zero same-index three-reading bridges. It supplies two inspectable text-identity candidates, not a semantic bridge or established phrase. Preregistration and executable sources were published in bd35761017212386223332e31a16ce639c1f2f4e before the target run.

## Scope and predecessor

GDT811 already matched complete cleaned local-label sequences to running text on four physical pages. This census instead retains complete eligible raw groups across the fixed GDT791 thirty-page / thirty-five-selector roster. It is not the first multigroup matching method. The old f81v.28 caption in SIDEQUEST_SCRIBE_WORKSHOP_MICROTHEORY.md motivated a specific check; earlier single-word recurrence does not establish recurrence of its complete inscription.

The inherited atlas contains 1,007 records: 392 LOCAL_LABEL_OR_MARKER, 612 RUNNING_PROSE and three empty transcription records. These metadata kinds are not independently established authorial phrases or sentences. All nonempty primary records have raw counterparts; IT2a lacks f17r.13. No raw locus lies outside the selected metadata frame. There is no scope expansion or newly admitted image.

Each candidate is a complete local record of at least two raw groups, each exactly its sole clean ASCII fragment. Internal uncertain spaces and drawing separators disqualify it. A hit must retain the whole candidate as a contiguous eligible raw window inside one running record. No group deletion, shortening, reverse search or cross-line concatenation is allowed. The three editions are alternate readings of one manuscript.

## Results

| Reading | Eligible local records | Distinct patterns | Matched local records | Running windows |
|---|---:|---:|---:|---:|
| ZL3b | 40 | 39 | 1 | 1 |
| IT2a | 78 | 77 | 1 | 1 |
| RF1b | 41 | 40 | 0 | 0 |

The complete two-row hit list is:

| Reading | Complete local record | Running endpoint | Raw window |
|---|---|---|---|
| ZL3b | f67r2.56: `tol daiin` | f89r2.8 | groups 1–2 of 13 |
| IT2a | f67r2.64: `s air` | f89r2.28 | groups 13–14 of 16 |

Both running endpoints have raw kind P. Both are on another physical leaf; neither is a same-selector or same-page-key match. There are zero bridges meeting the fixed same-locus, start-index, window-length and whole-running-count conditions in all three readings. Different eligibility counts, including some long IT2a records, reflect source annotation and segmentation; they are not independent samples or proof that every metadata local record is a short caption. RESULT.json retains the length-specific opportunity denominators.

For the focal f81v.28 inscription, ZL3b `otain olkal` and IT2a `otoin olkol` are eligible and have no complete bridge. RF1b is `@221;tain olkal` and is ineligible: it must not be reported as a tested zero or normalized silently to the historical cleaned `tain olkal`.

## Interpretation and next decision

The focal two-word reuse route has no exact support in its eligible views on this roster. This does not refute reuse of individual groups, a semantic reading, or recurrence outside the roster. The two other local-record identities are exploratory availability leads. Before treating either as phrase reuse, source-level reading and native visual ownership would need inspection; no such image inspection occurred in this experiment. No frequency significance, null result, translation, pictured-object binding or GDT388 relation score is claimed. No automatic broader scan or relaxed matching follows.

## Reproduction and validation

Run `python experiments/yolo/gdt874_raw_multigroup_record_bridge/src/run.py`, then `python experiments/yolo/gdt874_raw_multigroup_record_bridge/src/validate.py`. The runner recreates ignored selector-guarded caches from the fixed source receipts. The separately implemented validator enumerates every eligible local-record/running-window pairing and checks candidates, bridges, counts, completeness, opportunities and coordinate joins. It passes 1,176 local-record checks, the two bridges and zero same-index bridges. A synthetic fixture checks duplicate labels, a raw anomaly, a drawing separator, edition differences and the distinction between same-index and literally identical bridges. Validation establishes census fidelity, not semantics.
