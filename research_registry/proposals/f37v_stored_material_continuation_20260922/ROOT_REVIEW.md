# IDEA522 independent inventory and source review

2026-09-22, bounded review after the author's capacity stop. Author originals
remain unchanged. This review adds only `validate_capacity.py`, `VALIDATION.json`
and this note. No new meanings, productions, bindings, semantic replay, scope
expansion or cap change was made.

**The exact lexical-capacity stop is upheld.** Its machine-readable 16/13/19
unknown counts are correct after including the complete stipulated inherited
family. CONTENT_STOP contains a local prose counting error, and the claimed
17:20 freeze timestamp is not supported by the observed creation chronology.
Neither correction removes the capacity stop. This is not a semantic
contradiction or a successful reading of the continuation.

## Independent dictionary construction

The validator constructs its dictionary directly from the claim-bearing
primaries, rather than trusting the author's retained-hit list:

| Primary block | Exact forms | Audit |
|---|---:|---|
| Original powder lexicon | 65 | equal to RAW512 frozen parent and INHERITED_FREEZE |
| Original reader alternatives | 15 | all complete entries equal, including unresolved/entity/composition fields |
| RAW512 new exact entries | 20 | complete entries equal |
| Closed f4r extra entries | 13 | includes dchor; all extras checked for overlap |
| Distinct combined inventory | **113** | no duplicate keys or conflicting entries |

The separately retained dchor entry equals both the full f4r entry and RAW512's
additional-known-family constraint. It is already one of the 13 f4r forms and
is not counted a second time. All V2 global effects in INHERITED_FREEZE equal
the original V2 and RAW512 copies. The author did not serialize all 12 other
f4r extras into INHERITED_FREEZE, but RAW522's explicit overlap obligation is
checked independently against all of them: **none occurs exactly in either
selected reader**. The 15 alternative forms likewise have no exact target hit.
No alias resolution, fuzzy spelling match or imported meaning from another
family is used.

## Complete source and arithmetic

The selected ID is exactly `f37v|f37v.8-f37v.13` in both ZL3b and IT2a. The
validator verifies the full owned cache hash, selects only these two fixed
records, and compares every field with SOURCE. No other paragraph's vocabulary,
frequencies, eligibility or content consequences are evaluated. All six loci,
48 source IDs, word order, offsets, source flags, raw uncertain forms and whole
paragraph start/end flags match. Both canonical record hashes agree with
SOURCE_RECEIPT. GROUPS preserves every field and global ordinal. The pre-body
metadata also agrees with the retrieved source.

| Reader | Groups | Types | Original65 hits | RAW512 hits | Known positions | Unknown exact types |
|---|---:|---:|---:|---:|---:|---:|
| ZL3b | 25 | 22 | 5 | 1 | 9 | **16** |
| IT2a | 23 | 20 | 6 | 1 | 10 | **13** |

ZL's five original types are `chor`, `cthol`, `daiin`, `sheaiin`, `sho`.
IT additionally has `shey`. Both have the retained RAW512 `dor=UNTIL`.
Thus ZL has **six known types in total**, not “six old values and one dor”.
The correct arithmetic is 22−(5+1)=16; IT is 20−(6+1)=13. The union of unknown
forms is 19, exactly the machine inventory's union. Each reader already exceeds
the maximum12 independently, so the union rule is not needed to establish stop.

The retained source has three anchor-eligible ZL lines and five IT lines out
of six. These are source flags, not a reason to omit uncertain groups or grant
the two readings independent evidential status. The ZL `{ch'}ey`, separate
`o koiin`, `sh[y:o]ly`, `do tody` and their differing IT groups remain exact.
In particular, `daiiin` is not normalized to inherited `daiin` or alternate
`daii`; `do`/`dotody` are not the f4r `doiin`.

## Timing and receipt limits

INHERITED_FREEZE says `created_utc=2026-09-22T17:20:00Z`. This review does not
endorse that timestamp. The parent reports the drafting task arrived around
17:26. The following local filesystem birth/mtime observations were read during
this audit and converted from the displayed +0200 offset to UTC:

| File | Observed local birth time UTC | Observed mtime UTC |
|---|---|---|
| INHERITED_FREEZE.json | 17:26:47.687054008 | 17:26:47.687958201 |
| DECISION.md | 17:26:47.688054022 | 17:26:47.689054037 |
| SOURCE.json | 17:27:27.257617317 | 17:27:27.258000993 |
| SOURCE_RECEIPT.json | 17:29:45.124822657 | 17:29:45.124987329 |

These observations support the limited local file-order statement that the
freeze files existed before the saved source packet. They do not independently
prove when the author first read the target body, public registration, or a
17:20 freeze. SOURCE_RECEIPT's ordering booleans are author assertions; it has
no independent acquisition timestamp. Preserve the original field and publish
this correction beside it. No intent is inferred from the erroneous timestamp.

DECISION also calls `f0def5...88483` a “page hash”. It is actually the SHA256
of the complete PAGE_ALLOWLIST.tsv file, as INHERITED_FREEZE correctly names it;
it is not a hash of a manuscript image or of one page's textual body. The
validator hashes that file without parsing its mixed TSV records.

## Interpretation and reproduction

The result is conditional on the selected exact-whole-form budget. It does not
prove that these forms can never receive a compositional reading under another
explicit design, or that stored-material continuation is false. The inherited
material ledger stays conditional on the unresolved RAW512 prerequisites:
adequate hydration, Boolean DRY_STATE and organ transitions remain unresolved.
The known POWDER, PASTE, WATER, Q, OVERNIGHT and UNTIL terminals do not construct
a complete withdrawal, fresh input or type assertion. No rival is selected.

The prose claim that new-input/assertion constructions cannot yet be completed
means only that this complete exact-word account exceeds its authorized cap;
it must not be recast as evidence that no input or assertion exists in the text.
Publish the whole retained source and stop with the corrected counts and timing
qualification. No extra paragraph, quota expansion or semantic simulation follows.

Reproduce the deterministic, nonsemantic check from repository root:

```text
python research_registry/proposals/f37v_stored_material_continuation_20260922/validate_capacity.py --execute
```

It produces `CAPACITY_STOP_COUNTS_VALIDATED_WITH_DOCUMENTATION_ERRORS`, with
all original-file and primary hashes, full per-reader known/unknown sets,
inventory provenance, and the unchanged12-value cap. An initial validator
adapter used line-local ordinals; inspection established GROUPS uses paragraph-
global ordinals. The validator was corrected to offset+local ordinal before
the successful audit. No author source, interpretation or threshold changed.
The tool's successful audit is a source/inventory check, not a semantic PASS.

The bounded `ideas show IDEA522` attempt encountered the temporarily stale
imported ledger snapshot. No refresh or registry mutation was attempted; the
exact frozen RAW522 primary and its linked family files supplied the contract.
