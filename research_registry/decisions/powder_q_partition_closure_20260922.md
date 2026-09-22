# Gemeinsames q: neue Einschränkung, keine vollständige Wortzerlegung

22. September 2026. Entscheidung aus dem vorab begrenzten Entwicklungsversuch
14:48–15:25 UTC. Grundlage: `powder_q_composition_development_decision_20260922.md`
und die vor Angebotsprüfung geschriebenen Anforderungen in
`powder_q_partition_requirement_review_20260922.md`.

Das eingefrorene Angebot
`research_registry/proposals/raw370_q_partition_composition_offer_20260922.json`
(SHA256 57808d1291a9b47839e047112ea5395e76a647f7c22986f62b6807d9818845c1)
enthält alle 65+15 Formen, 238 Leserpositionen und 18 Konstruktionen. Der
beiliegende Validator rekonstruiert die unveränderten Übernahmen und sämtliche
q-Positionen einschließlich des bekannten f4r. Kein neuer Manuskriptzugriff.

| Ganzwort / Basis | Konkrete zusätzliche Konsequenz | Prüfergebnis |
|---|---|---|
| qotaiin / otaiin | Auch f32v.8 muss ein Sieb verwenden. | Neue methodische Einschränkung, keine unabhängige Beobachtung. Die alte Trennung war methodenoffen. |
| qotchol / otchol | Das grobe Mahlgut muss Ausgang des lokal gebundenen Rahmens sein. | Mit den geschriebenen Fällen verträglich; die alte Ganzwortreferenz leistete einen wesentlichen Teil dieser Bindung bereits. |
| qotchy / otchy | Neue Teilung von C in F/G, anschließend Herausheben beider Produkte. | Ausdrückliche neue Teilhandlungen; bloßes Herausheben im alten C/P-Rahmen reicht nicht. Physische Ausführbarkeit nicht bewiesen. |
| qotey / fehlendes otey | WATER müsste aus einer Basis und einem passenden Rahmen folgen. | Undefiniert; kein passender Basiswert oder vollständiger Rahmen gegeben. Kein Widerspruch allein aus fehlender Eingabe. |

Ein gemeinsamer Partitionskern ist formulierbar. Seine drei Typanhebungen
bleiben jedoch drei neue Festlegungen, mit jeweils nur einer gepaarten Basis.
Diese Daten unterscheiden eine allgemeine Typregel nicht von drei passend
gebauten Fällen. Die 65 ganzen Werte bleiben nötig; keine Reduktion auf 62.

**Sachkorrektur am eingefrorenen Angebot:** Sein Beispiel f21r.12 als formal
zulässiger Gegenrahmen ist zu stark formuliert: Der Q-Vertrag verlangt zwei
geschriebene Produktbeschreibungen, dort ist der Rest lediglich implizit.
Der Autor meldete dies nach Freeze selbst, ohne Dateien zu ändern. Der
tatsächlich passende vorhandene Gegenrahmen ist f32v.9: zwei geschriebene
Produkte FIBRES/GRANULES, beide weiterhin grob, und WITH_SIEVE. Damit ist
Q(WITH_SIEVE, Π32_SORT) zulässig, ohne SEPARATE_BY_GRADE zu liefern. Dies
widerlegt die behauptbare Gleichheit mit dem vollständigen alten Wortwert,
nicht die Verträglichkeit der neuen zusätzlichen Einschränkung. Das alte
Feinheitskriterium kann nicht aus der bloßen Werkzeugbindung gestrichen werden.

Root prüfte das vollständige Angebot, die alten Rahmen und diese korrigierte
Gegeninstanz. Root wirkte an den vorherigen Anforderungen mit; dies ist keine
verblindete unabhängige Bedeutungsprüfung. Der maschinelle PASS betrifft nur
Hashes, vollständige Übernahmen und Inventar, nicht die englischen Glossen.

**Entscheidung: PARTIAL_NEW_RESTRICTION; EXACT_DECOMPOSITION_NOT_OBTAINED.**
Die neue Siebpflicht und verteilten Teilhandlungen bleiben als explizite
Arbeitsannahmen erhalten. Kein Decoder, keine Simulation oder größere
Korpussuche auf dieser Grundlage. Weiterführung benötigt einen neuen ganzen
Fall mit vorhandener Basis und unabhängig festgelegtem Rahmen, an dem die
stärkere Lesung eine andere beobachtbare Konsequenz als die Ganzwortlesung
hat; bloße erneute Verträglichkeit genügt nicht. Der bekannte qotey-Fall und
f4rs fehlende Gesamtbindung bleiben sichtbar. CARRY/FRESH/TWO bleiben offen,
REITERATEDs alte Mengenunverträglichkeit und DRY_STATEs Lücke unverändert.
Keine bestätigte Bedeutung, keine Signifikanz, keine Reserveöffnung.

Als getrennte nächste Kandidatur liegt IDEA000518 vor: eine einheitliche
atomare oder binäre Wortpackung über vollständige frühere Amulett-Lesungen.
Sie ist hier lediglich registriert, noch nicht getestet oder ausgewählt.
