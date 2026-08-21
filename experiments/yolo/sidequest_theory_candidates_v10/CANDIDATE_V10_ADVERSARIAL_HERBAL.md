# V10 adversarial Herbal candidate: exemplar-copied abbreviated prose

Date: 2026-08-21

Status: **independent speculative sidequest candidate; not a GDT result, not a
translation, and not a plant identification**.

## Isolation and scope

This pass read only the compact current route, the compact ten-page theory, the
frozen V10 protocol, guarded slices of GDT276/GDT327, the two target images and
historical comparator descriptions. It did not open or read another V10
candidate. A repository-wide source-location grep did incidentally print a few
isolated matching lines from concurrently written V10 files; those fragments
were ignored and were not used to construct or score this candidate.
The target pages are `f10r` and `f56r`; `f11r` and `f55v` are controls. No
`f84` or `f84r` material was requested, opened or used.

The guarded extraction was:

```text
./vmanus-exp query-tsv gdt276_event_inventory.tsv
  --selector page
  --allow f10r --allow f56r --allow f11r --allow f55v
  --columns [explicit observation/form/layout columns]
  --forbid-prefix f84

./vmanus-exp query-tsv gdt327_joint_tuple_interlinear.tsv
  --selector page
  --allow f10r --allow f56r --allow f11r --allow f55v
  --columns [explicit opaque tuple/layout columns]
  --forbid-prefix f84
```

Both guarded calls selected exactly 100 events and skipped 8,348 unrequested
events. Tuple IDs below are shortened display names for exact GDT327 IDs.

## Forced winner

The strongest adversarial account is:

```text
EXEMPLAR ARTICLE
  ordinary Herbal/encyclopedic prose, probably formulaic and abbreviated
        ↓ copied or adapted independently of the local picture geometry
PICTURE AND TEXT
  two parallel descendants of an entry in a source exemplar
        ↓ image was placed first on this particular leaf
SCRIBAL REFLOW
  prose was fitted into the remaining space around the drawing
        ↓ local shorthand and workshop spelling/rendering
VISIBLE VOYNICH GROUPS
```

In this model the drawing is the page topic but is **not a silent database row
whose visible organs supply missing operands**. The text need not have been
composed by looking at this drawing. Both can descend from an inherited Herbal
article, and text can have been written after the image was drawn.

The underlying article may still mention a plant's names, description,
qualities, habitat, preparation and uses. The adversarial claim is narrower:
the visible sequence is better treated as highly abbreviated continuous prose
than as a card-filled medical form. A recurrent exact tuple can therefore be a
common word or conventional abbreviation; a rare exact tuple can be ordinary
content vocabulary. Neither needs to be a database code.

## Why this rival is strong

The two target pages contain 65 scored events but 42 exact tuple types. Thirty-
two of those types are singletons within the target pair. Each target page also
has a large page-local tail:

| page | events | exact types | singleton types | repeated-type events | attached DY/B3 |
|---|---:|---:|---:|---:|---:|
| f10r | 38 | 25 | 19 | 19 | 0 / 0 |
| f56r | 27 | 21 | 17 | 10 | 1 / 0 |
| f11r control | 17 | 15 | 14 | 3 | 1 / 0 |
| f55v control | 18 | 16 | 15 | 3 | 2 / 1 |

Every scored Herbal-A physical line is one open field. f10r has no attached
DY/B3 close in any of its five scored lines; f56r has one DY close in seven.
This is the opposite of the short committed-cell ecology that motivated the
Biological form interpretation. It is exactly what line-wrapped prose can look
like after a later parser calls each uninterrupted line a field.

The line openings do not reveal one demonstrated page name. All five f10r
scored lines begin with different exact tuples. The seven f56r openings contain
one repeated local `CHO/SHO` tuple, but otherwise vary. Line endings vary too.
That weakens a fixed row stencil and supports discourse whose clause boundaries
need not coincide with physical lines.

Only four exact types cross directly between f10r and f56r. Those four are
ordinary candidates for shared grammatical or high-frequency technical
vocabulary, not page owners:

| exact tuple | target occurrences | surfaces | structural reading only |
|---|---:|---|---|
| `2f1c5e56...` | 5 | `daiin/taiin` | mobile AIIN card |
| `10488b91...` | 2 | `qotchor/otchor` | cross-page content/function card |
| `276a7c2d...` | 3 | `oky/choky` | cross-page content/function card |
| `9ad66e67...` | 3 | `qokchy/okchy/chokchy` | cross-page content/function card |

None occurs exactly once in the privileged heading position of both pages.

## Complete exact-card accounting

### f10r: 38 events

```text
f10r.2  dchey[65f320e7] cthoor[dedc383b] char[4d455901]
         chty[80ebbbbf] os[df109883] chair[12efe866]
         otytchol[62ff0597] oky[276a7c2d] daiin[2f1c5e56]
         etyd[a6939862]

f10r.5  qokchy[9ad66e67] qotchol[e8a6105b] chol[dcda95c8]
         cthy[e0b630cb]

f10r.6  ycheor[7249edc4] cthy[e0b630cb] chor[7a4bb813]
         cthaiin[f3c23f42] qoctholy[af816c04] dy[b921a237]
         chy[b921a237] taiin[2f1c5e56] shy[b921a237]

f10r.8  qotchor[10488b91] chor[7a4bb813] otol[497cbd9c]
         chol[dcda95c8] cholor[dec40177] chol[dcda95c8]
         daiin[2f1c5e56] dar[4d455901]

f10r.9  oykchor[27d97af8] shor[7a4bb813] chor[7a4bb813]
         chy[b921a237] kaiiin[409de023] dy[b921a237]
         chodaiin[834825c6]
```

The important fact is not the similar-looking strings but the exact tuple
ecology: f10r has a reusable middle deck (`AIIN`, `Y`, `OR`, `CHOL`, `CTHY`)
embedded in nineteen singleton events. In an ordinary-prose account those can
be function/technical words among page-specific content. Their meanings remain
unassigned.

### f56r: 27 events

```text
f56r.5   chochor[b9d7b6d6] cho[2cc05435]
          chodaly[0ec6a45e] daiin[2f1c5e56]
f56r.7   sho[2cc05435] kchol[893c570f] otchor[10488b91]
          choky[276a7c2d] dal[dd0ecaf5]
f56r.8   schol[d665560c] choy[c10aec6d] choky[276a7c2d]
          cheeckhody[95987d6f]
f56r.12  sh[ad3581d3] cho[2cc05435] kchey[b74e9e65]
          qokokchy[1322bc17]
f56r.13  okchy[9ad66e67] chokcheo[087a47b5] kchal[75a523fc]
f56r.18  sho[2cc05435] chokchy[9ad66e67] kchoar[c71c72da]
          sotodan[61a075bc]
f56r.19  otchey[faf32194] keol[9bb7122b] daiin[2f1c5e56]
```

f56r has one strong page-local recurrent tuple, `2cc05435...` (`CHO/SHO`), at
four occurrences. It moves between line entry and interior, so it is not yet a
page title or a visible-organ label. Seventeen of 21 exact types are singletons.

### Fixed Herbal controls: 35 events

```text
f11r.1  tshol[953ad19b] schoal[428a5e36] cfhy[bdad9f9e]
         shfydaiin[a8af08e6] cphy[deb37738] shey[b5df9126]
         tchody[2e2027b1] shoyty[577c03a9]
f11r.4  dchol[d665560c] chy[b921a237] kchy[b2812c82]
         dy[b921a237] daiin[2f1c5e56]
f11r.7  qotchy[a48efd6c] okchol[322281bd] cthy[e0b630cb]
         dy[b921a237]

f55v.5  qokaiin[b5fcea1e] chaiin[2f1c5e56] ykain[403c1592]
         ykan[d929a14e] ody[97cc9ac1] daiin[2f1c5e56]
         chedy[6f7ff828] talam[e026af58]
f55v.11 ykaiin[f7dc90b2] cheoar[807591ef] cheeky[2c1a5fd9]
         oldy[1b1ffdd8] aiin[2f1c5e56] okal[308e8ea2]
         oltchy[204b0483] or[7a4bb813] y[b921a237]
         orain[6afeb5c9]
```

The controls are even more singleton-rich: 27/29 types occur once in their
35-event panel. The few transfers are the same portable deck already known
from the compact theory. This does not look like a four-page inventory of
shared plant-part or habitat codes.

### Exhaustive recurrent-type reconciliation

Across all 100 events, every repeated exact type is accounted for here:

| tuple | n | pages | placement summary |
|---|---:|---|---|
| `2f1c5e56...` | 9 | all four | FIRST 2 / MIDDLE 4 / LAST 3 |
| `b921a237...` | 9 | f10r,f11r,f55v | MIDDLE 7 / LAST 2 |
| `7a4bb813...` | 5 | f10r,f55v | MIDDLE 5 |
| `2cc05435...` | 4 | f56r | FIRST 2 / MIDDLE 2 |
| `276a7c2d...` | 3 | f10r,f56r | MIDDLE 3 |
| `9ad66e67...` | 3 | f10r,f56r | FIRST 2 / MIDDLE 1 |
| `dcda95c8...` | 3 | f10r | MIDDLE 3 |
| `e0b630cb...` | 3 | f10r,f11r | MIDDLE 2 / LAST 1 |
| `4d455901...` | 2 | f10r | MIDDLE 1 / LAST 1 |
| `10488b91...` | 2 | f10r,f56r | FIRST 1 / MIDDLE 1 |
| `d665560c...` | 2 | f11r,f56r | FIRST 2 |

The remaining 55 events are singleton exact types. This gives a complete
100-event reconciliation without invoking spelling or substring similarity.

## Image audit and the water/habitat fork

The f10r image shows one plant with a tall stem, paired broad serrated/banded
leaves, flower-like structures and two dark swollen basal bodies joined by a
horizontal root-like structure. f56r shows one highly stylized plant with dark
radial/spiny heads, a very large spiral-centred radial structure and two smaller
dark heads. These descriptions deliberately stop before species names.

Nothing on either page visibly depicts a stream, pool, vessel, rain, irrigation
or an unambiguous aquatic organ. A basal swelling can be a root, tuber, fruit,
copying distortion or emblematic invention. A spiral/radial disk can be a
flower head or schematic pattern. Therefore:

```text
HABITAT/MOISTURE = historically plausible article content
WATER            = not independently pictured or localized
```

The text's accommodation to the drawings is layout evidence only. It does not
assign the interrupted phrase to the leaf, flower, root or water. In the
adversarial model, the image was put down first and prose was then reflowed
around it, exactly as the user-supplied production order allows.

## Historical comparators

The comparators favor prose articles much more strongly than a four-column
technical checklist:

1. The University of Pennsylvania catalogue for fifteenth-century northern
   Italian **LJS 419** describes an illustrated herbal whose notes concern
   medicinal properties and preparations and are written around, and sometimes
   over, illustrations. It also records multiple illustration styles and later
   additions. This is a direct historical mechanism for independent textual
   prose plus image-sensitive reflow:
   <https://openn.library.upenn.edu/Data/0001/html/ljs419.html>.
2. The British Library identifies **Sloane MS 4016**, c. 1440, as a north
   Italian Herbal copied from MS Masson 116, with full-page plant miniatures and
   captions. Copying an inherited text-image tradition is therefore ordinary,
   not an exotic explanation:
   <https://searcharchives.bl.uk/catalog/040-002116409>.
3. The scholarly Herbaria manuscripta database defines medieval simple-medicine
   entries by the medicine they treat and explicitly unifies variant spellings
   under one medieval name. Fifteenth-century Bohemian herbals combine entries,
   glosses and vernacular or Latin names:
   <https://herbaria.phil.muni.cz/en/help>.
4. The edited Lelamour Herbal is described as following a repeated entry
   pattern: Latin name, vernacular synonyms, morphology and habitat. This
   supplies a concrete source order for a prose entry without implying that
   Voynich has English or Latin words:
   <https://www.peterlang.com/document/1056214>.
5. The Wellcome catalogue describes a c. 1475 Herbal with medicinal plant names
   and short receipts for their use, illustrated in watercolour. This is a
   useful compact control for name plus practical prose:
   <https://wellcomecollection.org/works/kjxqdfr6>.
6. A true scribal pattern book, Beinecke MS 439, contains alphabets, sample
   scripts and decorative initials arranged alphabetically. Its observable
   organization is unlike two long prose blocks fitted around one plant:
   <https://beinecke.library.yale.edu/collections/highlights/medieval-scribal-pattern-book>.

These sources support a production family, not Voynich geography, language,
species, plaintext or direct descent.

## Model competition

The following scores are forced abductive judgments under the V10 rubric, not
probabilities:

| rival | score / 100 | decision |
|---|---:|---|
| exemplar-copied abbreviated Herbal prose | 91 | **winner** |
| medical formula/checklist with picture-supplied fields | 81 | live main-theory rival |
| mixed prose heading + technical recipe tail | 78 | plausible, but no boundary identifies the switch |
| plant-name/synonym list | 62 | plausible only as an article head |
| nonsemantic index/nomenclator | 54 | lacks visible key/value layout and stable page key |
| visual exemplar/pattern book | 47 | image tradition plausible; text ecology wrong |
| graphic/cryptographic code independent of prose | 44 | structurally possible but adds an unnecessary mechanism |

### Why the alternatives lose

- **Plant-name/synonym list:** medieval glossaries exist, but they are compact
  lists or entry-head material. Twelve and nineteen lines around a single image
  are excessive, and no exact tuple is demonstrated as the once-per-page name.
- **Index/nomenclator:** there is no visible number, alphabetic ordering,
  columnar equivalence or recurrent page-key slot on these two leaves.
- **Pattern book:** copied plant exemplars explain stylization, but surviving
  scribal model books advertise scripts, alphabets or motifs. They do not by
  themselves predict sustained lexical-looking prose around each plant.
- **Graphic/cryptographic code:** a code can reproduce any opaque sequence but
  currently explains neither the local singleton tail nor the historical
  article shape better than abbreviated language.
- **Medical form:** it remains strong at manuscript scale, especially in Bio,
  but Herbal-A lacks the short cells and repeated attached commits that made
  that model concrete. Importing Bio's form architecture here is optional, not
  compelled.

## Controlled consecutive pseudo-translation

This is a source-class paraphrase of f10r's first five-line paragraph, not a
word alignment:

> **[Entry heading:]** The simple shown here, under its inherited name and
> local names. **[Description:]** distinguish it by its principal visible or
> conventional features. **[Quality/habitat clause:]** record its customary
> class or place of occurrence. **[Use clause:]** state the first preparation
> or application and its condition. **[Close:]** finish this short article
> unit before continuing with the second block of properties or uses.

Provenance of that paraphrase:

| phrase | basis | status |
|---|---|---|
| entry for one simple | one full-page plant plus historical herbal article | picture/history |
| name/local names | common comparator entry head | speculation |
| description | common comparator component | speculation |
| quality/habitat | common comparator component | speculation |
| preparation/application | common comparator component | speculation |
| first versus second block | two visible f10r paragraphs | layout |

No line is assigned one of these functions. The paragraph can distribute them
in another order, repeat one, or omit several. The point is that one continuous
historical article can generate the amount of text without a technical card
form.

A stricter exact-card paraphrase of the fully scored f10r.2 line is:

> Continue the first article with **[opaque content] [opaque content]
> [relation/content] [property/content] [opaque content] [relation/content]
> [opaque compound] [shared technical/function item] [current/reference item]
> [opaque clause-final item]**.

That sounds less useful precisely because 8/10 exact cards on the line have no
current functional assignment. The adversarial model refuses to turn them into
form slots merely to create fluency.

For f56r, the best complete-record source class is similarly broad:

> Give the illustrated simple's inherited designation and distinctions;
> describe its conspicuous structures; state one or more customary qualities,
> environments or collection conditions; then enumerate preparations or uses.

The large radial drawing does not license SUN, WATER, flower, eye or a named
drug. Those are alternative expansions of an opaque content noun.

## Hard contradictions

1. **No recovered syntax.** High singleton density is compatible with prose but
   does not prove it. Voynich's low-level distributions can arise from other
   generators.
2. **No page lemma.** A copied Herbal article normally has an identifying name;
   the current exact-card slice has not located one.
3. **No sentence boundaries.** Prose predicts clauses, but physical lines and
   DY/B3 do not yet provide reliable Herbal-A sentence punctuation.
4. **Exact cards are not demonstrated words.** The model makes the source level
   language-like without claiming one visible group equals one source word.
5. **f55v is more closure-rich.** Hand/register variation can explain this, but
   a true shared prose system must explain why the B page looks more cellular.
6. **The pictures are strange.** Exemplar drift can explain stylization but not
   every deliberate composite structure. A nonbotanical diagrammatic reading
   remains possible.
7. **Medical content is inherited, not observed.** The page class and historical
   comparisons motivate materia medica; none of the 65 target events proves a
   cure, dose, action, water or disease.

## Fixed-page predictions

The prose model should lose if any of the following is established within the
already fixed pages:

1. a small set of opaque exact tuples occupies the same field/card slots across
   f10r, f11r, f55v and f56r with slot stability stronger than their ordinary
   line-placement frequencies;
2. page-local exact identities recur as stable leaf/root/flower/habitat values
   at homologous image-owned positions rather than behaving as ordinary local
   vocabulary;
3. full Herbal-A records decompose into the same short committed-cell stencil
   as Biological records after drawing interruptions are accounted for;
4. an exact once-per-page tuple can be localized independently as the pictured
   plant's owner/key on multiple fixed Herbal pages;
5. the local singleton tail is largely generated by a small auditable value
   table rather than by freely varying clause content.

Predictions favoring the prose rival:

1. newly reconciled groups on the same four pages should expand the local tail
   more than the small shared deck;
2. recurrent portable cards should remain mobile inside clauses rather than
   lock to one universal field ordinal;
3. exact page-specific types should recur mainly within the same article or
   closely related content, not across every Herbal record;
4. line length and interruption should follow available space around the image,
   while logical continuation crosses physical lines;
5. no dedicated WATER card should emerge from these four pages unless habitat
   is independently annotated outside the strings.

## Bottom line

The strongest adversarial reading is not a nomenclator, a pattern book or an
independent cipher. It is **an inherited illustrated Herbal article compressed
by workshop abbreviation and reflowed around a previously drawn image**.

This model naturally produces a small recurrent grammatical/technical deck, a
large page-local lexical tail, mobile recurrent forms and long mostly open
Herbal-A lines. It permits names, synonyms, qualities, habitat, preparation and
uses, but assigns none to an exact tuple. It is currently a stronger explanation
of f10r/f56r alone than the image-owned checklist, while the checklist remains
stronger for the Biological register. The best manuscript-wide synthesis may
therefore require register-specific source organization rather than one form
grammar imposed on all sections.
