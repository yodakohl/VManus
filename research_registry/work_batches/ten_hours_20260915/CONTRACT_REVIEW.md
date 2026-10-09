# Contract review: three-entry Dioscorides content code

I read the fixed decision note and only the cached Wellmann I.1–I.3 source texts. The source gives three complete entries: Iris, Acorus and Meum. They are short enough for a full trace, but their useful evidence is relational rather than a list of isolated plant names.

## What the source actually supplies

The entries repeatedly mention root material and warming quality, and each has a boiled preparation, but their preparation scopes and effects must remain typed rather than silently identified. Iris and Acorus are explicitly compared: Acorus has leaves and roots resembling Iris, and one Acorus use is stated to be like Iris. Iris includes a headache relieving application with vinegar and rose oil. Meum includes a contrary polarity: when more than needed is drunk, it produces headache. These relational statements are stronger source constraints than singleton descriptive details (geography, colour, exact morphology, named mixtures). “External application” should be recorded only on clauses that actually state it; it should not be promoted to a shared atom by assumption.

A minimal source graph should therefore distinguish at least:

```
entity -> material/part -> preparation -> route/medium -> effect
comparison(entity, entity, feature)
polarity(effect, helps | causes)
quantity/condition(excess or ordinary use)
```

The atom inventory must be frozen from these three entries before target comparison. `ROOT` and `WARMING` are plausible repeated source atoms; `HEADACHE` recurs in Iris and Meum but with opposite polarity. `DECOCTION`, `DRINK`, `URINARY`, and `MENSTRUAL` recur in narrower entry or application scopes and must not be collapsed without an explicit typed relation. Singleton values can remain in the trace for completeness, but they must not earn identification credit or become arbitrary “unknown plant” IDs.

## What prefix-freeness does and does not establish

The earlier wording overstated the degeneracy. A free codebook can serialize a finite source if the output string is also free to choose, but a fixed target string and fixed source pattern need not fit any injective prefix-free code. For example, source `ABBA` and target `abcd` require positive codeword lengths satisfying `2|A|+2|B|=4`, so both words have length one; the target would then have to have the form `abba`, which it does not. No added alphabet or delimiter may be smuggled in to repair that contradiction.

GDT908 supplies a relevant precedent: its exact cancellation certificate excludes the unchanged GDT899 source/compiler/code/target conjunction under all six header orders. Thus a constrained prefix-code model can have a real necessary contradiction. The weaker problem remains that allowing post hoc singleton atoms makes a surviving trace hard to identify semantically. Singleton coverage should therefore be reported separately, and no atom may be introduced after seeing a target line. This is an identifiability weakness, not a proof that every finite target fits.

## Minimal contract that would be meaningful

Before target fitting, freeze the typed fields and their source order: entry identity and comparison; physical description; material/part; preparation and medium; route/application; benefit; adverse effect or conditional exception. Require every source clause to occupy exactly one field, with no free prose or block field. Reuse an atom only when the same typed source relation is explicitly present; do not equate the scopes of the three boiled preparations or invent a shared external-application atom. Allow source-specific values to remain unresolved without claiming a match.

The useful necessary consequence is a linked three-entry polarity test. A provisional reading must reuse the same atom for the shared headache effect while changing the relation and condition: Iris has an application that helps headache, whereas excess Meum drunk causes headache. Acorus supplies the explicit comparison edge to Iris. A qualifying target trace would therefore need (a) recurrence of the shared effect atom in the two relevant records, (b) distinct typed relation/polarity operators for relief versus causation, (c) a condition/quantity marker on the Meum adverse clause, and (d) a comparison relation connecting Acorus to Iris. A repeated atom by itself is not a win; the linked polarity and comparison pattern is the discriminator.

This consequence remains testable without a confirmed word: the target parser can report exact raw groups and unresolved fields, and the preregistered serializer can ask whether the same typed relation graph is present across three complete pages. It does not require assigning an English gloss to any target form. A failure would reject this fixed typed graph and serializer, while unknown or unavailable pages would remain capacity/unknown outcomes.

## Small source-only serializer check

Within 5–10 minutes, a source-only check can freeze and emit one canonical trace for each of I.1–I.3. Use the fields `entry`, `part`, `quality`, `preparation`, `route`, `effect`, `polarity`, `condition`, and `comparison`; preserve source order and attach every clause to exactly one field. Emit `field=value` tokens from a fixed alphabet with no extra delimiter. Permit only the explicitly repeated `ROOT` and `WARMING` atoms as unqualified shared values; encode `HEADACHE` with its entry-specific polarity, and keep `DECOCTION` and `DRINK` attached to their typed preparation and route fields. Field-specific values remain tagged as source-singleton coverage. Assert that the traces preserve Iris `HEADACHE + HELPS`, Meum `EXCESS_DRINK + HEADACHE + CAUSES`, and Acorus `COMPARISON→IRIS`. This checks source completeness and the intended non-singleton constraint without fitting target text or claiming that any target form means one of these atoms.

## Recommendation

Do not implement the unconstrained global prefix-free code as currently phrased. The 60-minute source collation is worth preserving, and a small content test could be worthwhile after the typed field inventory, shared-atom rule, polarity/comparison operators, and no-singleton-credit rule are frozen. Without those restrictions, a positive complete trace would have weak semantic identification value, even though a fixed target string can still contradict the code model.

Sources: `research_registry/work_batches/ten_hours_20260915/dioscorides_cache/Wellmann_I_1.txt`, `Wellmann_I_2.txt`, `Wellmann_I_3.txt`; decision scope in `DIOSCORIDES_THREE_ENTRY_DECISION.md`; GDT908 report: `experiments/yolo/gdt908_mutual_reference_cancellation/REPORT.md`. No target text was opened.
