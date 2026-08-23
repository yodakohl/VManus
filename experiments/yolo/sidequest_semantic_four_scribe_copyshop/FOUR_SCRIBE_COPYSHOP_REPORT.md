# Vier-Schreiber-Kopierwerkstatt

## Ergebnis

Dieselbe Bedeutungs- und Exact-Tuplefolge kann durch vier einfache Schreibprofile laufen, ohne dass ein Schreiber das Wörterbuch ändert oder eine neue Kartenform erfindet. Die Profile sind didaktische Werkstattrollen: bare Meisterform, q nach lokaler Schließung, s am neuen Zeilenanfang und ein kompaktes Mischprofil.

Das Prosa-Inventar enthält 34 exakte Kartenfamilien mit mehr als einer registrierten Oberfläche. Über alle 116 Aussagen entstehen 464 Gegenkopien. 68 Aussagen erhalten unter den vier Profilen mindestens zwei verschiedene sichtbare Folgen; die übrigen besitzen an den betreffenden Stellen nur feste oder für diese Regeln nicht alternative Formen. Alle Tuplefolgen und Bedeutungsrücklesungen bleiben gleich.

Die sechzehn neuen Diktierübungen ergeben 64 Kopien; 10 Übungen werden sichtbar in mindestens zwei Varianten gesetzt. Kein erzeugtes Token liegt außerhalb seiner beobachteten Exact-Tuple-Familie.

## Die vier Rollen

1. **S1 Bare Master:** bevorzugt die erste unmarkierte registrierte Form.
2. **S2 Q Cell Scribe:** nimmt nach einer geschlossenen Karte die q-Form des nächsten Postens, falls diese bereits zur Familie gehört.
3. **S3 S Line Scribe:** bricht nach drei Karten um und nimmt am neuen Zeilenanfang die registrierte s-Form.
4. **S4 Mixed Compact:** schreibt vier Karten je Zeile, kombiniert s-Zeilenanfang und q-nach-Schluss und benutzt sonst die kürzeste registrierte Form.

## Was der Lehrling tatsächlich lernen muss

Die Bedeutungsseite endet vor dem Renderer: Meisterbefehl -> Makros -> Exact Tuple. Erst dann folgt: lokale Position -> registrierte Oberfläche. Dadurch können mehrere Schreiber dieselbe Werkstattanweisung unterschiedlich aussehen lassen, ohne Synonyme, andere Lautungen oder andere Fachwörter anzunehmen.

Im vollständigen Tokenprotokoll verteilen sich die Entscheidungen auf {'BARE_REGISTERED_FALLBACK': 995, 'SHORTEST_REGISTERED_FALLBACK': 339, 'REGISTERED_S_LINE_ENTRY': 136, 'FIXED_OR_MARKED_ONLY_FALLBACK': 192, 'REGISTERED_Q_AFTER_COMMIT': 70}. Gegenüber den jeweils vorliegenden Ausgangsoberflächen ändern die Profile zusammen {'S1_BARE_MASTER': 146, 'S2_Q_CELL_SCRIBE': 128, 'S3_S_LINE_SCRIBE': 142, 'S4_MIXED_COMPACT': 124} Tokens in den 464 Aussagekopien.

Die vier Profile sind kreative Ausführungsmodelle und keine Zuweisung an reale Handschriftenhände. `FOUR_HAND_116_STATEMENT_RENDERINGS.tsv` enthält alle Aussagekopien, `FOUR_HAND_16_EXERCISE_RENDERINGS.tsv` die neuen Diktierübungen, und `RENDERER_TOKEN_TRACE.tsv` begründet jede einzelne Formwahl.
