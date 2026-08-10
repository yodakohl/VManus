# SNPL002 — source-native local-query synthetic preflight

Status: **FROZEN TARGET-BLIND PREFLIGHT**.

## Purpose

Calibrate one mechanism-novel test for the four SNPL001 public repeated-plant
relations before any Herbal target prose is read. This does not reuse S99's
unordered parsed-root page sets or S100's exact parsed multi-root word test.

## Frozen representation and score

- Queries are the complete ZL3b, IT2a, and RF1b STA member-code sequences of
  f89v2.6, f102r2.21, f102r2.22, and f102v1.17.
- Candidate text consists of complete source-STA consensus groups. A match may
  occur only inside one group; motifs may not cross a visible group boundary.
- Query features are all distinct contiguous member-code windows of width four
  and five.
- For a candidate-page stratum and alternate reading, weight motif `m` by
  `log((N+1)/(df(m)+1))` over the non-target reference pages.
- A group's raw score is its share of total query weight. The page score is the
  maximum group score. Convert it to a midrank against the reference pages:
  `(less + 0.5*equal + 0.5)/(N+1)`.
- Build a 4x4 label-by-page matrix for each reading. The primary matrix is the
  elementwise mean of the three alternate-reading matrices. Readings are not
  independent samples.
- Enumerate all 24 assignments. The frozen true diagonal must be the unique
  top assignment in the primary and every reading-specific matrix.
- On the primary matrix, each of the three unambiguous labels must be the
  unique best label for its true page and have midrank at least .75. The
  ambiguous f89v2.6 relation must have midrank at least .50.

No threshold may be changed after opening this preflight or the target.

## Target-blind worlds

Use only non-target Herbal confirmed-prose pages from A/hand 1 and B/hand 5.
Each world deterministically selects three distinct A1 pages and one B5 page;
all selected pages are removed from that world's reference pool.

- 64 `NULL` worlds: no inserted group.
- 8 `GLOBAL_EDGE_MUTATION` worlds: insert the correct label in every true page
  and reading after changing the earliest member with a valid same-family
  alternative. This retains realistic partial four/five-window identity.
- 8 `ONE_LABEL` adversaries: insert only one correct label.
- 8 `WRONG_PAIRING` adversaries: insert every label into the next page.
- 8 `ONE_READING` adversaries: insert all correct labels in only one reading.
- 8 `FAMILY_ONLY` adversaries: replace every possible member by a different
  observed member of the same family before insertion.

## Frozen preflight gates

- at most 2/64 null worlds pass;
- at least 7/8 global edge-mutation worlds pass;
- 0/8 pass in each adversarial family;
- every stored result and selection is deterministic and finite;
- target pages f48v, f18v, f23r, and f19r are excluded before group values are
  retained; no target score is computed.

Only a full pass authorizes a separately hash-frozen target run. A target pass
could establish manuscript-internal same-plant reference signal only, not a
plant name, English word, sound, language, cipher, plaintext, or translation.
