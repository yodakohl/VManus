# AE: a concrete solar–plant content link, with different organs and operations

**Positive source result; no Voynich reading selected.** Isidore XVII.9.37
actually combines moving leaves, opening flowers at sunrise and closure at
sunset within one named plant account. This is a more specific content model
than a plant merely bearing a solar name. It is not a recovered sentence from
Voynich and does not independently identify any pictured plant.

The initial 35-minute intake began at15:38:36UTC on29September2026. The source
question was registered before external retrieval. The complete Pliny chapter
was already cached. Its opening does not name the organ that turns, so root
followed the precise Dioscorides/Isidore references in the historical apparatus,
reading complete IV.190–191 and XVII.9.37. This is a bounded source extension,
not a target-dependent repair: no Voynich target was selected, opened or scored.
Search results and the opening of the surrounding public books exposed some
neighboring historical entries, but they were not incorporated as extra evidence.

## Exact whole source units and their content

| Primary unit actually read | What it says | Qualifications that survive |
|---|---|---|
| Pliny, Natural History XXII.29, all three authorial HTML paragraphs, Bostock/Riley translation | Solar turning even in cloud; a blue flower closes at night. Then two kinds, their different growth/appearance and complete medicinal/ritual accounts. | The turning organ is not specified in the opening. Two kinds must not become one modern species. Blue color, height and modern identifications are questioned in the separate edition notes. |
| Dioscorides, Wellmann IV.190, both sections | The greater heliotropium has two named explanations: its curved flower resembles a scorpion tail; its leaves turn with the Sun's inclination. Further morphology and medicinal applications follow. | Leaves perform the turning; flower shape supplies the scorpion resemblance. The entry does not say the flower turns or that the whole plant circulates. Modern species identity and the physical truth of the reported actions are not established. |
| Dioscorides, Wellmann IV.191, both paragraphs | The lesser kind has similar but rounder leaves, rounded hanging fruit, a wet habitat, and distinct preparations. | The local morphology comparison does not explicitly repeat the solar-turning claim. Do not automatically export all IV.190 properties into IV.191. |
| Isidore, Etymologiae XVII.9.37, complete entry | Alternative explanations for the name: summer-solstice flowering or leaves turning with solar motion. The account further gives flowers opening at sunrise and the plant reclosing at sunset, aliases and wart-treatment uses. | The naming explanations are alternatives (`vel`), not a conjunction proved for a modern taxon. `idem se reclaudit` uses the same plant as grammatical subject; flowers are the locally implied closing organ, not a second explicitly written noun. |

The complete primary wording, apparatus and extraction boundaries are retained
in AE_COMPLETE_SOURCES.json. AE_EXTRACT.py reproduces it from bound inputs.
Greek text and its adapted TEI extraction retain the source's CC BY-SA4.0
attribution to the Wellmann edition / Harvard College Library / First1KGreek.
The Pliny and Isidore historical texts are public domain. Edition commentary
is explicitly separated from ancient authorial claims. The Isidore transcription
marks `eo` as a poor reading; the marker is retained. No outside person was
contacted. No new medical recommendation is being made.

Sources: [Pliny XXII.29](https://www.gutenberg.org/files/61113/61113-h/61113-h.htm#BOOK_XXII_CHAP_29),
[Wellmann Greek TEI](https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg0656/tlg001/tlg0656.tlg001.1st1K-grc1.xml),
[Isidore XVII.9.37](https://penelope.uchicago.edu/Thayer/L/Roman/Texts/Isidore/17%2A.html#9.37).
These editions are not inspected fifteenth-century exemplars and do not establish
a Voynich transmission chain. The accounts are historically related, not three
independent confirmations of a plant identification or a manuscript reading.

## Concrete consequences for a possible reading

Let P be the plant, L its leaves, F its flowers and S the Sun. These letters are
analyst variables, not transcribed signs or assigned Voynich meanings.

1. **Different organs, same plant.** The source permits FOLLOW_ORIENTATION(L,S)
   together with OPEN(F, sunrise) and CLOSE_AGAIN(P, sunset), with F as the
   locally inferred closing organ. A reading that makes the root perform all
   three actions would add content absent from these entries.
2. **Changing orientation is not transport.** Turning leaves toward solar motion
   does not move the plant to the Sun, exchange source and recipient, or make
   the flower trace a spatial circle. A shared relational construction must
   preserve what changes and what remains in place.
3. **Two solar phases constrain one cycle.** Isidore's sunrise opening and sunset
   closure attach to the same plant account. A reversed schedule is a genuinely
   different account; a single unspecified 'change' would discard this content.
   It still would not be rejected as Voynich meaning unless a complete target
   construction actually bound these participants and phases.
4. **The cloud qualification is source-specific.** Pliny states tracking even
   with cloud cover. Neither direct visibility of the solar disk nor a physical
   mechanism is thereby written. Do not add the cloud qualification to Isidore
   as though he expressed it, or treat it as proof of modern phototropism.
5. **Orientation, flower closure and a derived plant name are distinct.** A
   solar compound name may refer to a reported property without itself asserting
   a time-dependent action. Name occurrence is not three recovered predicates.
6. **The complete entries are more than the attractive opening.** They include
   comparisons, aliases, habitat, organ-specific preparations and different
   attributed uses. A proposed literal whole-entry correspondence must account
   for that remainder rather than silently discarding it.

This is the useful new constraint supplied by the source reading. It gives a
content account in which a celestial referent can also occur in a botanical
discussion without being a plant name, and where two different botanical organs
take different predicates. No EVA word has been chosen from its frequency or
shape to stand for P, L, F, S, OPEN or CLOSE.

## Complete-entry details and unresolved readings

Pliny's second paragraph distinguishes the greater helioscopium from tricoccum
by size and habitat, then enumerates food/potion, juice preservation, topical
and ingested uses involving leaves, root and seed. Its third paragraph gives
the other kind's smaller drooping leaves and scorpion-tail seed resemblance,
followed by protection, confinement/killing, fever, topical and ritual claims.
The final knot prescription is attributed to the Magi: the patient binds a
rooted plant and hopes to recover to untie it. Recovery and actual untying are
not asserted outcomes. This remainder is being independently examined by the
bounded AF producer; root does not convert its reported operations into a new
Voynich constructor here.

Dioscorides IV.190 retains the descriptive three-or-four root branches, further
branching, pale/purplish curved flower, thin root and rough habitat. Its root is
called useless in the description, yet a later report attributes root wearing
to some practitioners. These scopes are preserved, not rewritten as one flat
authorial useful-and-useless assertion. The main text continues after the long
apparatus and page break: root wearing, fever-seed numbers, external fruit/leaf
uses and the final menstrual/embryo claim all remain in the extraction. The exact
attachment of the one-hour-before phrase in the fever sentence is not resolved
by this solar inquiry and is not used as a timing constraint. IV.191 preserves
its supplied word `τόποις` and the encoded vertical bar; no editorial cleanup
creates a new source variant.

## Decision and next step

Retain IDEA741 as a now source-supported **exploratory content mechanism**, not
as a selected target experiment or translation. The plant-to-Sun relation is
present in primary wording; static direction alone cannot substitute for it.
The next useful step is one complete written construction that binds the same
plant, its distinct organs and the solar phases, with every new word/component
meaning explicitly costed and its already known corpus use accounted for. A
blue or curved flower selected from a picture is insufficient by itself.

Do not build a classifier or new code search from this source intake. GDT1079,
IDEA780/781, the old plant-name tests, their counterexamples and all reserve
stops remain unchanged. Independent Voynich meaning confirmation capacity is
zero here; no significance or confirmed lexical value is claimed.
