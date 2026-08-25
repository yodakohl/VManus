# Pass 1020 — f67r2 mit dem Einseitenblatt gelesen

## Das unveränderte Blatt

Der Rundlauf benutzt ausschließlich das in Pass 1018/1019 konsolidierte
Inventar:

```text
19 KERNE
Y AKTIVER POSTEN   OK SETZEN       OL FORTSETZEN   OT DANACH
AL ZIELORT         CH NEHMEN       SH HALTEN       AR AUSGANG
K GEBEN            AIIN WERT       S WÄHLEN        CHD UMSETZEN
OR EINHEIT         L VERBINDUNG    T EINSTELLEN    AIN ANTEIL
R MARKIEREN        P EINSETZEN     AIR LAUF

8 KONTROLLEN
E / EE / EEE = GRAD I / II / III
DY = SCHLUSS   O = AUSFÜHRUNG   Q = BEGINNMARKER
IIN = STUFE    DA = ZWEITE STUFE

4 LOKALE KANÄLE
HIER | VARIANTE | KLASSE | VORBEZUG

10 ERLAUBTE RESEGMENTIERUNGEN
CTH=CH+T   CKH=CH+K   CPH=CH+P   CFH=CH+LOCAL_F
CHEO=CH+E+O   CHK=CH+K   SHED=SH+E   LSH=L+SH
SOLK=OL+K   LD=L+D_ADDR
```

`LOCAL_F`, `D_ADDR`, `S_ADDR`, `AM_ADDR` und `A_ADDR` werden dabei nicht zu
neuen Wörtern: Sie passieren den lokalen Kanal `HIER`. `LOCAL_G`, `LOCAL_I`
und `G_LABEL` passieren `VARIANTE`, `AN` passiert `KLASSE`, und `OS` passiert
`VORBEZUG`. Keines dieser Zeichen erhält eine portable Himmelsbedeutung.

Die auf f67r2 tatsächlich benötigten Resegmentierungen sind `CFH`, `CTH`,
`CKH`, `CHK` und `CHEO`. Die übrigen fünf bleiben unbenutzt. Keine sichtbare
Form erhält deshalb einen zusätzlichen Operator.

## Seiteneinsatz

f67r2 umfasst hier die vollständige Aussagenfolge `P1009-S031` bis
`P1009-S041`: 11 Aussagen, 126 Karten und die Loci f67r2.13 bis f67r2.74.
Die Lücke zwischen S040 und S041 enthält lokale Himmelsbeschriftungen; das
Blatt übersetzt sie nicht in Sachbedeutungen.

- S031, S034 und S038 schließen mit dem lizenzierten `DY=SCHLUSS`.
- S032, S033, S035–S037, S039 und S040 enden an sichtbaren Grenzen.
- S041 bleibt am Seitenende offen.
- Verwendete lokale Kanäle sind `HIER`, `VARIANTE`, `KLASSE` und
  `VORBEZUG`; ein Kanalwort benennt noch keinen konkreten Sektor oder Stern.

Die vollständige Kette

> sichtbare Kartenfolge → Komponentenkarten → wörtliche Kernlesung →
> flüssige Rad-/Tabellenlektüre → offene Bindungsstelle

steht zeilenweise in `F67R2_COMPLETE_ROUNDTRIP.tsv`. Hier folgt dieselbe
Folge als lesbare Werkstattfassung.

## Vollständige Rad-/Tabellenlektüre

### P1009-S031 — f67r2.13 bis f67r2.14

`opodchol s ain aldy soeey doiin oldy`

> Am bezeichneten Platz einen Eintrag einsetzen und fortführen. Einen Anteil
> wählen, ihn dem örtlichen Zielplatz zuordnen, den aktiven Posten in Grad II
> auswählen, auf der bezeichneten Stufe fortsetzen und schließen.

Das Blatt erklärt nicht, welcher sichtbare Sektor oder Ringplatz `HIER` und
`ZIELORT` ist und ob `ANTEIL` eine Fläche, Position oder bloße
Tabellenunterteilung bezeichnet.

### P1009-S032 — f67r2.16 bis f67r2.21

`odaeiin okoes oekain y otchey soraiir dy qopchy daiin dal ydchos ain ar amy chocfhy saral sain am ar`

> Auf der zweiten Stufe in Grad I wählen und einen Anteil geben. Danach den
> aktiven Eintrag wieder aufnehmen, seine Einheit und seinen Wert wählen und
> markieren, ihn mit dem angegebenen Wert am Zielplatz einsetzen und am
> bezeichneten Platz Anteil, Ausgang und Ziel auswählen; an der sichtbaren
> Grenze enden.

Die Karte hat keinen `BEGINNMARKER`; daher wird hier keine „neue Reihe“
erfunden. Offen bleiben die Bindung der mehrfachen Posten, der lokale Platz
von `CFH` sowie die Frage, ob die letzten Ausgangs- und Zielkarten zu demselben
Eintrag gehören.

### P1009-S033 — f67r2.23 bis f67r2.27

`oparchy salsain sodar ofar ar ydam yteoor yto ykor okeo r aiin am`

> Den aktiven Posten am Ausgang einsetzen und nehmen, Zielort und Anteil
> wählen und auf der zweiten Stufe markieren. Den bezeichneten Ausgang und
> den örtlichen Posten übernehmen; die aktuelle Einheit in Grad I einstellen,
> geben und setzen, dann Wert und lokale Stelle markieren; an der sichtbaren
> Grenze enden.

Das Blatt entscheidet weder, welcher der wiederholten Ausgänge sichtbar
gemeint ist, noch wie `HIER`, `WERT` und `EINHEIT` auf Ring, Sektor oder
Tabellenzeile verteilt werden.

### P1009-S034 — f67r2.29

`ytody`

> Den aktiven Posten einstellen, ausführen und schließen.

Das ist mechanisch vollständig, doch der aktive Posten muss aus dem vorherigen
lokalen Kontext erinnert werden; das Einseitenblatt benennt ihn nicht.

### P1009-S035 — f67r2.29 bis f67r2.30

`saiin ochol olol`

> Den Wert wählen und die Eintragsfolge bis zur sichtbaren Grenze
> fortsetzen.

`WERT` kann auf dem Blatt eine Zahl, Position, Kategorie oder Phase sein. Der
konkrete Wert und die genaue Grenze sind nicht aus den drei Karten allein zu
bestimmen.

### P1009-S036 — f67r2.32 bis f67r2.33

`dosar odas air alaiin dokan oear odal`

> Am bezeichneten Platz den Ausgang wählen. Auf der zweiten Stufe den Lauf und
> den Zielwert auswählen, die örtliche Klasse setzen und in Grad I Ausgang
> sowie die Verbindung der zweiten Stufe ausführen; an der sichtbaren Grenze
> enden.

`AUSGANG`, `LAUF`, `ZIELORT` und `VERBINDUNG` bilden hier ein
Adressinventar, aber keine Pfeilrichtung. Ungeklärt bleiben die lokale Klasse
und die Zuordnung dieser vier Karten zu den beiden getrennten Rädern.

### P1009-S037 — f67r2.35 bis f67r2.36

`chol giin okol ytor daiin or`

> Bei der örtlich benannten Variante und Stufe fortsetzen. Die Fortsetzung
> setzen und die aktuelle Einheit einstellen; danach folgen Wert und Einheit.
> An der sichtbaren Grenze enden.

Der lokale Himmelsname hinter `VARIANTE` bleibt ein Name. Das Blatt sagt nicht,
ob die beiden `EINHEIT`-Vorkommen dieselbe Ringgruppe wiederholen oder zwei
verschiedene Eintragsgruppen bezeichnen.

### P1009-S038 — f67r2.38 bis f67r2.44

`otoldos octhole sor chedaiin dy yteos oiin og ytoeopchey chekody sosho chos ockhy daiin aiin os qsg ofydy`

> Danach am bezeichneten Platz fortsetzen und wählen; in Grad I nehmen,
> einstellen und fortsetzen. Eine Einheit wählen und ihren Wert umsetzen. Den
> aktiven Posten am örtlichen Platz und auf der Stufe einstellen, dann die
> lokal benannte Variante verwenden. Den Posten in Grad I einstellen,
> einsetzen, nehmen, geben und halten; zwei Werte übernehmen, den örtlichen
> Vorbezug wieder aufnehmen, einen variantbenannten Eintrag beginnen und am
> bezeichneten Posten schließen.

`CTH`, `CHK`, `CKH` und die lokalen Zeichen werden vollständig zerlegt; keines
von ihnen liefert Richtung oder Rotation. Offen bleiben der genaue Antezedent
von `VORBEZUG`, die Zugehörigkeit der zwei Werte und der Geltungsbereich des
späten `BEGINNMARKER`.

### P1009-S039 — f67r2.44 bis f67r2.46

`sheody aiin ycheody es odaiiin yekees oraly`

> Den aktiven Posten am bezeichneten Platz in Grad I halten; danach folgt sein
> Wert. Den Posten dort in Grad I nehmen und wählen; auf der zweiten
> Stufe die lokal benannte Variante verwenden, den Posten zwischen Grad I und
> Grad II geben und wählen. Die Folge endet mit Einheit, Zielplatz und aktivem
> Posten an der sichtbaren Grenze.

`CHEO` ist nur `NEHMEN+GRAD I+AUSFÜHRUNG`. Die lokale Variante, der konkrete
Wert und der Geltungsbereich des Gradwechsels sind mit dem Blatt nicht
auflösbar.

### P1009-S040 — f67r2.48 bis f67r2.51

`todaiin dain dy os choer aiin choeea sal dadaiin`

> Wert und Anteil des aktiven Postens einstellen, den örtlichen Vorbezug
> aufnehmen, in Grad I einen Wert nehmen und markieren, in Grad II den
> bezeichneten Wert nehmen und den Zielplatz wählen. Es folgen zweite Stufe,
> örtliche Stelle und Wert; an der sichtbaren Grenze enden.

Das Blatt nennt den Antezedenten des `VORBEZUGS` nicht und entscheidet nicht,
ob die drei Werte identisch, gestuft oder verschiedenen Einträgen zugeordnet
sind.

### P1009-S041 — f67r2.72 bis f67r2.74

`dar aldaiin ydaiin qkoy ydaiin qofair ypair ykoaiin ydoly ytalchos oly okey sshey sy shees qeykeey ykchey ykchey qokeochy oaiin okol ar olar yshey qokeeody cheos oeeos qockhy chos aiin okeeody qokoaiin odain ar air ay`

> Die Kopfkarten nennen den bezeichneten Ausgang, den örtlichen Zielwert und
> den aktuellen örtlichen Wert. Einen Posten beginnen und geben; den lokal benannten Lauf beginnen, den
> aktiven Posten darin einsetzen und ihm einen Wert geben. Den Posten am
> bezeichneten Platz fortsetzen, Zielort, Nehmen und Wahl einstellen und ihn
> in Grad I beziehungsweise II setzen, halten, geben und nehmen. Am Ausgang
> fortsetzen. Einen weiteren Eintrag beginnen, nehmen, geben und wählen, seinen
> Wert am bezeichneten Platz in Grad II setzen, Wert und Anteil ausführen und
> Ausgang, Lauf und örtlichen aktiven Posten offen weiterführen.

Die 36 Karten sind abgedeckt, aber das Blatt löst die Satzklammer nicht:
ungeklärt bleiben die Träger der drei `BEGINNMARKER`, die Wiederaufnahme der
mehrfachen Posten, die lokalen Namen, die Zugehörigkeit der Werte und der
offene Anschluss nach dem Seitenende.

## Was das Einseitenblatt erklärt — und was nicht

Die vollständige Folge lässt sich ohne zusätzliche Kernbedeutung als
Verwaltung von Einträgen in getrennten Rädern und einer Tabelle lesen:

> Eintrag wählen/setzen/nehmen/halten/geben → Wert, Anteil, Einheit oder Grad
> übernehmen → lokalen Platz, Namen, Klasse oder Vorbezug einsetzen → an einer
> sichtbaren Grenze fortsetzen oder mit `DY` schließen.

Der stärkste lokale Satz ist S035: `S+AIIN = WÄHLEN+WERT` passt unmittelbar zu
einem auswählbaren Rad- oder Tabellenfeld. S036 zeigt zudem, dass
`AUSGANG–LAUF–ZIELORT–VERBINDUNG` gemeinsam lesbar sind, ohne daraus eine
Bewegungsrichtung zu machen. S038 und S041 zeigen dagegen die Grenze des
Blattes: Alle Karten sind expandierbar, aber Referenzbindung und
Klammerstruktur bleiben zu offen für eine eindeutige Prosafassung.

Das Rundblatt erklärt insbesondere noch nicht:

- welcher konkrete Sektor, Ring, Sternname oder Tabelleneintrag jeweils lokal
  gemeint ist;
- ob `WERT` numerisch, ordinal oder kategorial ist;
- wie wiederholte aktive Posten, Werte und Einheiten über lange Aussagen
  gebunden werden;
- wo der Geltungsbereich von Grad, Beginn und Vorbezug endet;
- ob die sichtbaren Räder überhaupt eine Arbeitsrichtung haben.

Darum wird keine Richtung oder Rotation behauptet. Ein `LAUF` bleibt eine
lokal benannte Folge, ein `AUSGANG` eine Ausgangsadresse und ein Himmelslabel
ein lokaler Name. Der Rundlauf ist kartenseitig vollständig, aber seine
konkreten Referenten bleiben exemplar- und diagrammgebunden.
