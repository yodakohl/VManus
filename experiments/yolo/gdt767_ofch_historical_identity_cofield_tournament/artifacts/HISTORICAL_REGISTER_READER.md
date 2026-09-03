# GDT767 historical identity and co-field reader

The closest historical model is a mixed pharmacy record: a learned whole name, an optional part or preparation form, quality/state and degree fields; recipes add an opening formula, ingredient, amount, process and result. This is an architecture bridge, not a spelling equation.

## Target-excluding result

The 25 observed OFCH-containing wholes contribute 43 exact positions. After blocking every target whole, pchor and all 172 GDT754 source-composed surfaces, independent OFCH contacts are: DRY 4/10/14, MOIST 3/6/13, STAGE 8/21/29, VALUE/AMOUNT 5/9/11, PREP 0/6/8. Exact cthy and exact chor identity anchors are both 0/0/0.

That supports drug/preparation and state/form classes. It does not independently select flower, seed, root, leaf, wood, resin, salt, oil, water, wine or vinegar.

## Working dictionary

| whole | n | portable class | forced concrete default | form evidence | identity confidence |
|---|---:|---|---|---|---|
| `chofchdy` | 1 | zusammengesetzte Arzneizubereitung; target-freie Kontextklasse Arzneiform offen | Blütenmischung im Zwischenzustand | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `chofchol` | 1 | Trockenmaterial oder Trockenbereitung; target-freie Kontextklasse Arzneiform offen | getrocknete Blütenmischung | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `chofchy` | 1 | zusammengesetzte Arzneizubereitung; target-freie Kontextklasse Zubereitung | Blütenmischung | `F04:2` | `C0_REPLACEABLE_DEFAULT` |
| `chor` | 176 | anderer oder reproduktiver Pflanzenteilposten; nicht Blattgut | Blütenstand | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `lchor` | 2 | internes Drogen- oder Zubereitungsfeld | Blütenzubereitung | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `ofchar` | 2 | Drogenportion oder Drogenanteil; target-freie Kontextklasse getrocknete Droge | Blütenanteil | `F02:2` | `C0_REPLACEABLE_DEFAULT` |
| `ofchdy` | 4 | benannter Drogen- oder Pflanzenteilkopf; target-freie Kontextklasse Zubereitung | aufbereitete Blütendroge | `F04:4` | `C0_REPLACEABLE_DEFAULT` |
| `ofcheds` | 1 | Endprodukt oder Abschlusszubereitung einer Droge; target-freie Kontextklasse Zubereitung | fertige Blütenzubereitung | `F04:2` | `C0_REPLACEABLE_DEFAULT` |
| `ofchedy` | 5 | Trockenmaterial oder Trockenbereitung; target-freie Kontextklasse getrocknete Droge | vollständig getrocknete Blütenmasse | `F02:2` | `C0_REPLACEABLE_DEFAULT` |
| `ofcheefar` | 1 | Drogenportion oder Drogenanteil; target-freie Kontextklasse Arzneiform offen | abgemessene Blütendosis | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `ofcheol` | 1 | benannte Zubereitung; Auszug oder Flüssigkeit nicht identifiziert; target-freie Kontextklasse Arzneiform offen | Blütenzubereitung | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `ofchey` | 3 | Zubereitung einer benannten Droge; target-freie Kontextklasse Zubereitung | Blütenzubereitung | `F04:4` | `C0_REPLACEABLE_DEFAULT` |
| `ofchol` | 1 | Trockenmaterial oder Trockenbereitung; target-freie Kontextklasse Arzneiform offen | getrocknete Blütendroge | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `ofchor` | 1 | Drogenportion oder Drogenanteil; target-freie Kontextklasse Rohdroge | Blütenportion | `F01:2` | `C0_REPLACEABLE_DEFAULT` |
| `ofchoshy` | 1 | feuchte Zubereitung einer benannten Droge; target-freie Kontextklasse Arzneiform offen | eingeweichte Blütenmasse | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `ofchr` | 1 | Endprodukt oder Abschlusszubereitung einer Droge; target-freie Kontextklasse Arzneiform offen | Blütenrückstand | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `ofchtar` | 1 | Drogenportion oder Drogenanteil; target-freie Kontextklasse Arzneiform offen | abgemessener Blütenanteil | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `ofchy` | 3 | benannter Drogen- oder Pflanzenteilkopf; target-freie Kontextklasse Rohdroge | Blütenmasse | `F01:4` | `C0_REPLACEABLE_DEFAULT` |
| `qofchal` | 1 | Trockenmaterial oder Trockenbereitung; target-freie Kontextklasse getrocknete Droge | heiß-trockener Blütenrohstoff | `F02:2` | `C0_REPLACEABLE_DEFAULT` |
| `qofchdar` | 1 | Drogenportion oder Drogenanteil; target-freie Kontextklasse Rohdroge | abgemessener Blütenanteil | `F01:2` | `C0_REPLACEABLE_DEFAULT` |
| `qofchdy` | 1 | feuchte Zubereitung einer benannten Droge; target-freie Kontextklasse Arzneiform offen | angefeuchtete Blütenzubereitung | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `qofchedy` | 5 | Trockenmaterial oder Trockenbereitung; target-freie Kontextklasse getrocknete Droge | vollständig getrocknete Blütenfraktion | `F02:4` | `C0_REPLACEABLE_DEFAULT` |
| `qofcheepy` | 1 | Zubereitung einer benannten Droge; target-freie Kontextklasse Arzneiform offen | feine Blütenzubereitung | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `qofcheol` | 2 | benannte Zubereitung; Auszug oder Flüssigkeit nicht identifiziert; target-freie Kontextklasse Arzneiform offen | Blütenzubereitung | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `qofchey` | 1 | feuchte Zubereitung einer benannten Droge; target-freie Kontextklasse Arzneiform offen | angefeuchtete Blütenzubereitung | `F00:0` | `C0_REPLACEABLE_DEFAULT` |
| `qofchol` | 2 | Trockenmaterial oder Trockenbereitung; target-freie Kontextklasse getrocknete Droge | getrocknete Blütenzubereitung | `F02:2` | `C0_REPLACEABLE_DEFAULT` |
| `qofchor` | 1 | Drogenportion oder Drogenanteil; target-freie Kontextklasse Rohdroge | Blütenportion | `F01:2` | `C0_REPLACEABLE_DEFAULT` |
| `schor` | 3 | Pflanzenteil-Unterposten | Blütenstandsposten | `F01:2` | `C0_REPLACEABLE_DEFAULT` |

## The useful plant-part bridge

Exact chor and cthy occur in parallel at 15 chor positions on 14 loci; 5 are direct pairs in both written orders. With the inherited cthy leaf-drug lead, chor is best treated as a different plant-part head. Flower versus seed/fruit remains unresolved.

The four OFCH contacts with schor/chory/shor remain useful C0 shadows, but none is an exact chor anchor or score-ready relation. They keep the flower default alive; they do not raise it above seed or another drug.

## Observationally tied historical candidates

- `F00|F06|F07|F08|F09`: identical observed target-free support vector.
- `S00|S01|S02|S03|S05|S06|S07`: identical observed target-free support vector.

## Five complete working lines

### f22r.4

EVA: `pchaiin ofchy daiin cfhy doroiin ypchol sy schor daiin`

Haupteintrag; Trockenklasse III; Blütenmasse; drei Einheiten; Feldwechsel; abgemessene Drogenportion; Form III; dazugehöriges Trockenmaterial; Unterposten; Blütenstandsposten; drei Einheiten.

### f22v.1

EVA: `pysaiinor ofchar oky tchy otdy sor shy qod`

Eintragskopf; Inhalt offen; Blütenanteil; erste Wärmestufe; kalt-trockener Gradanfang; kalter Anfangsansatz; abgeschlossen; Unterposten; Portionsträger; feucht oder angefeuchtet; Anfangsstufe; Zubereitung abschließen.

### f41v.2

EVA: `pcheody qofcheepy ofchdy cfhekchdy ypchedy chepchefy shdchdy qotal dar`

Haupteintrag; weitere Bestimmung offen; feine Blütenzubereitung; aufbereitete Blütendroge; heiß-trocken gemischter Anteil; Zwischenprodukt; getrocknet als C0-Rivale; fein zerkleinerte Trockendroge; angefeuchtete Drogenportion; kalter Rohstoff I am Gradanfang; abgemessener Anteil I.

### f93r.2

EVA: `ycham s chol chotom cthodar sheo s oteodal s ofchoshy cthoshol`

ferner; je; getrocknet; möglicherweise zerkleinertes Blattgut; möglicherweise abgemessener Blattanteil; Feuchtzubereitung; je; kalter Rohstoffanteil I; je; eingeweichte Blütenmasse; möglicherweise angefeuchtetes Blattgut.

### f107r.38

EVA: `poaral orar ofchey qoteedy qotaiin opchedy qokchey otlchdain aly`

Eintragskopf; möglicherweise Rohstoffanteil I; möglicherweise erste Portion; Blütenzubereitung; kalt bis zur Endstufe; abgeschlossen; Kältegrad III; getrocknete Zubereitung; heiß-trocken bis zur Mittelstufe; möglicherweise zweiter kalter Trockenanteil; Rohstoffklasse I; Grundform.

## Historical sources

- [Vatican Pal.lat.1234](https://digi.vatlib.it/view/MSS_Pal.lat.1234) — circa 1400; plant-part rubrics; hot/cold dry/moist degree tables
- [Wellcome MS.542 medical miscellany](https://wellcomecollection.org/works/n674z2xd) — early 15th century; learned materia wholes plus part/form quality and degree; concise recipes
- [Salzburg UB M I 89](https://manuscripta.at/?ID=8162) — turn of 14th and 15th century; Accipe recipes; semen; gummi; pulvis; folia; vinum
- [Durham Cathedral MS B.III.12 endleaf recipes](https://reed.dur.ac.uk/xtf/view?docId=ark/32150_s18623hx81c.xml) — 14th to 15th centuries; Recipe or Accipe; ingredient amount process and result; oil water wine salt leaves
- [Wellcome MS.105 medical and pharmacological treatises](https://wellcomecollection.org/works/skrr7xc6) — 1430-1434; separate simple and compound medicines; alphabetical learned simples; oils syrups and short recipes
- [Wellcome MS.683 recipe collection](https://wellcomecollection.org/works/w6ne7k4t) — mid 15th century; Recipe plus gum or oil; infuse in strong vinegar; ointments oils powders pills and doses

No EVA character, initial or substring receives a Latin value. Every concrete noun in the five lines is a replaceable working default; none is confirmed plaintext.
