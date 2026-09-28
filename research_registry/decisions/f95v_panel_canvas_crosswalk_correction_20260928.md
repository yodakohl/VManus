# f95v panel-to-canvas crosswalk correction (2026-09-28)

Status: source-attribution correction after prior image exposure; no newly
registered independent test, botanical identity or translated word.

The Yale image [1006242](https://collections.library.yale.edu/catalog/2002046?child_oid=1006242)
shows the physical folio number `95` at upper right, seven text lines in one
block, unpainted oval terminals, hairy leaves and forked brown roots. The Yale
image [1006243](https://collections.library.yale.edu/catalog/2002046?child_oid=1006243)
shows thirteen text lines in several blocks, blue round heads, lobed leaves
and large red bulbous roots. The independent folio/quire description
[Voynich.nu, Quire 17](https://www.voynich.nu/q17/index.html) explicitly
assigns the numbered, seven-line drawing to **f95v2 / Yale 1006242** and the
thirteen-line blue-flower drawing to **f95v1 / Yale 1006243**; its Yale links
resolve to those same child IDs. The visible folio number and line counts are
the discriminators, not the ambiguous abbreviated Yale labels `95v (part)`
and `95v`.

The earlier LM001 visual-selection row explicitly assigned f95v2 to 1006243.
It was read here solely through the selector-first guard:

`./vmanus-exp query-tsv experiments/semantic_assumptions/results/lm001_herbal_leaf_margin_visual_selection.tsv --selector page --allow f95v1 --allow f95v2 --columns page,physical_folio,canvas_id,canvas_label --forbid-prefix f84`

That projection returned one row, `f95v2 / f95 / 1006243 / 95v`. It is a
historical misassignment. LM001's original bytes and decision remain intact;
image-derived f95v2 claims that depend on this row need re-attribution to the
actual pictured panel. Text-only measurements grouped by physical f95 are not
invalidated by this correction.

GDT866's two viewers examined and agreed on a real local upper trace in
1006243. Their observation of a two-upright link with zero complete intervening
groups stands **for image 1006243, now identified as f95v1**. The report's
f95v2 label, source provenance and any extension of the result specifically to
f95v2 are withdrawn. The upper-left trace on f95v2/1006242 has not been
examined under that frozen GDT866 question. No retrospective target swap or
new positive result follows. Its negative nonadjacent-link decision for the
actual photographed trace is unchanged.

The two drawings are visibly distinct, but this crosswalk does not determine
whether they portray different botanical subjects or one subject in different
states. IDEA668 remains unreviewed and untested. Historic suggested plant
names in catalogs are unverified guesses, not translations.
