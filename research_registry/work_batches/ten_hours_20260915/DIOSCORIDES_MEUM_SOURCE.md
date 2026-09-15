# Dioscorides I.3 Meum: bounded source case

**Status:** `SOURCE_ONLY_UNREVIEWED` (2026-09-15). This note deepens `IDEA000334`; it does not test a Voynich target, open data, assign a gloss, or alter a decoder. Cache and source metadata: `dioscorides_cache/meum_1_3_excerpt.txt` and `dioscorides_cache/SOURCE_METADATA.json`.

## Source and exact scope

The complete relevant English entry is **Dioscorides, *De materia medica*, Book I, chapter 3, “MEON,” printed p. 5** in *The Herbal of Dioscorides the Greek*. The PDF is a new indexed modern-English version by **T. A. Osbaldeston and R. P. A. Wood**, first published by Ibidis Press in 2000. Its editorial preface says it modernizes the Goodyer translation and does not attempt a new correction against Greek; it discusses Gunther’s 1933 edition as the earlier edited Goodyer tradition. The older Greek parallel is **I.3.1, “mêon Athamantikon”** in the Wellmann/Berendes digital transcription. The English edition is a translation/edition, while the Greek page is an editorial digital transcription; neither is treated as evidence for a Voynich lexicon. The Greek confirms the same branch sequence and adverse clause, with wording differences noted below.

Sources: [Gunther/UPenn English edition](https://web.english.upenn.edu/~cavitch/pdf-library/Dioscorides_De_materia_medica.pdf); [Greek I.3.1 transcription](https://plantuse.plantnet.org/fr/Dioscoride%3A_livre_1); [Perseus/CTS Wellmann-edition locator](https://atlas.perseus.tufts.edu/library/urn%3Acts%3AgreekLit%3Atlg0656.tlg001.1st1K-grc1/).

## Bounded meaning structure of the complete entry

The entry has a descriptive identification layer followed by a material/operation/result layer. The source gives no numeric dose and does not state that every complaint is a separate preparation.

| ID | Source role and arguments | Claimed consequence |
|---|---|---|
| D0 | Item: Meum called athamanticum; origin Macedonia and Spain; stalk/leaves like dill but thicker; long thin fragrant roots; warming tongue | Identification/quality description, not a treatment step |
| M | Material argument: roots (Greek plural `ῥίζαι`) | The following operations act on the roots |
| P1 | Alternative preparation: roots boiled with water; administration: drink | Relieves pains from obstructions around bladder/kidneys; suits urinary difficulty, gas-filled stomach, griping, womb disease, joint pain |
| P2 | Alternative preparation: roots pounded smooth/fine without boiling; administration: drink | Same disease/result cluster as P1; the source explicitly contrasts boiled and unboiled-pounded preparation |
| P3 | Preparation: pounded into small pieces with honey; administration: syrup/electuary | Helps a rheumatic chest |
| P4 | Preparation: boiled; application: hip/sitz bath | Draws menstrual blood |
| P5 | Application: plaster on lower part of children’s bellies / pubic region | Induces movement of urine |
| N1 | Condition: more decoction than suitable, taken as a drink | Causes headache; this is a named adverse result, not another benefit |

The source’s shared argument is therefore **roots**, with at least two drink alternatives (boiled vs. unboiled/fine-pounded), one honey preparation, one external bath, and one plaster. P3–P5 are not stated to inherit every disease in P1/P2. P4’s “boiled” preparation does not repeat “with water” in the English sentence, though “decoction” and the Greek `ἀποζεσθεῖσαι` support a boiled preparation. N1 says excess “more than needed” but gives no quantity or threshold.

## Greek/English collation and open textual choices

The Greek transcription preserves: `ἀποζεσθεῖσαι μεθ' ὕδατος` (boiled with water), `λεῖαι δίχα ἑψήσεως ποθεῖσαι` (made smooth/fine and drunk without boiling), `σὺν μέλιτι ... ἀντὶ ἐκλεικτοῦ` (with honey as an electuary), `... εἰς ἐγκάθισμα` (for a sitz bath), and `τοῦ ἐφηβαίου` (the pubic/lower-belly region). It closes with `πλεῖον ἢ δεῖ πινόμενον` (drunk in an amount beyond what is needed) and headache.

Keep these uncertainties open:

- `λεῖαι` supports “smooth” or “fine”; it does not decide a target operation token.
- `ἀντὶ ἐκλεικτοῦ` is rendered “as syrup” in the English edition and more literally “instead of/as an electuary”; this is an administration-form distinction, not a new ingredient.
- “Diseases of the womb” and “hysterical states” are translation choices for `ὑστερικαῖς διαθέσεσι`.
- `ἐφηβαίου` is more specifically pubic region than the English “lower part of children’s bellies.”
- The Greek makes the adverse clause adjectival (“headache-producing”) rather than supplying a measured overdose protocol. There is no numerical dose, timing, or quantified ingredient ratio.
- The source does not explicitly say whether P1 and P2 are equal in efficacy; it only places them before the same broad result list.

## At most three global coding hypotheses

These are content mechanisms, not proposed meanings or a target-language decoder.

### H1 — compositional process bundle
A recurring material component can combine with preparation, administration/application, and result operators. P1/P2 share the material and drink/result frame while differing in boil vs. unboiled-pounding; P3–P5 reuse the material with honey, bath, or plaster and change the result class.

**Distinct consequence:** in a target paragraph with a repeated material component, branch-specific operator positions should predict changed administration/result slots; a static word equality is insufficient. **Nearest rival:** a flat catalogue whose adjacent notes happen to repeat a material. The rival does not require co-varying preparation and result roles.

### H2 — conditional state graph with polarity reversal
Encode material state → preparation state → application route → effect, with N1 as an explicit conditional edge: excess decoction + drink changes the effect to headache. The adverse branch is structurally tied to a threshold condition, not merely appended as another property.

**Distinct consequence:** a complete target record should preserve the order/attachment of a condition and a negative result, and should distinguish ordinary branches from the excess branch. **Nearest rival:** a list of independent benefits plus a detached warning; it predicts no required conditional attachment or polarity marker.

### H3 — reusable frame/operator cards
The source item may be carried by omitted/reused material context while fixed process frames express “drink,” “honey/electuary,” “sitz bath,” “plaster,” and “excess.” The same frame could recur in another entry with a different material core; a target form need not be one whole-word name.

**Distinct consequence:** cross-entry recurrence of a preparation/application frame with changed material and effect would support frame coding, whereas a static item-name analysis predicts recurrence of the same material anchor. This cross-entry comparator is not opened or tested here. **Nearest rival:** one lexical form per named preparation or one fixed plant-name token; it cannot explain frame recurrence with changed arguments without extra homonymy.

## Limits and primary predecessors

The Greek/English agreement supports the historical branch structure, not a Voynich mapping. A repeated target component, if later observed, would still need a source-frozen role and result position; no arbitrary gloss or whole-word identity is licensed. This is a stronger semantic asymmetry than plant-name/image matching because it includes alternatives, routes, and a negative conditional. A jointly fixed formal parser plus this complete source structure could nevertheless be tested exploratively before any target role has confirmed meaning; such a pass would assess a predeclared structural/content hypothesis, not certify a translation.

Primary route predecessors for the proposal remain **GDT608** (fixed component parser/formal composition), **GDT735** (Herbal paragraph/content route), and **GDT928** (complete-paragraph windows and content hypotheses). They are pointers only; this note does not reopen their decisions.

## Corrections recorded after source review

- **Edition attribution:** the downloaded UPenn PDF is Osbaldeston/Wood’s 2000 modern-English indexed edition. “Gunther/UPenn edition” was too broad; Gunther 1933 is described in its preface as the earlier Goodyer-based edition, not the PDF’s editor.
- **Cache characterization:** `dioscorides_cache/meum_1_3_excerpt.txt` contains a bounded English paraphrase and a Greek digital-transcription excerpt. It must not be cited as a verbatim English transcription.
- **Exploratory status:** absence of confirmed target roles is not an execution prohibition. A fixed parser and complete source-derived branch structure may support an explicitly exploratory test; confirmed semantic binding remains a separate gate.
