# Elf vollständige Werkstatt-Records nach Mengen-/Zubereitungsabschluss

Jede Aussage behält die sichtbare Kartenreihenfolge. Das Slotmuster ist eine
optionale Werkstatt-Checkliste, keine Behauptung über eine moderne Satzsyntax:

`GEGENSTAND → QUELLE → MENGE → ZUBEREITUNG → ARBEITSGANG → LAUF → ZIEL → GRAD → SCHLUSS`

## H1 — f10r

1. **H1-S001** `OWNER_ITEM>SOURCE>QUANTITY>PREPARATION>OPERATION>FLOW_TRANSFER` — Wurzelteil; säubern; aus demselben Vorrat; zerkleinern; Gefäß; Flüssigkeitszulauf; ersten Auszug auffangen; den laufenden Posten anwenden oder in Arbeit nehmen; vorgeschriebenes Maß; Wurzelteil.
2. **H1-S002** `OWNER_ITEM>OPERATION>STATE_GRADE` — Den laufenden Posten anwenden oder in Arbeit nehmen; gelind erwärmen; mit Vorigem weiter; bereit.

## H2 — f10r

1. **H2-S001** `OWNER_ITEM>QUANTITY>PREPARATION>OPERATION>STATE_GRADE` — Pflanzenspitzen; bereit; Zubereitung; Kraut zerstoßen; durch Tuch; der laufende Posten; dies oder es; der laufende Posten; dies oder es; vorgeschriebenes Maß; der laufende Posten; dies oder es.
2. **H2-S002** `SOURCE>QUANTITY>PREPARATION>OPERATION` — Die nächste Zubereitung; Zubereitung; danach weiter; mit Vorigem weiter; mit der vorigen Zubereitung; mit Vorigem weiter; vorgeschriebenes Maß; aus demselben Vorrat.
3. **H2-S003** `OWNER_ITEM>QUANTITY>PREPARATION>OPERATION>STATE_GRADE` — Glasiertes Gefäß; Zubereitung; Zubereitung; der laufende Posten; dies oder es; weiche Konsistenz; der laufende Posten; dies oder es; Geschwür.

## H3 — f11r

1. **H3-S001** `OWNER_ITEM>QUANTITY>OPERATION>FLOW_TRANSFER>STATE_GRADE>CLOSE` — Blütenkraut; in Wein kochen; durch Tuch wringen; für die vorgeschriebene Zeit stehen lassen; nochmals seihen; klare Flüssigkeit; abkühlen; Ende.
2. **H3-S002** `OWNER_ITEM` — Blütenanteil zurückhalten.
3. **H3-S003** `OWNER_ITEM>SOURCE>QUANTITY>OPERATION` — Vom vorigen Posten nehmen; der laufende Posten; dies oder es; als Trank geben; der laufende Posten; dies oder es; vorgeschriebenes Maß.
4. **H3-S004** `OWNER_ITEM>OPERATION>STATE_GRADE` — Zurückbehaltene Blüten; mit dem vorigen Arbeitsgut weiterarbeiten; bereit; der laufende Posten; dies oder es.

## H4 — f55v

1. **H4-S001** `OWNER_ITEM>QUANTITY>OPERATION>STATE_GRADE>CLOSE` — Auf das vorgeschriebene Maß einstellen; vorgeschriebenes Maß; eine Portion des laufenden Postens; diese Portion; kühl lagern; Ende.
2. **H4-S002** `OWNER_ITEM>QUANTITY>PREPARATION>OPERATION` — Vorgeschriebenes Maß; den laufenden Posten umsetzen oder durcharbeiten; klaren Auszug verwahren.
3. **H4-S003** `OWNER_ITEM>SOURCE>QUANTITY>PREPARATION>OPERATION>STATE_GRADE>CLOSE` — Maß des laufenden Postens; Auszug daraus entnehmen; länger warm halten; weiterführen; Ende.
4. **H4-S004** `OWNER_ITEM>QUANTITY>PREPARATION>OPERATION>TARGET` — Vorgeschriebenes Maß; an der Zielstelle einsetzen; gelind erwärmen; Zubereitung; der laufende Posten; dies oder es; eine Portion der Zubereitung.

## H5 — f56r

1. **H5-S001** `OWNER_ITEM>QUANTITY>PREPARATION>OPERATION>TARGET` — Pflanzenzubereitung; Pflanze; Blütebeginn; vorgeschriebenes Maß; Pflanze; auflegen; die nächste Zubereitung; den laufenden Posten anwenden oder in Arbeit nehmen; Zielstelle.
2. **H5-S002** `OWNER_ITEM>SOURCE>OPERATION>FLOW_TRANSFER>CLOSE` — Vom vorigen Posten nehmen; mit Wasser waschen; den laufenden Posten anwenden oder in Arbeit nehmen; äußerlich anwenden; Ende.
3. **H5-S003** `OWNER_ITEM>OPERATION` — Pflanzenteil; Pflanze; grob zerreiben; den laufenden Posten erneut in Arbeit nehmen.
4. **H5-S004** `OWNER_ITEM>PREPARATION>OPERATION>FLOW_TRANSFER` — Den laufenden Posten anwenden oder in Arbeit nehmen; Auszugsflüssigkeit zugeben; durch Tuch.
5. **H5-S005** `OWNER_ITEM>OPERATION` — Pflanze; den laufenden Posten anwenden oder in Arbeit nehmen; Brusttrank; gebrauchen.
6. **H5-S006** `OWNER_ITEM>QUANTITY>OPERATION` — Den nächsten Posten wählen; je Gabe; vorgeschriebenes Maß.

## B1 — f81v

1. **B1-S001** `OPERATION>FLOW_TRANSFER>CLOSE` — Kurz spülen oder benetzen und den Schritt abschließen.
2. **B1-S002** `SOURCE>QUANTITY>PREPARATION>OPERATION>FLOW_TRANSFER>TARGET>STATE_GRADE>CLOSE` — Auf das vorgeschriebene Maß einstellen; laufende Beckenflüssigkeit; an der Zielstelle einsetzen; aus demselben Vorrat; mit Vorigem weiter; eine Portion; eine weitere Portion zugeben; Zielstelle; mit Vorigem weiter; vor dem Abkühlen; Badezusatz; mit der vorigen Zubereitung; mit Vorigem weiter; mäßige Menge; vorgeschriebenes Maß; an der Zielstelle anhaltend in Kontakt halten; vorgeschriebenes Maß; durch verbundenen Lauf; Arbeitsbewegung abschließen.
3. **B1-S003** `OPERATION>CLOSE` — Mit Vorigem weiter; unter besonderer Bedingung umsetzen; Schluss.
4. **B1-S004** `OWNER_ITEM>OPERATION>STATE_GRADE>CLOSE` — Den laufenden Posten umsetzen oder durcharbeiten; mit Vorigem weiter; kurz oder gewöhnlich ruhen lassen; Schluss.
5. **B1-S005** `OPERATION>FLOW_TRANSFER>CLOSE` — Weiterführen; Schluss.
6. **B1-S006** `QUANTITY>PREPARATION>OPERATION` — Eine Portion zugeben; durch verbundenen Lauf; Badezusatz; abkühlen.
7. **B1-S007** `PREPARATION>OPERATION>CLOSE` — Ansatz umsetzen; Schluss.
8. **B1-S008** `OWNER_ITEM>OPERATION>STATE_GRADE>CLOSE` — Der laufende Posten; dies oder es; mit Vorigem weiter; kurz oder mild erwärmen; mit Vorigem weiter; kurz oder gewöhnlich ruhen lassen; Schluss.
9. **B1-S009** `OPERATION>FLOW_TRANSFER>CLOSE` — Kurz spülen oder benetzen und den Schritt abschließen.
10. **B1-S010** `OPERATION>FLOW_TRANSFER>CLOSE` — Kurz spülen oder benetzen und den Schritt abschließen.
11. **B1-S011** `OWNER_ITEM>OPERATION` — Durch verbundenen Lauf; den laufenden Posten anwenden oder in Arbeit nehmen.
12. **B1-S012** `OWNER_ITEM>OPERATION>FLOW_TRANSFER>STATE_GRADE>CLOSE` — Spülung beginnen; den laufenden Posten kurz anlegen oder benetzen; waschen; Ende.
13. **B1-S013** `FLOW_TRANSFER>CLOSE` — Waschen; Ende.
14. **B1-S014** `OWNER_ITEM>SOURCE>OPERATION>FLOW_TRANSFER>TARGET` — Den laufenden Posten umsetzen oder durcharbeiten; betroffene Stelle; Auslassstelle; mit Vorigem weiter; danach auslassen.
15. **B1-S015** `PREPARATION>OPERATION>CLOSE` — Gefäß füllen; Ansatz umsetzen; Schluss.
16. **B1-S016** `OWNER_ITEM>OPERATION>TARGET>STATE_GRADE>CLOSE` — An der Zielstelle einsetzen; den laufenden Posten anhaltend in Kontakt halten; mit Vorigem weiter; kurz oder gewöhnlich ruhen lassen; Schluss.
17. **B1-S017** `OPERATION>TARGET>CLOSE` — Zielstelle; erste Öffnung; Umsetzung abschließen.
18. **B1-S018** `QUANTITY>OPERATION>TARGET>STATE_GRADE>CLOSE` — Gefäß füllen; Stelle bestreichen; vorgeschriebener Grad; an der Sammelstelle stehen oder absetzen lassen; Schluss.
19. **B1-S019** `STATE_GRADE>CLOSE` — Kurz oder gewöhnlich ruhen lassen; Schluss.
20. **B1-S020** `STATE_GRADE>CLOSE` — Kurz oder mild erwärmen; durch Tuch seihen; Ende.
21. **B1-S021** `TARGET` — Zielstelle.

## B2 — f82r

1. **B2-S001** `OPERATION>CLOSE` — Arbeitsbewegung abschließen.
2. **B2-S002** `OPERATION>FLOW_TRANSFER>CLOSE` — Weiterführen; Schluss.
3. **B2-S003** `OWNER_ITEM>QUANTITY>OPERATION>CLOSE` — Eine Portion zugeben; der laufende Posten; dies oder es; eintauchen oder einweichen und den Schritt abschließen.
4. **B2-S004** `OWNER_ITEM>OPERATION>FLOW_TRANSFER>TARGET>STATE_GRADE>CLOSE` — An der Zielstelle einsetzen; zweite Öffnung; hinausführen; den laufenden Posten anhaltend in Kontakt halten; klar seihen; Ende.
5. **B2-S005** `OWNER_ITEM>QUANTITY>OPERATION>TARGET>CLOSE` — Den laufenden Posten an der Zielstelle einsetzen; durch Tuch; durch verbundenen Lauf; auf das vorgeschriebene Maß einstellen; auf das vorgeschriebene Maß einstellen; gleiche Einstellung; breites Gefäß; abziehen; Ende.
6. **B2-S006** `OWNER_ITEM>OPERATION>TARGET>STATE_GRADE` — Den laufenden Posten danach anhaltend einwirken lassen; an der Zielstelle einsetzen; über der Stelle; den laufenden Posten anwenden oder in Arbeit nehmen.
7. **B2-S007** `OPERATION>CLOSE` — Sauberes Wasser zugeben; Schluss.
8. **B2-S008** `SOURCE>QUANTITY>OPERATION>STATE_GRADE>CLOSE` — Das nächste Maß; daraus in den Arbeitsgang nehmen; kurz oder gewöhnlich ruhen lassen; Schluss.
9. **B2-S009** `STATE_GRADE>CLOSE` — Warm halten; Ende.
10. **B2-S010** `OWNER_ITEM>OPERATION>FLOW_TRANSFER>STATE_GRADE` — Den laufenden Posten anhaltend in Kontakt halten; den laufenden Posten anwenden oder in Arbeit nehmen; erste Öffnung; klare Flüssigkeit.
11. **B2-S011** `SOURCE>QUANTITY>OPERATION>CLOSE` — Eine Portion zugeben; aus demselben Vorrat; eine Portion zugeben; eintauchen oder einweichen und den Schritt abschließen.
12. **B2-S012** `OWNER_ITEM>QUANTITY>OPERATION>FLOW_TRANSFER>TARGET>STATE_GRADE>CLOSE` — Den flüssigen Anteil des laufenden Postens abziehen; klare Flüssigkeit; den laufenden Posten bereit halten; den laufenden Posten anhaltend in Kontakt halten; benetzte Körperstelle; vorgeschriebenes Maß; der laufende Posten; dies oder es; vollständig durchtränken und den Schritt abschließen.
13. **B2-S013** `OPERATION>FLOW_TRANSFER>CLOSE` — Hinausführen; Schluss.
14. **B2-S014** `OPERATION` — Unterer Ablauf.
15. **B2-S015** `OPERATION>CLOSE` — Spülung beginnen; eintauchen oder einweichen und den Schritt abschließen.
16. **B2-S016** `OWNER_ITEM>SOURCE>QUANTITY>OPERATION>FLOW_TRANSFER>TARGET>STATE_GRADE>CLOSE` — Zielstelle; aus der Quelle hinausführen; gleiche Anteile; vorgeschriebenes Maß; den laufenden Posten danach anhaltend einwirken lassen; auf das vorgeschriebene Maß einstellen; den laufenden Posten kurz anlegen oder benetzen; hineinführen; Schluss.
17. **B2-S017** `STATE_GRADE>CLOSE` — Warmes Wasser; zweite Öffnung; Ende.
18. **B2-S018** `OPERATION>CLOSE` — Eintauchen oder einweichen und den Schritt abschließen.
19. **B2-S019** `CLOSE` — Teil als Waschung; Schluss.
20. **B2-S020** `CLOSE` — Danach anhaltend einwirken lassen und abschließen.
21. **B2-S021** `OPERATION>CLOSE` — Eintauchen oder einweichen und den Schritt abschließen.
22. **B2-S022** `OPERATION>FLOW_TRANSFER>CLOSE` — Den Rest hinausführen; Schluss.

## B3 — f83r

1. **B3-S001** `TARGET>STATE_GRADE>CLOSE` — An der Sammelstelle stehen oder absetzen lassen; Schluss.
2. **B3-S002** `TARGET>CLOSE` — Danach zur Zielstelle; vollständig benetzen; Ende.
3. **B3-S003** `OWNER_ITEM>QUANTITY>OPERATION>FLOW_TRANSFER>CLOSE` — Der laufende Posten; dies oder es; vorgeschriebenes Maß; der laufende Posten; dies oder es; hinausführen; Schluss.
4. **B3-S004** `SOURCE>QUANTITY>OPERATION>TARGET` — Auf das vorgeschriebene Maß einstellen; danach zur Zielstelle; aus demselben Vorrat.
5. **B3-S005** `OPERATION>CLOSE` — Arbeitsbewegung abschließen.
6. **B3-S006** `OWNER_ITEM>OPERATION>FLOW_TRANSFER>TARGET>CLOSE` — Den laufenden Posten zuführen oder umsetzen; an der Zielstelle einsetzen; weiterführen; Schluss.
7. **B3-S007** `OWNER_ITEM>QUANTITY>OPERATION>CLOSE` — Auf das vorgeschriebene Maß einstellen; den laufenden Posten umsetzen oder durcharbeiten; eintauchen oder einweichen und den Schritt abschließen.
8. **B3-S008** `OPERATION>FLOW_TRANSFER>CLOSE` — Hinausführen; Schluss.
9. **B3-S009** `OWNER_ITEM>OPERATION` — Den laufenden Posten anwenden oder in Arbeit nehmen.
10. **B3-S010** `OPERATION>FLOW_TRANSFER>TARGET>CLOSE` — Einfüllstelle; danach kurz oder gewöhnlich einwirken lassen und abschließen.
11. **B3-S011** `OWNER_ITEM>OPERATION` — Stelle bestreichen; den laufenden Posten anwenden oder in Arbeit nehmen; den laufenden Posten umsetzen oder durcharbeiten; abkühlen.
12. **B3-S012** `PREPARATION>STATE_GRADE>CLOSE` — Zubereitung; kurz oder gewöhnlich ruhen lassen; Schluss.
13. **B3-S013** `OWNER_ITEM>QUANTITY>OPERATION>FLOW_TRANSFER>STATE_GRADE>CLOSE` — Auf das vorgeschriebene Maß einstellen; eine Portion; den laufenden Posten bereit halten; kurz spülen oder benetzen und den Schritt abschließen.
14. **B3-S014** `OPERATION>FLOW_TRANSFER>STATE_GRADE>CLOSE` — Flüssigkeit in den Lauf bringen; länger ruhen oder nachwirken lassen; Schluss.
15. **B3-S015** `OPERATION>FLOW_TRANSFER>CLOSE` — Hinausführen; Schluss.
16. **B3-S016** `PREPARATION>OPERATION>CLOSE` — Unterer Ablauf; Ansatz umsetzen; Schluss.
17. **B3-S017** `OPERATION>CLOSE` — Eintauchen oder einweichen und den Schritt abschließen.
18. **B3-S018** `STATE_GRADE>CLOSE` — Kurz oder gewöhnlich ruhen lassen; Schluss.
19. **B3-S019** `PREPARATION>OPERATION>STATE_GRADE>CLOSE` — Ansatz zur Ruhe bringen oder absetzen lassen; abschließen.
20. **B3-S020** `OPERATION>FLOW_TRANSFER>TARGET>CLOSE` — Zielstelle; hinausführen; Schluss.
21. **B3-S021** `OWNER_ITEM>QUANTITY>OPERATION>TARGET>STATE_GRADE>CLOSE` — Auf das vorgeschriebene Maß einstellen; bereit; Zielstelle; der laufende Posten; dies oder es; vorgeschriebenes Maß; Ruhe- oder Absetzstelle; warmes Wasser; der laufende Posten; dies oder es; Zielstelle; bereit; lokal umsetzen; Schluss.
22. **B3-S022** `OPERATION>CLOSE` — Danach oder erneut umsetzen; Schluss.
23. **B3-S023** `OPERATION>FLOW_TRANSFER>CLOSE` — Hinausführen; Schluss.
24. **B3-S024** `OPERATION>CLOSE` — Arbeitsbewegung abschließen.
25. **B3-S025** `PREPARATION>OPERATION>CLOSE` — Ansatz umsetzen; Schluss.
26. **B3-S026** `OWNER_ITEM>QUANTITY>OPERATION>TARGET>STATE_GRADE>CLOSE` — Beckenstation; bis zum vorgeschriebenen Stand absetzen lassen; den laufenden Posten umsetzen oder durcharbeiten; eine Portion zugeben; bereit; bis klar; an der Sammelstelle stehen oder absetzen lassen; Schluss.
27. **B3-S027** `CLOSE` — Danach anhaltend einwirken lassen und abschließen.
28. **B3-S028** `OWNER_ITEM>OPERATION>FLOW_TRANSFER>STATE_GRADE>CLOSE` — Den laufenden Posten anhaltend in Kontakt halten; kurz spülen oder benetzen und den Schritt abschließen.
29. **B3-S029** `OPERATION>FLOW_TRANSFER>CLOSE` — Mit Vorigem weiter; erste Spülung; kurz spülen oder benetzen und den Schritt abschließen.
30. **B3-S030** `OWNER_ITEM>QUANTITY>OPERATION>FLOW_TRANSFER>CLOSE` — Den laufenden Posten anwenden oder in Arbeit nehmen; vorgeschriebenes Maß; fließende Flüssigkeit durch den Lauf führen; danach oder erneut umsetzen; Schluss.
31. **B3-S031** `OPERATION>CLOSE` — Eintauchen oder einweichen und den Schritt abschließen.
32. **B3-S032** `OWNER_ITEM>QUANTITY>OPERATION>CLOSE` — Eine Portion umsetzen; den laufenden Posten umsetzen oder durcharbeiten; breites Gefäß; das nächste Maß; danach kurz oder gewöhnlich einwirken lassen und abschließen.
33. **B3-S033** `CLOSE` — Abziehen; Ende.
34. **B3-S034** `QUANTITY>OPERATION>TARGET>STATE_GRADE>CLOSE` — Vorgeschriebener Grad; bereit; zerkleinern; das nächste Maß; untere Zielstelle; kurz oder gewöhnlich ruhen lassen; Schluss.

## B4 — f83r

1. **B4-S001** `OPERATION>CLOSE` — Eintauchen oder einweichen und den Schritt abschließen.
2. **B4-S002** `OWNER_ITEM>OPERATION>FLOW_TRANSFER>STATE_GRADE>CLOSE` — Gefäß füllen; den laufenden Posten anhaltend in Kontakt halten; kurz spülen oder benetzen und den Schritt abschließen.
3. **B4-S003** `OWNER_ITEM>OPERATION>TARGET>STATE_GRADE>CLOSE` — Den laufenden Posten umsetzen oder durcharbeiten; danach zur Zielstelle; den nächsten Posten wählen; den laufenden Posten anhaltend in Kontakt halten; den laufenden Posten anwenden oder in Arbeit nehmen; mit Vorigem weiter; kurz oder gewöhnlich ruhen lassen; Schluss.
4. **B4-S004** `OWNER_ITEM>OPERATION>CLOSE` — Den laufenden Posten als Auflage befestigen; Schluss.
5. **B4-S005** `OWNER_ITEM>OPERATION>CLOSE` — Durch Tuch; den laufenden Posten umsetzen oder durcharbeiten; eintauchen oder einweichen und den Schritt abschließen.
6. **B4-S006** `CLOSE` — Durch Tuch seihen; Ende.
7. **B4-S007** `CLOSE` — Durch Tuch seihen; Ende.
8. **B4-S008** `QUANTITY>OPERATION>FLOW_TRANSFER>STATE_GRADE>CLOSE` — Vorgeschriebenes Maß; länger warm halten; erste Öffnung; kurz spülen oder benetzen und den Schritt abschließen.
9. **B4-S009** `STATE_GRADE>CLOSE` — Kurz oder gewöhnlich ruhen lassen; Schluss.
10. **B4-S010** `CLOSE` — Weiterführen; Ende.
11. **B4-S011** `OWNER_ITEM>QUANTITY>OPERATION>FLOW_TRANSFER>STATE_GRADE>CLOSE` — Vorgeschriebenes Maß; kurz oder mild erwärmen; anhaltende Anwendung mit dem Vorigen fortführen; eine Portion zugeben; den laufenden Posten umsetzen oder durcharbeiten; mit Vorigem weiter; zweimal waschen; Ende.
12. **B4-S012** `OPERATION>FLOW_TRANSFER>CLOSE` — Hinausführen; Schluss.
13. **B4-S013** `OPERATION>STATE_GRADE>CLOSE` — Vorigen Arbeitsgang weiterführen; kurz oder gewöhnlich ruhen lassen; Schluss.
14. **B4-S014** `OWNER_ITEM>PREPARATION>OPERATION>FLOW_TRANSFER>CLOSE` — Zubereitung; der laufende Posten; dies oder es; über der Stelle; den Flüssigkeitslauf abschließen.
15. **B4-S015** `QUANTITY>OPERATION>FLOW_TRANSFER>TARGET>CLOSE` — Eine Portion zugeben; klare Flüssigkeit; eine Portion; Dauer; Sammelstelle kurz öffnen oder aktiv halten; hinausführen; Schluss.
16. **B4-S016** `SOURCE>QUANTITY>OPERATION>TARGET>STATE_GRADE>CLOSE` — Eine weitere Portion zugeben; Zielstelle; erwärmtes Medium ausgießen; kurz oder gewöhnlich ruhen lassen; Schluss.

## B5 — f83r

1. **B5-S001** `OPERATION>CLOSE` — Danach umsetzen; Schluss.
2. **B5-S002** `PREPARATION>OPERATION>CLOSE` — Ansatz umsetzen; Schluss.
3. **B5-S003** `OWNER_ITEM>QUANTITY>OPERATION>TARGET>STATE_GRADE` — Ruhe- oder Absetzstelle; Zielstelle; mit Vorigem weiter; bis warm; an der Zielstelle umsetzen; vorgeschriebenes Maß; mit Vorigem weiter; zweite Öffnungsstufe; den laufenden Posten umsetzen oder durcharbeiten.

## B6 — f83r

1. **B6-S001** `OWNER_ITEM>QUANTITY>OPERATION>TARGET>STATE_GRADE` — Sammelstelle länger offen halten; ungekocht; erste Öffnung; mit Vorigem weiter; vorgeschriebenes Maß; mit Vorigem weiter; durch Tuch; der laufende Posten; dies oder es; bezeichnete Zielstelle.
