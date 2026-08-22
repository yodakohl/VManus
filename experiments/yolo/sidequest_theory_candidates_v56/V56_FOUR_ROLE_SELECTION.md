# V56 — Auswahl des Herbal↔Biological-Phrasebooks

Status: kreative Quellenphrasenschicht, keine Entzifferung.

## Auswahl

Die vier Rollen ergeben kein gemeinsames medizinisches Wörterbuch, sondern
ein zweistufiges Werkstatt-Phrasebook.

### Tier A — ausführbare gemeinsame Kontrollprompts

Diese vier Regeln überleben den strengsten R3-Pass und decken 45/381
Prosaereignisse in 35/135 Feldern:

```text
daiin                    -> VORGABEPARAMETER?
SET(<ARG_AIIN>)          -> STANDARDSLOT SETZEN
SET(<ARG_AL>)            -> LOKALEN RELATIONSSLOT SETZEN
FRAME_O(LINK)            -> AKTIVEN ARBEITSSTAND VERKNÜPFEN
```

Nur `VORGABEPARAMETER?` ist eine schwache Quellenphrase. Die anderen drei sind
formale Steueroperationen. RIGHT-Klassen erben weder MASS noch AN.

### Tier B — portable, aber exponierte Quellenmnemonics

Auf exakter GDT327-Joint-Tuple-Identität sind weitere kurze Werte in beiden
Registern brauchbar:

```text
MASS?        VERWENDEN?     BEREIT?       BEREITUNG?
AN?          KLAR?          ZUVOR?        TEIL?
```

Zusammen mit SET und LINK bilden elf gemeinsame exakte Karten zehn
Promptklassen und decken 96/136 Ereignisse der Joint-Tuple-Brücke. Diese
größere Schicht bleibt `EXPLORATORY_SHARED_MNEMONIC`, weil dieselbe deutsche
Lesung aus den bereits kreativen V53/V54-Kontexten stammt. Sie ist die
brauchbare Arbeitssprache des Sidequests, nicht die harte Untergrenze.

## Was nicht überträgt

- `WARM?`, `SPÜLEN?` und `ABLASSEN?` sind entweder Bio-lokal oder besitzen
  keine gemeinsame exakte Karte.
- `CKHY`, `E` und terminal gebundenes `oldy` liefern keine Quellenphrase.
- `CURRENT`, `MISCHEN`, `DARAUS` und `GLEICHMÄSSIG BEARBEITEN` bleiben
  lokale Kandidaten.
- Es gibt keine gemeinsame vollständige sichtbare oder formale Feldfolge.
- Nur zwei normalisierte exakte Kartenbigramme aus behaltenen Tier-B-Karten
  erscheinen in beiden Registern: `ZUVOR? | LINK` und `USE? | MASS?`. Sie
  bleiben parataktische Prompts, keine Sätze.

## Registerlokale Rücklesung

```text
Herbal:
  STANDARDSLOT = Pflanzenteil / Auszug / Dosis
  ACTIVE_STATE = laufender Simplex-Artikel oder vorige Bereitung

Biological:
  STANDARDSLOT = Charge / Badzelle / Station / Dauer
  ACTIVE_STATE = Vorlauf, Behandlung oder Beckenbestand
```

Ein Prompt benennt nie Pflanze, Wasser, Wein, Körper, Becken, Rohr, Krankheit
oder Richtung. Diese Wörter werden erst nach dem Prompt aus Bild und Record
eingesetzt.

## Historischer Mechanismus

Knappe Rezept- und Registerformeln wie „nach Maß“, „mit dem Vorigen“,
„verwenden“, „an“, „setzen“, „wenn bereit“ oder „wie zuvor“ konnten in
Materia-medica-, Bade- und Rezepttexten gewöhnlich wiederkehren. Das erklärt,
warum dieselbe kleine Werkstattschicht verschiedene Sachregister bedient. Es
identifiziert weder Latein noch eine andere Sprache und keine Lautung.

## Abdeckung

- 17 gemeinsame exakte Joint-Tuple-Typen;
- 44 Herbal- und 92 Biological-Ereignisse, zusammen 136;
- Tier A: 45/381 Ereignisse und 35/135 Felder, inklusive formaler
  Konstruktionen über weitere Oberflächen;
- Tier B: 11 exakte Brückenkarten, 96/136 Brückenereignisse;
- fünf gemeinsame Kartentypen bleiben lokal, eine terminale Quellenphrase
  wird zurückgezogen.

Die ausgewählte Schicht steht in `V56_SELECTED_SHARED_PHRASEBOOK.tsv`; der
vollständige 17-Typen-Audit bleibt in den vier Rollentabellen erhalten.

## Arbeitsurteil

`SMALL_CROSS_REGISTER_CONTROL_PHRASEBOOK_NOT_SHARED_MEDICAL_LEXICON`

Dies verbessert die vollständigen Texte: Sie können denselben kurzen
Werkstattkern verwenden, ohne dass ihre konkreten Herbal- und Bio-Nomen
vorgeben, entziffert zu sein.

`f84` und `f84r` blieben versiegelt.
