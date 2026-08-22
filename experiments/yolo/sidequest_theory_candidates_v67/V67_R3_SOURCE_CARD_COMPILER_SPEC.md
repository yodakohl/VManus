# V67 R3 — deterministischer Quelltext-zu-Karten-Compiler

## Entscheidung

Die 1420er Werkstatttheorie ist als **exemplargebundener Transducer** ausführbar, aber nicht als selbständiger semantischer Codec. Mit dem vollständigen Werkstattexemplar laufen exakte Gruppenidentität, Reihenfolge, Feldgliederung, physischer Reflow und ausgewählte lokale Quellintention für **776/776 Gruppen in 14 Einheiten** vorwärts und rückwärts. Ohne das lokale Exemplar bleibt die formale Hülle 776/776 erhalten, die vollständige konkrete Quellintention aber 0/776.

Der produktive gemeinsame Prosaanteil bleibt klein: elf Mnemonic-Karten und vier formale Promptkarten, mit einer Kartenüberschneidung, ergeben **14 exakte Control-Karten**. Sie erkennen 119/381 Prosaereignisse; 262/381 sind `EXEMPLAR_ONLY`. Die 395 Astrogruppen besitzen ausschließlich lokale Diagrammadressen und keine Prosa-Kartenwerte.

Damit ist die stärkste präzise Aussage: Eine Werkstatt konnte die vorhandenen Seiten mit Registermarken, Tabellen und Ganzkartenexemplaren zuverlässig fortschreiben. Sie konnte aus einer beliebigen neuen Sachklausel nicht allein anhand der sichtbaren Kartenregeln neuen Text erzeugen.

## Typisierte Eingabe

```text
PROSE_CLAUSE :=
  unit_id × statement_id × clause_class
  × pre_state[OWNER, ACTIVE, TARGET, PREVIOUS]
  × ordered_source_slots
  × existing_event_exemplar_keys
  × field_cuts × physical_locus_map

EVENT_KEY :=
    EXACT_MNEMONIC(exact_joint_card)
  | STRICT_FORMAL_PROMPT(exact_joint_card)
  | EXEMPLAR_WHOLE_CARD(exact_joint_card)

ASTRO_FRAGMENT :=
  diagram_namespace × drawn_locus × page_local_group_id
  × local_formal_role × local_exemplar_key
```

Die Klauseltypen sind die bereits ausgewählten V63-Klassen: 12 `CONTROLLED_UNIQUE`, 49 `MIXED_AMBIGUOUS` und 55 `OPAQUE_UNPARSED`. Ein Typ ist eine Parserklasse, keine Satzart oder Wortfolge einer identifizierten Sprache.

## Fester Kartenbestand

Die elf exakten V60-Karten bleiben unverändert:

```text
MASS?  ANWENDEN?  BEREIT?  ANSATZ?  ZIEL?  KLAR?
VORIGES?  ANTEIL?  TEMPERIEREN?  SPÜLEN?  ABLASSEN?
```

Die vier strikten formalen Prompts sind:

```text
VORGABEPARAMETER?
STANDARDSLOT_SETZEN
LOKALEN_RELATIONSSLOT_SETZEN
AKTIVEN_ARBEITSSTAND_VERKNÜPFEN
```

`VORGABEPARAMETER?` liegt auf derselben exakten Karte wie `MASS?`; formaler Prompt und kreatives Mnemonic bleiben getrennte Kanäle. Somit sind es 14, nicht 15, verschiedene Control-Karten. Die übrigen 159 Prosa-Kartentypen werden nur als ganze opake Exemplarkarten kopiert. Kein sichtbarer Teilstring, keine Komponente und kein PAGE_HOST erhält einen Wert.

## Compiler

Für Prosa arbeitet der Schreiber deterministisch:

1. Am Recordanfang `OWNER`, `ACTIVE`, `TARGET` und `PREVIOUS` löschen und eine recordlokale ID-Reihe eröffnen.
2. Die Quellklausel als `UNIQUE`, `AMBIGUOUS` oder `UNPARSED` markieren.
3. Den ausgewählten V62-Übergang vollständig buchen: Präzustand, beobachtete Trigger, erschlossene stille Slots, vier Registeroperationen und Postzustand.
4. Bei einem exakten Mnemonic dessen einzige exakte Ganzkarte wählen. Bei einem formalen Prompt dessen exakte Ganzkarte wählen, ohne ein deutsches Wort zu vererben. Sonst den vorhandenen ganzen Kartenpayload über den Ereignisexemplarschlüssel holen.
5. Die Karte atomar in den Feldpuffer kopieren. Zwischen ganzen Karten wird `SPACE` gesetzt; innerhalb der Karte wird nichts zerlegt.
6. Den gespeicherten Feldschnitt anwenden. Die 90 sichtbaren Schlüsse werden nur als `CLOSE_AND_COMMIT` gebucht; die 45 offenen Felder enden als `OPEN_FIELD_CUT`. `CLOSE` wird nie gesprochen.
7. Erst nach der Feldbildung den V61-Locusplan anwenden. `LINE_RESET` ist Reflow, kein Satzende; 18/116 Aussagen überschreiten eine oder zwei physische Zeilengrenzen.
8. Der Handschreiber kopiert die vollständige gespeicherte Oberfläche. Er erzeugt keine Zeichenfolge aus Lauten, Buchstabenwerten oder Komponenten.

Astro umgeht die vier Prosaregister. Der Schreiber benutzt ausschließlich Diagrammnamespace, gezeichneten Locus und lokale Gruppenadresse. A1, A2 und A3 bleiben getrennt; insbesondere entsteht kein f68→f69-Schlüssel.

Der veröffentlichte Automat hat zehn Arbeitszustände plus `REJECT` und 22 deterministische Übergänge. Fünf Übergänge scheitern geschlossen: fehlendes Registerlog, fehlender Ganzkartenpayload, falscher Feldschluss, unlizenzierter Reflow sowie semantische/phonologische/querseitige Vererbung.

## Decoder

```text
visible whole groups + unit/locus address
  -> exact prose card ID or page-local Astro group ID
  -> stored field cuts and locus resets
  -> prompt/template labels where licensed
  -> reverse replay of the complete four-register transition log
  -> local source payload only when the external exemplar key is present
```

Der Decoder darf ohne Exemplar nur `UNKNOWN/EXEMPLAR`, die formale Operation oder das kurze ausgewählte Mnemonic ausgeben. Er darf fehlende Gegenstände, Ziele, Pflanzen, Flüssigkeiten, Körperteile, Stationen oder Regeln nicht aus der Karte ergänzen.

## Reversibilitätsbilanz

| Schicht | Ergebnis | notwendige Beilage |
|---|---:|---|
| exakte ID, Gruppenreihenfolge und Layout | 776/776 | exakte Karten-/lokale Adressbücher |
| Prosa-Oberfläche → exakte ID | 381/381 | Prosa-Namespace; keine Segmentierung |
| Prosa-ID → exakte Oberflächenvariante | 179/381 ohne, 381/381 mit Selektor | 202 Vorkommen in 34 IDs brauchen den Vorkommensselektor |
| Astro-Oberfläche → lokale Gruppe | 255/395 ohne, 395/395 mit Adresse | 140 Wiederholungsvorkommen brauchen Diagramm/Locus/Gruppe |
| 135 Feldschnitte und 90 Schlüsse | 135/135 | Feldkarte; Schluss bleibt still |
| 57 Prosa-Loci und 46 Grenzklassen | vollständig | V61-Reflowkarte |
| Register rückwärts | 116/116 mit Übergangslog; 47/116 nur aus Postzustand | vollständiges V62-Verlaufsbuch |
| wiederverwendbare Prosa-Templatefunktion | 119/381 Ereignisse | 14 Control-Karten und V63-Parser |
| vollständige konkrete Quellintention | 0/776 ohne; 776/776 mit Exemplar | 776 lokale Payloads oder 116 Klausel- plus 142 Locus-Exemplare mit Binnenalignment |

Formale Rückführung bedeutet hier Datenbewahrung, nicht Richtigkeit der kreativen deutschen Quelltexte.

## Minimaler Zustand und Codebuchkosten

Die bereits erschöpfend verglichenen Registermodelle erzeugen 9/116 Aussagen ohne Zustand, 27/116 mit `OWNER`, 88/116 mit `OWNER+ACTIVE`, 107/116 nach zusätzlichem `PREVIOUS` und 116/116 erst mit allen vier Registern einschließlich `TARGET`. Vier recordlokale Slots sind daher für diese Edition minimal. Aus dem nackten Endzustand bleiben dennoch 69 Aussagen rückwärts mehrdeutig; das Verlaufsbuch ist nicht optional.

| Codebuch | Schlüssel | Abdeckung | Grenze |
|---|---:|---:|---|
| elf Mnemonics | 11 | 85/776 | nur kurze kreative Promptwerte |
| vier Formalprompts | 4 | 45/776 | eine Karte überlappt `MASS?` |
| vereinigter Controlbestand | 14 | 119/776 | 657 Gruppen ohne globalen Prompt |
| vollständiges Prosa-ID-Buch | 173 | 381/776 | Identität, keine Quellintention |
| vollständiges Rendererbuch | 568 | 776/776 | 173 Prosa-IDs + 395 Astro-Lokaladressen |
| aggregierte Quellenexemplare | 258 | 776/776 | 116 Klauseln + 142 Astro-Loci, Binnenalignment weiterhin gespeichert |
| Ereignispayloadbuch | 776 | 776/776 | vollständige bestehende Edition, keine Produktivität für neue Klauseln |

Historisch genügt dafür kein modernes Rechenwerk: vier Rand- oder Gedächtnisposten, ein Ganzkartenmusterbuch, Feldschlusszeichen und eine Locus-Abschreibereihenfolge reichen als Handverfahren. Der Preis ist das große Exemplar.

## Abstrakter Ordnungsvergleich

Zwei vorab festgelegte Slotproxies wurden nur auf den 116 Prosa-Aussagen geprüft:

```text
LATIN_LIKE_DEPENDENT_FIRST:
  SELECT > TARGET > PARAMETER > STATE > LINK > ACTION > TERMINAL

VERNACULAR_LIKE_HEAD_FIRST:
  ACTION > LINK > SELECT > TARGET > PARAMETER > STATE > TERMINAL
```

Nur 28 Aussagen enthalten überhaupt mindestens ein vergleichbares Paar verschiedener Slotfamilien. Beide Modelle verletzen **42 von 94** beobachteten Paarordnungen. Der erste Proxy passt 13 Aussagen ohne Verletzung, der zweite 14; nach Gesamtdistanz herrscht Gleichstand. Der Compiler darf deshalb keine Reihenfolge normalisieren und identifiziert weder Latein noch eine Volkssprache, weder S/V/O noch irgendeine Wortart.

## Vollständige Langspuren

Die Schritttabelle führt sieben vollständige, nicht gekürzte Spuren aus:

- H5-S001: neun Gruppen über zwei physische Loci;
- B1-S002: längste Prosa-Aussage, 19 Gruppen über zwei Loci;
- B2-S005: acht Gruppen mit dem entscheidenden f82r.3→f82r.4-Reflow;
- B5-S003: neun Gruppen über drei Loci;
- A1:L074: 13 lokale f67-Gruppen;
- A2:L001: neun lokale f68-Kopfgruppen;
- A3:L001: 40 lokale f69-Kopfgruppen.

Alle 107 Spurenschritte bestehen formal und mit ausgewähltem Exemplar. Ohne Exemplar bleiben nur Karten-/Adressidentität, formale Rolle und Registerhülle.

## Typische Fehlkodierungen

Die schärfsten Fehler sind: aus einem Slot eine neue Karte erfinden; bei 202 variantenbedürftigen Prosaereignissen die Oberfläche aus der ID erraten; eine der 140 mehrdeutigen Astro-Oberflächen ohne Adresse rücklesen; Postzustand statt Übergangslog verwenden; `CLOSE` aussprechen; `LINE_RESET` als Satzende behandeln; `PREVIOUS` über eine Recordgrenze tragen; die beiden Ordnungsproxies erzwingen; OKE/LCHE allein aus dem Schluss als Spülen/Ablassen ableiten; A2 und A3 verbinden; oder Teilstrings beziehungsweise Lautwerte vererben. Der Automat weist alle diese Wege zurück oder markiert den Informationsverlust.

## Artefakte

- `V67_R3_776_GROUP_ROUNDTRIP_AUDIT.tsv` — vollständiger 381+395-Gruppenaudit.
- `V67_R3_116_TYPED_SOURCE_CLAUSES.tsv` — typisierte Klauseln, Register, Felder, Reflow und Ordnungsmetriken.
- `V67_R3_116_RUNTIME_REGISTER_TRANSITIONS.tsv` — vollständiges Laufzeitbuch.
- `V67_R3_COMPILER_TRANSITIONS.tsv` — deterministischer Automat.
- `V67_R3_14_UNIT_SUMMARY.tsv` — elf vollständige Prosa- und drei Diagrammeinheiten.
- `V67_R3_LONG_TRACE_STEPS.tsv` — sieben vollständige Langspuren.
- `V67_R3_STATE_CODEBOOK_COMPARISON.tsv`, `V67_R3_2_ABSTRACT_ORDER_MODELS.tsv`, `V67_R3_ERROR_AUDIT.tsv` — Kosten, Ordnungsnull und Fehler.
- `V67_R3_BUILD_SOURCE_CARD_COMPILER.py` und `V67_R3_VALIDATE_SOURCE_CARD_COMPILER.py` — deterministischer Build und Validator.

Ausführen:

```bash
python3 experiments/yolo/sidequest_theory_candidates_v67/V67_R3_BUILD_SOURCE_CARD_COMPILER.py
python3 experiments/yolo/sidequest_theory_candidates_v67/V67_R3_VALIDATE_SOURCE_CARD_COMPILER.py
```
