# IDEA518 / GDT1038: preregistration critique only

Status: pre-execution design review, 2026-09-22 15:24 UTC. This note does not
inspect a split census, reader fit, experiment code or result. It neither
changes the registered card nor selects a further experiment.

Decision reviewed: `research_registry/decisions/amulet_binary_packing_decision_20260922.md`.
The decision explicitly fixes the previously open coordinate question:
original physical-line units are retained; the extension is one ordered
33-terminal stream over three whole physical lines; one written group can
span a canonical clause seam but cannot span physical lines. Its 9+4 schemas
remain authored tag patterns. No general typed grammar is thereby obtained.
There is no substantive design blocker remaining on those points.

Three implementation conditions should be made explicit before locking code:

1. `ALWAYS_DECOMPOSE_WHEN_AVAILABLE` suppresses an atomic interpretation when
   **any lexical** ordered binary split exists, even if every such split later
   fails the fixed terminal stream. Defining availability by successful fit
   would make this rival an undeclared rescue rule.
2. Preserve independent `source_status` and `parse_status`. A failure for a raw
   uncertain reading is conditional on those raw groups; it neither repairs
   the source nor proves a semantic contradiction. The copied projection and
   each complete literal alternative retain their own identity and flags.
3. Seal the complete lexical alternative table and input hashes before fitting,
   after locking the enumeration rule/program. Distinct lexical derivations
   with identical tags remain distinct. An exhaustive DAG with an exact count
   can preserve all paths without printing an exponential list; a resource
   limit cannot silently become an exhaustive failure or unique fit.

The exact-old-space comparator requires exact projected raw groups, not only
their tags or counts. The selected decision already states this. Atomic and
binary alternatives are both retained by the main rule, all 88 denotations
stay fixed, and unknown groups remain unknown. A full match recovers an
authored whole tag stream. It does not resolve the original assembly/stone
claim rival, independently establish references, or favor these meanings over
an opaque relabelling of the same tags. The decision already retains this
scientific ceiling and all old GDT1023/IDEA492 outcomes.
