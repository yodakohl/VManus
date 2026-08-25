# Vollständiger funktionaler Renderer

Alle 16 Mehrfachfamilien werden nun nach einer beabsichtigten Unterfunktion gerendert, nicht nach Seite, Auftrag oder Position.
Das Mikrolexikon enthält 36 funktionale Allographen und zwei echte lokale Ganzwörter.

## Die 23 neuen Funktionsformen

- `AIIN` + **OPERATIONAL_MEASURE** → `daiin` — das Maß innerhalb einer Prosaoperation.
- `AIIN` + **BARE_CONDITION_MEASURE** → `aiin` — das bloße Maß in einer Bedingungsreihe.
- `AR` + **ACTIVE_SOURCE** → `char` — die aktiv benutzte Quelle einer Prosaoperation.
- `AR` + **BARE_CONDITION_SOURCE** → `ar` — die bloße Quelle einer Bedingungsreihe.
- `CHD+Y` + **DEFAULT_OPEN_TRANSFER** → `chedy` — den laufenden Posten gewöhnlich umsetzen.
- `CHD+Y` + **MARKED_STATION_OPEN_TRANSFER** → `chedchy` — den Posten an einer markierten Station umsetzen.
- `CHD+Y` + **CONDITION_STATE_TRANSFER** → `chdy` — einen Bedingungs- oder Zustandsposten umsetzen.
- `CHK+EE+Y` + **MATERIAL_LONG_WARM** → `cheeky` — einen Materialposten lange warm halten.
- `CHK+EE+Y` + **APPARATUS_LONG_WARM** → `chkeey` — einen Geräte- oder Beckenposten lange warm halten.
- `OK+CHD+DY` + **STANDALONE_TRANSFER_CLOSE** → `qokchdy` — einen alleinstehenden Umsetzschritt ansetzen und schließen.
- `OK+CHD+DY` + **CHAIN_FINAL_TRANSFER_CLOSE** → `okchedy` — den letzten Umsetzschritt einer Kette schließen.
- `OK+OL` + **PRODUCTION_CONTINUATION_START** → `okchol` — eine Herstellungsfolge weiter ansetzen.
- `OK+OL` + **APPLICATION_CONTINUATION_START** → `qokol` — eine Anwendungsfolge weiter ansetzen.
- `OK+Y` + **DEFAULT_CURRENT_START** → `qoky` — den gewöhnlichen aktuellen Posten ansetzen.
- `OK+Y` + **ARTICLE_INITIAL_CURRENT_START** → `qokchy` — den ersten aktuellen Posten eines Herstellungsartikels ansetzen.
- `OK+Y` + **CONDITION_CURRENT_START** → `choky` — den aktuellen Bedingungsposten ansetzen.
- `OL+Y` + **APPLICATION_CURRENT_CONTINUATION** → `qolchey` — den aktuellen Anwendungsposten fortsetzen.
- `OL+Y` + **CONDITION_CURRENT_CONTINUATION** → `choly` — den aktuellen Bedingungsposten fortsetzen.
- `OT+CHD+DY` + **STANDALONE_FOLLOW_CLOSE** → `qotchedy` — einen alleinstehenden Folgeschritt umsetzen und schließen.
- `OT+CHD+DY` + **CHAIN_FINAL_FOLLOW_CLOSE** → `otchedy` — den letzten Folgeschritt einer Kette schließen.
- `OT+CHD+DY` + **COMPACT_FOLLOW_CLOSE** → `otchdy` — einen kompakten Folgeschritt schließen.
- `OT+Y` + **PRODUCTION_FOLLOW_REFERENT** → `qotchy` — den Folgeposten einer Herstellungsfolge aufnehmen.
- `OT+Y` + **APPLICATION_FOLLOW_REFERENT** → `otchey` — den Folgeposten einer Anwendungsfolge aufnehmen.

## Vollständige Familien

- `AIIN`: BARE_CONDITION_MEASURE->aiin | OPERATIONAL_MEASURE->daiin.
- `AL`: EMBEDDED_TARGET->cheal | DEFAULT_TARGET->dal.
- `AR`: BARE_CONDITION_SOURCE->ar | ACTIVE_SOURCE->char.
- `CHD+DY`: DIRECT_TARGET_CLOSE->dchdy | DEFAULT_TRANSFER_CLOSE->schedy.
- `CHD+Y`: CONDITION_STATE_TRANSFER->chdy | MARKED_STATION_OPEN_TRANSFER->chedchy | DEFAULT_OPEN_TRANSFER->chedy.
- `CHK+EE+Y`: MATERIAL_LONG_WARM->cheeky | APPARATUS_LONG_WARM->chkeey.
- `NONE`: MOISTURE_STAGE_WHOLE_WORD->daiial | WEATHER_CLASS_WHOLE_WORD->iokeeor.
- `OK+CHD+DY`: CHAIN_FINAL_TRANSFER_CLOSE->okchedy | STANDALONE_TRANSFER_CLOSE->qokchdy.
- `OK+OL`: PRODUCTION_CONTINUATION_START->okchol | APPLICATION_CONTINUATION_START->qokol.
- `OK+Y`: CONDITION_CURRENT_START->choky | ARTICLE_INITIAL_CURRENT_START->qokchy | DEFAULT_CURRENT_START->qoky.
- `OL`: ATTACHED_OR_RING_CONTINUATION->chol | TRANSFER_CONTINUATION->ls | GENERAL_CONTINUATION->ol.
- `OL+Y`: CONDITION_CURRENT_CONTINUATION->choly | APPLICATION_CURRENT_CONTINUATION->qolchey.
- `OT+CHD+DY`: COMPACT_FOLLOW_CLOSE->otchdy | CHAIN_FINAL_FOLLOW_CLOSE->otchedy | STANDALONE_FOLLOW_CLOSE->qotchedy.
- `OT+Y`: APPLICATION_FOLLOW_REFERENT->otchey | PRODUCTION_FOLLOW_REFERENT->qotchy.
- `SH+EE+Y`: GENERAL_LONG_HOLD->cheey | MARKED_LONG_HOLD->sheey.
- `Y`: MATERIAL_OR_QUALITY_REFERENT->chey | STATE_OR_BODY_REFERENT->chy | ECHOED_CURRENT_REFERENT->dy | BARE_CURRENT_REFERENT->y.
