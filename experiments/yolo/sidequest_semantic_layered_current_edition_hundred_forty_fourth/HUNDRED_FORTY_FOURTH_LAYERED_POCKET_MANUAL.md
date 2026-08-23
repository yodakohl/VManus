# Aktuelles Schichtwörterbuch und Satzheft

## Drei getrennte Ebenen

1. PORTABLE CARD VALUE: the short learned card word or prompt.
2. OWNER ARGUMENT: plant, basin, batch, station, source or target supplied by picture/register.
3. FLUENT EXPANSION: German syntax combining the first two; never fed back into the dictionary.

## Zehn revidierte Moulds

- M01_MATERIAL_PREPARATION: `OWNER>MATERIAL>PROCESS` — Bildmaterial und örtliche Zubereitung bearbeiten — Do not force a product unless a product card appears
- M02_SOURCE_SHARE_MEASURE: `SOURCE>SHARE>[MEASURE]` — davon einen Anteil nehmen; nur mit AIIN/OKAIIN ausdrücklich bemessen — Measure is optional, not automatic
- M03_TARGET_TRANSFER: `ITEM>TARGET>TRANSFER>[CLOSE]` — Posten an die vom Besitzer gelieferte Stelle führen — Body, basin or vessel target comes from owner
- M04_ORDER_CONTINUATION: `ORDER>LINK>ITEM>ACTION` — Folge oder Fortsetzung im kopierten Ablauf — Keep exact endpoint position
- M05_STATE_CLOSE: `ITEM>PROCESS_OR_STATE>[CLOSE]` — örtlichen Prozesszustand ausführen — Do not default every state to heat
- M06_FILTER_CLEAR_PRODUCT: `ITEM>FILTER_OR_WASH>[PRODUCT]>[CLOSE]` — waschen, auswringen oder seihen; Klarauszug nur mit product card — Cloth and water require card or owner
- M07_PAIRED_MEASURE_FRAME: `ITEM>MEASURE>ITEM` — zwei Posten unter demselben Sollmaß — Keep both item boundaries
- M08_CARRIED_PREPARATION_FRAME: `LINK>PREPARATION>LINK` — Fortsetzung mit demselben Ansatz — Payload may sit inside boundaries
- M09_APPLICATION_FASTEN: `LOCAL_APPLICATION_OR_STORAGE_WHOLE_CARD` — örtlich anwenden, verwahren oder festbinden — Three learned variants; not freely interchangeable
- M10_LOCAL_EXACT_CELL: `LOCAL_WHOLE_CARD_SEQUENCE` — örtliche Ganzzelle aus Vorlage kopieren — Change owner only

## Aktive Karten

- `okeey` = lange einwirken [DURATIVE_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `ldy` = abziehen; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `okchedy` = einführen; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `okey` = kurz einwirken [DURATIVE_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `dl` = Zusatz [OBJECT]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `otchor` = Folgeansatz [ORDERED_OBJECT]; owner: ACTIVE_SEQUENCE
- `okain` = Anteil zugeben [QUANTITY_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `oldy` = fertig [TERMINAL_STATE]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `dchedy` = überführen; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `choky` = einsetzen [ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `olchedy` = weiterführen; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `cheeky` = länger bearbeiten [DURATIVE_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `cho` = weitere Zutat [OBJECT]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `chckhy` = durchleiten [ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `aiin` = Sollmaß [QUANTITY]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `okal` = dorthin einsetzen [TARGET_ACTION]; owner: VISIBLE_OR_REGISTERED_TARGET
- `olkeedy` = lange sammeln; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `char` = davon [SOURCE_ANAPHOR]; owner: INHERITED_SOURCE_OR_PREVIOUS_BATCH
- `otaiin` = Folgemaß [ORDERED_QUANTITY]; owner: ACTIVE_SEQUENCE
- `chdy` = überführen [ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `chor` = Ansatz [OBJECT]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `qokeedy` = lange einwirken; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `qokedy` = kurz einwirken; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `chety` = Anteil [QUANTITY_OBJECT]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `qokchdy` = einführen; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `otal` = danach dorthin [TARGET_ANAPHOR]; owner: VISIBLE_OR_REGISTERED_TARGET
- `chokchy` = weiterbearbeiten [ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `chkain` = Anteil [QUANTITY_OBJECT]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `cheey` = Klarauszug [PRODUCT_OBJECT]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `okaiin` = bemessen [QUANTITY_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `chey` = dies [ITEM_ANAPHOR]; owner: ACTIVE_WORK_ITEM
- `cheedy` = kurz absetzen; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `dchol` = vom vorigen [SOURCE_ANAPHOR]; owner: INHERITED_SOURCE_OR_PREVIOUS_BATCH
- `shckhedy` = seihen; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `cheky` = kurz wärmen [ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `cheol` = weiter [CONTINUATION_LINK]; owner: ACTIVE_SEQUENCE
- `al` = dorthin [TARGET_ANAPHOR]; owner: VISIBLE_OR_REGISTERED_TARGET
- `lchedy` = abführen; Schluss [TERMINAL_ACTION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `cholor` = derselbe Ansatz [CARRIED_PREPARATION]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `checthy` = bereit [STATE]; owner: ACTIVE_WORK_ITEM_OR_BATCH
- `otchey` = das nächste [ORDER_ANAPHOR]; owner: ACTIVE_SEQUENCE
