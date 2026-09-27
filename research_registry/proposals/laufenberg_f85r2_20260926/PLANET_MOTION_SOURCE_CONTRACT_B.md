# RAW602 source-contract critique B

Prepared 2026-09-27 from the live route, RAW602 idea summary, and the already owned complete Steele text unit `external_cache/steele_science_complete_unit_20260927.txt` (planet-motion passage beginning “All the planets move by double moving”). This is source-side contract advice only. I did not read target text or images, inspect RAW602 authoring, run queries, select forms, or access reserves. Parent is separately checking GDT1030/936/939 and the closed astronomy primary.

## Source-side structure that a whole reading must preserve

The source begins with two top-level modes: motion by each planet’s own kind, west-to-east contrary to the firmament, and the firmament’s carried/ravishing motion east-to-west, occurring daily. It then says the own/kindly motion itself is double: first and second. The first is the planet’s bounded round motion in its own eccentric circle; the second is its motion under the Zodiac through like space in like time. Eccentric and Zodiac do not share a centre. An epicycle is separately defined, followed by direct, stationary, and retrograde manners located respectively at its upper, middle, and lower parts.

This hierarchy is the strongest semantic source constraint: a summary with three flat top-level motions—carried, first, second—or treating Direct/Stationary/Retrograde as sibling motion engines would misstate the text. A common planet record is source-compatible as an analytical representation because the passage generalizes over “all planets” and later “a planet”; however, the text does not itself state a formal reusable record constructor or a single law that fuses every motion, period, and circle statement.

The causal attributions must remain narrow. The firmament is what carries the planets daily east-to-west; the planets’ own motion runs the contrary way. The text associates differing course lengths with shorter or longer completion times. It does not say that circle circumference alone determines every listed period, or that per-sign stay times calculate full-course periods by multiplying by twelve. Later claims about generation/corruption, creature inclination/destruction, and variation by climate/country stay within the source’s own broad medieval account; they do not authorize a modern force model or more specific planet-to-effect assignments.

## Seven literal period pairs and all remaining duties

A complete candidate must preserve all seven per-sign/full-course pairs under their exact listed planet owners and roles:

| Planet | Stays in each sign | Completes course |
|---|---|---|
| Saturn | 30 months | 30 years |
| Jupiter | 1 year | 12 years |
| Mars | 45 days | 2 years |
| Sun | 30 days, 10 hours, and one-half | 365 days, 6 hours |
| Mercury | 28 days, 6 hours | 338 days |
| Venus | 29 days | 348 days |
| Moon | 2.5 days, 6 hours, and one bisse less | 27 days, 8 hours from point to point |

These are source claims, not a consistent modern arithmetic table. Keep all numbers, units, mixed components, and the lunar “one bisse less” phrase as written. Do not normalize Mars, infer a universal 12-sign multiplication, repair Mercury or the Moon, convert bisse into a modern unit, or change a total to make it match a stay value.

The surrounding unit duties are also mandatory: the shorter/longer course-duration contrast and its stated course-length reason; entry and exit of the seven stars into/from twelve signs varying and disposing generation/corruption in the lower world; the quoted Mesalath sphere/Earth-center and moving-elements account, with other stars helping the planets; the source’s creature-inclination and destruction claims; climate/country variation including the blue-men/Slav comparison; the nested first/second natural-motion and eccentric/Zodiac/epicycle explanations; and Direct/Stationary/Retrograde as manners located on the epicycle. The exact citation span must be fixed before authoring so the closing epicycle claims cannot become optional after the period table fits.

## Smallest useful nontrivial construction requirement

The most economical source-grounded minimum is one **duration constructor** with a written magnitude argument and written time-unit argument, yielding a duration description used in a named planet’s period slot. To count as productive rather than a mere free whole-value list, require the unchanged constructor on at least three distinct derived whole quantities, at least two distinct planet inputs, at least two distinct unit types, and at least two magnitude values. Source recurrence offers prospective anchors without choosing target values: “30” occurs with months, years, and days across Saturn/Sun; “6 hours” occurs in the Sun, Mercury, and Moon entries. These are source-side selection facts only. Do not privilege those entries after observing target forms; once any future test is selected, include all seven pairs.

This `Duration(magnitude,unit) -> DurationDescription` is a compositional representation of stated quantities, not a physical law. Per-sign and full-course relations remain separate written arguments; the constructor must not infer one from the other. Compound duration phrases retain each written component and any “less” qualification without arithmetic normalization. This requirement is smaller and more testable than a bespoke multi-clause planetary-state machine, while demanding more than fifteen unrelated period glosses. It does not by itself establish the rest of the whole motion account.

A stronger optional criterion, appropriate only if the selected hypothesis explicitly claims integrated motion-reference reuse, is the same written `PlanetMotionRecord(P)` constructor applied to at least two distinct planet inputs. Each derived reference must then be used in both (a) the opposed direction/cause claims and (b) its owned period/circle claim, without turning the source’s universal statements into a new motion law. This would bind the repeated participant across clauses more directly, but it is not the smallest criterion and the source does not force the record as the only valid analysis. If used, all seven planet pairs and the remaining paragraph duties above still have to be accounted for.

## Feasibility and principal limits

Source feasibility is positive for either constructor as a prospective hypothesis: the passage repeatedly gives quantity phrases with explicit magnitudes and units, and speaks of individual planet names under general motion/circle claims. The source itself therefore supplies more structure than an arbitrary list of glosses. Whether the target contains a repeated written constructor, suitable explicit arguments, or the necessary participant reuse is wholly unexamined here; no target values, segmentation, or translation are endorsed.

The principal source-correctness limit is hierarchical: both a flat three-mode rendering and an unqualified equation from stay-in-sign duration to full-course duration are contradicted by the passage’s organization/content. The numerical tensions must remain unresolved. Any whole-reading contract should additionally disclose that Steele is an edited English witness/translation, and the source claims do not establish a Voynich mapping or direct copying. This critique does not select a new experiment or override the parent’s predecessor and novelty review.

## Check of `PLANET_MOTION_SOURCE_GRAPH_ROOT.md`

I checked the exact owned id00108 text against M01–M12 and the 14 table entries. All twelve duties are supported by the text as bounded and qualified, and all seven planet period pairs are correctly transcribed. The nested first/second treatment, separate eccentric/Zodiac centre relation, epicycle account, planetary/climate claims and M06 Mesalath attribution/awkward syntax are retained. No correction is needed to the source graph's duty set.

The Sun's `30 DAY + (10 + 1/2) HOUR` and `365 DAY + 6 HOUR` entries match “xxx days and ten hours and a half” and “ccclxv days and vi hours.” The Moon's `2.5 DAY + 6 HOUR - 1 BISSE` is appropriately disclosed as an interpretation, not a manuscript-certified expansion. For a later transcription, I recommend displaying the wording as “2.5 days; six hours, one bisse less” with the subtraction's exact attachment marked unresolved, rather than visually giving `- 1 BISSE` the appearance of a normalized arithmetic term. BISSE remains untranslated/unconverted. The other entries match the source. No arithmetic relation across a stay and a full course is licensed.

For prospective authoring, I favor the narrower shared `Duration(magnitude, unit) -> DurationDescription` construction over a bespoke full `PlanetMotionRecord` as the minimum nontrivial construction. Require the identical explicit number/unit internal scheme to support at least three derived whole quantities, with at least two distinct magnitudes, two distinct units, and two planet-owned entries; enumerate every actual application. The 30/month-year-day recurrence and 6-hour recurrence give source-selected structural anchors, without choosing any target strings. All fourteen temporal entries and all M01–M12 duties remain mandatory, with exact planet and stay/course roles. This is an exploratory compositional requirement, not a claim about historical notation or a source law. A PlanetMotionRecord that carries one derived planet reference into both direction/cause and period/circle claims is a stronger optional integration gate, but the anthology's general-to-individual links do not force it to be the only valid grammar.
