# GDT621 final source double-reading result

Status: `SOURCE_DOUBLE_READING_COMPLETE__TARGET_UNOPENED`

## Outcome

The five Latin scoring pages and five Clm locator controls form five real,
manually verified source pairs. The Latin side was frozen publicly in commit
`2ab45096cc2a46fc59f5bf50aa3be12cde022e25` before any Clm control opened.
The later Clm reader found all five expected labels and made no change to the
frozen Latin. No Voynich target, f84, or f84r was opened.

| ID | Frozen Latin rubric | Independent Clm label | Contextually corrected content of the same twelve-token opening |
| --- | --- | --- | --- |
| DEV01 | `De balſamo. ſiū opobalſamo. Rx.` | `Balsamꝰ.` | balsam/opobalsam; some call it a tree, but it is more truly a shrub |
| DEV02 | `De cerofolio. Rx.` | `Cerfolium.` | chervil; a familiar herb frequently used by cooks |
| DEV03 | `De liquiricia.` | `Liquiritia.` | liquorice; warm and moist in degree one; the root of a particular plant |
| DEV04 | `De Cucurbita. Rx.` | `Cucurbita.` | cucurbita, pumpkin/gourd; cold and moist in degree two, according to Isaac; cultivated and eaten |
| DEV05 | `De Diptamo. Rx.` | `Diptamus.` | dittany; warm and dry in degree three; another name follows |

The Clm observations also visually locate the entries: balsam is a labelled
tree inside a crenellated enclosure; chervil is a tall, finely divided plant;
liquorice is labelled beneath a broad-leaved specimen's root network;
cucurbita is labelled beside a large dark fruit on a vine; and dittany is a
labelled flowering plant with branching roots.

## Post-checkpoint contextual correction

The public checkpoint remains immutable, but subsequent full-context manual
reading and historical-source comparison exposed several palaeographic errors
in its provisional twelve-token layer. These corrections do not come from Clm
and do not alter the canonical result payload. They are the current readable
expansions of the same visible openings:

1. `Balsamus arbor est ut quidam dicunt, vel frutex, quod verius est,
   attestante …` — “Balsam is a tree, as some say, or rather a shrub, which is
   more correct, as … attests.” The frozen `in fructu ... interius` sequence was
   a misreading of `vel frutex ... verius`.
2. `Cerfolium herba est satis nota, qua frequenter utitur in coquis. Usus
   cerfolii …` — “Chervil is a sufficiently familiar herb, frequently used by
   cooks. The use of chervil …”. Direct reinspection confirms the checkpoint's
   `coquis`; the preceding abbreviation expands to `in`.
3. `Liquiritia calida est et humida in primo gradu. Est autem radix cuiusdam …`
   — “Liquorice is warm and moist in the first degree. It is the root of a
   certain …”; read `radix cuiusdam`, not frozen `maior cum`.
4. `Cucurbita frigida est et humida in secundo gradu, teste Ysaac. Colitur
   autem …` — “Cucurbita is cold and moist in the second degree, according to
   Isaac. It is cultivated …”; read `teste Ysaac` and `Colitur autem`, not
   frozen `debet esse` and `Colatur aut`.
5. `Diptamus sive diptamum calidum est et siccum in tertio gradu, quod alio …`
   — “Dittany, or *diptamum*, is warm and dry in the third degree, which by
   another …”. Direct reinspection resolves the final abbreviation as `quod`,
   not the checkpoint's `et`; the sentence continues with another name.

This correction is substantive: DEV01 encodes a tree-versus-shrub judgment,
DEV03 identifies the medicinal part as a root, and DEV04 names Isaac as the
authority. It also demonstrates that twelve isolated words were too narrow for
reliable palaeographic resolution; future manual readings must use the full
sentence context while preserving the originally frozen evidence separately.

The corrections were checked on the original BnF images for
[Balsamus](https://gallica.bnf.fr/ark:/12148/btv1b6000517p/f58.image),
[Cerfolium](https://gallica.bnf.fr/ark:/12148/btv1b6000517p/f96.image),
[Liquiritia](https://gallica.bnf.fr/ark:/12148/btv1b6000517p/f178.image),
[Cucurbita](https://gallica.bnf.fr/ark:/12148/btv1b6000517p/f91.image), and
[Diptamus](https://gallica.bnf.fr/ark:/12148/btv1b6000517p/f122.image). External
comparison identifies the codex as Manfredus de Monte Imperiali's Pisa
`Liber/Tractatus de herbis et plantis` of about 1330–1340, an expanded
*Tractatus de herbis* compilation built principally on *Circa instans* with
other sources. See the [Biblissima manuscript
description](https://iiif.biblissima.fr/collections/manifest/d1a397a91c342e195a1dacd635a34fe1392b00c2)
and [Ventura's critical-edition
record](https://cris.unibo.it/handle/11585/628097). This source-family
identification is a post-checkpoint historical interpretation, not an input to
the isolated readings.

## The usable semantic template

The result supplies a small but concrete source grammar rather than a generic
recipe paraphrase:

> **plant identity** + **is** + **hot/cold** + **and** + **moist/dry** +
> **in** + **ordinal degree**

DEV03–DEV05 instantiate three different values in that same frame:

- liquorice = hot + moist + degree 1;
- cucurbita = cold + moist + degree 2;
- dittany = hot + dry + degree 3.

The other two entries add different content slots: a tree-versus-shrub
classification for balsam, and familiar-herb plus culinary use for chervil. These are now the
minimum concrete distinctions a later target model has to recover. A gloss such
as “take material, perform work, pass it onward” does not encode them and is not
an acceptable translation.

## Control integrity

The five Clm pages opened between `2026-08-29T09:16:52Z` and
`2026-08-29T09:18:09.423176629Z`, strictly after the checkpoint commit time
`2026-08-29T09:15:05Z`. The controller viewed each full page first, used no OCR
or automatic recognition, captured only the visible locator label and notes,
and did not transcribe running text. The controller accessed no Latin JPEG,
catalog, edition, network source, other agent, repository, Voynich target, f84,
or f84r.

The final result retains byte-identical copies of the checkpoint's two raw
bundle commitments, five reconciled readings, and 63-row difference ledger.
Its access audit contains the ten original Latin events followed by the five
Clm events, with all target, Voynich, f84, and f84r counts equal to zero.

## Claim boundary and next use

This completes the source-reading gate; it does not yet decode a Voynich word.
The next useful step is to turn the three repeated quality statements into an
exact slot template and obtain the remaining independent illustrated-witness
views needed for target-facing picture matching. Only after that source packet
is fixed should candidate Voynich folios be paired. The first target test must
then predict the held plant identity and these explicit quality/degree values,
not merely fit word shapes after seeing them.
