# GDT089 — source-human plant descriptor localization inside HPR2

Status: **YOLO hypothesis generation; postselected archived panel**

Restrict the frozen annotation inventory to complete loci that are human-tagged
PLANT labels, `UNHEDGED`, and kind `L`.  The 85 resulting loci on six physical
folios are scored once each.  Extract only the transparent neutral descriptor
patterns published in `gdt089_descriptor_manifest.tsv`; no image inference or
English lexical mapping is added.

Using the fixed GDT068 settings (`K=5`, shrinkage `4`), leave one physical
folio out and compare:

- raw source-token character trigrams;
- PAGE_HOST character trigrams after HPR2 layer stripping; and
- compiler-only signatures.

The baseline is target-folio-excluded descriptor prevalence.  Complete
descriptor vectors are permuted within physical folio 5,000 times, preserving
folio ecology and descriptor co-occurrence.  Report local and max-search
probabilities across all eligible descriptor/representation pairs.

Separately inventory exact PAGE_HOST/descriptor recurrences on two or more
folios.  Those are weak visual-association hypotheses, not glosses.  All tried
descriptor patterns, including capacity exclusions and negative results, are
retained.  f84r is asserted absent before parsing or scoring.
