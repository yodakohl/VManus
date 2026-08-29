# GDT621 Latin reconciliation checkpoint

Status: `LATIN_RECONCILIATION_FROZEN__CLM_UNOPENED`

## Result

Two isolated readers independently read the rubric and first twelve running
tokens on each of the five registered Latin pages. A third isolated reader
then reconciled every recorded difference against only the two frozen bundles
and the same five Latin JPEGs. The checkpoint contains five reconciled
readings and 63 explicit difference rows. No Clm control page, Voynich target,
catalog, edition, OCR, network source, f84, or f84r was used.

The canonical raw-bundle commitments are:

- Reader A: `c510b732b236cdb44454f8965a82e4df1ab0d5276630d6b99e1e237b7d2b4136`
- Reader B: `a1400636cbe86855c6725751c6930363355f3fc2770acce76be81b693d04c512`
- Reconciliation checkpoint: `4b56894b3046e7fd4b1695ff81a381022a72bb81f6fd4a8caf1203a54ef27905`

The following expansions and German renderings are a readable working layer,
not changes to the frozen diplomatic text. Square brackets mark an expansion
or a continuation that remains uncertain. Each passage stops after exactly the
registered twelve running tokens, even where that cuts a sentence in half.

## Reconciled passages and concrete reading

### DEV01 — balsam

Diplomatic:

> De balſamo. ſiu<SIGN:OVERBAR> opobalſamo. Rx.
> Balſamus arbor eſt ut <UNCERTAIN:qđi> dicunt in fructu q<SIGN:OVERBAR> i<SIGN:OVERBAR>terius eſt <UNCERTAIN:atteſtante>

Working expansion:

> De balsamo, sive opobalsamo. Recipe. Balsamus arbor est, ut [quidam]
> dicunt, in fructu qui interius est [atteſtante …]

German working translation:

> Über Balsam, oder Opobalsam. Nimm. Balsam ist ein Baum; wie manche
> sagen, [liegt/es befindet sich] in der Frucht, die innen ist …

Concrete content retained without the uncertain ending: the entry is about
balsam/opobalsam, calls balsam a tree, and discusses the inside of its fruit.

### DEV02 — chervil

Diplomatic:

> De cerofolio. Rx.
> Cerfoliu<SIGN:OVERBAR> h<SIGN:ABBREVIATION-STROKE>ba e<SIGN:OVERBAR> ſatis nota q<SIGN:ABBREVIATION-STROKE> frequenter utitur i<SIGN:ABBREVIATION-STROKE> coquis. <UNCERTAIN:Vſus.> <UNCERTAIN:cerofolii>

Working expansion:

> De cerofolio. Recipe. Cerfolium herba est satis nota, qua[e]
> frequenter utitur in coquis. [Usus] cerofolii …

German working translation:

> Über Kerbel. Nimm. Kerbel ist ein hinreichend bekanntes Kraut, das
> häufig beim Kochen/in Speisen verwendet wird. Der Gebrauch des Kerbels …

The syntax around abbreviated `q…` and `utitur` still needs the parallel
witness, but the plant, `herba`, familiarity, frequency, and culinary context
are already explicit.

### DEV03 — liquorice

Diplomatic:

> De <UNCERTAIN:liquiricia>.
> <UNCERTAIN:Liquiricia>. ca. e<SIGN:OVERBAR> 7 hu. i. p<SIGN:SUPERSCRIPT-MO>. g<SIGN:OVERBAR>. E<SIGN:OVERBAR> aut maior cum

Working expansion:

> De liquiritia. Liquiritia calida est et humida in primo gradu. Est
> autem maior cum …

German working translation:

> Über Süßholz. Süßholz ist warm und feucht im ersten Grad. Es ist aber
> größer/stärker, wenn …

The first sentence is a concrete medieval quality classification: plant,
warmth, moisture, and first degree. The following comparison is cut off.

### DEV04 — cucurbita

Diplomatic:

> De Cucurbita. Rx.
> Cucurbita. frigida e<SIGN:OVERBAR> 7 hu. i. <UNCERTAIN:ij<SIGN:SUPERSCRIPT-O>.> gradu debet eſſe. Colatur aut

Working expansion:

> De cucurbita. Recipe. Cucurbita frigida est et humida in secundo gradu
> debet esse. Colatur autem …

German working translation:

> Über Cucurbita, also Kürbis/Gurke. Nimm. Cucurbita ist kalt und feucht
> im zweiten Grad, wie sie sein soll. Sie werde angebaut / Man seihe sie
> aber …

`Colatur` remains genuinely ambiguous between a form of *colere* (cultivate)
and recipe Latin related to straining. The preceding classification—cold,
moist, second degree—is not ambiguous.

### DEV05 — dittany

Diplomatic:

> De Diptamo. Rx.
> Diptamus. ſiu<SIGN:OVERBAR> <UNCERTAIN:diptam<SIGN:OVERBAR>.> calid<SIGN:OVERBAR> e<SIGN:OVERBAR> 7 ſic. i. <UNCERTAIN:tto.> g<SIGN:OVERBAR>. 7 alio

Working expansion:

> De diptamo. Recipe. Diptamus sive diptamum calidum est et siccum in
> tertio gradu et alio …

German working translation:

> Über Diptam. Nimm. Diptam, oder *diptamum*, ist warm und trocken im
> dritten Grad und in anderer …

This preserves four concrete anchors before the cut: dittany, warmth,
dryness, and third degree.

## What is now fixed, and what is not

The checkpoint fixes visible Latin letterforms and all recorded disagreements;
the later Clm control cannot change them. It gives five independent semantic
anchors: Balsam, Kerbel, Süßholz, Cucurbita, and Diptam. It also gives a
repeated miniature grammar in which a named plant is followed by
`calida/frigida`, `humida/sicca`, and an ordinal `gradu`. That is the concrete
structure to seek in the paired witness and only afterward in a still-unopened
Voynich target.

This checkpoint does **not** translate a Voynich token. It eliminates the
previous generic-action shortcut: any later target interpretation must recover
specific plant identity or at least the explicit hot/cold, moist/dry, and
degree contrasts on held pages. A reading that says only “take material,
process it, pass it onward” will not satisfy that requirement.

## Validation and access boundary

Both raw files, the reconciled file, bundle hashes, five-page order,
twelve-token counts, source hashes, session separation, canonical JSON bytes,
63-row ledger, reconciliation timestamps, and zero-access attestations pass the
offline checkpoint validator. Its 69 in-memory mutation tests also pass.

The ten Latin view events attest full-page-first manual reading, no OCR or
automation, no catalog/edition/network/profile/repository access, and no access
to the other reader's material. The adjudicator attests that only both frozen
bundles and the five Latin JPEGs were used. All Clm, Voynich, target, f84, and
f84r access counts remain zero at this checkpoint.
