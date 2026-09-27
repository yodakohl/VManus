# Salzburg native source C: rendering erratum

The frozen Markdown report printed literal `undefined` for its first ten
per-face entries because its renderer expected a `native` field while those
JSON entries use structured fields. This is a presentation error. The
observations remained present in the frozen JSON.

Neither original file is changed:

- [Frozen JSON](SALZBURG_NATIVE_SOURCE_C.json), SHA256
  `79f53469a2323eb7d04584eaf673bffb91c2a1a00bbd4d92feb8809eb5140d7f`.
- [Frozen report](SALZBURG_NATIVE_SOURCE_C.md), SHA256
  `90165b1c53a9b36b185271447cdff970276059ee2610cb739dbb99f782c7eb85`.

The following ten complete entries are copied losslessly as JSON field names
and values from the frozen `page_notes` array, in their original order.
Whitespace is presentation only. No image was reread, no new interpretation
was inserted into these entries, and no uncertainty was resolved.

```json
[
  {
    "face": "236r",
    "central": "Saturnus named; nude bent gray-bearded man with long staff and sickle, star over groin, green ground within large ring.",
    "satellites": "Capricorn-like horned animal at left; clothed water pourer at right; banner names Capricornus and urne as Saturn's domus.",
    "lower": "Infancia label, red Metten label; two naked children with red balls in lower roundel.",
    "text": "German declares Saturn harmful to living beings; several middle words uncertain. Latin top and ribbon describe Saturn and his houses. Small bottom Latin annotation refers to inferior figure, age/state and planet, but complete syntax unread.",
    "limits": "Central old figure and lower infancy scene are different domains; no same-actor equation. No source image implies four seasons."
  },
  {
    "face": "236v",
    "central": "Iupiter named; bearded nude crowned figure, bundle of arrow/lightning-like objects and knobbed staff.",
    "satellites": "Archer and paired fish roundels; banner In Iovis domo Pisces simulque Chirona approximately readable.",
    "lower": "Puericia and red Prime; young clothed male/female figures with tablet/board-like objects and a basket.",
    "text": "German clear contrast approximately Was Saturnus übels tüt / Das bringet Iupiter ze güt, followed by Jupiter's children good/rich and holy/beautiful/personally phrased traits. Full Latin not diplomatically transcribed.",
    "limits": "Contrast is written, but no measured individual intervention or particular Saturn event repaired by Jupiter. Bottom marginal Latin partly unread."
  },
  {
    "face": "237r",
    "central": "Mars named; nude man in blue cap with spear/banner and shield, both with flame-like red motifs; star at groin.",
    "satellites": "Ram left and scorpion right; horizontal ribbon Est Aries martis ... Scorpio ... gives two houses.",
    "lower": "Age label uncertain, visually V...licias/Puerilitas?; red canonical-hour label approximately Terce. Clothed man raises club toward clothed woman, who raises hand.",
    "text": "German links Mars's evil to being in his houses, his children to angry disposition, and their shedding human blood. Approximate lines So er in sinen husen stat / Sine kint ... zornigen mut / Sy vergiessent gern menschen blut.",
    "limits": "Do not supply uncertain age from a canonical list; hostile act is depicted, but no detailed medical event or named victims."
  },
  {
    "face": "237v",
    "central": "Sol named; nude crowned man with sceptre and orb, sun-face at groin.",
    "satellites": "Lion repeated in both small satellite roundels. Ribbon approximately In leone Sol ... nec in alia hospitatur: explicit restriction to Leo, despite duplicated visual slots.",
    "lower": "Adolescencia label; red Sexte. Seated male/female at round table with drinking/serving vessels; woman holds distaff, man holds round patterned item.",
    "text": "Latin top describes Sun-born person and states Phoebus resides in Leo. German extols sun among planets and health-related effect, some words uncertain.",
    "limits": "Two lion images do not imply two distinct Sun houses. Hour and age labels remain different semantic domains."
  },
  {
    "face": "238r",
    "central": "Venus named; nude long-haired wreath-bearing woman, two-flowered stem in left hand, red rectangular mirror-like object with central disk/four corner disks in right; star at groin.",
    "satellites": "Bull and scales; ribbon names Libra and Taurus with Venus.",
    "lower": "Iuventus; hour approximately None. Young man plays string instrument; seated young woman holds leafy wreath/stem.",
    "text": "German says Venus is Jupiter holt (favourably disposed/friendly); both give a joy-related result (exact middle words uncertain); children live with dancing, pipes and string play. Latin top characterizes Venus-born and gives Taurus/Libra.",
    "limits": "Friendship/joint subject are textual, but a causal law from alliance to every child's act is not established. Flower-holder is explicitly Venus, not automatically Spring."
  },
  {
    "face": "238v",
    "central": "Mercurius named; nude youth with hat, double-headed entwined staff, hanging purse/cloth-like object and red winged feet.",
    "satellites": "Clothed seated maiden left; two nude figures right. Ribbon names twins and virgin.",
    "lower": "Senium; red Vesper. Older clothed man with beads and woman, hands in devotional/expressive positions.",
    "text": "German names houses maget und zwilling, ability to write/read, and mind full of wisdom. Latin says ... sub Mercurio generatus and qualities including Instabilis; other words uncertain.",
    "limits": "Central youthful Mercury, zodiac twins/maiden and older lower pair are distinct roles. German/Latin nuance not silently harmonized."
  },
  {
    "face": "239r",
    "central": "Luna named; nude long-haired woman holding curved horn and burning torch, crescent face at groin, small wheels under both feet.",
    "satellites": "Two matching red lobster/crab-like Cancer figures. Ribbon explicitly restricts horned Moon to Cancer alone, approximately solum cancrum inhabita.",
    "lower": "Senectus; red Complet. Elderly man in bed and a clothed woman beside him touching/gesturing near him.",
    "text": "German explicitly calls Moon moist and cold; children differently shaped, followed by sickness/old-age words with unresolved syntax. Latin gives Moon-born traits and Cancer.",
    "limits": "Same two visual satellite slots again represent one named house. Bedside woman is not labelled physician; no medical treatment inferred from pose."
  },
  {
    "face": "239v",
    "central": "Grammatica, female allegorical figure chopping standing trees with axe; felled trunks, branches and timber in foreground.",
    "lower": "Magister Priscianus labelled seated teacher at lectern/book, hand raised toward three cloud-like openings.",
    "text": "Large German stanza about grammar teaching right arrangement of words is crossed with repeated red diagonal cancellation strokes; small red replacement/additional lines above remain partly unread. Lower Latin clearly links grammar preceding the arts and failure to reach arts without the prior requirement; exact middle wording uncertain.",
    "limits": "Cancellation and replacement must remain separate witnesses/states; do not treat every large cancelled line as current accepted text. Wood preparation is visible; full building/learning analogy awaits remaining art pages."
  },
  {
    "face": "240r",
    "central": "Retorica, female figure using broad axe/adze to work a long rough timber resting on supports; cut-off irregular strips visible, two trees behind.",
    "lower": "Magister Tullius seated with open book at lectern, three cloud-like forms above.",
    "text": "German says Rhetorica works/colours speech, removes the rough (das grop hin dan), and teaches words/meaning; two Roman-number groups are present but not securely transcribed. Latin concerns ratio dicendi and flore loquendi; full syntax uncertain.",
    "limits": "Pruning/shaping image has a textual speech-work counterpart. No certainty that every visible piece is the identical tree from previous page."
  },
  {
    "face": "240v",
    "central": "Loyca, woman with large two-handled auger drilling a wooden hub-like piece; three curved wooden segments with holes lie nearby.",
    "lower": "Magister Aristoteles, seated teacher with open book, raised finger, three cloud-like forms.",
    "text": "German explicitly concerns whether speech is true or false (Ob wor/falsch ... rede) and words/names; a comparison involving a wheel/rim-like object is partly unread. Latin says sisters/teachers work in vain without her and distinguishes truth from falsehood, with exact phrase uncertain.",
    "limits": "Truth discrimination is not equivalent to rhetorical ornament. Auger/hub interpretation is visual, not an exact restored technical noun."
  }
]
```

## Reading differences retained without harmonization

The root's later communication reports **237r Virilitas/None**. C's frozen
entry remains uncertain about the age and provisionally reads the hour as
Terce. For **238r**, root reports Tercie, while C's entry says approximately
None. These are disputed native readings, not silently corrected results.
Neither dispute affects the two Latin art clauses underlying IDEA592. No
reread or external edition was requested or used for this erratum.

## Prospective source-only assessment of IDEA592

The frozen source supports **two distinct uses of a negative-prerequisite
argument**, beyond repeating figure names:

1. Grammar's `Qui nescit partes / frustra tendit ad artes` connects a person's
   lack of knowledge of partes, that same person's pursuit of arts, and a
   stated futility consequence.
2. Logic's `Frustra doctores sine me coluere sorores` makes the doctors the
   actors cultivating the sisters, identifies the omitted resource through
   the figure-bound me, and again states futility.

The repeated structure is absence or ignorance of a prerequisite during an
attempted intellectual activity, with an explicit adverse outcome. The
arguments vary: generic learner versus doctors, not knowing partes versus
without Logic, pursuit of arts versus cultivation of sister arts. Moving me
to the lower master or exchanging the omitted resource changes a written
argument. Thus this source supplies more than two labeled figures.

The scope is limited. Partes as grammatical components and sorores as the
other arts remain context-supported interpretations. These are rhetorical
claims, not two observed controlled input/output cases, and their occurrence
in one illustrated program is not independent attestation. Neither clause
states that possession of the prerequisite guarantees success. The whole
woodworking/wagon sequence does not prove one continuously tracked physical
object or an explicit causal theory of learning. IDEA553 already retains
necessity and IDEA538 speaker binding;592's contribution is this particular
repeated source instantiation with distinct argument ownership, not a claim
of a new primitive or certified novelty.

**Prospective decision:** retain592 as a useful unreviewed source-content
option. It has two actual written dependency uses, with the limits above.
No target test, selection, new card, registry review or reopening follows.

## Mechanical receipt

Started2026-09-27 08:38:39 UTC; bounded5-minute correction. Original JSON and
report hashes were checked before and after writing. Parsing the copied JSON
block reproduces exactly the original first ten entries, including every
field name, value and uncertainty. No image access, source fetch, CLI action,
ledger/state/route/Git mutation occurred.

Frozen 2026-09-27T08:39:37.998901+00:00.
