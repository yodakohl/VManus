# ZLA001 target-validator report-order amendment

The single ZLA001 target completed once under freeze
`26e362ea431e696e215e3fde53fd3f49bc93d0fd0c7cccfa596e19ccb1bba470`.
Its result and report are immutable and must not be rerun or rewritten.

The frozen production-free validator independently reconstructed the source
join, orbit, complete evaluation, target gates, and dihedral diagnostics, then
stopped only at the last report-text equality check. The target runner rendered
`positive_folio_counts` from the in-memory fixed reading order
`ZL3b, IT2a, RF1b`. The canonical JSON was written with `sort_keys=True`, so
the validator reloaded that dictionary in alphabetical order
`IT2a, RF1b, ZL3b` and rendered a byte-different but value-identical string.

The only authorized correction is to make the validator render that one
dictionary explicitly in the frozen reading order. No input join, sequence,
statistic, null, threshold, gate, target artifact, target report, scientific
core, or runner may change. A replacement validation freeze must bind:

- this amendment and corrected validator;
- the original freeze and original validator hash recorded inside it;
- the unchanged target JSON and report hashes; and
- every unchanged original frozen input.

The target remains a clear nonconfirmation before and after this correction:
the weakest-reading effect is negative and the joint p is approximately .646.
The amendment cannot create a confirmation or any ownership, serial-code,
number, degree, word, meaning, plaintext, or translation claim.
