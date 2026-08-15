# GDT035 target-coverage correction before outcome access

The public GDT035 v1 freeze targeted f101v correctly from visible geometry but
specified `gdt016_group_state_inventory.tsv` as its query table.  A page-key
coverage check after freeze found zero f101v rows of any host in that table.
Therefore the initial zero-row query is `UNSCORABLE_TARGET_OUTSIDE_INVENTORY`,
not a CKHY absence and not a semantic failure.

No f101v source group, token, family, or CKHY surface was inspected during the
coverage check.  The page, visual observation, semantic gloss, binary decision,
and four allowed surface forms remain unchanged.  Before source-group access,
v2 freezes the only correction: use the complete alternate-reading
`source_sta_group_alignment.tsv` and count a physical source group only when
ZL3b, IT2a, and RF1b all render it as the same one of `ckhy`, `chckhy`,
`checkhy`, or `shckhy`.  No fuzzy or family-neighbor match is allowed.

This correction precedes the actual target query and cannot turn an observed
miss into a hit.  f84r remains sealed.
