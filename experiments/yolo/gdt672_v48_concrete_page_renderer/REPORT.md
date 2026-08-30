# GDT672 — konkreter V48-Seitenrenderer

## Ergebnis

f1r ist jetzt vollständig vierstufig lesbar: 214/214 EVA-Token, 214/214 unveränderte Kartenwerte, siebzehn explizite Mengenbindungen und 28/28 vorsichtige Zeilenlesungen. 129 Positionen bzw. 84 Oberflächen kommen unverändert aus V48. Die übrigen 85 Positionen bzw. 80 Oberflächen erhalten explizite lokale Transferkarten: 54 kompositionelle, 23 gelernte und 8 occurrence-spezifische Stellen.

Die gelernte Schicht wird nicht heimlich als V48-Erfolg gezählt: 19/28 Zeilen enthalten mindestens ein lokales Ganzwort; 9/28 kommen ohne ein solches Ganzwort aus. GDT589s 214-Token-Folge stimmt bytegenau mit der guarded f1r-Quelle überein, dient aber ausschließlich als Vergleich. Seine generische Prosa hat 191 harte Füllworttreffer; die neue Ausgabe hat 0. Sie enthält jedoch weiterhin 85 breite Trägerwörter wie Ansatz, Kompositum oder Species. Das ist sichtbare Restunbestimmtheit, kein verschwundener Befund.

## Was der Renderer tatsächlich tut

V48 liefert Stoff-, Prozess-, Zustands-, Mengen- und Formwerte. Zwölf explizite Regeln binden nur vorhandene Slots: ein Imperativ braucht eine Aktionskarte, Mengen werden am Kopf typisiert, Prozessreihenfolge bleibt erhalten, nominale Zeilen bleiben Katalogzeilen und Unsicherheit bleibt sichtbar. Aus dem lokalen GDT600-Entwurf wurden nur diese Valenz- und Ordnungsprinzipien neu formuliert; seine Wörter `Stationsansatz`, `Arbeitsgang` und `Arbeitsstelle` werden nicht importiert.

Sechs Kontrollpassagen decken sechs Register, zwei Sprachen und drei Hände ab. Fünf sind in V48 vollständig; die sechste hält `dsheody` absichtlich offen. Damit prüft die Ausgabe sowohl konkrete Flüssigkeit als auch Abstinenz.

## Grenze

A complete exploratory f1r working reader: 129/214 positions inherit exact V48 cards; 85/214 positions use explicit f1r transfer cards, of which learned and occurrence-scoped cards are not promoted to V48. This does not establish plaintext, language, phonetics, a historical codebook, a plant identity, a disease, a patient, a cure, or manuscript-wide meanings.
