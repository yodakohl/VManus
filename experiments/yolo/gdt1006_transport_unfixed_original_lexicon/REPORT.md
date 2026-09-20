# GDT1006 — free all original word assignments

The complete 63-group source reading remains conditionally coherent after all
47 old word assignments are released. It is not uniquely recovered. Under the
bijective family the complete eleven-role/five-setting projection has 36
solutions, independently exhausted. The functional family has at least 66
solutions and an unexamined remainder. Neither family is selected by this result.
There are zero confirmed words and zero independent meaning capacity.

## Actual candidate consequences

| Fixed family | Complete maps evaluated | Maps with a coherent variant | Maps failing all 32 | Positive projected tuples | Remainder |
|---|---:|---:|---:|---:|---|
| FUNCTIONAL (aliases allowed) | 1,136 | 21 | 1,115 | 66 | CANDIDATE_CAP; cvc5 residual SAT; next syntax witness semantically unexamined |
| BIJECTIVE (47 distinct values) | 96 | 12 | 84 | 36 | Exhausted; Z3 and independent cvc5 residual UNSAT |

[All evaluated maps](artifacts/CANDIDATES.tsv),
[all 102 positive projected candidates](artifacts/PROJECTED_CANDIDATES.tsv),
[all 47 word-domain rows per family](artifacts/WORD_DOMAINS.tsv), and
[all 33 complete coherent readings in German](artifacts/READINGS.md) are retained.
The latter include complete literal group spans, complete dictionaries, all
coherent settings, hazard pairs, seven voyages and resolved references.
All failures under all 32 settings remain in the two FAMILY JSON files; no
matching clause was selected separately. There are 126 coherent full-map/variant
witnesses: some functional maps witness already-seen projected tuples.

## What meaning adds, and what the syntax already assumed

[Domain attribution](artifacts/SYNTAX_VS_WORLD.tsv) is based on the preregistered
coverage theorem, not agreement between restarts. In BIJECTIVE the assumed
syntax allows 18 eleven-role tuples times 32 settings = 576 combinations;
the full world conditions leave 36. This is a finite conditional exclusion,
not a probability or significance level. The eight singleton role assignments
already follow from the assumed clause inventory and the bijective contract:

| Form | Conditional role | Contribution of world consistency to this singleton |
|---|---|---|
| otaiin | THERE | None; already syntax-forced |
| otedy | RETURN | None; already syntax-forced |
| otor | COLOC | None; already syntax-forced |
| qoteedy | B (boat) | None; already syntax-forced |
| sar | UNSAFE | None; already syntax-forced |
| shedy | M (attendant) | None; already syntax-forced |
| sol | THEN | None; already syntax-forced |
| solkeedy | WITH_TRIP | None; already syntax-forced |

The other three projected words retain alternatives. qokedy and lchedy may each
be any of the three anonymous cargo identities. chedy may be a cargo identity
or FIRST_CARGO; it cannot be OTHER_CARGO under this complete bijective contract.
All six global cargo renamings survive. There are six name-valued role tuples
with four settings each, plus six FIRST_CARGO-valued tuples with two settings
each. In the latter, FIRST must mean the first introduced cargo, not the most
recent. The bare terminals are structural roles inside a hypothetical reading,
not independently translated English words.

The chedy=OTHER_CARGO exclusion has an inspectable cause. Across all 24 evaluated
complete maps having that value, the 768 variant checks give 384 NO_PAIR_FOR_OTHER,
192 COPIED_PAIR_ARGUMENTS_IDENTICAL and 192 SOURCE_CONTENT_MISMATCH outcomes.
With OTHER interpreted as first-mentioned cargo, the surviving binding cases
assert only one distinct hazard pair, whereas this test requires two. Other
physical contradictions may coexist; the status accounting uses the frozen
priority order and does not excuse them. The requirement of two hazard pairs
comes from the proposed source content, not independently from the manuscript.

FUNCTIONAL has 45 syntax role tuples witnessed, not exhausted. Its witnessed
values cannot justify excluding unseen alternatives: for example, its saved
qokedy values are only C/G although global cargo renaming immediately permits
other identities. All its domain exclusions remain UNKNOWN. The 36 other,
nonprojected word domains in both families are witnessed-only. No invariant
hazard-centrality claim is inferred for a word from saved representatives.

## Remaining observational equivalence

[SYMMETRY.json](artifacts/SYMMETRY.json) groups the projected tuples under all
six anonymous cargo renamings: six complete classes for BIJECTIVE, 18 witnessed
classes for FUNCTIONAL. It does not collapse different reference settings.
[Actual witness consequences](artifacts/CANDIDATE_CONSEQUENCES.json) and
[identical observed consequences](artifacts/OBSERVATION_GROUPS.json) retain the
126 witnesses in six exact physical-trace/hazard/location groups. The six groups
are cargo relabelings of the same observed transport pattern. This is a
statement about saved witnesses, not enumeration of all dictionaries and parses
inside each positive projection.

A cargo name and a correctly resolved first-mention reference can yield the
same voyages. GOAL versus CURRENT for THERE coincides at the observed uses.
FIRST/RECENT is inactive in maps without FIRST_CARGO. The data here also do not
distinguish instruction from report, nor identify wolf, goat or cabbage.

## Source and independence boundary

ZL3b f83r.18–24 is complete but its sol/chedy boundary is uncertain. Its search
is conditional on 63 literal groups. IT2a has a strict whole-paragraph contract
but 64 groups and contradicts the fixed 63-group source inventory; that count
fact was already present before this experiment. RF1b has 63 raw groups but no
whole-paragraph contract and remains UNKNOWN_PARAGRAPH_CONTRACT. They are
alternate readings of one manuscript, not independent witnesses. Leaf 83 and
the source/template construction were previously exposed. No new manuscript
content, image, reserve, f84/f84r or f116v was opened. No outside contact occurred.

All 17 patterns, their terminals and complete counts were retained; no old
word-to-terminal assignment entered either search. However, the patterns and
source story themselves were constructed while the earlier reading was known.
Releasing the dictionary does not remove that prior. Whole word aliases do not
explain productive morphology. No suitable control for the entire source search
or independent meaning identification is present, so no significance, historical
language, source identity, animal name or confirmed translation is claimed.

## Reproduction, validation and decision

Registration was public in commit f3eb0a699 before free dictionary search.
The pinned-source and source-variation preflight preceded it. The frozen primary
run took 39.662 seconds FUNCTIONAL and 4.426 seconds BIJECTIVE. The independent
validator checked all 1,232 maps, 39,424 meaning settings and 94 domain rows;
its boundary-flow cvc5 search confirmed the bijective exhaustion and functional
remainder, with no unknown solver result. Source-only preflight had checked
1,312 changed-clause/pair settings and all original old-map outcomes. The local
bit-replay scope correction was registered before target search and left the
legacy GDT993/994 bytes unchanged. Presentation later corrected a count assertion:
126 coherent map/settings witnesses correspond to 102 distinct positive
projected tuples; no scientific search or decision changed.

Use Python with z3-solver and cvc5 versions in requirements.txt; run src/prepare.py,
src/preflight.py, src/run.py, src/validate.py, src/attribute.py and src/render.py.
Existing registered input hashes and every candidate are retained. The inclusive
20:20–21:20 UTC preparation/publication budget was respected; completion timing
is in the closure receipt. No count-cap extension or automatic rerun is licensed.

Decision: retain the complete transport reading as a conditional candidate with
explicit ambiguity. The physical/reference model contributes chedy's OTHER_CARGO
exclusion and setting restrictions; the eight singleton roles are not newly
learned meanings. A useful follow-up must supply a different complete context
whose shared-word or reference consequences distinguish surviving readings.
Replaying the same trajectory, another restart, or opening reserves would not
do that. The functional remainder stays open without a budget extension.
