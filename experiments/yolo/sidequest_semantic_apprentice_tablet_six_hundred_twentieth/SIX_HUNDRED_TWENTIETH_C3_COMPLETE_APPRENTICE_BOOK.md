# Fall C3: Lehrlingsbuch

Fallstoff: Blütenauszug der H3-Bildpflanze. Anwendung: Blütenwaschung oder Eintauchfolge an den B3-Stationen.

Der Meister nennt Besitzer, Fallstoff und Module. Der Lehrling spricht die 39 Wortwerte und kopiert danach die lokale exakte Karte aus dem C3-Exemplar.

## 1. H3-S001

Eingang: `RAW_FLOWER_MATERIAL`

Bild/Station: abgebildete dicht blau blühende Kronenpflanze

Module: M01_DOSIEREN → M03_ADRESSIEREN_WEITERLEITEN → M04_HALTEN_ABSETZEN → M06_FORTSETZEN → M08_SCHLIESSEN

Karten: `tshol schoal cfhy shfydaiin cphy shey tchody`

Sprechen: EINTRAGEN · HALTEN · FORTSETZEN | HALTEN · ARBEITSGANG · ZIELSTELLE | AUSWRINGEN · ARBEITSPOSTEN | HALTEN · ARBEITSPOSTEN · SOLLMASS | EINFUELLEN · ARBEITSPOSTEN | HALTEN · LANG · ARBEITSPOSTEN | EINTRAGEN · ABNEHMEN · ARBEITSGANG; SCHLUSS

Ausgang: `STEP_CLOSED`

## 2. H3-S002

Eingang: `STEP_CLOSED`

Bild/Station: abgebildete dicht blau blühende Kronenpflanze

Module: M04_HALTEN_ABSETZEN

Karten: `shoyty`

Sprechen: ARBEITSPOSTEN HALTEN · IM ARBEITSGANG EINTRAGEN · ARBEITSPOSTEN

Ausgang: `HELD_OR_SETTLED`

## 3. H3-S003

Eingang: `HELD_OR_SETTLED`

Bild/Station: abgebildete dicht blau blühende Kronenpflanze

Module: M01_DOSIEREN → M06_FORTSETZEN

Karten: `dchol chy kchy dy daiin`

Sprechen: WIEDERAUFNEHMEN | ARBEITSPOSTEN | ZUDOSIEREN · ARBEITSPOSTEN | ARBEITSPOSTEN | SOLLMASS

Ausgang: `CONTINUING`

## 4. H3-S004

Eingang: `CONTINUING`

Bild/Station: abgebildete dicht blau blühende Kronenpflanze

Module: M02_ANSETZEN_BEHANDELN → M06_FORTSETZEN → M07_BEREITSCHAFT_PRUEFEN

Karten: `qotchy okchol cthy dy`

Sprechen: DANACH · ARBEITSPOSTEN | ANSETZEN · FORTSETZEN | BEREIT · ARBEITSPOSTEN | ARBEITSPOSTEN

Ausgang: `READY`

## 5. B3-S001

Eingang: `READY`

Bild/Station: obere offene Fächerstation am Rand

Module: M05_AUFFANGEN → M08_SCHLIESSEN

Karten: `olkeedy`

Sprechen: AUFFANGEN · LANG; SCHLUSS

Ausgang: `STEP_CLOSED`

## 6. B3-S002

Eingang: `STEP_CLOSED`

Bild/Station: obere offene Fächerstation am Rand

Module: M03_ADRESSIEREN_WEITERLEITEN → M06_FORTSETZEN → M08_SCHLIESSEN

Karten: `qotal chkeedy`

Sprechen: DANACH · ZIELSTELLE | WAERMEN · LANG; SCHLUSS

Ausgang: `STEP_CLOSED`

## 7. B3-S003

Eingang: `STEP_CLOSED`

Bild/Station: obere offene Fächerstation am Rand

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `chey daiin chey lchedy`

Sprechen: ARBEITSPOSTEN | SOLLMASS | ARBEITSPOSTEN | WEITERLEITEN · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 8. B3-S004

Eingang: `STEP_CLOSED`

Bild/Station: obere offene Fächerstation am Rand

Module: M01_DOSIEREN → M02_ANSETZEN_BEHANDELN → M03_ADRESSIEREN_WEITERLEITEN → M06_FORTSETZEN

Karten: `qokaiin qotal dar`

Sprechen: ANSETZEN · SOLLMASS | DANACH · ZIELSTELLE | VORRAT

Ausgang: `CONTINUING`

## 9. B3-S005

Eingang: `CONTINUING`

Bild/Station: mittlere Randfigur im runden Gefäß

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `schedy`

Sprechen: UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 10. B3-S006

Eingang: `STEP_CLOSED`

Bild/Station: mittlere Randfigur im runden Gefäß

Module: M02_ANSETZEN_BEHANDELN → M03_ADRESSIEREN_WEITERLEITEN → M06_FORTSETZEN → M08_SCHLIESSEN

Karten: `chedchy qokal olchedy`

Sprechen: UMSETZEN · ARBEITSPOSTEN | ANSETZEN · ZIELSTELLE | FORTSETZEN · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 11. B3-S007

Eingang: `STEP_CLOSED`

Bild/Station: mittlere Randfigur im runden Gefäß

Module: M01_DOSIEREN → M02_ANSETZEN_BEHANDELN → M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `qokaiin chedy qokeedy`

Sprechen: ANSETZEN · SOLLMASS | UMSETZEN · ARBEITSPOSTEN | ANSETZEN · LANG; SCHLUSS

Ausgang: `STEP_CLOSED`

## 12. B3-S008

Eingang: `STEP_CLOSED`

Bild/Station: mittlere Randfigur im runden Gefäß

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `lchedy`

Sprechen: WEITERLEITEN · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 13. B3-S009

Eingang: `STEP_CLOSED`

Bild/Station: mittlere Randfigur im runden Gefäß

Module: M02_ANSETZEN_BEHANDELN

Karten: `qoky`

Sprechen: ANSETZEN · ARBEITSPOSTEN

Ausgang: `IN_TREATMENT`

## 14. B3-S010

Eingang: `IN_TREATMENT`

Bild/Station: untere Randfigur im korbartigen Gefäß

Module: M03_ADRESSIEREN_WEITERLEITEN → M06_FORTSETZEN → M08_SCHLIESSEN

Karten: `pchedal otedy`

Sprechen: EINFUELLEN · UMSETZEN · ZIELSTELLE | DANACH · KURZ; SCHLUSS

Ausgang: `STEP_CLOSED`

## 15. B3-S011

Eingang: `STEP_CLOSED`

Bild/Station: untere Randfigur im korbartigen Gefäß

Module: M02_ANSETZEN_BEHANDELN → M03_ADRESSIEREN_WEITERLEITEN → M04_HALTEN_ABSETZEN → M07_BEREITSCHAFT_PRUEFEN

Karten: `shecthedchy qoky chedy chary`

Sprechen: HALTEN · KURZ · BIS BEREIT; UMSETZEN · ARBEITSPOSTEN | ANSETZEN · ARBEITSPOSTEN | UMSETZEN · ARBEITSPOSTEN | VORRAT · ARBEITSPOSTEN

Ausgang: `READY`

## 16. B3-S012

Eingang: `READY`

Bild/Station: untere Randfigur im korbartigen Gefäß

Module: M04_HALTEN_ABSETZEN → M08_SCHLIESSEN

Karten: `sor shedy`

Sprechen: ANSATZ | ABSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 17. B3-S013

Eingang: `STEP_CLOSED`

Bild/Station: untere Randfigur im korbartigen Gefäß

Module: M01_DOSIEREN → M02_ANSETZEN_BEHANDELN → M07_BEREITSCHAFT_PRUEFEN → M08_SCHLIESSEN

Karten: `qokaiin chkain shcthey qokedy`

Sprechen: ANSETZEN · SOLLMASS | ZUDOSIEREN · PORTION | BEREIT · KURZ · ARBEITSPOSTEN | ANSETZEN · KURZ; SCHLUSS

Ausgang: `STEP_CLOSED`

## 18. B3-S014

Eingang: `STEP_CLOSED`

Bild/Station: untere Randfigur im korbartigen Gefäß

Module: M02_ANSETZEN_BEHANDELN → M03_ADRESSIEREN_WEITERLEITEN → M04_HALTEN_ABSETZEN → M08_SCHLIESSEN

Karten: `okair sheedy`

Sprechen: ANSETZEN · FLUESSIGKEITSLAUF | HALTEN · LANG; SCHLUSS

Ausgang: `STEP_CLOSED`

## 19. B3-S015

Eingang: `STEP_CLOSED`

Bild/Station: untere Randfigur im korbartigen Gefäß

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `lchedy`

Sprechen: WEITERLEITEN · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 20. B3-S016

Eingang: `STEP_CLOSED`

Bild/Station: untere Randfigur im korbartigen Gefäß

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `lo qokchedy`

Sprechen: WEITERLEITEN · ARBEITSGANG | ANSETZEN · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 21. B3-S017

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M02_ANSETZEN_BEHANDELN → M08_SCHLIESSEN

Karten: `qokeedy`

Sprechen: ANSETZEN · LANG; SCHLUSS

Ausgang: `STEP_CLOSED`

## 22. B3-S018

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M04_HALTEN_ABSETZEN → M08_SCHLIESSEN

Karten: `shedy`

Sprechen: ABSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 23. B3-S019

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M02_ANSETZEN_BEHANDELN → M04_HALTEN_ABSETZEN → M08_SCHLIESSEN

Karten: `qokshedy`

Sprechen: ANSETZEN · HALTEN · KURZ; SCHLUSS

Ausgang: `STEP_CLOSED`

## 24. B3-S020

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `dal lchedy`

Sprechen: ZIELSTELLE | WEITERLEITEN · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 25. B3-S021

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M01_DOSIEREN → M02_ANSETZEN_BEHANDELN → M03_ADRESSIEREN_WEITERLEITEN → M04_HALTEN_ABSETZEN → M07_BEREITSCHAFT_PRUEFEN → M08_SCHLIESSEN

Karten: `qokaiin shcthy dal sy saiin shedal shecthy chey tal shcthy dalchdy`

Sprechen: ANSETZEN · SOLLMASS | BEREIT · ARBEITSPOSTEN | ZIELSTELLE | ARBEITSPOSTEN | SOLLMASS | ABSETZEN · ZIELSTELLE | HALTEN · KURZ · BEREIT · ARBEITSPOSTEN | ARBEITSPOSTEN | ZIELSTELLE | BEREIT · ARBEITSPOSTEN | ZIELSTELLE · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 26. B3-S022

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M03_ADRESSIEREN_WEITERLEITEN → M06_FORTSETZEN → M08_SCHLIESSEN

Karten: `qotchedy`

Sprechen: DANACH · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 27. B3-S023

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `lchedy`

Sprechen: WEITERLEITEN · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 28. B3-S024

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `tchedy`

Sprechen: UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 29. B3-S025

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `qokchdy`

Sprechen: ANSETZEN · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 30. B3-S026

Eingang: `STEP_CLOSED`

Bild/Station: unverbundener Zwischenbereich

Module: M01_DOSIEREN → M02_ANSETZEN_BEHANDELN → M03_ADRESSIEREN_WEITERLEITEN → M05_AUFFANGEN → M07_BEREITSCHAFT_PRUEFEN → M08_SCHLIESSEN

Karten: `cheedar chldaiin chedy qokain checthy chealror solkeedy`

Sprechen: LANG · VORRAT | WEITERLEITEN · SOLLMASS | UMSETZEN · ARBEITSPOSTEN | ANSETZEN · PORTION | BEREIT · ARBEITSPOSTEN | ZIELSTELLE · KUEHLEN · ANSATZ | AUFFANGEN · LANG; SCHLUSS

Ausgang: `STEP_CLOSED`

## 31. B3-S027

Eingang: `STEP_CLOSED`

Bild/Station: sichtbares Figurenpaar mit gemeinsamem Bogen in B3

Module: M06_FORTSETZEN → M08_SCHLIESSEN

Karten: `qoteedy`

Sprechen: DANACH · LANG; SCHLUSS

Ausgang: `STEP_CLOSED`

## 32. B3-S028

Eingang: `STEP_CLOSED`

Bild/Station: sichtbares Figurenpaar mit gemeinsamem Bogen in B3

Module: M02_ANSETZEN_BEHANDELN → M08_SCHLIESSEN

Karten: `qokeey qokedy`

Sprechen: ANSETZEN · LANG · ARBEITSPOSTEN | ANSETZEN · KURZ; SCHLUSS

Ausgang: `STEP_CLOSED`

## 33. B3-S029

Eingang: `STEP_CLOSED`

Bild/Station: sichtbares Figurenpaar mit gemeinsamem Bogen in B3

Module: M02_ANSETZEN_BEHANDELN → M06_FORTSETZEN → M08_SCHLIESSEN

Karten: `sol cheeety qokedy`

Sprechen: FORTSETZEN | VOLL · EINTRAGEN · ARBEITSPOSTEN | ANSETZEN · KURZ; SCHLUSS

Ausgang: `STEP_CLOSED`

## 34. B3-S030

Eingang: `STEP_CLOSED`

Bild/Station: sichtbares Figurenpaar mit gemeinsamem Bogen in B3

Module: M01_DOSIEREN → M02_ANSETZEN_BEHANDELN → M03_ADRESSIEREN_WEITERLEITEN → M06_FORTSETZEN → M08_SCHLIESSEN

Karten: `qoky saiin schedair otchedy`

Sprechen: ANSETZEN · ARBEITSPOSTEN | SOLLMASS | UMSETZEN · FLUESSIGKEITSLAUF | DANACH · UMSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 35. B3-S031

Eingang: `STEP_CLOSED`

Bild/Station: sichtbares Figurenpaar mit gemeinsamem Bogen in B3

Module: M02_ANSETZEN_BEHANDELN → M08_SCHLIESSEN

Karten: `qokeedy`

Sprechen: ANSETZEN · LANG; SCHLUSS

Ausgang: `STEP_CLOSED`

## 36. B3-S032

Eingang: `STEP_CLOSED`

Bild/Station: sichtbares Figurenpaar mit gemeinsamem Bogen in B3

Module: M03_ADRESSIEREN_WEITERLEITEN → M06_FORTSETZEN → M08_SCHLIESSEN

Karten: `chedain chedy qotedaiin otaiin otedy`

Sprechen: UMSETZEN · PORTION | UMSETZEN · ARBEITSPOSTEN | DANACH · KURZ · SOLLMASS | DANACH · SOLLMASS | DANACH · KURZ; SCHLUSS

Ausgang: `STEP_CLOSED`

## 37. B3-S033

Eingang: `STEP_CLOSED`

Bild/Station: sichtbares Figurenpaar mit gemeinsamem Bogen in B3

Module: M03_ADRESSIEREN_WEITERLEITEN → M08_SCHLIESSEN

Karten: `ldy`

Sprechen: WEITERLEITEN; SCHLUSS

Ausgang: `STEP_CLOSED`

## 38. B3-S034

Eingang: `STEP_CLOSED`

Bild/Station: sichtbares Figurenpaar mit gemeinsamem Bogen in B3

Module: M01_DOSIEREN → M03_ADRESSIEREN_WEITERLEITEN → M04_HALTEN_ABSETZEN → M06_FORTSETZEN → M07_BEREITSCHAFT_PRUEFEN → M08_SCHLIESSEN

Karten: `soiiin checthy chety otaiin olsaly shedy`

Sprechen: ARBEITSGANG · ARBEITSSTUFE | BEREIT · ARBEITSPOSTEN | EINTRAGEN · ARBEITSPOSTEN | DANACH · SOLLMASS | FORTSETZEN · ZIELSTELLE · ARBEITSPOSTEN | ABSETZEN; SCHLUSS

Ausgang: `STEP_CLOSED`
