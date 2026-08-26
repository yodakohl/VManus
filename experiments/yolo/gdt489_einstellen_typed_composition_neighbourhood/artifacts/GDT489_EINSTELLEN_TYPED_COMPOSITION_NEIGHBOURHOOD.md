# GDT489 — EINSTELLEN im typisierten Kompositionsnetz

GDT489 nimmt die elf exakten GDT428-T/R-Austauschrahmen und fragt zweierlei getrennt: Ist ihr unveränderter Nachbarkontext in den 183 lokalen Events vorhanden? Und berührt ein lokales T-Event tatsächlich den vollständigen T-Teilrahmen? Nur der zweite Befund erzeugt eine Kompositionskante.

- T/R-Rahmen: **11** mit **30 T-** und **46 R-Ereignissen**.
- Nichtleere Nachbarkontexte: **10**; lokal vorhanden: **9**.
- Lokale Kontextzeugen: **168** Rahmen×Event-Zeugen / **175** Positionen in **121** Events.
- Nichttriviale lokale T-Rahmenkontakte: **3** in zwei Events; daraus **2** typisierte Nachbarkanten.

## Elf T/R-Kompositionsrahmen

| Rahmen | Nachbarkontext | GDT428 T/R | lokale Kontextzeugen | lokale T-Kontakte | Einordnung |
|---|---|---:|---:|---:|---|
| `@ACTION` | `NONE` | 1/21 | 0 | 0 | `EMPTY_CONTEXT_ACTION_BASELINE` |
| `@ACTION+AIIN` | `WERT` | 5/8 | 18 | 0 | `LOCAL_CONTEXT_ONLY` |
| `@ACTION+AIN` | `ANTEIL` | 2/3 | 11 | 0 | `LOCAL_CONTEXT_ONLY` |
| `@ACTION+AL` | `ZIELORT` | 3/2 | 48 | 0 | `LOCAL_CONTEXT_ONLY` |
| `@ACTION+AL+Y` | `ZIELORT · POSTEN` | 1/1 | 12 | 0 | `LOCAL_CONTEXT_ONLY` |
| `@ACTION+CH+E+Y` | `NEHMEN · GRAD I · POSTEN` | 1/1 | 1 | 0 | `LOCAL_CONTEXT_ONLY` |
| `@ACTION+CHD+Y` | `BEARBEITEN · POSTEN` | 5/2 | 0 | 0 | `ABSENT_LOCAL_CONTEXT` |
| `@ACTION+OL` | `FORTSETZEN` | 7/4 | 26 | 0 | `LOCAL_CONTEXT_ONLY` |
| `@ACTION+OR+Y` | `EINHEIT · POSTEN` | 1/1 | 2 | 0 | `LOCAL_CONTEXT_ONLY` |
| `@ACTION+Y` | `POSTEN` | 3/2 | 40 | 1 | `LOCAL_CONTEXT_AND_T_CONTACT` |
| `CH+@ACTION` | `NEHMEN` | 1/1 | 10 | 2 | `LOCAL_CONTEXT_AND_T_CONTACT` |

Neun der zehn nichtleeren Kontexte sind lokal vorhanden. Nur `CHD+Y = BEARBEITEN · POSTEN` fehlt als zusammenhängender Kontext in diesen 183 Events. Ein vorhandener Kontext allein setzt T noch nicht hinein; deshalb werden die sieben bloßen Kontextkontakte nicht zu EINSTELLEN-Kanten hochgestuft.

## Drei wirkliche lokale T-Rahmenkontakte

| Event | lokales Rezept | GDT428-Rahmen | Lage | Lesung |
|---|---|---|---|---|
| `G485-E133` | `CH+T+Y` | `@ACTION+Y` | `CONTIGUOUS_PARTIAL_FRAME` | Nimm den Drogeneintrag »cheo« und den Drogenposten und stelle den Drogeneintrag »cheo« und den Drogenposten ein. |
| `G485-E118` | `CH+T` | `CH+@ACTION` | `EXACT_WHOLE_EVENT` | Nimm den Sternstelleneintrag »o« und den Sternstelleneintrag »o« auf und stelle den Sternstelleneintrag »o« und den Sternstelleneintrag »o« ein. |
| `G485-E133` | `CH+T+Y` | `CH+@ACTION` | `CONTIGUOUS_PARTIAL_FRAME` | Nimm den Drogeneintrag »cheo« und den Drogenposten und stelle den Drogeneintrag »cheo« und den Drogenposten ein. |

`G485-E118 CH+T` trifft `CH+@ACTION` als ganzen Event. `G485-E133 CH+T+Y` trägt denselben Rahmen als Präfix und zusätzlich `@ACTION+Y` als Suffix. Damit erscheint EINSTELLEN lokal nicht als freies Einzelwort, sondern mit einem linken Handlungsnachbarn und einem rechten Argumentnachbarn.

## Zwei typisierte Kompositionskanten

| Kante | Richtung | lokale Kontakte | GDT428-Rahmen | Rolle |
|---|---|---:|---|---|
| `EINSTELLEN — NEHMEN` | BEFORE_EINSTELLEN | 2 | `CH+@ACTION` | `LOCAL_COMPOSITION_PLUS_EXTERNAL_T_R_SUBSTITUTION_FRAME` |
| `EINSTELLEN — POSTEN` | AFTER_EINSTELLEN | 1 | `@ACTION+Y` | `LOCAL_COMPOSITION_PLUS_EXTERNAL_T_R_SUBSTITUTION_FRAME` |

In Werkstattdeutsch ist die beobachtete Form konkret: links „nimm … und stelle … ein“, rechts „… sowie den Posten … stelle beide ein“. Das sind die zwei vorhandenen Lesungen, keine analog ergänzten Sätze.

## Der letzte Singleton ist typisiert verbunden

`EINSTELLEN —KOMPOSITION→ POSTEN —G486 WIEDERKEHRENDER ERSATZ→ HIER —G486 SINGLETON-ERSATZ→ EINSTELLEN`

Der Weg ist vollständig, aber absichtlich gemischt: Die erste Kante ist Komposition, die zweite eine zweimal wiederkehrende Ersatzkante. Deshalb bleibt `EINSTELLEN ↔ HIER` **kein reiner Ersatzzyklus**. Für die Arbeitslesung ist EINSTELLEN nun dennoch direkt an das alte lokale Netz angebunden, ohne einen Ersatzpartner zu erfinden.

## Seitenkapazität

| Seite | Kontextzeugen | Positionen | verschiedene Events | T-Kontakte |
|---|---:|---:|---:|---:|
| f17r | 0 | 0 | 0 | 0 |
| f71v | 19 | 19 | 12 | 0 |
| f72r | 97 | 101 | 68 | 1 |
| f77r | 5 | 5 | 4 | 0 |
| f88v | 6 | 6 | 5 | 2 |
| f89r | 41 | 44 | 32 | 0 |

## Nächster Schritt

Die beiden echten T-Kompositionskanten können nun in ein kleines vorhersagendes Satzmuster überführt werden: bekannte T-Rahmen mit WERT, ANTEIL, ZIELORT, FORTSETZEN oder POSTEN erhalten nur dann eine konkrete Formulierung, wenn die entsprechende GDT428-T-Seite selbst einen lesbaren Träger liefert. Der fehlende Kontext `CHD+Y` bleibt offen; aus bloßer Nachbarschaft wird kein Satz erfunden.
