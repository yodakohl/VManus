# GDT567 — 39 kleine Karten geben der ganzen Ausgabe eine gemeinsame Fachstimme

Status:
`PASS_39_CARD_OWNER_VOICE_ADAPTER__1639_STATE_CLAUSES_HARMONIZED__1209_ARGUMENT_SEAMS_0_TO_1209_EXACT__20_RELATION_SEAMS_3_TO_20_EXACT__ZERO_ROOT_CHANGE`

## Der konkrete Fund

GDT566 machte erstmals alle Anschlüsse sichtbar. Von4.329 Kartenübergängen
innerhalb einer Aussage wechseln1.580 zwischen einer generierten Zustandszeile
und einer ownergebundenen Nichtzustandszeile:

```text
2.426 Nichtzustand → Nichtzustand
  969 Nichtzustand → Zustand
  611 Zustand      → Nichtzustand
  323 Zustand      → Zustand
────────────────────────────────
4.329 Binnenanschlüsse
```

Der häufigste harte Anschluss war keine widersprüchliche Bedeutung, sondern ein
Wechsel der Fachstimme. Die Zustandszeile sagte allgemein „Posten“, „Wert“,
„Anteil“ oder „Einheit“, während die Nachbarkarte denselben Slot als
„Stationsposten“, „Arbeitswert“, „Drogenanteil“ oder „Eintragseinheit“
aussprach.

## Der 39-Karten-Adapter

Die vorhandenen Kontrollzeilen liefern eine vollständige kleine Tabelle:

| Register | Y | AIIN | AIN | OR |
|---|---|---|---|---|
| Text | laufender Eintrag | Kennwert | Teilwert | Eintragseinheit |
| Pflanzen | Pflanzenposten | Arbeitswert | Materialanteil | Arbeitseinheit |
| Himmel | Positionsposten | Positionswert | — | Positionseinheit |
| Stationen | Stationsposten | Stationswert | Stationsanteil | Stationseinheit |
| Pharma | Drogenposten | Mengenwert | Drogenanteil | Ansatzeinheit |

Das sind19 tatsächlich benutzte Argumentzellen. Hinzu kommen18 beobachtete
Relationszellen für AL/AR/L/AIR, etwa Zielspalte, Ausgangsmaterial,
Ringverbindung, Stationsbahn und Gefäßverbindung. Nicht vorkommende Zellen
bleiben leer. Zwei allgemeine Karten schließen die Tabelle:

- `hier` wird in123/123 passenden Kontrollzeilen „an der bezeichneten Stelle“;
- `abschließen` wird in705/705 passenden Kontrollzeilen „schließe den Schritt“.

Alle37 Register-Wurzel-Karten treffen zusammen1.807 Zustandsereignisse, und
1.807/1.807 Kontrollzeilen tragen das jeweilige Zielwort. Der Adapter ist also
nicht aus einem frei erfundenen Stillexikon gebaut, sondern aus der bereits
vorhandenen zweiten Leseschicht.

## Was an den echten Anschlüssen besser wird

An1.209 gemischten Anschlüssen nennen beide Seiten denselben Argumenttyp. Vor
dem Adapter hatten0/1.209 denselben ganzen Fachwortkopf; danach1.209/1.209.
Zwanzig Anschlüsse teilen eine Relation: Dort steigt die Übereinstimmung von3
auf20.

Beispiel Nichtzustand→Zustand:

```text
alt: Lege den Kennwert fest … | Weiter: halte den Wert.
neu: Lege den Kennwert fest … | Weiter: halte den Kennwert.
```

Beispiel Zustand→Nichtzustand:

```text
alt: Weiter: halte den Posten; hier. | Wähle … den laufenden Eintrag.
neu: Weiter: halte den laufenden Eintrag; an der bezeichneten Stelle.
     | Wähle … den laufenden Eintrag.
```

Eine Relation wird zugleich hörbar konsistent:

```text
alt: … Pflanzenposten; zur Zielstelle. | Nimm den Posten; zum Zielort; abschließen.
neu: … Pflanzenposten; zur Zielstelle. | Nimm den Pflanzenposten; zur Zielstelle;
     schließe den Schritt.
```

Die exakte Ganzwortprüfung korrigierte dabei einen ersten losen Zählwert von
1.219 auf1.209: Zehn vermeintliche Kontakte waren nur Teilwörter wie `Eintrag`
in `Eintragseinheit`.

## Die vollständige Ausgabe bleibt reversibel

1.639/1.656 Zustandszeilen ändern ihre deutsche Fachstimme;17 benötigen keine
der39 Karten. 774/793 Aussagen und alle28 laufenden Seiten werden hörbar
einheitlicher. Trotzdem werden die Zustandszeilen nicht einfach durch die lange
ownergebundene Ausgabe ersetzt: Nur20 werden bytegleich mit ihr. Die knappe
GDT565-Komposition bleibt also erhalten, erhält aber die passende Sachterminologie.

Alle3.466 Nichtzustandszeilen bleiben bytegleich. Rezepte, Atome, Ereignis- und
Aussagegrenzen sowie beide älteren Lesekanäle bleiben separat sichtbar.

## Nächster Arbeitsweg

Nach den Substantiven und Relationen sitzt der größte verbleibende Stilwechsel
in den Handlungen: generisches „gib/nimm/setze“ steht neben registertypischem
„ordne zu/entnimm/setze im Stationsgang an“. Der nächste Pass soll deshalb die
neun Handlungswurzeln gegen ihre vorhandenen ownergebundenen Verbformen legen
und nur wiederkehrende kleine Aktionsschablonen übernehmen. Keine Wurzel wird
umgedeutet und keine Seite geöffnet.

Alle43 unabhängigen Prüfungen bestehen.
