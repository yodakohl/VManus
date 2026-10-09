# GDT1211 — eine abweichende Wortform pro Zeile reicht nicht im ganzen Vergleich

**ONE_VARIANT_PER_LINE_CAPACITY_EXCLUDED.** Zwei der zwölf notwendigen
Buch-/Leserfälle scheitern. Beide betreffen die Quelle gr1 und die Konzentration
der häufigsten zehn Formen; die anderen zehn Fälle bleiben unter dieser
optimistischen Schranke nicht ausgeschlossen. Das ist ein enger Quellen-/
Projektionsbefund, keine allgemeine Widerlegung von Kürzung oder Platzdruck.
Keine neue Wortbedeutung, kein vollständiger Schreiber.

## Vertrag und vollständiges Ergebnis

Außer an höchstens einer Position je berührter Schriftzeile wird jedes genaue
Quellwort durch eine feste ganze Form dargestellt. Jede Quelleinheit bleibt eine
nichtleere Ausgabegruppe. Änderungen dürfen beliebig viele Varianten haben und
an beliebigen Positionen liegen; sogar Unlesbarkeit wäre für die optimistische
Schranke erlaubt. Eine wirkliche Zeilenendkürzung hat weniger Freiheit.
[Methode](METHOD.md) und [Vorregistrierung](PREREGISTRATION.md) sind vor der
Zählung gehasht; alle Quellen/Zielzusammenfassungen waren schon exponiert.

Die exakt rekonstruierte1174-Auswahl umfasst je8.000zulässige Gruppen.
Sie berührt1.000IT-,1.171RF- und1.160ZL-Transkriptionszeilen. Angeschnittene
Zeilen sind eingeschlossen; getrennte erhaltene Fragmente derselben Zeile
zählen einmal. Die unterschiedliche Zeilenzahl entsteht in den jeweiligen
gefilterten Leserproben, nicht aus drei unabhängigen Manuskripten.

Bei D verschiedenen Quellformen, S10Vorkommen ihrer zehn häufigsten Formen und
höchstens K veränderten Vorkommen gilt D_out<=D+K und S10_out>=S10-K.
K darf hier die Zahl berührter Zeilen nicht überschreiten. Die unveränderten
Toleranzen erlauben jeweils400Formen bzw.Top10Vorkommen Abstand von den
beobachteten8.000er-Werten. Jede Leserbedingung bleibt getrennt.

|Quelle|Basistypen|Basis-Top10|nötige Änderungen mindestens IT/RF/ZL|Schranke IT/RF/ZL|
|---|---:|---:|---|---|
|b4|1131|2418|953 /1010 /988|offen /offen /offen|
|w1|1275|2263|798 /855 /833|offen /offen /offen|
|bs1|1105|2364|946 /1025 /995|offen /offen /offen|
|gr1|1199|2587|1122 /1179 /1157|scheitert /scheitert /offen|

Alle zwölf Typenzahl-Obergrenzen reichen formal aus. Nur gr1s Top10-Untergrenze
verletzt zwei Bedingungen: IT mindestens1.587Vorkommen bei höchstens1.465,
RF mindestens1.416bei höchstens1.408. Das sind122bzw.8fehlende Änderungen
unter dem jeweiligen Ein-pro-Zeile-Budget. ZL liegt mit mindestens1.427knapp
unter der erlaubten1.430. Der kleine RF-Abstand wird weder verschwiegen noch
zur nachträglichen Toleranzänderung benutzt. Die Originalentscheidung verlangt
alle zwölf Fälle; sie scheitert. Die zehn offenen Fälle werden nicht als
vollständige oder gleichzeitig erreichbare Schreibererfolge ausgegeben.

Die notwendigen Änderungsschwellen liegen je nach Quelle/Leser zwischen
798und1.179von8.000Vorkommen (9,975–14,7375Prozent). Das sind Untergrenzen
für den angenommenen Vergleich, keine gemessene Änderungsrate des Manuskripts.
Bei festem Wortcode können K Ersatzvorkommen höchstens K neue Formen erzeugen
und der ursprünglichen Kopfmenge höchstens K Vorkommen entziehen. Kollisionen,
wiederverwendete Kurzformen oder engere Zulässigkeit können die Schranke nicht
verbessern. Ihr Bestehen wäre aber nicht hinreichend.

## Quellen- und Auswahlgrenzen

1202s gespeicherte genaue Editions-Tokens bleiben unverändert, einschließlich
Großschreibung und Interpunktion. Die8.000er-Zielprobe verwirft unklare Ränder
und Zeichen außerhalb des22er-Arbeitsinventars; es sind nicht8.000aufeinander-
folgende physische Wörter. Die Aussage ist deshalb bedingt auf die bestehende
Projektion und eine Quelleinheit pro ausgewählter Gruppe. Keine Behauptung,
eine unbekannte tatsächliche Ausgangssprache habe dieselbe Basisverteilung.
Keine Quelle wurde als Voynich-Klartext ausgewählt.

Die Manuskriptseiten waren bereits in1170/1174zugelassen und exponiert. Nur
berührte Zeilen wurden zusätzlich gezählt; keine Bildbreite, kein neuer Scan,
kein verfügbarer rechter Anschlag und keine kausale Schreibentscheidung wurde
gemessen. Physische Zeile bedeutet die vorhandene Transkriptionszeilen-ID.
ZL/IT/RF sind alternative Lesungen; ihre Bedingungen sind keine unabhängigen
Bestätigungen. Mehrere Änderungen pro Zeile, eine andere Grundsprache oder
Gruppierung bleiben außerhalb des Vertrags und werden hier nicht angehängt.

## Vorgänger und Entscheidung

1202schloss höchstens zwei Schreibweisen je Quellwort aus, unabhängig von ihrer
Zahl veränderter Vorkommen. Hier sind beliebig viele Schreibweisen erlaubt,
aber nur begrenzt viele veränderte Positionen. Es ist ein anderer Falsifikator;
kein neuer Lauf des Zwei-Varianten-Schreibers.801/802s Zeilenrand-/Familieneffekt
bleibt, ohne ihn als Kürzung oder Gleichbedeutung zu interpretieren. IDEA200s
Kontext-/Restlängenfrage und die zurückgestellten Breitenideen bleiben separat.
Die heutige Vertragsprüfung war keine Ausführung dieser alten Rohkarte.

Für den festgelegten Gesamtvergleich keine Kürzeltabelle oder Breitenoptimierung
bauen. Die drei nicht ausgeschlossenen Quellen liefern lediglich eine offene
Kapazität, keine bevorzugte Sprache und keinen funktionierenden Mechanismus.
Eine spätere Änderung benötigt einen ausdrücklich anderen vollständigen
Vertrag; kein automatisches Erhöhen der Änderungszahl. Diese Prüfung ist
Konstruktionskritik und kein Entzifferungsfortschritt durch übersetzte Wörter.

## Reproduktion und Validierung

Lauf: `python experiments/yolo/gdt1211_one_variant_per_line_capacity/src/run.py`
Prüfung: `python experiments/yolo/gdt1211_one_variant_per_line_capacity/src/validate.py`
Ein sauberer Reproduktionsstand ohne bestehendes Ergebnis ist erforderlich.
REGISTRATION_LOCK bindet18Eingaben/Programme vor dem Lauf21:56:23UTC.
Der erste METHOD-Patch traf nur die Schablonenüberschrift nicht; er änderte
keine Datei und wurde vor Registrierung korrigiert. Keine Ergebnisreparatur.

Der getrennte Validator zählt sämtliche Quellwörter aus1177erneut, rekonstruiert
mit eigenem22-Zeichen-Regex genau dieselben24.000Zielgruppen-IDs/Zeilen und
bestätigt alle alten Typen-/Top10-Werte sowie zwölf Entscheidungen.37.448kleine
vollständige Ersatzfälle prüfen die allgemeinen Typen-/Top-m-Schranken mit
Zusammenfällen und neuen Formen. PASS ist Quellen-/Auswahl-/Rechenprüfung
des gleichen Autors, keine unabhängige Manuskriptbestätigung. Der Produzent
hatte nur die Vertragslogik/Vorgänger gesehen; er kennt dieses Ergebnis nicht.
Lokaler Konstruktionscheckpoint nach bestehender Ausnahme, kein Push.
