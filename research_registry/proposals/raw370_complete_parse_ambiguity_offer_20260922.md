# RAW370: a new complete grammar hypothesis for an all-parse content audit

**RAW / UNREVIEWED / NOT EXECUTED.** Construction feasibility offer, 2026-09-22; requested budget18:31–18:51 UTC. The old65 primary entries,15 alternate-form assumptions, V2 material contract and four rival settings remain fixed. This document supplies a **new grammar completion**, not a claim that the old18 schematic productions already defined every parse. It adds no word meaning, material effect, source, target or spelling repair. The companion JSON binds the exact inputs and compact contract.

The smallest useful question is: after removing the authored clause partition, does every complete derivation of the fixed words under this single declared grammar retain the same material-argument graph and the previously claimed mass/provenance consequences? A different complete tree must be retained even when its consequence is unfavorable. The test would not choose the grammar, translate a word or recover historical clause boundaries.

## Actual specification gaps and predecessors

The V1 field `schematic_productions.parsing_limit` expressly says the supplied clause trees select intended scope and competing parses were not exhaustively searched. Its18 rule families leave the following unspecified:

1. `Clause`, `OperationClause`, `Kind`, `ProductKind`, `UnaryOperation`, `Property`, `Adjunct`, `ExternalSupplyNP`, `ExistingMaterialNP` and the partition-NP categories have no exhaustive expansions. In particular SIEVE is tagged PartitionOperation, although its occurrence before UNTIL needs a one-patient operation construction. RINSE must not silently become a supply-free unary verb.
2. Root concatenation, whether bare nominal lists are complete statements, how often initialization is allowed, and the grammatical effect of physical line boundaries are not executable rules. The authored clause strings use INVENTORY/INGREDIENTS descriptions which are not extra written terminals.
3. `Property* [UnitRun] Property*` and `Adjunct* ... Adjunct* [NP] Adjunct*` admit representational duplicate trees unless absent-unit/absent-NP cases are specified. There is no declared nearest-head, longest-NP or greedy attachment rule.
4. The six frozen compound/grouping hypotheses need explicit interfaces: some bind inside one NP/action, while `otshchor` contains IN_SHADE followed by THEN and genuinely crosses a clause seam. Free arbitrary word splitting is not supplied by these six entries.
5. The material contract specifies latest compatible stock, active stock, and a relevant partition frame, but does not give a complete reference-machine update order for every possible new tree. The hand ledger alone cannot be used as a locus-indexed resolution oracle. Goal-to-final-output binding, and the general truth maintenance of DRY_STATE after wetting, retain the limits already noted in the content-entailment memo.

The V2 JSON explicitly preserves these18 schemas. It closes material classes/access and revises comminution/carrier effects; it does not replace the schematic grammar with a parser. Therefore **ALL_OLD_DERIVATIONS is presently undefined**. The proposed experiment must be labelled an audit of the new grammar below.

Bounded navigation consulted composition/recipes context, IDEA516, the DEV516 ledger pointer and linked primary review, IDEA514/517 navigation, duplicates and route-check. No exact earlier all-parse audit of this fixed82-position offer was returned; this is a bounded search result, not a project-wide absence claim. GDT581's assigned renderer hosts/aliases do not determine this new powder grammar. GDT972 tests a different fixed account header. GDT1040's actual whole-prefix-valency failure concerns a different six-production loan grammar and remains closed. The older P14 quantity interpretation, W89 recipe pause, f4r incomplete extension, GDT1037 spelling failure and the separate q-partition offer are not repaired or imported.

## Input and exposure

Use only `complete_positional_alignment` and the bound original source packet: the complete f21r.8–12 and f32v.7–11 spans. The primary question includes **all82 ZL raw groups**. The same fixed grammar must also be applied to all78 IT and78 RF groups as separate whole-reader accounts, retaining the existing RF boundary qualification and every source uncertainty. The six whole-reader units are fixed now; no new target or census is authorized. Exact unit identities and group order come from the existing packet, not the authored `primary_whole_readings.clauses`.

All238 raw groups must appear once in a coverage table, including units with no complete tree. Physical line/locus data are provenance only and cannot create a clause boundary, reset a referent or license a rule. Only the two already fixed paragraph boundaries reset stock. No cross-leaf stock identity is inferred. A partial prefix is not a complete derivation. The source was exposed before this new design.

All65+15 entries are bound byte-for-byte by input hash. The terminal inventory is their **existing full value**, not a free POS assignment. All available values must be accounted for, including unused reader alternatives. No word can gain another category merely because parsing fails.

## G-P82: exhaustive terminal classes

Below, capital names are fixed semantic values in V1, not new lexemes. A class lists all of its members; every unlisted member is forbidden.

| Class | Complete value set |
|---|---|
| Kind | ROOT_MATERIAL, PLANT_MATERIAL, PREPARED_BULK, COARSE_GRIST, COARSE_PART, COARSE_FRACTION, FINE_PART, RESIDUE, POWDER, FIBRES, GRANULES, PASTE, WATER, OIL |
| Property | FRESH, DRY_STATE, CLEAN, FINE, COARSE |
| UnaryOperation | DRY, CRUSH, SPREAD, GRIND, MIX, COVER, SIEVE |
| Manner | THINLY, EVENLY, COARSELY, THOROUGHLY |
| Location | IN_SUN, IN_SHADE |
| Duration | OVERNIGHT |
| Tool | WITH_SIEVE, WITH_CLOTH |
| SupplyKind | WATER, OIL |
| CoarsePartKind | COARSE_PART, COARSE_FRACTION, RESIDUE |
| FinePartKind | FINE_PART |
| PartKind | COARSE_PART, COARSE_FRACTION, FINE_PART, RESIDUE |
| ProductKind | FIBRES, GRANULES, PASTE |
| GradeSelector | FINE, COARSE |

The other terminals are ACQUIRE, RINSE, THEN, FOR_OUTPUT, UNTIL, SEPARATE_BY_GRADE, FROM, LIFT_OUT, DEFINITE, SORT, KEEP, STORE_SEPARATELY, RETRIEVE, KNEAD, TO_RESULT, ONE, PORTION, WITH_MEDIUM and MASS_UNIT_Q. POWDER_MASS_Q is the already composed NP described below. There are no generic unknown terminals, implicit noun insertions or epsilon argument values.

Adding SIEVE to the explicit unary **patient-valency** class is a new syntactic completion, not a change to SIEVE's two-fraction material effect. CRUSH's unresolved exact spelling retains its existing CRUSH hypothesis. RINSE, SEPARATE, SORT, KEEP, STORE, RETRIEVE, LIFT_OUT and KNEAD are not UnaryOperation alternatives. This prevents treating their required written material/partition constructions as optional after seeing a failure.

## Complete grammar, without source-clause boundaries

`*`, `+`, `?` below have their ordinary finite-sequence meanings. Every repeated item consumes at least one terminal. Each category is defined here; lexical classes are the terminal sets above. Capital rule IDs identify the18 inherited families, but the root/union/list helpers and explicit alternatives are **additional formalization costs**, not18 independently established grammar rules.

```text
Paragraph          ::= Initial Clause*
Clause             ::= OperationClause | G1 | G2 | T1
OperationClause    ::= A1 | A2 | P1 | P2 | R1 | P3 | K1 | K2 | R2 | J1 | M1
Initial / I1       ::= Kind | ACQUIRE MaterialNP
MaterialNP / N1    ::= Kind Property*
                    | Kind Property* UnitRun Property*
UnitRun / N2       ::= MASS_UNIT_Q | MASS_UNIT_Q MASS_UNIT_Q
PortionNP / N3     ::= ProductKind ONE PORTION
Adjunct            ::= Manner | Location | Duration | Tool
ToolAdjunct        ::= Tool
ExistingMaterialNP ::= MaterialNP
ExternalSupplyNP   ::= SupplyKind
PartNP             ::= PartKind Property* | PartKind Property* UnitRun Property*
CoarsePartNP       ::= CoarsePartKind Property*
                    | CoarsePartKind Property* UnitRun Property*
FinePartNP         ::= FinePartKind Property*
                    | FinePartKind Property* UnitRun Property*
Condition          ::= Property | MaterialNP
A1                 ::= Adjunct* UnaryOperation Adjunct*
                    | Adjunct* UnaryOperation Adjunct* ExistingMaterialNP Adjunct*
A2                 ::= RINSE ExternalSupplyNP
T1                 ::= THEN Clause
G1                 ::= FOR_OUTPUT MaterialNP
G2                 ::= OperationClause UNTIL Condition
P1                 ::= SEPARATE_BY_GRADE CoarsePartNP FROM FinePartNP ToolAdjunct
P2                 ::= MaterialNP MaterialNP SEPARATE_BY_GRADE
R1                 ::= LIFT_OUT DEFINITE PartNP
P3                 ::= SORT ToolAdjunct KEEP MaterialNP MaterialNP
K1                 ::= KEEP GradeSelector
K2                 ::= STORE_SEPARATELY ExistingMaterialNP
R2                 ::= RETRIEVE MaterialNP
J1                 ::= MaterialNP+ KNEAD TO_RESULT PortionNP
M1                 ::= WITH_MEDIUM SupplyKind UnaryOperation
```

An exposed exact `cthodaiin` contributes the frozen composed sequence POWDER MASS_UNIT_Q, locked inside one MaterialNP; its two components cannot become separate clauses. The other five existing compound entries are expanded only as declared: `fchokshy`→ACQUIRE ROOT_MATERIAL inside one I1; `shcthey`→THEN SPREAD with the SPREAD operation inside that THEN's clause; `chyky`→GRIND COARSELY inside one A1 with COARSELY attached to that GRIND; `otshchor`→IN_SHADE THEN in that order, with the former an adjunct of the preceding eligible operation and the latter a genuine next-clause introducer; `cphol`→KNEAD TO_RESULT inside one J1. These are the **six finite old lexical exceptions**, not a new general packing rule. Their internal virtual terminals share their one raw source-group ID and do not inflate coverage counts. No other internal seam is legal. Already declared same-value reader entries resolve only to their exact named old entry; unresolved entity strings remain literal source forms.

No naked NP/list forms a noninitial clause. Lists receive their entire role from P2 or J1. A prospective G1 is a complete goal declaration in sequence and creates no stock. THEN recursively introduces one complete Clause, without an empty following clause or boundary reset. G2 wraps one actual OperationClause; no free lookback past a different operation or goal is allowed. If its wrapped operation has no uniquely designated output under V2, that complete syntax tree receives MISSING_OUTPUT_BINDING, not a silently selected branch.

Absent UnitRun and absent explicit object use the separate first alternatives above: epsilon-list bookkeeping is not counted as different syntax. Trees differ when a terminal has a different governing operation, NP, binder, list or clause. Do not merge such trees merely because their mass consequences agree. Canonical tree IDs must preserve every terminal position, rule, parent and compound-lock relation.

No new operation-specific adjunct compatibility matrix is invented. All four old adjunct sorts may attach to any A1 operation exactly where this grammar allows. Their full lexical value remains an operation modifier; this weak syntactic policy does not declare every such physical action feasible. In particular location/tool/manner ownership is recorded, never discarded as a filler. P1/P3 retain their written tool slots; no tool terminal is reassigned to an unspoken participant.

## Compositional audit, not a replacement material simulator

Every complete tree is first retained **before** any reference, type or mass filtering. The output includes all reference failures and contradictory quantity variants, not only physically feasible trees. The four old settings are CARRY_ADD, FRESH_INPUT_LISTS, REITERATED_QUANTITY_ASSERTION and TWO_EQUAL_PORTIONS; there is no new Cartesian combination of their changes.

For each tree produce an ordered instruction/argument graph from the rule meanings already in V1 plus V2's replacement effects. Each operation node is identified by its written head occurrence; a component/branch is identified by its producer occurrence and written output role. These are deterministic graph addresses, not looked-up desired A/B/C/P/U identities. The accompanying nominal head and all properties/quantities stay attached to their actual tree argument. Tools, manner, times and goals create no plant stock. Every raw group must contribute its value to this graph even if it has no plant-mass coefficient.

Use V2's closed kind/form/property/partition matching and free/contained/consumed access. Source introduction occurs only at I1, authorized first written WATER/OIL supplies, or the old FRESH input-list exception. Measured P2 arguments describe the current prepared bulk in CARRY and a newly supplied bulk in FRESH; P3's two product descriptions are disjoint exhaustive outputs of its current input. J1 incorporates the selected written ingredients, leaving their component identities contained. M1 refers to the existing contained medium, never another supply. A prospective goal is not a referent in stock.

Reference-machine completion is deliberately **not hidden inside a successful parse**. At any lookup, report the entire eligible set before the old latest-compatible selection, with producer/release times, mention positions, active pointer and partition frame. If the old text does not determine which chronology or frame update governs a genuine tie, retain UNRESOLVED_REFERENCE_RULE for that tree and stop the universal content verdict. Do not break ties by an expected clause, letter, later desired predicate, locus or hand ledger. Likewise any unresolved selected output or incompatible operation argument remains a named failure. The proposed grammar is complete syntactically; it does not pretend to have repaired every possible semantic binding.

The **smallest adequate semantic check is a mass/provenance projection**, not enumeration of arbitrary worlds or numeric recipe trials. Preserve all full operation/modifier records, then introduce symbolic positive Q and plant-solid masses, parent/component incidences, source ancestry and free/contained status. Add exactly the inherited quantity, disjointness, conservation and source-introduction constraints. Unknown grinding extents, sieve remainders and initial masses remain symbolic under V2 bounds; do not assign them convenient observed numbers. ONE PORTION contributes a batch count, never a mass Q. Report any needed physical/property premise not discharged by V2 separately. In particular this audit cannot certify a full general DRY_STATE update rule, actual sieve feasibility or a historical mesh size.

A complete tree with unbound physical conditions can still have an explicitly labelled conditional mass consequence. It cannot be called an executable full-material reading. If an unresolved reference changes which mass variable a word denotes, no universal mass/provenance verdict is allowed. This is a stopping condition, not permission to add another rule. The authored clause trees/hand ledgers may be compared **after** all results as exposed witnesses; they cannot restrict parsing or resolve references.

## Exact questions, retained rivals and outcomes

For **each** whole unit/tree and each applicable old rival, report the written argument graph, independent stock/node equalities, quantity constraints and whether each claim below is forced, contradicted, permitted-but-not-forced or unresolved. No universal claim over an empty parse set is a PASS.

1. f21r: the final UNTIL condition quantifies the SIEVE-selected output U, not input P or the merely prospective goal; U has plant mass Q and original-source ancestry. Keeping a positive coarse branch plus conservation requires initial plant mass M>Q. p=Q and zero unnamed final remainder remain allowed. DRY/FINE/CLEAN are distinct; the uncertainty concerning general DRY predicate maintenance is retained.
2. f32v CARRY_ADD: the measured initial partition is C:2Q plus P:Q; the SORT/KEEP construction gives disjoint F:Q and G:Q from C; J1 uses the surviving P for the plant component of T. Thus initial source plant mass3Q is retained as F+G+T_plant. Test that the words actually force those owners under every complete tree, rather than copying C/P labels from the intended line interpretation.
3. f32v REITERATED: if that same written C is Q while its two disjoint exhaustive products are Q each, retain the old local Q=2Q contradiction for Q>0. A complete differently bound tree avoiding the antecedent would show that the old rejection depended on an authored parse. Do not reject the tree merely for avoiding the intended argument graph; evaluate its unchanged V2 rules.
4. f32v FRESH: the initial prepared source is not used in the later listed inputs; new measured bulk supplies F/G, and new powder supplies T while the earlier fine P remains. Test this causal distinction, not just total external mass. No written exhaustive-use requirement is added to make FRESH fail.
5. TWO_EQUAL_PORTIONS: the aggregate 2Q branch and overall3Q account remain equal to ADD. Do not infer which original Q portion supplies which later sorted product; the existing words do not identify those individual contributions.

Possible outcomes change different decisions:

| Outcome | Research decision |
|---|---|
| No complete primary ZL tree | Reject this newly completed grammar; the old handwritten reading remains a separate hypothesis, not globally refuted. No grammar repair in this run. |
| A complete tree changes a decisive material owner/quantity relation | The corresponding claimed consequence is parse-dependent; preserve both full trees and qualify the old informal argument. This does not choose the rival as true. |
| All complete primary trees retain the graph/consequence | Establish robustness only within G-P82 and the fixed V2 assumptions; manual line segmentation is unnecessary for that specific consequence. This supplies no independent support for meanings or the grammar. |
| Only adjunct ownership varies | Report which process descriptions remain ambiguous although the mass argument survives. Do not count multiple equivalent equations as independent evidence. |
| Different reader gives no complete tree or different graph | Preserve the whole alternate-reading failure/difference; no normalization, alias extension or reader deletion. Primary robustness is not reader robustness. |
| Reference/physical premise needed for a mass claim is unspecified | MISSING_BINDING for that claim/tree; retain the complete syntax forest, no simulator or arbitrary state convention. |
| Resource/budget limit | UNKNOWN_CAP, with complete counts known so far and explicit unfinished obligation; no threshold enlargement. |

A concrete **unexecuted** ambiguity witness follows already from the new A1 alternatives: in the fixed sequence DRY IN_SUN GRIND COARSELY, IN_SUN can attach backwards to DRY or forwards to GRIND. The two process descriptions differ even if mass/ancestry do not. It is not evidence that every other boundary is forced. No parse count or universal result is predicted as an observed fact here.

## Cost, selection gate and proposed later budget

New costs are the exhaustive type-class membership, the exact root/union/list grammar, optional-case disambiguation, compound constituent locks, syntactically unrestricted adjunct compatibility and explicit whole-tree output/failure protocol. These are not18 recovered rules. There are zero new lexical values, sources, material effects or word-specific exceptions beyond the six already listed compound hypotheses. No new active-pointer, recency, goal, moisture or physical-cut rule is authorized in this offer; a necessary missing rule blocks selection/content evaluation instead of being silently supplied.

Before selecting implementation, an independent reader must check full65+15 value coverage, literal source/compound interfaces, category closure, and that the mass projection needs no unspecified reference decision. If it does, root should decline the proposed test or register a **separate explicit new binding hypothesis**; this document does not authorize one. The paper grammar is a concrete reviewable offer even if that final readiness gate fails.

If selected, allow at most45 minutes including decision, implementation, independent validation, public lock, execution and publication. Six units only; no census. Fixed ceilings:100,000 complete canonical trees per unit,10,000 distinct argument graphs per unit and eight minutes combined execution after registration. A packed forest may certify equivalent subtrees only if it preserves their exact total count and all possible argument attachments; a first successful parse or the authored tree cannot stand in for the forest. If these ceilings cannot cover the forest, report UNKNOWN_CAP. No solver, parser, source-world replay or target algorithm has been implemented/executed for this offer.
