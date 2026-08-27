# GDT546 — ausführbarer Reader für 81 Fragmentkarten

Status: `PASS_81_CARD_FRAGMENT_READER__4_DUAL_BRIDGES__12_EXPLICIT_DEFAULTS`

Der Reader zieht die bisher verstreuten Angaben pro Oberfläche in genau eine
Karte zusammen: vollständiges Rezept, deutsche Komponentenlesung,
Hauptstamm, sichtbare Stammform, gerichtete linke/rechte Erweiterungen,
Kürzelkanäle, alte Andockkanten, Satzkontext und gegebenenfalls eine zweite
Herleitung. Alle 81 bekannten Oberflächen liefern eine Karte; unbekannte
Oberflächen stoppen, statt durch Ähnlichkeit stillschweigend zu erben.

## Die vier Karten mit zwei Herleitungen

| Oberfläche | Hauptzerlegung | zusätzliche Zerlegung | repariert | Arbeitslesung |
| --- | --- | --- | --- | --- |
| `chckhedy` | `CH+CH+[K+E+DY]` | `CH+[CH+K]+E+DY` | CONTEXT | Nehmen, erneut nehmen und geben; auf Grad I; abschließen. |
| `chepakeo` | `[CH+E+P]+A_ADDR+K+E+O` | `CH+E+P+A_ADDR+K+[E+O]` | INTERFACE | Nehmen, einsetzen und geben; auf Grad I; hier; erneut auf Grad I; zur Ausführung. |
| `chepos` | `[CH+E+P]+O+S` | `[CH+E]+P+O+S` | CONTEXT | Nehmen, einsetzen und wählen; auf Grad I; zur Ausführung. |
| `tosheo` | `T+[O+SH+E+O]` | `T+O+[SH+E]+O` | CONTEXT | Einstellen und halten; zur Ausführung; auf Grad I; erneut zur Ausführung. |

Die zweite Herleitung ändert weder Hauptstamm noch Rezept noch Bedeutung.
Bei `chckhedy` bleibt ihre sichtbare Richtung ausdrücklich abweichend.

## Die zwölf expliziten Defaults

`aiicthy`, `chady`, `chap`, `folchol`, `kody`, `ofaram`, `qoekedy`, `qokshd`, `qoteeod`, `rotaiin`, `saiis`, `shokaiir`

Diese Karten werden weiterhin vollständig gelesen. Ihr Kontext oder eine
Andockkante ist aber nicht durch eine qualifizierte zweite Stammbrücke
abgesichert. Das ist eine benannte Arbeitslücke und kein leeres Wort.

## Bedienung

```bash
python3 experiments/yolo/gdt546_consolidated_fragment_reader/src/read_fragment.py \
  --surface chepakeo
```

Die Ausgabe bleibt zweikanalig: Komponentenfolge und strukturelle Herleitung
sind beobachtbare Arbeitskarten; der deutsche Satz ist die heutige
Arbeitslesung und kein behaupteter Klartext.
