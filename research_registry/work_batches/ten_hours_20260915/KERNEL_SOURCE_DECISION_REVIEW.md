# GDT963 two-marker kernel: source-only decision review

**Date:** 2026-09-15. **Scope:** source and method derivation only. No target frame, target string, result, solver output, or new GDT allocation was used.

The frozen GDT963 source contains four complete ordered atom streams. Let `A` be the fixed target image of `AND` and `D` the fixed target image of `DE_PARTICLE`. From `src/SOURCE.json`, the marker counts and the exact marker signatures are:

The table below is generated and checked programmatically from `experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json`; no marker signature is manually transcribed.

| record | total atoms | AND | DE_PARTICLE | residual atoms | marker signature (`A`/`D`) |
|---|---:|---:|---:|---:|---|
| I.1 | 265 | 36 | 17 | 212 | `DAADADAAAAAAAADDDDADADAAADAAAADADAAADADADAADAAAADAAAA` |
| I.2 | 120 | 12 | 11 | 97 | `DADDAADADAADADDDAAAADDA` |
| I.3 | 102 | 9 | 3 | 90 | `AADAAAAAADDA` |
| IV.20 | 126 | 7 | 10 | 109 | `DDADDDDAADAADADAD` |

The residual count is exact for each source stream after deleting the two fixed marker labels. It is the minimum number of residual codeword occurrences compatible with preserving every source atom position. The fast relaxed kernel gives each residual occurrence a free nonempty string and omits all equality/distinctness relations among residual occurrences; the registered global-code model restores source-atom identity and is therefore strictly stronger.

For fixed nonempty strings `A,D` and a complete target text `T`, the finite necessary kernel is:

1. Enumerate every pairwise non-overlapping placement of `A` and `D` in `T`. Retain only placements whose labels, read left-to-right, equal the record's marker signature. Require `A` and `D` to be prefix-incomparable.
2. Delete the occupied marker intervals. Partition the remaining intervals, in their original positions, into exactly the record's residual count of nonempty residual strings. For a target of length `L`, every residual string is a contiguous target substring of length at most `L`; therefore no arbitrary residual length is admitted.
3. In the fast relaxed kernel, leave all residual occurrences free relative to one another: each is only required to be nonempty and prefix-incomparable with `A` and `D`. Do not impose either equality or distinctness among residual occurrences, including repetitions of one source atom. This is weaker than the registered model and supports a polynomial dynamic program for each fixed `A,D` pair. The strict registered model must be checked separately: repeated occurrences of the same source atom share one image, while images of distinct atom labels are prefix-incomparable (the repeated image is not treated as a second distinct codeword).
4. Check the full source atom order, including marker/residual interleaving, across each complete record. A candidate survives only if all required record/page cases survive with the same `A,D`; page capacity and distinct-leaf requirements remain separate contract checks.

The length inequality for each case is immediate:

`|T| >= count_AND·|A| + count_DE·|D| + residual_count`.

Thus a candidate marker pair can be rejected before residual assignment when this lower bound fails. Candidate enumeration is finite because each codeword must occur as a substring of a finite target text. A global shortlist using non-overlapping frequency at least 36 for `A` and 17 for `D` is a safe superset for the highest-demand source record, but per-case thresholds must be used when pages are assigned one record at a time; applying the maxima to every page would be an extra restriction.

This kernel has a real falsifying outcome: an exhaustive `UNSAT` over all eligible complete target cases under the frozen source order, marker strings, prefix condition, and unknown policy would falsify the fixed two-marker code hypothesis conditionally. A `SAT` or surviving relaxed segmentation would establish only compatibility of a deliberately weakened decoder and would add no meaning evidence. It cannot establish `AND`, `DE_PARTICLE`, any plant name, or any translation.

The current local `UNKNOWN` results do not by themselves justify this follow-up. The 15-minute kernel is worth allocating only after the registered joint solver checkpoint if GDT963 remains unresolved and the implementation can enumerate the finite target-substring placements exhaustively under the already frozen frame contract. If the joint run is `UNSAT`, the kernel adds no research decision. If it is `SAT`/ambiguous, the kernel is validation or decoder work without semantic value. If an exact relaxed kernel resolves remaining `UNKNOWN` cases to `UNSAT`, that is a useful model falsifier; otherwise no new experiment should be opened.

## Source and claim ceiling

The derivation uses only `experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json` and `METHOD.md`. The source projection retains printed lexical order and treats all non-marker atoms as opaque. The construction preserves the source's marker order and minimum residual occurrence count; it does not compile complete Greek semantics or infer target meanings. Confirmed words remain zero.
