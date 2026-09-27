# Independent bounded audit of the frozen RAW565 honey draft

## Replay result

I independently rebuilt the four-block census from the owned GDT1042 safe projection `artifacts/guarded_projection.tsv`; I did not import `run.py` or read any mixed source TSV. The projection SHA-256 is `489c3960116c88f76de39187eef3d2f9d3dd68d3c2e514f54abe7a2294d185e9`, and the locked METHOD hash matches the preregistration. The frozen draft hash matches the supplied `30e20e160e20cdd09931e44135b36668afa6cd1885d04663c2190c496e7d30bc`.

The validator independently matched all 324 N/E/S/W rows field-for-field, including exact IDs, raw groups, line positions, paragraph/separator flags, block allocation, and literal assignment status. Its 18 authored ZL clauses partition all 108 ZL group IDs exactly once, and each clause’s saved raw sequence and row backlinks match the projection. Recounting exact whole-form matches gives ZL 108/108 assigned, IT 96/107 with 11 literal gaps, and RF 91/109 with 18 literal gaps. The all-24-locus index of assigned whole forms exactly matches the safe projection; it contains 85 forms. The separate outside-block table also matches all 47 assigned occurrences exactly, while its surrounding contexts remain expressly unparsed.

## Reused constructions

The qod compounds are all and only the three licensed cuts, with these ZL spans: `qodar` E.10 G002; `qodaiin` S.16 G002 and W.21 G005; `qodain` W.19 G002. Their reader distribution preserves a concrete alternate: IT S.16 G002 has literal `qodain` (the draft’s IN(FOOD)) where ZL has `qodaiin` (IN(BODY)); this fails transfer of the specifically body-located phrase but does not logically prove contradiction, since food may be inside a body. RF’s `qo@152;ain` at W.19 is a marked unmatched literal and remains a gap. The draft does not normalize these forms.

The repeated `shedy` Product token occurs in ZL at S.13 G002, W.20 G008, W.21 G004 and W.22 G003. The repeated `chol` transition occurs in ZL at N.4 G004 and W.23 G003. The exact whole-form contexts in all three readers are listed in the machine result. The explicitly declared input/output orders, generic case binding, and W.4 plural product-set lift yield no mechanical role swap in these spans. The qod function’s container-type inputs are recipient, body and food, each supplied by a declared role; it is not used as an unrestricted alias.

The type/domain audit found no concrete operand mismatch within these specifically reused constructions. Two qualifications remain material. First, `chol=BECOME` spans both a physical honey portion/property and an epistemic argument/clarity pair. The draft declares that polymorphic transition domain; it is a substantial authored extension, not independently supported by a second natural-language domain. Second, W.4’s `shedy` use requires the separately declared plural/set-valued comparison construction. It is costed and type-described but tailored to the comparison clause. These are model obligations rather than literal counterexamples.

A concrete unchanged-reading countercase is retained in the draft itself: IT and RF W.20 begin with `ar` (RECIPIENT), not ZL’s `or` (HONEY), although the later honey token remains. The exact ZL topic/opening template therefore does not transfer unchanged. IT/RF unmatched groups remain gaps rather than repairs. No new aliases, assignments, or readings were added here.

## Disposition and limits

The reproducible validator is `HONEY_WHOLE_VALIDATOR_B.py`; its machine output is `HONEY_WHOLE_VALIDATOR_B.json`. The replay passes structural coverage and occurrence indexing. This establishes literal bookkeeping only: it does not establish that any English value is correct, that the 18 editorial clause boundaries are recovered, that 85 guesses form a coherent translation, that the source is Galen, or that the causal/provenance hypothesis is true. In particular, 108 completed ZL groups do not amount to all-reader completion or full consistent parses; the 11 IT and 18 RF gaps and 47 outside-context debts remain.

## Prompted follow-up: `odain` and process typing

This check was added after the first-pass review at root’s request. In S.16 G003–G005 the literal sequence is `odain an chey …`; the draft assigns `odain` a BY(production,process) relation and `an` a KIND_CHANGE relation with lineage endpoints. G12 describes the clause as “by kind change” and separately types `KindChange(z,y,c)`, but introduces no distinct Process/Event individual. If BY requires a Process-typed entity, its second argument is not supplied. If BY instead relates the production and change predicates/descriptions at a higher order, that coercion and type rule are not explicitly stated. This is a formalization gap/underspecification, not a forced contradiction: the higher-order construal remains possible, but should not be reported as an already complete typed event representation.
