# f56r: Zutatenplätze und wiederholte Arbeitszyklen

Bildbesitzer: **die mehrkoepfige stachelige Pflanze**

## H5-S001 — BUILD_MEASURED_INGREDIENT_BATCH

Karten: `chochor cho chodaly daiin sho kchol otchor choky dal`

Quelle: *Additamentum de praeparatione sume, ad locum ut rem fer et ad mensuram continua addere; deinde de praeparatione sume et rem ad locum pone.*

Rücklesung: Bei der mehrkoepfigen stacheligen Pflanze: Eine Zutat fuer den Ansatz entnehmen, zur Zielstelle bringen und nach Sollmass weiter zugeben; danach vom Ansatz entnehmen und den Posten an der Zielstelle ansetzen.

Register: `PICTURE_OWNER+INGREDIENT_SLOT → MEASURED_INGREDIENT_BATCH_A`

## H5-S002 — RESUME_PASS_THROUGH_AND_CLOSE

Karten: `schol choy choky cheeckhody`

Quelle: *Ex eo additamentum ut rem pone; diu per meatum in opere sume et fini.*

Rücklesung: Bei der mehrkoepfigen stacheligen Pflanze: Davon, die Zutat als laufenden Posten fuehren und ansetzen; laenger im Arbeitsgang durch den Durchlass entnehmen und schliessen.

Register: `MEASURED_INGREDIENT_BATCH_A → CLOSED_PASSAGE_PRODUCT_A`

## H5-S003 — START_SECOND_INGREDIENT_CYCLE

Karten: `sh cho kchey qokokchy`

Quelle: *Additamentum tene, rem cito adde et bis pone.*

Rücklesung: Bei der mehrkoepfigen stacheligen Pflanze: Die Zutat halten, dem laufenden Posten kurz zugeben und ihn zweimal ansetzen.

Register: `PICTURE_OWNER+INGREDIENT_SLOT → APPLICATION_CYCLE_B`

## H5-S004 — WORK_AND_TRANSFER_TO_TARGET

Karten: `okchy chokcheo kchal`

Quelle: *Rem pone; in opere cito pone et sume; ad locum adde.*

Rücklesung: Bei der mehrkoepfigen stacheligen Pflanze: Den laufenden Posten ansetzen; dann kurz im Arbeitsgang ansetzen und entnehmen; dann zur Zielstelle zugeben.

Register: `APPLICATION_CYCLE_B → TARGET_PORTION_B`

## H5-S005 — ADD_SOURCE_INGREDIENT_AND_TAKE_PORTION

Karten: `sho chokchy kchoar sotodan`

Quelle: *Additamentum et rem pone; additamentum ex fonte adde; deinde portionem in opere sume.*

Rücklesung: Bei der mehrkoepfigen stacheligen Pflanze: Die Zutat bereiten, den laufenden Posten ansetzen und die Zutat aus der Quelle zugeben; danach eine Portion in den Arbeitsgang nehmen.

Register: `PICTURE_OWNER+INGREDIENT_SLOT+SOURCE → SOURCE_PORTION_C`

## H5-S006 — CONTINUE_TO_MEASURE

Karten: `otchey keol daiin`

Quelle: *Deinde rem cito adde et continua ad mensuram.*

Rücklesung: Bei der mehrkoepfigen stacheligen Pflanze: Danach den laufenden Posten kurz weiter zugeben, bis das Sollmass erreicht ist.

Register: `SOURCE_PORTION_C → OPEN_MEASURED_PORTION_C`

## Die vier HO-Vorkommen

`cho → sho → cho → sho` sind vier Renderings derselben ZUTAT-Karte. Das Bild
liefert den Artikelbesitzer; HO öffnet einen Zutatenplatz. Lokal darf dieser
Platz Bildpflanzenmaterial meinen, doch HO bedeutet weder PFLANZE noch NEHMEN.
