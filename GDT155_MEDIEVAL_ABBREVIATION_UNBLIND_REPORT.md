# GDT155 — unblinded medieval abbreviation calibration

## Outcome

**REAL_MEDIEVAL_ABBREVIATION_POSITIVE_CONTROL_CALIBRATED**

The frozen form-only analysis was unblinded only after its public source and
analysis checkpoints.  Across the four held Nuremberg books, raw diplomatic
site identity recovers 103702/110683 expanded spans
(93.7%); training-only raw-character backoff recovers
104956/119031 (88.2%).  The HPR2-like
`PAGE_HOST` representation recovers 82981/110045
(75.4%), while compiler signature alone recovers
15618/118239 (13.2%).  The two Ste1
technical records are a strict Nuremberg-trained descriptive transfer:
21/23 sites are recovered by exact
raw-site identity; their small size does not make them a separate statistical
replication.

The blind transformation inventory contained thousands of complete formal
rectangles before meanings were visible.  Unblinding shows which selected
edge contrasts survive literally in expanded spelling and which collapse to
the same expansion or become ordinary lexical/orthographic contrasts.  This
is the central positive-control warning: rectangles and reusable edge
operations are expected in real abbreviated natural language, but do not by
themselves localize semantics or establish a linguistic analysis.

For GDT148-style document retrieval, the target for every query is selected
mechanically as the non-co-page, same-book record with greatest regularized
content (or addressee) token-set overlap.  Raw character retrieval has content
MRR 0.5922, PAGE_HOST character retrieval
MRR 0.5704, and compiler-only retrieval
MRR 0.1942.  Raw therefore exceeds the
stripped host by 0.0218
MRR, whereas the host exceeds compiler-only retrieval by
0.3762.
These are effect-size calibrations, not evidence that the blind host is a stem
or semantic unit.

### Interpretation

Real medieval abbreviated language produces strong local string families,
left/right asymmetry, complete transformation rectangles, record-position
effects, and recurrent stripped hosts.  The known expansion truth nevertheless
shows that raw visible spelling usually retains more exact lexical information
than aggressive PAGE_HOST stripping.  Compiler features can encode document
formula and position, but are not an independent content vocabulary.

No Voynich source, image, or f84 material was accessed.  The next checkpoint
applies the already frozen `VMS_HPR2_ABBR_V1` encoder to this readable control
and labels every resulting property as imposed or emergent.
