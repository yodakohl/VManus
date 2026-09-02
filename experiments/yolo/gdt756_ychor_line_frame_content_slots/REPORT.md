# GDT756 — `ychor` ist wahrscheinlich eher „Item/ferner“ als nur „nimm“

Status: `PARTIAL__YCHOR_ITEM_LEAD__13_OF13_LINE_INITIAL_0_OF13_PARAGRAPH_INITIAL__4_OF13_RECIPE_TRIADS_VS22_OF247_MATCHED__RANK4_OF113_INITIAL_FRAME_FORMS__71_OF71_BODY_TOKENS_CANDIDATE_RENDERED__53_BODY_WHOLES__ZERO_CONFIRMED_LEXEMES__NO_NEW_PAGE`

## Ergebnis

GDT755 hatte `ychor=nimm` als stärksten neuen Kandidaten gefunden. GDT756
behält diese Lesart, setzt aber einen besseren Hauptkandidaten davor:

```text
ychor  →  Item / ferner / ebenso       C2, stärkste Arbeitshypothese
        →  Recipe / Accipe / nimm      stärkster Rivale
        →  Item take / ferner: nimm    dritter Rivale
        →  De / Ad / For / für-gegen   schwächerer Themenrival
```

Der Grund ist nicht EVA-Latin-Ähnlichkeit. `ychor` steht 13/13 Mal am
Zeilenanfang, aber 0/13 Mal am kodierten Absatzanfang. Es erscheint auf dreizehn
Seiten in vier Sektionen (`H:9`, `P:2`, `S:1`, `T:1`) und liegt zwischen der
zweiten und 28. Zeile eines Absatzes. Das passt besonders gut zu einem Marker
für einen weiteren Eintrag oder ein weiteres Mittel.

Genau diese Konstruktion ist zeitnah belegt. Wellcome MS.407 aus dem frühen
15. Jahrhundert hat nach einem Mittel `Item. Tak ...`. Durham Cosin MS V.iv.1
von der Wende zum 15. Jahrhundert beginnt eine Folge mit `Take ...` und führt
sie mit `Item stampe ...` und `Item take ...` fort. Harley MS 2378 aus dem
späten 14./frühen 15. Jahrhundert bietet ebenfalls `Item take ...`.

Quellen: [Wellcome MS.407](https://wellcomecollection.org/works/me5nzvw8),
[Durham Cosin MS V.iv.1](https://reed.dur.ac.uk/xtf/view?docId=ark%2F32150_s19s1616306.xml),
[British Library Harley MS 2378](https://searcharchives.bl.uk/catalog/040-002032704).

## Die folgenden Linien sind tatsächlich rezeptartiger

Das `ychor`-Wort selbst wird vor der Körperprüfung entfernt. Unter den übrigen
Ganzwortkarten besitzen 4/13 Linien gemeinsam einen Inhalts-, Mengen- und
Vorgangsslot. Bei 247 nahe gelegenen Fortsetzungszeilen gleicher Sektion,
Sprache, Hand und fast gleicher Länge sind es 22/247. Die deskriptive Rate ist
damit 3,455-mal so hoch.

| Merkmal im Linienkörper | `ychor` | gematchte Kontrollen | Verhältnis |
|---|---:|---:|---:|
| Inhalt | 9/13 | 148/247 | 1,155 |
| Menge oder Grad | 6/13 | 91/247 | 1,253 |
| Vorgang | 4/13 | 40/247 | 1,900 |
| Qualität oder Stufe | 6/13 | 151/247 | 0,755 |
| Inhalt + Menge + Vorgang | 4/13 | 22/247 | 3,455 |

Unter 113 geschriebenen Anfangsformen mit mindestens fünf initialen Linien
liegt `ychor` beim vollständigen Dreierschema auf Rang 4. Es ist also nicht bloß
ein Positionskuriosum: Hinter ihm folgt ungewöhnlich oft ein kompakter
Rezeptkörper. Die geringere Qualitätsrate spricht zugleich dagegen, `ychor`
einfach als Überschrift eines Qualitätslexikons zu lesen.

## Der komplette 13-Linien-Renderer

Alle 71 Positionen nach `ychor` und alle 53 dort vorkommenden Ganzformen haben
jetzt einen Default und zwei Rivalen. Fragezeichen und generische Sätze über
„Arbeitsgut“ gibt es in dieser Schicht nicht. Beispiele:

```text
f6v.8
ferner: Blätter; heiße trockene Zubereitung; erhitze eine Handvoll

f17v.15
ferner: Wurzel; trockne vollständig, dann erwärme; trockene Zubereitung;
eine kalte Portion; kühle bis zur Mittelstufe

f45v.9
ferner: Wurzel; trockenes Kraut; erhitze eine Handvoll; Samen;
gib Samen zu; erhitze und trockne eine Handvoll

f99r.52
ferner: Heilmittel; eine Portion; eine Handvoll, dritter Anteil

f102v2.35
ferner: eingeweichtes Kraut; eine Portion Pulver; Wein; weiche ein;
heiß am Anfang; trockene Zubereitung; kühle ab und beende;
heiß im zweiten Grad; dritter Grad
```

Die vollständigen dreizehn Primär- und Rivalenlesungen stehen in
`artifacts/GDT756_YCHOR_FRAME_READER.md`.

## Welche konkreten Wörter jetzt Kandidaten sind

Die unmittelbaren Folger liefern erste inhaltliche Slots:

- `chor → Blätter` mit `Wurzel/Samen` als Rivalen;
- `cthy → Wurzel` mit `Blätter/Kraut` als Rivalen;
- `s → Samen` mit `Salz/Blätter` als Rivalen;
- `sheol → eingeweichtes Kraut` mit `Wasser/Wein` als Rivalen;
- `ols → Heilmittel` mit `Arzneistoff/Öl` als Rivalen;
- `chshoty → weiche ein` mit `trockne/kühle ab` als Rivalen;
- `odol → miss den Arzneistoff ab`;
- `qokchol → heiß getrocknetes Kraut` mit `Pulver/Wurzel` als Rivalen.

Diese spezifischen Substantive sind bewusst explorativ. Besonders
`Blätter`, `Wurzel`, `Samen`, `Wein`, `Holz` und `Pulver` sind noch keine
Identifikationen; ihre Funktion ist, vollständige vorhersagbare Lesungen zu
erzeugen, die an weiteren Vorkommen verbessert oder verdrängt werden können.
Kein Kandidat wurde aus dem ersten EVA-Zeichen gewonnen.

## Was die bessere Arbeitstheorie jetzt sagt

Die `ychor`-Zeilen lesen sich am ehesten als kompakte Listen- oder
Rezeptfortsetzungen:

```text
FERNER / EBENSO :  INHALT ODER VORGANG  [QUALITÄT]  [MENGE]  [VORGANG]
```

Das ist konkreter als der frühere Universalbefehl `nimm`, weil es sowohl die
preskriptiven als auch die deskriptiven `ychor`-Felder zulässt. In rein
preskriptiven Linien kann die praktische Langlesung weiterhin `ferner: nimm`
sein.

## Nächster Schritt

Der nächste Pass verfolgt zwei Linien gleichzeitig:

1. Die anderen Anfangsformen mit besonders rezeptartigem Körper—vor allem
   `pchor`, `ykar` und `yteedy`—werden auf Initialreinheit,
   Absatzfortsetzung und wiederkehrende Folgeslots geprüft. So entsteht ein
   kleines Inventar verschiedener Einleitungsformeln statt eines einzigen
   Allzweckmarkers.
2. Die elf direkten `ychor`-Folger werden an allen ihren Vorkommen geprüft.
   Wenn `chor=Blätter`, `cthy=Wurzel` oder `s=Samen` brauchbar ist, muss die
   jeweilige Ganzform außerhalb dieser dreizehn Linien weiterhin überwiegend
   einen konkreten Pflanzen-/Zutatenslot tragen. Schlechtere Kandidaten werden
   nicht gelöscht, sondern durch den besseren Rivalen ersetzt.

## Grenze

GDT756 bestätigt kein lateinisches Wort, kein deutsches Klartextwort und keine
vollständige Übersetzung. Es verbessert die Arbeitstheorie auf Ebene ganzer
Formen und ganzer Linien. Kein EVA-Zeichen oder Teilstring erhält Bedeutung;
keine neue Seite oder Transkription wurde geöffnet, f84 und f84r blieben
gesperrt.
