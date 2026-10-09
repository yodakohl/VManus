# GDT1250 — leeres Absatzgedächtnis widerspricht obligatorischen Verweisen

**DISJOINT_RESET_CACHE_CONTRADICTED.** Fünf vollständige Formen in ZL3b,
acht in IT2a und fünf in RF1b stehen sowohl in unmittelbaren inneren
Doppelungen als auch am Anfang eines übereinstimmend markierten Absatzes.
Damit scheitert der unten festgelegte Verweisschreiber unabhängig von seiner
Speichergröße. Keine Wortbedeutung, keine allgemeine Widerlegung von Kurzschrift.

## Vorher festgelegte Konstruktion

Ein Quellwort erzeugt eine vollständige Schriftgruppe. Ein noch nicht
vorhandenes Wort wird mit einer global eindeutigen Vollschreibung geschrieben
und sofort gespeichert; beim nächsten Quellwort ist es noch verfügbar. Ein
bereits gespeichertes Wort MUSS als Verweis erscheinen. Vollschreibungen und
Verweisformen sind global getrennte Mengen. An jedem geprüften Absatzanfang
ist das Gedächtnis leer; kein unsichtbarer Vorspann oder vorgefülltes Wörterbuch.
Innerhalb einer physischen Zeile gibt es keinen versteckten Neustart.

Bei `X X` können nicht beide X Vollschreibungen sein: Nach dem ersten wäre
sein Wort gespeichert und müsste als Verweis erscheinen. Wegen der getrennten
Formmengen ist X daher eine Verweisform. Am leeren Absatzanfang muss dagegen
eine Vollschreibung stehen. Eine Form in beiden Populationen widerspricht der
Konstruktion, gleichgültig wie viele Speicherplätze oder welche Zeichenwerte
verwendet werden. FIFO/LRU/Move-to-front ändern dieses Argument nicht, sofern
die unmittelbare Speicherung erhalten bleibt.

Die frühere Adressgrenze58/50/36 erlaubte ausdrücklich überlappende Modi und
verwendete keine Absatzanfänge. Deren Befund bleibt unverändert. Hier werden
zusätzliche Annahmen geprüft; es ist kein erneuter Größenvergleich.

## Ergebnis und vollständige Auswahl

| Lesung | innere Doppelungen / Typen | Absatzanfänge / Typen | widersprüchliche Typen |
|---|---:|---:|---|
| ZL3b |192 /80|557 /438|dain, okedy, otedy, qokeedy, qokeey|
| IT2a |219 /87|652 /493|dain, okedy, ol, otedy, qokeedy, qokeey, qotol, sho|
| RF1b |158 /67|561 /447|dain, otedy, qokeedy, qokeey, qotol|

Das sind alternative Lesungen derselben Handschrift. Die Zahlen werden nicht
zusammengezählt. ZL3b war vorab die Hauptlesung. Für655 physische Textloci stimmen
ZL/IT-Erstgruppen in P-Art und Absatzanfangsflag1 überein. Dieses Flag wird auf
alle Lesungen projiziert; das bekannte RF-Metadatenproblem wird nicht ignoriert.
Zusätzliche strikte Abstands-/Rohformfilter erklären die kleineren Nenner.

Eine Doppelung muss innerhalb einer Prosa-Zeile liegen und tatsächliche
Nachbarn auf beiden Außenseiten besitzen. Alle drei Fugen müssen beidseitig
DEFINITE_SPACE und die Indizes aufeinanderfolgend sein. Anfangsformen müssen
Index1, LINE_START und rechts DEFINITE_SPACE oder LINE_END haben. Nur exakte
kleingeschriebene ASCII-Gruppen zählen; Entities werden nicht normalisiert.
Alle Ereignisse stehen in EVENTS.json; alle18 lesungsspezifischen Typzeugen
mit vollständigen Zeilen und Rohgrenzen in WITNESSES.json. Keine Auswahl nur
besonders überzeugender Treffer und kein nachträglich veränderter Filter.

Ein gleichseitiges ZL-Beispiel:

```
f103r.33: qokeey chechy qokey shckhy choldy qokal y shedy yteedy qotail shedy
f103r.46: chol keey qokeey cheol chorol shedy qokeey qokeey ol loiin chedan
```

Der Absatzanfang in .33 und die innere Doppelung an Gruppen7–8 in .46 sind
unter dem festgelegten Transkriptions-/Metadatenvertrag der Widerspruch. Eine
neue Bildprüfung dieser Stellen wurde nicht durchgeführt. Gleich geschriebene
Verweise könnten bei wechselndem Speicherinhalt Unterschiedliches bezeichnen;
auch daraus folgt weder Synonymie noch eine Übersetzung.

## Grenzen und Entscheidung

Ausgeschlossen ist die GEMEINSAME Konstruktion aus obligatorischem Speichern/
Verweisen, global getrennten Formmengen, einer Operation pro Gruppe und leeren
Absatzanfängen. Nicht ausgeschlossen sind überlappende Modi mit einem lesbaren
Zustandsparser, fakultative Vollschreibungen, selektive Speicherung, andere
Einheiten oder unabhängig begründete andere Rücksetzstellen. Diese Alternativen
werden nicht nachträglich eingebaut oder als bestätigt behandelt.

Der Absatz ist hier durch die vorhandenen Quellflags operationalisiert, nicht
als eigenständige historische Mitteilung bewiesen. Die Transkriptionen und die
Wortgrenzen bleiben Voraussetzungen. Keine Signifikanz, Kontrollkorpuswahl,
Sprachidentifikation, neue Glyphenidentität oder semantische Relationsevidenz.

Keinen größeren Cache oder Decoder für diesen Vertrag bauen. Die vorhandenen
Wortfamilien und anderen positiven Strukturtests bleiben unberührt.

## Reproduktion und Prüfung

SPEC/METHOD wurden lokal um07:43:37UTC am7.Oktober2026 gespeichert; Code-Lock
um07:46:41UTC vor dem Ziel-Lauf.9837 kleine künstliche Quellenfolgen prüfen
vor Zielzugriff die behauptete Notwendigkeit im disjunkten MTF-Beispiel.
Der eigentliche Runner liest die bereits guarded1170-Wörter. Nur Absatzmetadata
werden erneut durch den179-Selektoren-Guard gelesen; f84/f84r bleiben davor
gesperrt. Keine neuen Wortdaten, Bilder, Reserven oder unabhängige Bestätigung.

Der getrennt implementierte Validator rekonstruiert Ereignisse mit SQL-Joins
statt den Runner zu importieren; alle Mengen, Konflikte und vollständigen
Zeugenzeilen stimmen überein. **PASS** betrifft Rechnung und Quellenabbildung,
nicht historische Absatzidentität oder Lesungsrichtigkeit. Gleicher Autor.

```
python experiments/yolo/gdt1250_cache_reset_doublet_conflict/src/run.py
python experiments/yolo/gdt1250_cache_reset_doublet_conflict/src/validate.py
```

Wiederholung nutzt den hashgebundenen Metadatencache. Originale Eingaben,
Auswahl und Code sind im Manifest und REGISTRATION_LOCK.json gebunden.
Lokaler Konstruktionscheckpoint gemäß bestehender Nutzerausnahme; kein Push.
