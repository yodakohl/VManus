# V63 R4 — Korrektoraudit der Maß-/Zustands-/Relationsslots

Status: unabhängiger kreativer Pass, keine Sprache oder Morphologie. Keine
V63-Geschwister, weiteren Seiten oder `f84`/`f84r`-Daten gelesen.

## Parservertrag

Der Parser kennt nur elf exakte V60-Kartenwerte, vier bereits strikte formale
Prompts und die vier anonymen V62-Register. Er sieht keine PAGE_HOSTs,
Komponenten oder neuen Bedeutungen.

Die fünfzehn elementaren Vorlagen sind:

```text
PARAMETER_VALUE       REQUEST_STANDARD_PARAMETER  FORMAL_SET_STANDARD_SLOT
TARGET_VALUE          FORMAL_SET_RELATION_SLOT    FORMAL_LINK_ACTIVE_STATE
BIND_WORKING_BATCH    TEST_READY_STATE            TEST_CLEAR_STATE
SELECT_PREVIOUS       SELECT_PART                 APPLY_ACTIVE
TEMPER_ACTIVE         FLUSH_AND_COMMIT            DRAIN_AND_COMMIT
```

Mehrere Trigger im selben Feld werden nur in sichtbarer Reihenfolge zu
`COMPOSITE_SEQUENCE` verkettet. Ein Feld ohne Trigger bleibt
`EXEMPLAR_ONLY`; es wird nicht passend gemacht.

## Beispielhafte Ausführung

```text
ANTEIL? TEMPERIEREN? ANWENDEN?
SELECT_PART > TEMPER_ACTIVE > APPLY_ACTIVE
A := part_of(A); temper(A); apply(A,T?)
```

Die lokale Lesung darf daraus „Nimm einen Anteil, temperiere ihn und wende ihn
am bezeichneten Ort an“ machen. Nur die erste Zeile ist Karteninput, die
zweite eine anonyme Vorlage und die dritte Registerpseudocode. Objekt, Ort,
Medium und Patient bleiben Exemplarfunktionen.

Ein weiteres Muster ist:

```text
VORIGES? LINK MASS?
A := P; link(A); parameter := EXEMPLAR_VALUE
```

Auch hier bezeichnet `VORIGES?` den Antezedenten nicht und `MASS?` liefert
weder Zahl noch Einheit.

## Grenze des Erfolgs

Der Parser ist deterministisch, weil die Bedeutungswette schon in V60
eingefroren wurde. Das ist kein unabhängiger Grammatikbeweis. Sein Wert liegt
darin, dass er:

1. Quellklassen nicht mehr vermischt;
2. Kartenreihenfolge erhält;
3. stille Argumente explizit aus V62 bezieht;
4. ungestützte Felder ungelöst lässt;
5. Feldschluss nicht als Wort ausspricht.

Der stärkste Rivale ist ein ungeordnetes Mnemonic-Bündel plus
Ganzfeldexemplar. Wenn die geordnete Vorlage bei der nächsten Herbal-/Bio-
Edition keine Widersprüche repariert, gewinnt dieser billigere Rivale.

## Ergebnis

V63 liefert eine kleine ausführbare **Arbeitsgrammatik**, nicht eine
syntaktische oder semantische Grammatik des Manuskripts. Vollständige
Feld-/Statementtabellen und die tatsächlichen Deckungszahlen stehen in den
validierten Artefakten; kein unankertes Feld erhielt eine neue Rolle.
