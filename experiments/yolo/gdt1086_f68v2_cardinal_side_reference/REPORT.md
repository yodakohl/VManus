# GDT1086 — corrected f68v2 sectors; registered echo test invalid

**Decision: `INVALID_OWNER_MAPPING__TEXT_ECHO_NOT_RUN`.** The preregistered
Walters-style local-reference model assumed that the four catalogued star-label
loci were the four multi-star fields. A direct reread of the admitted
[Yale f68v2 panel](https://collections.library.yale.edu/iiif/2/1006197/3300,500,2400,2500/full/0/default.jpg)
and [Stolfi's explicit diagram description](https://vib.tamagothi.de/index.php?id=f68v2&show=page)
shows that assumption is wrong. The eight sectors alternate **four clusters
of 9, 8, 9, 9 unlabelled stars** with **four single stars each flanked by two
short inscriptions**. Eight other written rays leave the eight blue central
lobes along sector boundaries. The four S1 *records* are the four isolated
single-star sectors, not four inscriptions naming the multi-star fields; each
S1 record itself contains two inscriptions around its star.

The text-blind 12-row inventory was queried by guarded `page=f68v2` and
confirms eight E1 ray-title slots (`.18,.7,.9,.10,.12,.13,.15,.16`) and four
S1 single-star slots (`.17,.8,.11,.14`). It does not give the four assumed
cardinal owners. The registered stop rule therefore fired **before any
transcription TSV query or echo score**. The planned 8/8 local and 24
non-neighbor comparisons were not run; none can be reported as either a pass
or a failure. [RESULT.json](artifacts/RESULT.json) retains all twelve
metadata records and [VALIDATION.json](artifacts/VALIDATION.json) verifies the
bounded inventory and stop, but cannot verify the image reading.

This corrects the wording in GDT1085 that placed a star-label locus in each
multi-star field. GDT1085's registered negative Trier result still stands:
there is no twelve-sector same-role wind/month register or independent
compass phase. The corrected positive topology is **four many-star sectors,
four one-star/two-inscription sectors, eight boundary rays**. It could support
a different model later, but cannot be converted post hoc into four cardinal
wind names. Walters W.73 f.2r remains an attested source-side 4+8 hierarchy,
not an identified template here. GDT353's eight-title formal nonalignment
remains intact. Confirmed translated words: **zero**.

Exposure note: after preregistration, opening the public Stolfi/VIB page for
its spatial description also displayed its f68v2 P/C transcription and R/S
readings. P/C content exceeded this GDT's twelve-locus grant; none was used
for this decision, extracted into artifacts or treated as newly admitted.
This is recorded as historical exposure, not independent evidence or a
retroactive access expansion. f84/f84r and all reserved leaves stayed closed.
The source page is not an institutional image; Yale's native image supplies
the visual cross-check. No significance or word meaning is claimed.

This topology was **not newly discovered** here. An [8 August ledger row](../../../experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv)
already described f68v2's four sparse star centres with eight surrounding
boundaries in comparison with f68r3. Its cited detailed report is missing from
the current tree, so the row is an exposure and predecessor warning, not
claim-bearing validation. GDT1086's contribution is the explicit correction
of the current GDT1085 owner error and the consequent registered stop.
