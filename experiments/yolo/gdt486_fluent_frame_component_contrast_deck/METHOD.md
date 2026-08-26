# GDT486 — Methode

## Question

Ändert ein einzelner funktionaler Komponentenwechsel innerhalb desselben
GDT485-Satzrahmens stets genau die passende lesbare Bedeutung, oder entstehen
Widersprüche, die eine Wörterbuchbedeutung unter Druck setzen?

## Inputs

- GDT485: 135 flüssige/technische Recordzeilen;
- GDT485: 183 Event-Rückprojektionen mit normalisierten Komponenten und
  Eventgrenzen.

## Method

1. Jeder Record erhält eine lesbare Satzklasse. Anweisungen werden nach ihrer
   ersten Handlung, Kataloge nach Einzel-/Folge-/Fortsetzungsform und
   Koordinaten nach Einzel-, Danach-, Mehrfach- oder Sequenzspur geordnet.
2. Zwei Records werden nur verglichen, wenn Register, aktive Modellfolge,
   lesbare Satzklasse, Eventzahl, Komponentenzahl und Separatorfolge gleich
   sind.
3. Die flachen Komponentenfolgen müssen an genau einer Position verschieden
   sein. Wechsel eines gelernten Namen-/Familienplatzes werden ausgeschlossen.
4. Der strenge Stapel verlangt zusätzlich dieselbe physische Seite. Die
   Erweiterung erlaubt verschiedene Seiten desselben Registers; sie ändert
   keine Seite und öffnet kein neues Material.
5. Gelernte Namen werden nur für den deutschen Textvergleich durch `{NAME}`
   ersetzt. Ein Token-Diff zeichnet jede ersetzte, gelöschte oder eingefügte
   deutsche Wortspanne auf.
6. Paare werden nach aktivem Modell, lesbarer Satzklasse und ungeordnetem
   Komponentenwechsel gruppiert. Eine wiederkehrende Gruppe ist exakt, wenn
   alle Paare dieselbe deutsche Änderungssignatur besitzen. Mehrere Signaturen
   verlangen entweder eine konkrete Grammatik-/Zählungserklärung oder werden
   als Wörterbuchdruck markiert.
7. Für beide Seiten jedes Paars muss ein expliziter deutscher Hinweis auf den
   jeweiligen Arbeitswert sichtbar sein, etwa `Ausgang`, `Ziel`, `Posten`,
   `Wert`, `halte`, `stelle` oder `fort`.

## Decision rule and claim ceiling

Ein Wörterbuchwert bleibt unbelastet, wenn jede Mehrfachsignatur vollständig
durch den unveränderten Satzkontext erklärt wird und beide Bedeutungsmarker
sichtbar bleiben. Eine nicht erklärte Mehrfachsignatur wird nicht geglättet,
sondern als `DICTIONARY_PRESSURE` ausgegeben.

Der Stapel prüft die interne Redaktion derselben Arbeitstheorie; er bestätigt
die Grundwerte nicht unabhängig. Keine Wurzel, Bedeutung, Namensidentität,
Modellwahl, Grenze, Oberfläche, Rezept, Event oder Seite darf geändert werden.
