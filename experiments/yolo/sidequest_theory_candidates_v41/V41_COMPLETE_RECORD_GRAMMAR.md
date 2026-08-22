# V41 — vollständige Feld- und Recordgrammatik

## Ziel

V40 las die zwölf gemeinsamen Karten als wiederholbare Arbeitsblatt-Prompts.
V41 ordnet nun **jedem der 135 tatsächlichen Felder** mindestens eine konkrete
Werkstattfrage zu und setzt daraus die elf vollständigen Prosarecords zusammen.
Kein Feld und kein Record bleibt funktionslos.

Die Rollen sind aus den spekulativen V25/V40-Bedeutungen abgeleitet. Sie sind
also eine ausführbare Verdichtung der Arbeitstheorie, keine neue unabhängige
semantische Evidenz.

## Siebzehn Feldfragen

Das rekonstruierte Formular kennt:

1. WAS IST ZU NEHMEN?
2. WIE VIEL / NACH WELCHEM MASS?
3. WORAUS / MIT WELCHEM VORANSATZ?
4. BLEIBT DIE QUELLE DIESELBE?
5. WELCHER POSTEN IST AKTIV?
6. WELCHES ARBEITSMATERIAL LIEGT VOR?
7. WIE WIRD ES BEARBEITET?
8. BIS WANN / BIS ZU WELCHEM ZUSTAND?
9. WAS IST JETZT AUSZUFÜHREN?
10. WOHIN / AN WELCHES ZIEL?
11. WIE SPÜLEN, SEIHEN ODER ABLASSEN?
12. WIE ERHITZEN, KÜHLEN ODER RUHEN LASSEN?
13. WIE ANWENDEN, BADEN ODER BINDEN?
14. WELCHER SIMPLEX ODER PFLANZENTEIL?
15. WELCHES MEDIUM ODER WELCHER ZUSATZ?
16. FÜR WELCHEN BESCHWERDE-/ANWENDUNGSFALL?
17. WELCHES WEITERE ARTIKEL- ODER VERFAHRENDETAIL?

Ein Feld kann mehrere Fragen beantworten. Für die Recordübersicht erhält es
zusätzlich genau eine primäre Frage; weitere Rollen bleiben als sekundäre
Füllungen sichtbar.

## Zwei verschiedene Recordsprachen

### Herbal: komprimierter Artikel

Die vier Herbal-Seiten enthalten fünf Records mit zusammen 20 Feldern und 100
Karten:

- durchschnittlich 5,0 Karten pro Feld;
- 15/20 Felder enden offen;
- vier DY-Schlüsse und ein B3-Schluss;
- pro Record 2, 3, 4, 4 oder 7 Felder.

Die primären Fragen betreffen besonders Maß, Zustand, Arbeitsmaterial,
Pflanzenteil und Anwendung. Ein Herbal-Record ist daher am besten als kurzer
illustrierter Artikel lesbar:

```text
HERBAL_RECORD := PICTURED_OWNER + ARTICLE_CLAUSE{2..7}

ARTICLE_CLAUSE :=
    [PART_OR_MATERIAL]
    [MEASURE_OR_SOURCE]
    [PREPARATION_OR_STATE]
    [USE_OR_INDICATION]
    [OPEN_CONTINUATION | LOCAL_CLOSE]
```

Der abgebildete Simplex ist häufig stiller Eigentümer. Eine physische Zeile
kann mitten in einer Klausel enden; ein offenes Feld kann seine Aussage über
die nächste Zeile fortsetzen.

### Biological: Kette kurzer Arbeitszellen

Die drei Biological-Seiten enthalten sechs Records mit zusammen 115 Feldern
und 281 Karten:

- durchschnittlich 2,44 Karten pro Feld;
- 85/115 Felder tragen DY;
- 30 Felder bleiben offen;
- die Hauptrecords umfassen 24, 26, 38 und 20 Zellen, dazu zwei kurze
  Fortsetzungsrecords mit 5 und 2 Zellen.

Die primären Fragen werden von Spülen/Transfer (31), Erhitzen/Ruhen (27),
Vorbezug (9), Verfahrensdetail (8), Anwendung (7), Vollzug (6) und Ziel (6)
dominiert. Das ergibt:

```text
BIO_RECORD := PROCEDURE_CELL+

PROCEDURE_CELL :=
    [PRIOR_SOURCE | CURRENT_ITEM | MATERIAL]
    [HEAT | REST | WASH | STRAIN | DRAIN | APPLY]
    [STATE_GATE]
    [DESTINATION]
    [CONTENT_BEARING_CLOSE]
```

Das Bild liefert Körper, Becken, Leitung, Öffnung oder Arbeitsstation; die
Textzelle trägt die konkrete Operation und ihren lokalen Abschluss.

## Was im heutigen Sinn ein „Satz“ wäre

Die beste Rückleseeinheit ist weder physische Zeile noch einzelne sichtbare
Gruppe. Für Herbal entspricht eine Aussage meist einer **mehrkartigen offenen
Artikelklausel**. Für Biological entspricht sie eher einer **kurzen
abgeschlossenen Arbeitszelle**, während mehrere Zellen zusammen einen
Verfahrensschritt bilden können.

Damit gelten drei Ebenen:

```text
KARTE  = Prompt, Inhalt oder terminale Aktion
FELD   = lokale Frage/Antwort beziehungsweise Arbeitszelle
RECORD = vollständiger Artikel oder Arbeitsablauf
```

Zeilen sind räumliche Schreibträger. Sie können Feld und Aussage unterbrechen,
ohne deren Inhalt abzuschließen.

## Zwei konkrete Recordlesungen

### f10r, Record 1

Primärpfad:

`GLEICHE QUELLE/BEARBEITUNG → VORANSATZ/ZUSTAND`

> Nimm die faserige untere Wurzel, wasche und bearbeite sie aus demselben
> Ansatz; gib Rotwein zu, verwende die vorgeschriebene Menge und halte den Rest
> trocken. Fahre mit der vorigen Zubereitung fort und wende sie an, sobald der
> erforderliche Zustand erreicht ist.

Zwei lange Felder bilden einen Artikelabschnitt, nicht zwei einzelne Wörter
oder zwingend zwei Sätze.

### f81v, Record 1

Der Record besteht aus 24 kurzen Zellen. Sein komprimierter Pfad beginnt:

`SPÜLEN → VORANSATZ/ZIEL → VORANSATZ/MASS → VORANSATZ → ERHITZEN → ...`

und läuft weiter über Arbeitsflüssigkeit, wiederholtes Spülen, Ruhen,
Anwendung, Zielzuführung und Endreinigung.

Flüssige Expansion:

> Spüle die bezeichnete Stelle. Nimm aus demselben vorbereiteten Ansatz die
> vorgeschriebene Menge und führe sie zum vorgesehenen Ziel. Halte den
> Arbeitsgang warm, lasse ihn ruhen, spüle oder seihe weiter, verwende die
> fertige Portion und wasche anschließend Gefäß und Leitungen aus.

Das ist eine Zusammenfassung des ganzen Zellenwegs, keine wortgetreue
Ein-Satz-Behauptung.

## Aktuelle Gesamtgrammatik

```text
PAGE
  -> PICTURED_OWNER
  -> RECORD+

HERBAL_RECORD
  -> LONG_OPEN_ARTICLE_FIELD{2..7}

BIO_RECORD
  -> SHORT_PROCEDURE_CELL+

FIELD/CELL
  -> LOCAL_CONTENT*
  -> SHARED_PROMPT*
  -> LOCAL_SPECIFICATION*
  -> LICENSED_CONTENT_TERMINAL?
```

Diese Grammatik ist für mehrere Schreiber lehrbar: gemeinsames Promptdeck,
lokale Exemplarwerte, kurze lizenzierte Schlusskarten und flexible physische
Zeilenfüllung.

## Grenze

Alle 135 Felder besitzen nun eine Defaultfunktion und alle elf Records einen
vollständigen Rollenpfad. Die Rollen stammen jedoch aus unserem bereits
erfundenen Lexikon; die 64 Anwendungs- und 59 Wärme-/Ruhe-Zuordnungen im
Mehrfachrollen-Inventar sind keine unabhängigen statistischen Entdeckungen.

V41 verbessert die innere Übersetzungsarchitektur und Satzsegmentierung. Es
beweist weder Medizin noch Sprache oder historische Bedeutung. f84 und f84r
blieben versiegelt.

