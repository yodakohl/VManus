# V72 R1 — owner-aware 116-statement workshop reconstruction

## Result

This pass reconstructs all 116 frozen V69 prose statements as concrete source-class clauses while carrying only the centrally selected V71 visible owners. It covers all 135 prose fields and all 381 prose events exactly once. The result is a workshop reading aid, not a decipherment or scientific claim.

The decisive correction is practical: an image supplies an **owner**, while the master exemplar supplies every unpictured object choice, action, medium, measure, condition, and use. A physical line break does not close a statement. A real V71 scene gap does stop owner inheritance even when the old V69 statement ID continues across it.

Generated artifacts:

- `V72_R1_116_STATEMENTS.tsv`: 116 complete owner-aware statement rows;
- `V72_R1_REVISIONS.tsv`: one audit row for each of the eleven records;
- `V72_R1_VALIDATION.json`: executable coverage and constraint checks;
- `V72_R1_build_statements.py`: the minimal deterministic builder.

## Fixed R1 workshop perspective

1. Du bildest mehrere Schreiber aus, die dasselbe praktische Buch zuverlässig fortsetzen müssen.
2. Du denkst in vorzeigbaren Exemplaren, häufigen Ganzkarten, einfachen Regeln und prüfbaren Abschreibeschritten.
3. Du fragst bei jeder Theorie, wie ein Lehrling sie lernt, ausführt, korrigiert und an eine zweite Hand weitergibt.
4. Du bevorzugst keine Sprache oder Bedeutung, sondern den kleinsten praktisch lehrbaren Produktionsablauf.
5. Du lieferst eine konkrete Schreibanweisung, eine Rücklesung und die Fehler, die ein echter Lehrling machen würde.

## Teachable source-clause rule

A learner receives two things: a page with the previously drawn image and a master exemplar containing the clause content. The copying routine is:

1. At a record or local-scene entry, set the smallest V71 owner.
2. Copy events in frozen V69 order. For a known card or known formal slot, copy the existing uncertain label exactly, including `?`; do not turn it into a word meaning.
3. For every other event, copy one explicitly typed exemplar value: `OBJECT`, `ACTION`, `TARGET`, `MEDIUM`, `MEASURE`, `STATE/CONDITION`, or `CLOSURE_ACTION`.
4. If the next field has the same local owner, carry that owner without restating the image.
5. If only the physical line changes, continue the statement. Line end is spacing, not punctuation.
6. If V71 places the next field in another disconnected image zone, stop the owner clause and set a new owner. The two clauses may retain one archival V69 statement ID, but they are not one connected Bio apparatus or flow.
7. If the owner is `UNRESOLVED`, consult the master exemplar; do not inherit across the image gap.
8. The picture never licenses a substance, direction, disease, timing, dose, or use by itself. Those remain explicit exemplar content.

In compact workshop notation:

```text
SOURCE_CLAUSE := OWNER_SET_OR_CARRY + EVENT+
EVENT         := (KNOWN_CARD | KNOWN_FORMAL_SLOT)? + TYPED_EXEMPLAR_SLOT
STATEMENT     := SOURCE_CLAUSE (LINE_WRAP SOURCE_CLAUSE)*
SCENE_GAP     := OWNER_RESET, not a semantic connector
```

This is easy to teach because the apprentice makes only three decisions: **which owner is active, whether it carries, and which typed value is copied from the exemplar**.

## What “concrete” means here

Every row gives one complete exploratory source-class paraphrase. Herbal rows lead with an illustrated-simples clause; Biological rows lead with a local bath/application clause. Each also gives a concrete practical/workshop rival. The content is inherited from the already exposed V69 source editions and is now attached to V71 owners; it is not a new word, card, stem, or translation value.

The literal layer is stricter than the paraphrase. Every one of the 381 events has:

- its event serial;
- the active V71 owner;
- any already known card/formal prompt;
- one nonempty typed exemplar slot.

There is no bare `[EXEMPLAR CONTENT]` placeholder.

## Repair-cost scale

| Cost | Workshop meaning |
|---:|---|
| 0 | Direct visible owner and unique V69 parse; no owner repair. |
| 1 | Direct owner with parse expansion, or a uniquely parsed carried owner. |
| 2 | Same-scene owner carry plus parse expansion, or page-owner content with little additional repair. |
| 3 | Page-only/unresolved owner or unparsed/ambiguous source clause requires the master exemplar. |
| 4 | The old V69 statement crosses a real V71 owner reset and must be written as two owner clauses. |

Observed distribution: cost 1 = 17, cost 2 = 66, cost 3 = 29, cost 4 = 4. A high cost does not reject the statement membership; it records how much of the readable clause is supplied by the source tradition rather than the picture.

## Full eleven-record walkthrough

### H1 — f10r, 2 statements, 14 events

Owner throughout: `WHOLE_BROAD_TOOTHED_RADIAL_FLOWERED_HERB`. `H1-S001` opens the whole-plant article but lets the exemplar select an underground portion, then gives cleaning, cutting, liquid addition, use, measure, and storage. `H1-S002` takes the prepared first run, warms it, carries the active work state with the existing formal link, and tests the existing `BEREIT?` card. Strong rival: material-lot/sample handling. Contradiction: neither the underground-part choice nor the medium, use, measure, or storage is visibly labelled.

### H2 — f10r, 3 statements, 24 events

The owner resets at record start to the same whole illustrated f10r plant, not to a new labelled plant part. `H2-S001` selects young upper material from the exemplar, prepares a liquid post, carries an active state, and books a measure. `H2-S002` creates an earlier/pre-bloom comparison portion, resumes a prior post, and measures it. `H2-S003` treats the later fraction as a parallel preparation and gives mixing/holding/application content. Strong rival: comparative material-batch bookkeeping. Contradiction: harvest stage, parallelism, vessels, and use are not drawn.

### H3 — f11r, 4 statements, 17 events

Owner throughout: `WHOLE_DENSE_BLUE_FLOWERED_CROWN_PLANT`. `H3-S001` gives a spring collection and filtering sequence ending at the existing `KLAR?` gate. `H3-S002` retains a flower portion as an exemplar-defined secondary portion. `H3-S003` resumes the first extract, identifies a working portion/target, and books the existing measure card. `H3-S004` takes the retained flowers into a warm second preparation and closes at `BEREIT?`. Strong rival: reference-sample and batch handling. Contradiction: the drawing supports the whole specimen, not spring, filtering, a retained reference, or therapeutic use.

### H4 — f55v, 4 statements, 18 events

Owner throughout all text pockets: `WHOLE_BROAD_LEAF_PANICLED_PLANT_WITH_MNEMONIC_ROOT`; the pockets are not separate part captions. `H4-S001` starts and measures a first leaf post and prepares it. `H4-S002` takes a measured portion and performs the next mix/wash action. `H4-S003` supplies a concrete external-wash clause entirely from the exemplar. `H4-S004` measures the retained portion, sets the existing target/link slots, combines or compares the preparations, and gives use/storage content. Strong rival: four separate part/sample entries. Contradiction: the picture does not decide the medium, target, wound, or whether the grotesque root is mnemonic rather than literal.

### H5 — f56r, 6 statements, 27 events

Owner throughout: `WHOLE_MULTIHEAD_SPINY_OR_EMBLEMATIC_HERB`. `H5-S001` crosses f56r.5 to f56r.7 without ending: the exemplar selects a plant portion, sets measure, prepares it, applies the active portion, and sets a target. `H5-S002` closes the first application. `H5-S003` separates flowering and leaf portions for drying. `H5-S004` resumes a dried portion for a weak preparation/storage step. `H5-S005` introduces a fresh remainder with binder/mixing content. `H5-S006` selects a final pictured portion and books its measure. Strong rival: separate heads or growth-stage entries. Contradiction: no head is visibly tied to a separate paragraph, and all preparation/use detail is exemplar-supplied.

### B1 — f81v, 21 statements, 66 events

Owner throughout: `B1_SHARED_TWO_ROW_POOL`; no seven-stage circulation is restored. The complete order is: `S001` local flush/closure; `S002` measured post, local target and active-state continuation across f81v.2→.7; `S003` continuation across .7→.17; `S004` mix-to-condition; `S005` set aside/close; `S006` measured fill/addition; `S007` warm/close; `S008` active-portion continuation; `S009` and `S010` two formal flush closures; `S011` local run/application; `S012` begin wash; `S013` wash/close; `S014` mix and carry the local state; `S015` fill/cool; `S016` set local relation, temper, and continue; `S017` set local target; `S018` fill/apply/settle across .24→.27; `S019` stand to readiness; `S020` gentle-heat condition; `S021` final local target/action. All are clauses at one shared pool owner. Strong rival: two independent rows or an allegorical field. Nothing here establishes direction or a connection to another page.

### B2 — f82r, 22 statements, 62 events

This record has five local owners and therefore cannot be one linear machine. At `B2_UPPER_PAIRED_BASINS_AND_CYLINDER`, `S001` flushes/closes, `S002` sets aside, `S003` measures/fills, `S004` targets and tempers across .2→.3, `S005` continues a second run across .3→.4, and `S006` closes the upper clause. At `B2_MIDDLE_LEFT_DEVICE_AND_INLINE_NODE`, `S007` adds clean water, `S008` carries a duration, `S009` holds warm, and `S010` tempers/continues. `S011` belongs to unresolved `B2_MIDDLE_RIGHT_AMBIGUOUS_STATION`. `S012` is the critical repair: its first field draws off at that unresolved station, then a mandatory owner reset starts an independent temper/measure/application clause at `B2_LOWER_GREEN_MULTI_FIGURE_POOL`; no conduit is asserted. `S013` drains locally and `S014` closes that lower pool. At `B2_LOWER_POOL_EDGE_STATIONS`, `S015` starts a wash, `S016` carries it across .26→.27, and `S017`–`S022` give water addition, sitting/application, local wash, warm cloth, repeated sitting, and final equal-part mixing. These are source-class contents, not visible substance or flow labels.

### B3 — f83r, 34 statements, 86 events

Five owner zones are kept separate. At `B3_UPPER_MARGIN_OPEN_FAN_STATION`, `S001` settles/closes, `S002` names a local lower outlet as exemplar content, and `S003`–`S004` use and measure the active post. At `B3_MIDDLE_MARGIN_ROUND_VESSEL_STATION`, `S005` flushes, `S006` adds warmed water, `S007` measures, `S008` drains, and `S009` applies locally. At `B3_LOWER_MARGIN_BASKET_VESSEL_STATION`, `S010` fills, `S011` applies, `S012` continues the work state, `S013` measures, `S014` opens a source-specified run, and `S015` drains. `S016` closes that owner and then explicitly resets at the unresolved margin/main gap; it does not connect the zones.

Within `B3_MARGIN_TO_MAIN_GAP_UNRESOLVED`, `S017` washes/bathes, `S018` waits to readiness, `S019` warms, `S020` targets, `S021` measures/targets across .14→.15, `S022` mixes/closes, `S023` drains, `S024` flushes, and `S025` warms; every owner choice here is master-exemplar dependent. `S026` begins at that unresolved gap and then resets before its final settling action at `B3_MAIN_ARCH_LINKED_PAIR`. At the main pair, `S027` applies a warm cloth, `S028` tempers/flushes, `S029` continues/flushes, `S030` applies/measures across .20→.22, `S031` washes, `S032` begins a longer wash/clarification, `S033` draws off, and `S034` closes at a clarity/readiness condition. No global f83r cycle or direction is reintroduced.

### B4 — f83r, 16 statements, 47 events

At `B4_MAIN_ARCH_LINKED_PAIR`, `S001` immerses a cloth, `S002` fills/tempers/flushes, `S003` carries a selected active portion across .25→.26, `S004` applies a warm cloth, `S005` passes through cloth, `S006` and `S007` strain/close, `S008` measures/flushes, `S009` waits to readiness, and `S010` warms/closes. At `B4_MAIN_LEFT_OPEN_FRINGE_STATION`, `S011` measures and continues across .35→.37, `S012` drains, `S013` lets a mixture enter and settle, and `S014` carries the active post. `S015` measures/tests at the left station, then explicitly resets before a separate drain clause at `B4_MAIN_RIGHT_S_RUN_MULTIPORT_STATION`; this is not evidence of left-to-right flow. `S016` stays at the right station across .41→.44 and gives a local target/fill/readiness clause.

### B5 — f83r, 3 statements, 11 events

Owner throughout: `B5_LEFT_OPEN_FRINGE_STATION`, not the entire paired main scene. `B5-S001` draws off/closes, `B5-S002` warms/closes, and `B5-S003` crosses f83r.47→.48→.49 while carrying the same owner through duration, target, active-state link, measure, second opening, and mixing content. The line crossings do not create extra sentences. Strong rival: ownership by the whole pair. No visible direction or substance is inferred.

### B6 — f83r, 1 statement, 9 events

`B6-S001` sets `B6_RIGHT_S_RUN_MULTIPORT_STATION`, crosses f83r.52→.54, and carries the same owner through station setup, a no-heat condition, first opening, active-state link, measure, filtering/portion, and target content. Strong rival: ownership by the whole pair. The S-run and multiarm contour identify the local owner only; they do not prove a pipe, direction, or semantic operator.

## Line crossing is not statement closure

Eighteen statements cross at least one physical locus boundary:

`H5-S001`, `B1-S002`, `B1-S003`, `B1-S018`, `B2-S004`, `B2-S005`, `B2-S012`, `B2-S016`, `B3-S016`, `B3-S021`, `B3-S026`, `B3-S030`, `B4-S003`, `B4-S011`, `B4-S015`, `B4-S016`, `B5-S003`, and `B6-S001`.

The longest is `B5-S003`, spanning three physical loci. Conversely, only four statement rows contain a genuine V71 owner reset: `B2-S012`, `B3-S016`, `B3-S026`, and `B4-S015`. This cleanly separates typography from image ownership.

## Strongest revisions to V69

1. All Herbal part/species labels are demoted from visible ownership. The whole pictured plant owns the clause; a part may still appear as an explicit master-exemplar argument.
2. All Biological global apparatus/cycle readings are removed from the owner layer. Only local contact-bounded scenes carry.
3. Four old statement memberships cross new owner boundaries. They remain one archival statement row but are written as separate source clauses with no visual connection.
4. Thirteen statements touch unresolved owner fields; their local owner must be looked up rather than inherited.
5. Every previous free exemplar phrase is made typed and concrete. Known cards and formal prompts remain exactly the already frozen uncertain labels.

## Ceiling

The strongest result is a reproducible scribal procedure:

```text
VISIBLE OWNER → LOCAL CARRY OR RESET → KNOWN CARD/FORMAL SLOT → TYPED MASTER-EXEMPLAR VALUE
```

It supports a learnable way for several fifteenth-century scribes to place dense text around drawings made first. It does **not** establish that the preferred source class is correct, that any card is a word, or that any glyph sequence has the proposed readable content.
