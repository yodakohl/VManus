# All29 fixed complete readings under the new instruction law
All values remain hypothetical. No aliases were changed. C/G/W are unnamed cargo roles.

## FULL01_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–7|dair o|FERRY FERRY G|
|S03|8–11|laiin chefchdy sor orsheckhy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S04|12–13|ockhody shos|EXCLUDE RETURN_EXCLUDING C|
|S05|14–14|alol|THEN THEN|
|S06|15–15|dy|THEN THEN|
|S07|16–16|kar|THEN THEN|
|S08|17–18|oky daiiin|FERRY FERRY C|
|S09|19–19|okar|THEN THEN|
|S10|20–20|ar|THEN THEN|
|S11|21–21|okam|THEN THEN|
|S12|22–22|tshol|THEN THEN|
|S13|23–23|kar|THEN THEN|
|S14|24–24|sheedy|THEN THEN|
|S15|25–27|okeody qokedy chody|WITH_RETURN WITH_TRIP C RETURN|
|S16|28–29|kchdy pchdy|FERRY FERRY C|
|S17|30–31|chkaiin odam|STAY LEAVE THERE|
|S18|32–32|tchdy|THEN THEN|
|S19|33–34|qokas chedy|EXCLUDE RETURN_EXCLUDING G|
|S20|35–35|qokchdy|THEN THEN|
|S21|36–36|qokaiin|THEN THEN|
|S22|37–37|or|THEN THEN|
|S23|38–38|ar|THEN THEN|
|S24|39–39|alol|THEN THEN|
|S25|40–41|keodaiin ols|FERRY FERRY C|
|S26|42–43|solkchy chckhy|STAY LEAVE THERE|
|S27|44–44|qokchdy|THEN THEN|
|S28|45–45|qokchdy|THEN THEN|
|S29|46–46|okar|THEN THEN|
|S30|47–47|ar|THEN THEN|
|S31|48–48|y|THEN THEN|
|S32|49–49|qokchdy|THEN THEN|
|S33|50–50|kar|THEN THEN|
|S34|51–51|ar|THEN THEN|
|S35|52–53|okain ykain|STAY LEAVE THERE|
|S36|54–54|[sh:{c's}]ear|THEN THEN|
|S37|55–56|ol kchedy|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S38|57–57|okal|THEN THEN|
|S39|58–59|qotor cheeor|FERRY FERRY G|
|S40|60–61|olk[ee:a]dy daiin|FERRY FERRY C|
|S41|62–63|qoky todalain|FERRY FERRY C|
|S42|64–64|qotal|THEN THEN|
|S43|65–66|kaiin otaiin|STAY LEAVE THERE|
|S44|67–71|otal she ka[r:s] ariin okchedy|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S45|72–77|dariin yk ykaiin sheekar otchdy dar|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S46|78–78|kar|THEN THEN|
|S47|79–79|shedain|THEN THEN|
|S48|80–81|taipar orolkain|EXCLUDE RETURN_EXCLUDING C|
|S49|82–83|ytchdy kchedy|FERRY FERRY FIRST_CARGO|
|S50|84–84|ykeey|THEN THEN|
|S51|85–86|kaiin qokain|STAY LEAVE THERE|
|S52|87–87|ald|THEN THEN|
|S53|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 6.
- S25 FIXED_TRIP_FAILED; prefix S02:G, S04:empty, S08:C, S15:C, S16:C, S19:empty.
- S39 FIXED_TRIP_FAILED; prefix S02:G, S04:empty, S08:C, S15:C, S16:C, S19:C, S25:C, S37:empty.
- S39 FIXED_TRIP_FAILED; prefix S02:G, S04:empty, S08:C, S15:C, S16:C, S19:C, S25:C, S37:C.
- S25 FIXED_TRIP_FAILED; prefix S02:G, S04:G, S08:C, S15:C, S16:C, S19:empty.
- S49 FIXED_TRIP_FAILED; prefix S02:G, S04:G, S08:C, S15:C, S16:C, S19:C, S25:C, S37:empty, S39:G, S40:C, S41:C, S48:empty.
- S40 FIXED_TRIP_FAILED; prefix S02:G, S04:G, S08:C, S15:C, S16:C, S19:C, S25:C, S37:C, S39:G.

## FULL01_independent — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair o laiin chefchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–12|sor orsheckhy ockhody|CONVEY CONVEY_OUT NEXT W|
|S04|13–14|shos alol|STAY LEAVE THERE|
|S05|15–15|dy|THEN THEN|
|S06|16–16|kar|THEN THEN|
|S07|17–17|oky|THEN THEN|
|S08|18–18|daiiin|THEN THEN|
|S09|19–19|okar|THEN THEN|
|S10|20–21|ar okam|STAY LEAVE THERE|
|S11|22–22|tshol|THEN THEN|
|S12|23–23|kar|THEN THEN|
|S13|24–24|sheedy|THEN THEN|
|S14|25–25|okeody|THEN THEN|
|S15|26–31|qokedy chody kchdy pchdy chkaiin odam|PAIR C PAIRED_WITH UNATTENDED W WOULD_BE UNSAFE|
|S16|32–32|tchdy|THEN THEN|
|S17|33–34|qokas chedy|EXCLUDE RETURN_EXCLUDING G|
|S18|35–35|qokchdy|THEN THEN|
|S19|36–37|qokaiin or|FERRY FERRY W|
|S20|38–39|ar alol|STAY LEAVE THERE|
|S21|40–40|keodaiin|THEN THEN|
|S22|41–41|ols|THEN THEN|
|S23|42–43|solkchy chckhy|STAY LEAVE THERE|
|S24|44–44|qokchdy|THEN THEN|
|S25|45–45|qokchdy|THEN THEN|
|S26|46–46|okar|THEN THEN|
|S27|47–48|ar y|STAY LEAVE THERE|
|S28|49–49|qokchdy|THEN THEN|
|S29|50–50|kar|THEN THEN|
|S30|51–52|ar okain|STAY LEAVE THERE|
|S31|53–54|ykain [sh:{c's}]ear|ALONE RETURN ALONE|
|S32|55–57|ol kchedy okal|CONVEY CONVEY_OUT NEXT G|
|S33|58–58|qotor|THEN THEN|
|S34|59–60|cheeor olk[ee:a]dy|EXCLUDE RETURN_EXCLUDING G|
|S35|61–61|daiin|THEN THEN|
|S36|62–63|qoky todalain|FERRY FERRY W|
|S37|64–64|qotal|THEN THEN|
|S38|65–66|kaiin otaiin|STAY LEAVE THERE|
|S39|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S41|78–78|kar|THEN THEN|
|S42|79–80|shedain taipar|ALONE RETURN ALONE|
|S43|81–81|orolkain|THEN THEN|
|S44|82–84|ytchdy kchedy ykeey|CONVEY CONVEY_OUT NEXT C|
|S45|85–86|kaiin qokain|STAY LEAVE THERE|
|S46|87–87|ald|THEN THEN|
|S47|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 2.
- S19 FIXED_TRIP_FAILED; prefix S03:W, S17:empty.
- S36 FIXED_TRIP_FAILED; prefix S03:W, S17:W, S19:W, S31:empty, S32:G, S34:empty.

## FULL02_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–6|dair|THEN THEN|
|S03|7–10|o laiin chefchdy sor|WITH_OUT WITH_TRIP B TAKE_OUT G|
|S04|11–12|orsheckhy ockhody|EXCLUDE RETURN_EXCLUDING C|
|S05|13–13|shos|THEN THEN|
|S06|14–15|alol dy|FERRY FERRY W|
|S07|16–16|kar|THEN THEN|
|S08|17–18|oky daiiin|EXCLUDE RETURN_EXCLUDING W|
|S09|19–19|okar|THEN THEN|
|S10|20–20|ar|THEN THEN|
|S11|21–21|okam|THEN THEN|
|S12|22–22|tshol|THEN THEN|
|S13|23–23|kar|THEN THEN|
|S14|24–24|sheedy|THEN THEN|
|S15|25–26|okeody qokedy|FERRY FERRY C|
|S16|27–27|chody|THEN THEN|
|S17|28–30|kchdy pchdy chkaiin|WITH_RETURN WITH_TRIP G RETURN|
|S18|31–31|odam|THEN THEN|
|S19|32–32|tchdy|THEN THEN|
|S20|33–34|qokas chedy|FERRY FERRY G|
|S21|35–35|qokchdy|THEN THEN|
|S22|36–36|qokaiin|THEN THEN|
|S23|37–37|or|THEN THEN|
|S24|38–38|ar|THEN THEN|
|S25|39–40|alol keodaiin|FERRY FERRY W|
|S26|41–41|ols|THEN THEN|
|S27|42–43|solkchy chckhy|STAY LEAVE THERE|
|S28|44–44|qokchdy|THEN THEN|
|S29|45–45|qokchdy|THEN THEN|
|S30|46–46|okar|THEN THEN|
|S31|47–47|ar|THEN THEN|
|S32|48–48|y|THEN THEN|
|S33|49–49|qokchdy|THEN THEN|
|S34|50–50|kar|THEN THEN|
|S35|51–51|ar|THEN THEN|
|S36|52–53|okain ykain|FERRY FERRY W|
|S37|54–55|[sh:{c's}]ear ol|STAY LEAVE THERE|
|S38|56–57|kchedy okal|STAY LEAVE THERE|
|S39|58–61|qotor cheeor olk[ee:a]dy daiin|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S40|62–63|qoky todalain|FERRY FERRY FIRST_CARGO|
|S41|64–64|qotal|THEN THEN|
|S42|65–66|kaiin otaiin|STAY LEAVE THERE|
|S43|67–71|otal she ka[r:s] ariin okchedy|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S44|72–77|dariin yk ykaiin sheekar otchdy dar|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S45|78–78|kar|THEN THEN|
|S46|79–79|shedain|THEN THEN|
|S47|80–80|taipar|THEN THEN|
|S48|81–82|orolkain ytchdy|FERRY FERRY FIRST_CARGO|
|S49|83–84|kchedy ykeey|STAY LEAVE THERE|
|S50|85–86|kaiin qokain|STAY LEAVE THERE|
|S51|87–87|ald|THEN THEN|
|S52|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 2.
- S17 FIXED_TRIP_FAILED; prefix S03:G, S04:empty, S06:W, S08:G, S15:C.
- S17 FIXED_TRIP_FAILED; prefix S03:G, S04:G, S06:W, S08:empty, S15:C.

## FULL02_independent — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair o laiin chefchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–12|sor orsheckhy ockhody|CONVEY CONVEY_OUT NEXT G|
|S04|13–14|shos alol|STAY LEAVE THERE|
|S05|15–15|dy|THEN THEN|
|S06|16–16|kar|THEN THEN|
|S07|17–18|oky daiiin|FERRY FERRY G|
|S08|19–19|okar|THEN THEN|
|S09|20–21|ar okam|STAY LEAVE THERE|
|S10|22–22|tshol|THEN THEN|
|S11|23–23|kar|THEN THEN|
|S12|24–24|sheedy|THEN THEN|
|S13|25–25|okeody|THEN THEN|
|S14|26–31|qokedy chody kchdy pchdy chkaiin odam|PAIR C PAIRED_WITH UNATTENDED G WOULD_BE UNSAFE|
|S15|32–32|tchdy|THEN THEN|
|S16|33–34|qokas chedy|FERRY FERRY G|
|S17|35–35|qokchdy|THEN THEN|
|S18|36–36|qokaiin|THEN THEN|
|S19|37–37|or|THEN THEN|
|S20|38–39|ar alol|STAY LEAVE THERE|
|S21|40–40|keodaiin|THEN THEN|
|S22|41–41|ols|THEN THEN|
|S23|42–43|solkchy chckhy|STAY LEAVE THERE|
|S24|44–44|qokchdy|THEN THEN|
|S25|45–45|qokchdy|THEN THEN|
|S26|46–46|okar|THEN THEN|
|S27|47–48|ar y|STAY LEAVE THERE|
|S28|49–49|qokchdy|THEN THEN|
|S29|50–50|kar|THEN THEN|
|S30|51–52|ar okain|STAY LEAVE THERE|
|S31|53–54|ykain [sh:{c's}]ear|ALONE RETURN ALONE|
|S32|55–57|ol kchedy okal|CONVEY CONVEY_OUT NEXT W|
|S33|58–58|qotor|THEN THEN|
|S34|59–60|cheeor olk[ee:a]dy|EXCLUDE RETURN_EXCLUDING G|
|S35|61–61|daiin|THEN THEN|
|S36|62–63|qoky todalain|FERRY FERRY W|
|S37|64–64|qotal|THEN THEN|
|S38|65–66|kaiin otaiin|STAY LEAVE THERE|
|S39|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S41|78–78|kar|THEN THEN|
|S42|79–80|shedain taipar|ALONE RETURN ALONE|
|S43|81–81|orolkain|THEN THEN|
|S44|82–84|ytchdy kchedy ykeey|CONVEY CONVEY_OUT NEXT C|
|S45|85–86|kaiin qokain|STAY LEAVE THERE|
|S46|87–87|ald|THEN THEN|
|S47|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 1.
- S36 FIXED_TRIP_FAILED; prefix S03:G, S07:G, S16:G, S31:empty, S32:W, S34:empty.

## FULL03_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "FIRST", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–7|dair o|FERRY FERRY W|
|S03|8–9|laiin chefchdy|EXCLUDE RETURN_EXCLUDING W|
|S04|10–10|sor|THEN THEN|
|S05|11–11|orsheckhy|THEN THEN|
|S06|12–12|ockhody|THEN THEN|
|S07|13–13|shos|THEN THEN|
|S08|14–14|alol|THEN THEN|
|S09|15–15|dy|THEN THEN|
|S10|16–16|kar|THEN THEN|
|S11|17–18|oky daiiin|FERRY FERRY G|
|S12|19–19|okar|THEN THEN|
|S13|20–20|ar|THEN THEN|
|S14|21–22|okam tshol|EXCLUDE RETURN_EXCLUDING G|
|S15|23–23|kar|THEN THEN|
|S16|24–24|sheedy|THEN THEN|
|S17|25–26|okeody qokedy|FERRY FERRY C|
|S18|27–28|chody kchdy|EXCLUDE RETURN_EXCLUDING C|
|S19|29–30|pchdy chkaiin|FERRY FERRY OTHER_CARGO|
|S20|31–34|odam tchdy qokas chedy|RESULT JOINING_RESULT REST_CARGO COLOC G|
|S21|35–35|qokchdy|THEN THEN|
|S22|36–36|qokaiin|THEN THEN|
|S23|37–37|or|THEN THEN|
|S24|38–38|ar|THEN THEN|
|S25|39–39|alol|THEN THEN|
|S26|40–40|keodaiin|THEN THEN|
|S27|41–41|ols|THEN THEN|
|S28|42–43|solkchy chckhy|STAY LEAVE THERE|
|S29|44–44|qokchdy|THEN THEN|
|S30|45–45|qokchdy|THEN THEN|
|S31|46–46|okar|THEN THEN|
|S32|47–47|ar|THEN THEN|
|S33|48–48|y|THEN THEN|
|S34|49–49|qokchdy|THEN THEN|
|S35|50–50|kar|THEN THEN|
|S36|51–51|ar|THEN THEN|
|S37|52–55|okain ykain [sh:{c's}]ear ol|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S38|56–57|kchedy okal|FERRY FERRY OTHER_CARGO|
|S39|58–58|qotor|THEN THEN|
|S40|59–59|cheeor|THEN THEN|
|S41|60–60|olk[ee:a]dy|THEN THEN|
|S42|61–61|daiin|THEN THEN|
|S43|62–63|qoky todalain|FERRY FERRY FIRST_CARGO|
|S44|64–64|qotal|THEN THEN|
|S45|65–66|kaiin otaiin|STAY LEAVE THERE|
|S46|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S47|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S48|78–78|kar|THEN THEN|
|S49|79–79|shedain|THEN THEN|
|S50|80–81|taipar orolkain|EXCLUDE RETURN_EXCLUDING C|
|S51|82–82|ytchdy|THEN THEN|
|S52|83–84|kchedy ykeey|FERRY FERRY W|
|S53|85–86|kaiin qokain|STAY LEAVE THERE|
|S54|87–87|ald|THEN THEN|
|S55|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 2; failed eligible prefixes: 7.
- S19 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S11:G, S14:empty, S17:C, S18:empty.
- S19 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S11:G, S14:empty, S17:C, S18:G.
- S52 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S11:G, S14:empty, S17:C, S18:W, S19:W, S38:W, S43:W, S50:empty.
- S52 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S11:G, S14:empty, S17:C, S18:W, S19:W, S38:W, S43:W, S50:G.
- S52 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S11:G, S14:W, S17:C, S18:empty, S19:W, S38:W, S43:W, S50:empty.
- S52 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S11:G, S14:W, S17:C, S18:empty, S19:W, S38:W, S43:W, S50:G.
- S20 JOINING_RESULT_FALSE; prefix S02:W, S03:empty, S11:G, S14:W, S17:C, S18:G, S19:W.

## FULL03_independent — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "FIRST", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair o laiin chefchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–12|sor orsheckhy ockhody|CONVEY CONVEY_OUT NEXT C|
|S04|13–14|shos alol|STAY LEAVE THERE|
|S05|15–15|dy|THEN THEN|
|S06|16–16|kar|THEN THEN|
|S07|17–17|oky|THEN THEN|
|S08|18–18|daiiin|THEN THEN|
|S09|19–19|okar|THEN THEN|
|S10|20–21|ar okam|STAY LEAVE THERE|
|S11|22–22|tshol|THEN THEN|
|S12|23–23|kar|THEN THEN|
|S13|24–24|sheedy|THEN THEN|
|S14|25–25|okeody|THEN THEN|
|S15|26–31|qokedy chody kchdy pchdy chkaiin odam|PAIR C PAIRED_WITH UNATTENDED W WOULD_BE UNSAFE|
|S16|32–32|tchdy|THEN THEN|
|S17|33–34|qokas chedy|EXCLUDE RETURN_EXCLUDING G|
|S18|35–35|qokchdy|THEN THEN|
|S19|36–37|qokaiin or|FERRY FERRY C|
|S20|38–39|ar alol|STAY LEAVE THERE|
|S21|40–40|keodaiin|THEN THEN|
|S22|41–41|ols|THEN THEN|
|S23|42–43|solkchy chckhy|STAY LEAVE THERE|
|S24|44–44|qokchdy|THEN THEN|
|S25|45–45|qokchdy|THEN THEN|
|S26|46–46|okar|THEN THEN|
|S27|47–48|ar y|STAY LEAVE THERE|
|S28|49–49|qokchdy|THEN THEN|
|S29|50–50|kar|THEN THEN|
|S30|51–52|ar okain|STAY LEAVE THERE|
|S31|53–54|ykain [sh:{c's}]ear|ALONE RETURN ALONE|
|S32|55–57|ol kchedy okal|CONVEY CONVEY_OUT NEXT W|
|S33|58–58|qotor|THEN THEN|
|S34|59–59|cheeor|THEN THEN|
|S35|60–61|olk[ee:a]dy daiin|EXCLUDE RETURN_EXCLUDING C|
|S36|62–63|qoky todalain|FERRY FERRY G|
|S37|64–64|qotal|THEN THEN|
|S38|65–66|kaiin otaiin|STAY LEAVE THERE|
|S39|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S41|78–78|kar|THEN THEN|
|S42|79–80|shedain taipar|ALONE RETURN ALONE|
|S43|81–81|orolkain|THEN THEN|
|S44|82–84|ytchdy kchedy ykeey|CONVEY CONVEY_OUT NEXT W|
|S45|85–86|kaiin qokain|STAY LEAVE THERE|
|S46|87–87|ald|THEN THEN|
|S47|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 1.
- S19 FIXED_TRIP_FAILED; prefix S03:C, S17:empty.

## FULL04_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "FIRST", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–7|dair o|FERRY FERRY G|
|S03|8–8|laiin|THEN THEN|
|S04|9–9|chefchdy|THEN THEN|
|S05|10–10|sor|THEN THEN|
|S06|11–12|orsheckhy ockhody|FERRY FERRY OTHER_CARGO|
|S07|13–13|shos|THEN THEN|
|S08|14–15|alol dy|FERRY FERRY C|
|S09|16–17|kar oky|EXCLUDE RETURN_EXCLUDING OTHER_CARGO|
|S10|18–18|daiiin|THEN THEN|
|S11|19–20|okar ar|FERRY FERRY W|
|S12|21–21|okam|THEN THEN|
|S13|22–22|tshol|THEN THEN|
|S14|23–24|kar sheedy|EXCLUDE RETURN_EXCLUDING OTHER_CARGO|
|S15|25–26|okeody qokedy|FERRY FERRY C|
|S16|27–27|chody|THEN THEN|
|S17|28–29|kchdy pchdy|EXCLUDE RETURN_EXCLUDING W|
|S18|30–31|chkaiin odam|FERRY FERRY FIRST_CARGO|
|S19|32–32|tchdy|THEN THEN|
|S20|33–34|qokas chedy|FERRY FERRY G|
|S21|35–35|qokchdy|THEN THEN|
|S22|36–38|qokaiin or ar|CONVEY CONVEY_OUT NEXT W|
|S23|39–40|alol keodaiin|FERRY FERRY W|
|S24|41–41|ols|THEN THEN|
|S25|42–43|solkchy chckhy|STAY LEAVE THERE|
|S26|44–44|qokchdy|THEN THEN|
|S27|45–45|qokchdy|THEN THEN|
|S28|46–47|okar ar|FERRY FERRY W|
|S29|48–48|y|THEN THEN|
|S30|49–49|qokchdy|THEN THEN|
|S31|50–51|kar ar|EXCLUDE RETURN_EXCLUDING W|
|S32|52–52|okain|THEN THEN|
|S33|53–54|ykain [sh:{c's}]ear|FERRY FERRY FIRST_CARGO|
|S34|55–55|ol|THEN THEN|
|S35|56–57|kchedy okal|FERRY FERRY FIRST_CARGO|
|S36|58–61|qotor cheeor olk[ee:a]dy daiin|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S37|62–63|qoky todalain|FERRY FERRY C|
|S38|64–64|qotal|THEN THEN|
|S39|65–66|kaiin otaiin|STAY LEAVE THERE|
|S40|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S41|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S42|78–79|kar shedain|EXCLUDE RETURN_EXCLUDING G|
|S43|80–80|taipar|THEN THEN|
|S44|81–81|orolkain|THEN THEN|
|S45|82–82|ytchdy|THEN THEN|
|S46|83–84|kchedy ykeey|FERRY FERRY OTHER_CARGO|
|S47|85–86|kaiin qokain|STAY LEAVE THERE|
|S48|87–87|ald|THEN THEN|
|S49|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 2; failed eligible prefixes: 11.
- S15 FIXED_TRIP_FAILED; prefix S02:G, S06:G, S08:C, S09:empty, S11:W, S14:empty.
- S22 FIXED_TRIP_FAILED; prefix S02:G, S06:G, S08:C, S09:empty, S11:W, S14:C, S15:C, S17:empty, S18:G, S20:G.
- S22 FIXED_TRIP_FAILED; prefix S02:G, S06:G, S08:C, S09:empty, S11:W, S14:C, S15:C, S17:C, S18:G, S20:G.
- S15 FIXED_TRIP_FAILED; prefix S02:G, S06:G, S08:C, S09:empty, S11:W, S14:W.
- S22 FIXED_TRIP_FAILED; prefix S02:G, S06:G, S08:C, S09:C, S11:W, S14:empty, S15:C, S17:empty, S18:G, S20:G.
- S22 FIXED_TRIP_FAILED; prefix S02:G, S06:G, S08:C, S09:C, S11:W, S14:empty, S15:C, S17:C, S18:G, S20:G.
- S37 FIXED_TRIP_FAILED; prefix S02:G, S06:G, S08:C, S09:C, S11:W, S14:W, S15:C, S17:empty, S18:G, S20:G, S22:W, S23:W, S28:W, S31:empty, S33:G, S35:G.
- S49 FINAL_LOCAL_ASSERTION_FALSE; prefix S02:G, S06:G, S08:C, S09:C, S11:W, S14:W, S15:C, S17:empty, S18:G, S20:G, S22:W, S23:W, S28:W, S31:C, S33:G, S35:G, S37:C, S42:C, S46:G.
- S49 FINAL_LOCAL_ASSERTION_FALSE; prefix S02:G, S06:G, S08:C, S09:C, S11:W, S14:W, S15:C, S17:empty, S18:G, S20:G, S22:W, S23:W, S28:W, S31:C, S33:G, S35:G, S37:C, S42:W, S46:G.
- S49 FINAL_LOCAL_ASSERTION_FALSE; prefix S02:G, S06:G, S08:C, S09:C, S11:W, S14:W, S15:C, S17:C, S18:G, S20:G, S22:W, S23:W, S28:W, S31:empty, S33:G, S35:G, S37:C, S42:C, S46:G.
- S49 FINAL_LOCAL_ASSERTION_FALSE; prefix S02:G, S06:G, S08:C, S09:C, S11:W, S14:W, S15:C, S17:C, S18:G, S20:G, S22:W, S23:W, S28:W, S31:empty, S33:G, S35:G, S37:C, S42:W, S46:G.

## FULL04_independent — SUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "FIRST", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair o laiin chefchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–12|sor orsheckhy ockhody|CONVEY CONVEY_OUT NEXT C|
|S04|13–14|shos alol|STAY LEAVE THERE|
|S05|15–15|dy|THEN THEN|
|S06|16–16|kar|THEN THEN|
|S07|17–18|oky daiiin|FERRY FERRY C|
|S08|19–19|okar|THEN THEN|
|S09|20–21|ar okam|STAY LEAVE THERE|
|S10|22–22|tshol|THEN THEN|
|S11|23–23|kar|THEN THEN|
|S12|24–24|sheedy|THEN THEN|
|S13|25–25|okeody|THEN THEN|
|S14|26–31|qokedy chody kchdy pchdy chkaiin odam|PAIR C PAIRED_WITH UNATTENDED G WOULD_BE UNSAFE|
|S15|32–32|tchdy|THEN THEN|
|S16|33–34|qokas chedy|FERRY FERRY G|
|S17|35–35|qokchdy|THEN THEN|
|S18|36–36|qokaiin|THEN THEN|
|S19|37–37|or|THEN THEN|
|S20|38–39|ar alol|STAY LEAVE THERE|
|S21|40–40|keodaiin|THEN THEN|
|S22|41–41|ols|THEN THEN|
|S23|42–43|solkchy chckhy|STAY LEAVE THERE|
|S24|44–44|qokchdy|THEN THEN|
|S25|45–45|qokchdy|THEN THEN|
|S26|46–46|okar|THEN THEN|
|S27|47–48|ar y|STAY LEAVE THERE|
|S28|49–49|qokchdy|THEN THEN|
|S29|50–50|kar|THEN THEN|
|S30|51–52|ar okain|STAY LEAVE THERE|
|S31|53–54|ykain [sh:{c's}]ear|ALONE RETURN ALONE|
|S32|55–57|ol kchedy okal|CONVEY CONVEY_OUT NEXT C|
|S33|58–58|qotor|THEN THEN|
|S34|59–59|cheeor|THEN THEN|
|S35|60–60|olk[ee:a]dy|THEN THEN|
|S36|61–61|daiin|THEN THEN|
|S37|62–63|qoky todalain|FERRY FERRY C|
|S38|64–64|qotal|THEN THEN|
|S39|65–66|kaiin otaiin|STAY LEAVE THERE|
|S40|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S41|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S42|78–78|kar|THEN THEN|
|S43|79–80|shedain taipar|COPY LIKEWISE OTHER_CARGO|
|S44|81–81|orolkain|THEN THEN|
|S45|82–84|ytchdy kchedy ykeey|CONVEY CONVEY_OUT NEXT C|
|S46|85–86|kaiin qokain|STAY LEAVE THERE|
|S47|87–87|ald|THEN THEN|
|S48|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 0.
Voyages: S03:C → S07:C → S16:G → S31:empty → S32:C → S37:C → S45:C.

## FULL05_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "OTHER", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–7|dair o|FERRY FERRY C|
|S03|8–8|laiin|THEN THEN|
|S04|9–9|chefchdy|THEN THEN|
|S05|10–10|sor|THEN THEN|
|S06|11–11|orsheckhy|THEN THEN|
|S07|12–12|ockhody|THEN THEN|
|S08|13–14|shos alol|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S09|15–15|dy|THEN THEN|
|S10|16–16|kar|THEN THEN|
|S11|17–17|oky|THEN THEN|
|S12|18–18|daiiin|THEN THEN|
|S13|19–19|okar|THEN THEN|
|S14|20–21|ar okam|FERRY FERRY G|
|S15|22–22|tshol|THEN THEN|
|S16|23–23|kar|THEN THEN|
|S17|24–24|sheedy|THEN THEN|
|S18|25–26|okeody qokedy|FERRY FERRY C|
|S19|27–28|chody kchdy|FERRY FERRY W|
|S20|29–30|pchdy chkaiin|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S21|31–34|odam tchdy qokas chedy|WITH_OUT WITH_TRIP B TAKE_OUT G|
|S22|35–35|qokchdy|THEN THEN|
|S23|36–37|qokaiin or|STAY LEAVE THERE|
|S24|38–39|ar alol|FERRY FERRY FIRST_CARGO|
|S25|40–41|keodaiin ols|FERRY FERRY C|
|S26|42–43|solkchy chckhy|STAY LEAVE THERE|
|S27|44–44|qokchdy|THEN THEN|
|S28|45–45|qokchdy|THEN THEN|
|S29|46–46|okar|THEN THEN|
|S30|47–48|ar y|FERRY FERRY C|
|S31|49–49|qokchdy|THEN THEN|
|S32|50–50|kar|THEN THEN|
|S33|51–52|ar okain|FERRY FERRY C|
|S34|53–53|ykain|THEN THEN|
|S35|54–55|[sh:{c's}]ear ol|FERRY FERRY C|
|S36|56–56|kchedy|THEN THEN|
|S37|57–61|okal qotor cheeor olk[ee:a]dy daiin|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S38|62–63|qoky todalain|FERRY FERRY C|
|S39|64–64|qotal|THEN THEN|
|S40|65–66|kaiin otaiin|STAY LEAVE THERE|
|S41|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S42|73–76|yk ykaiin sheekar otchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S43|77–77|dar|THEN THEN|
|S44|78–78|kar|THEN THEN|
|S45|79–80|shedain taipar|ALONE RETURN ALONE|
|S46|81–82|orolkain ytchdy|FERRY FERRY FIRST_CARGO|
|S47|83–83|kchedy|THEN THEN|
|S48|84–84|ykeey|THEN THEN|
|S49|85–86|kaiin qokain|STAY LEAVE THERE|
|S50|87–87|ald|THEN THEN|
|S51|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 1.
- S21 FIXED_TRIP_FAILED; prefix S02:C, S08:empty, S14:G, S18:C, S19:W, S20:empty.

## FULL05_independent — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "OTHER", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair o laiin chefchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–12|sor orsheckhy ockhody|CONVEY CONVEY_OUT NEXT W|
|S04|13–14|shos alol|STAY LEAVE THERE|
|S05|15–15|dy|THEN THEN|
|S06|16–16|kar|THEN THEN|
|S07|17–17|oky|THEN THEN|
|S08|18–18|daiiin|THEN THEN|
|S09|19–19|okar|THEN THEN|
|S10|20–21|ar okam|STAY LEAVE THERE|
|S11|22–22|tshol|THEN THEN|
|S12|23–23|kar|THEN THEN|
|S13|24–24|sheedy|THEN THEN|
|S14|25–25|okeody|THEN THEN|
|S15|26–31|qokedy chody kchdy pchdy chkaiin odam|PAIR C PAIRED_WITH UNATTENDED W WOULD_BE UNSAFE|
|S16|32–32|tchdy|THEN THEN|
|S17|33–34|qokas chedy|EXCLUDE RETURN_EXCLUDING G|
|S18|35–35|qokchdy|THEN THEN|
|S19|36–37|qokaiin or|FERRY FERRY W|
|S20|38–39|ar alol|STAY LEAVE THERE|
|S21|40–40|keodaiin|THEN THEN|
|S22|41–41|ols|THEN THEN|
|S23|42–43|solkchy chckhy|STAY LEAVE THERE|
|S24|44–44|qokchdy|THEN THEN|
|S25|45–45|qokchdy|THEN THEN|
|S26|46–46|okar|THEN THEN|
|S27|47–48|ar y|STAY LEAVE THERE|
|S28|49–49|qokchdy|THEN THEN|
|S29|50–50|kar|THEN THEN|
|S30|51–52|ar okain|STAY LEAVE THERE|
|S31|53–54|ykain [sh:{c's}]ear|ALONE RETURN ALONE|
|S32|55–57|ol kchedy okal|CONVEY CONVEY_OUT NEXT G|
|S33|58–58|qotor|THEN THEN|
|S34|59–60|cheeor olk[ee:a]dy|EXCLUDE RETURN_EXCLUDING G|
|S35|61–61|daiin|THEN THEN|
|S36|62–63|qoky todalain|FERRY FERRY W|
|S37|64–64|qotal|THEN THEN|
|S38|65–66|kaiin otaiin|STAY LEAVE THERE|
|S39|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S41|78–78|kar|THEN THEN|
|S42|79–80|shedain taipar|ALONE RETURN ALONE|
|S43|81–81|orolkain|THEN THEN|
|S44|82–84|ytchdy kchedy ykeey|CONVEY CONVEY_OUT NEXT C|
|S45|85–86|kaiin qokain|STAY LEAVE THERE|
|S46|87–87|ald|THEN THEN|
|S47|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 2.
- S19 FIXED_TRIP_FAILED; prefix S03:W, S17:empty.
- S36 FIXED_TRIP_FAILED; prefix S03:W, S17:W, S19:W, S31:empty, S32:G, S34:empty.

## FULL06_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "OTHER", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–7|dair o|FERRY FERRY W|
|S03|8–13|laiin chefchdy sor orsheckhy ockhody shos|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S04|14–14|alol|THEN THEN|
|S05|15–15|dy|THEN THEN|
|S06|16–17|kar oky|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S07|18–18|daiiin|THEN THEN|
|S08|19–20|okar ar|FERRY FERRY G|
|S09|21–21|okam|THEN THEN|
|S10|22–22|tshol|THEN THEN|
|S11|23–24|kar sheedy|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S12|25–26|okeody qokedy|FERRY FERRY C|
|S13|27–27|chody|THEN THEN|
|S14|28–28|kchdy|THEN THEN|
|S15|29–29|pchdy|THEN THEN|
|S16|30–30|chkaiin|THEN THEN|
|S17|31–32|odam tchdy|EXCLUDE RETURN_EXCLUDING C|
|S18|33–34|qokas chedy|FERRY FERRY G|
|S19|35–35|qokchdy|THEN THEN|
|S20|36–36|qokaiin|THEN THEN|
|S21|37–38|or ar|FERRY FERRY G|
|S22|39–39|alol|THEN THEN|
|S23|40–40|keodaiin|THEN THEN|
|S24|41–41|ols|THEN THEN|
|S25|42–43|solkchy chckhy|STAY LEAVE THERE|
|S26|44–44|qokchdy|THEN THEN|
|S27|45–45|qokchdy|THEN THEN|
|S28|46–47|okar ar|FERRY FERRY G|
|S29|48–48|y|THEN THEN|
|S30|49–49|qokchdy|THEN THEN|
|S31|50–51|kar ar|EXCLUDE RETURN_EXCLUDING G|
|S32|52–52|okain|THEN THEN|
|S33|53–53|ykain|THEN THEN|
|S34|54–54|[sh:{c's}]ear|THEN THEN|
|S35|55–56|ol kchedy|FERRY FERRY FIRST_CARGO|
|S36|57–57|okal|THEN THEN|
|S37|58–61|qotor cheeor olk[ee:a]dy daiin|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S38|62–63|qoky todalain|FERRY FERRY FIRST_CARGO|
|S39|64–64|qotal|THEN THEN|
|S40|65–66|kaiin otaiin|STAY LEAVE THERE|
|S41|67–68|otal she|STAY LEAVE THERE|
|S42|69–69|ka[r:s]|THEN THEN|
|S43|70–71|ariin okchedy|FERRY FERRY C|
|S44|72–76|dariin yk ykaiin sheekar otchdy|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S45|77–77|dar|THEN THEN|
|S46|78–79|kar shedain|EXCLUDE RETURN_EXCLUDING G|
|S47|80–81|taipar orolkain|STAY LEAVE THERE|
|S48|82–83|ytchdy kchedy|FERRY FERRY FIRST_CARGO|
|S49|84–84|ykeey|THEN THEN|
|S50|85–86|kaiin qokain|STAY LEAVE THERE|
|S51|87–87|ald|THEN THEN|
|S52|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 10.
- S18 FIXED_TRIP_FAILED; prefix S02:W, S06:empty, S08:G, S11:empty, S12:C, S17:empty.
- S35 FIXED_TRIP_FAILED; prefix S02:W, S06:empty, S08:G, S11:empty, S12:C, S17:G, S18:G, S21:G, S28:G, S31:empty.
- S47 NO_CARGO_FOR_STAY; prefix S02:W, S06:empty, S08:G, S11:empty, S12:C, S17:G, S18:G, S21:G, S28:G, S31:C, S35:C, S38:C, S43:C, S46:empty.
- S48 FIXED_TRIP_FAILED; prefix S02:W, S06:empty, S08:G, S11:empty, S12:C, S17:G, S18:G, S21:G, S28:G, S31:C, S35:C, S38:C, S43:C, S46:W.
- S35 FIXED_TRIP_FAILED; prefix S02:W, S06:empty, S08:G, S11:empty, S12:C, S17:G, S18:G, S21:G, S28:G, S31:W.
- S18 FIXED_TRIP_FAILED; prefix S02:W, S06:empty, S08:G, S11:empty, S12:C, S17:W.
- S18 FIXED_TRIP_FAILED; prefix S02:W, S06:empty, S08:G, S11:W, S12:C, S17:empty.
- S35 FIXED_TRIP_FAILED; prefix S02:W, S06:empty, S08:G, S11:W, S12:C, S17:G, S18:G, S21:G, S28:G, S31:empty.
- S47 NO_CARGO_FOR_STAY; prefix S02:W, S06:empty, S08:G, S11:W, S12:C, S17:G, S18:G, S21:G, S28:G, S31:C, S35:C, S38:C, S43:C, S46:empty.
- S52 FINAL_LOCAL_ASSERTION_FALSE; prefix S02:W, S06:empty, S08:G, S11:W, S12:C, S17:G, S18:G, S21:G, S28:G, S31:C, S35:C, S38:C, S43:C, S46:C, S48:C.

## FULL06_independent — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "OTHER", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair o laiin chefchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–12|sor orsheckhy ockhody|CONVEY CONVEY_OUT NEXT G|
|S04|13–14|shos alol|STAY LEAVE THERE|
|S05|15–15|dy|THEN THEN|
|S06|16–16|kar|THEN THEN|
|S07|17–18|oky daiiin|FERRY FERRY G|
|S08|19–19|okar|THEN THEN|
|S09|20–21|ar okam|STAY LEAVE THERE|
|S10|22–22|tshol|THEN THEN|
|S11|23–23|kar|THEN THEN|
|S12|24–24|sheedy|THEN THEN|
|S13|25–25|okeody|THEN THEN|
|S14|26–31|qokedy chody kchdy pchdy chkaiin odam|PAIR C PAIRED_WITH UNATTENDED G WOULD_BE UNSAFE|
|S15|32–32|tchdy|THEN THEN|
|S16|33–34|qokas chedy|FERRY FERRY G|
|S17|35–35|qokchdy|THEN THEN|
|S18|36–36|qokaiin|THEN THEN|
|S19|37–37|or|THEN THEN|
|S20|38–39|ar alol|STAY LEAVE THERE|
|S21|40–40|keodaiin|THEN THEN|
|S22|41–41|ols|THEN THEN|
|S23|42–43|solkchy chckhy|STAY LEAVE THERE|
|S24|44–44|qokchdy|THEN THEN|
|S25|45–45|qokchdy|THEN THEN|
|S26|46–46|okar|THEN THEN|
|S27|47–48|ar y|STAY LEAVE THERE|
|S28|49–49|qokchdy|THEN THEN|
|S29|50–50|kar|THEN THEN|
|S30|51–52|ar okain|STAY LEAVE THERE|
|S31|53–54|ykain [sh:{c's}]ear|ALONE RETURN ALONE|
|S32|55–57|ol kchedy okal|CONVEY CONVEY_OUT NEXT W|
|S33|58–58|qotor|THEN THEN|
|S34|59–60|cheeor olk[ee:a]dy|EXCLUDE RETURN_EXCLUDING G|
|S35|61–61|daiin|THEN THEN|
|S36|62–63|qoky todalain|FERRY FERRY W|
|S37|64–64|qotal|THEN THEN|
|S38|65–66|kaiin otaiin|STAY LEAVE THERE|
|S39|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S41|78–78|kar|THEN THEN|
|S42|79–80|shedain taipar|ALONE RETURN ALONE|
|S43|81–81|orolkain|THEN THEN|
|S44|82–84|ytchdy kchedy ykeey|CONVEY CONVEY_OUT NEXT C|
|S45|85–86|kaiin qokain|STAY LEAVE THERE|
|S46|87–87|ald|THEN THEN|
|S47|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 1.
- S36 FIXED_TRIP_FAILED; prefix S03:G, S07:G, S16:G, S31:empty, S32:W, S34:empty.

## FULL07_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "FIRST", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–6|dair|THEN THEN|
|S03|7–7|o|THEN THEN|
|S04|8–8|laiin|THEN THEN|
|S05|9–9|chefchdy|THEN THEN|
|S06|10–10|sor|THEN THEN|
|S07|11–11|orsheckhy|THEN THEN|
|S08|12–12|ockhody|THEN THEN|
|S09|13–13|shos|THEN THEN|
|S10|14–14|alol|THEN THEN|
|S11|15–15|dy|THEN THEN|
|S12|16–16|kar|THEN THEN|
|S13|17–18|oky daiiin|FERRY FERRY W|
|S14|19–19|okar|THEN THEN|
|S15|20–20|ar|THEN THEN|
|S16|21–22|okam tshol|EXCLUDE RETURN_EXCLUDING G|
|S17|23–23|kar|THEN THEN|
|S18|24–24|sheedy|THEN THEN|
|S19|25–26|okeody qokedy|FERRY FERRY C|
|S20|27–28|chody kchdy|EXCLUDE RETURN_EXCLUDING OTHER_CARGO|
|S21|29–29|pchdy|THEN THEN|
|S22|30–31|chkaiin odam|FERRY FERRY OTHER_CARGO|
|S23|32–32|tchdy|THEN THEN|
|S24|33–34|qokas chedy|EXCLUDE RETURN_EXCLUDING G|
|S25|35–35|qokchdy|THEN THEN|
|S26|36–36|qokaiin|THEN THEN|
|S27|37–37|or|THEN THEN|
|S28|38–38|ar|THEN THEN|
|S29|39–39|alol|THEN THEN|
|S30|40–41|keodaiin ols|FERRY FERRY FIRST_CARGO|
|S31|42–43|solkchy chckhy|STAY LEAVE THERE|
|S32|44–44|qokchdy|THEN THEN|
|S33|45–45|qokchdy|THEN THEN|
|S34|46–46|okar|THEN THEN|
|S35|47–47|ar|THEN THEN|
|S36|48–48|y|THEN THEN|
|S37|49–49|qokchdy|THEN THEN|
|S38|50–50|kar|THEN THEN|
|S39|51–51|ar|THEN THEN|
|S40|52–52|okain|THEN THEN|
|S41|53–53|ykain|THEN THEN|
|S42|54–54|[sh:{c's}]ear|THEN THEN|
|S43|55–56|ol kchedy|EXCLUDE RETURN_EXCLUDING OTHER_CARGO|
|S44|57–60|okal qotor cheeor olk[ee:a]dy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S45|61–61|daiin|THEN THEN|
|S46|62–63|qoky todalain|FERRY FERRY G|
|S47|64–64|qotal|THEN THEN|
|S48|65–66|kaiin otaiin|STAY LEAVE THERE|
|S49|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S50|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE W|
|S51|78–78|kar|THEN THEN|
|S52|79–80|shedain taipar|FERRY FERRY W|
|S53|81–81|orolkain|THEN THEN|
|S54|82–83|ytchdy kchedy|FERRY FERRY OTHER_CARGO|
|S55|84–84|ykeey|THEN THEN|
|S56|85–86|kaiin qokain|STAY LEAVE THERE|
|S57|87–87|ald|THEN THEN|
|S58|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 2; failed eligible prefixes: 8.
- S22 FIXED_TRIP_FAILED; prefix S13:W, S16:empty, S19:C, S20:empty.
- S22 FIXED_TRIP_FAILED; prefix S13:W, S16:empty, S19:C, S20:C.
- S30 FIXED_TRIP_FAILED; prefix S13:W, S16:W, S19:C, S20:empty, S22:W, S24:empty.
- S58 FINAL_LOCAL_ASSERTION_FALSE; prefix S13:W, S16:W, S19:C, S20:empty, S22:W, S24:C, S30:C, S43:C, S46:G, S52:W, S54:W.
- S30 FIXED_TRIP_FAILED; prefix S13:W, S16:W, S19:C, S20:empty, S22:W, S24:W.
- S58 FINAL_LOCAL_ASSERTION_FALSE; prefix S13:W, S16:W, S19:C, S20:C, S22:W, S24:empty, S30:C, S43:C, S46:G, S52:W, S54:W.
- S52 FIXED_TRIP_FAILED; prefix S13:W, S16:W, S19:C, S20:C, S22:W, S24:W, S30:C, S43:empty, S46:G.
- S52 FIXED_TRIP_FAILED; prefix S13:W, S16:W, S19:C, S20:C, S22:W, S24:W, S30:C, S43:C, S46:G.

## FULL07_independent — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "FIRST", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair o laiin chefchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–12|sor orsheckhy ockhody|CONVEY CONVEY_OUT NEXT C|
|S04|13–14|shos alol|STAY LEAVE THERE|
|S05|15–15|dy|THEN THEN|
|S06|16–16|kar|THEN THEN|
|S07|17–17|oky|THEN THEN|
|S08|18–18|daiiin|THEN THEN|
|S09|19–19|okar|THEN THEN|
|S10|20–21|ar okam|STAY LEAVE THERE|
|S11|22–22|tshol|THEN THEN|
|S12|23–23|kar|THEN THEN|
|S13|24–24|sheedy|THEN THEN|
|S14|25–25|okeody|THEN THEN|
|S15|26–31|qokedy chody kchdy pchdy chkaiin odam|PAIR C PAIRED_WITH UNATTENDED W WOULD_BE UNSAFE|
|S16|32–32|tchdy|THEN THEN|
|S17|33–34|qokas chedy|EXCLUDE RETURN_EXCLUDING G|
|S18|35–35|qokchdy|THEN THEN|
|S19|36–37|qokaiin or|FERRY FERRY C|
|S20|38–39|ar alol|STAY LEAVE THERE|
|S21|40–40|keodaiin|THEN THEN|
|S22|41–41|ols|THEN THEN|
|S23|42–43|solkchy chckhy|STAY LEAVE THERE|
|S24|44–44|qokchdy|THEN THEN|
|S25|45–45|qokchdy|THEN THEN|
|S26|46–46|okar|THEN THEN|
|S27|47–48|ar y|STAY LEAVE THERE|
|S28|49–49|qokchdy|THEN THEN|
|S29|50–50|kar|THEN THEN|
|S30|51–52|ar okain|STAY LEAVE THERE|
|S31|53–54|ykain [sh:{c's}]ear|ALONE RETURN ALONE|
|S32|55–57|ol kchedy okal|CONVEY CONVEY_OUT NEXT W|
|S33|58–58|qotor|THEN THEN|
|S34|59–60|cheeor olk[ee:a]dy|EXCLUDE RETURN_EXCLUDING C|
|S35|61–61|daiin|THEN THEN|
|S36|62–63|qoky todalain|FERRY FERRY G|
|S37|64–64|qotal|THEN THEN|
|S38|65–66|kaiin otaiin|STAY LEAVE THERE|
|S39|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S41|78–78|kar|THEN THEN|
|S42|79–80|shedain taipar|ALONE RETURN ALONE|
|S43|81–81|orolkain|THEN THEN|
|S44|82–84|ytchdy kchedy ykeey|CONVEY CONVEY_OUT NEXT W|
|S45|85–86|kaiin qokain|STAY LEAVE THERE|
|S46|87–87|ald|THEN THEN|
|S47|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 1.
- S19 FIXED_TRIP_FAILED; prefix S03:C, S17:empty.

## FULL08_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "FIRST", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–6|dair|THEN THEN|
|S03|7–8|o laiin|FERRY FERRY W|
|S04|9–10|chefchdy sor|EXCLUDE RETURN_EXCLUDING C|
|S05|11–12|orsheckhy ockhody|FERRY FERRY W|
|S06|13–14|shos alol|EXCLUDE RETURN_EXCLUDING OTHER_CARGO|
|S07|15–15|dy|THEN THEN|
|S08|16–16|kar|THEN THEN|
|S09|17–17|oky|THEN THEN|
|S10|18–18|daiiin|THEN THEN|
|S11|19–19|okar|THEN THEN|
|S12|20–21|ar okam|FERRY FERRY G|
|S13|22–22|tshol|THEN THEN|
|S14|23–23|kar|THEN THEN|
|S15|24–24|sheedy|THEN THEN|
|S16|25–26|okeody qokedy|EXCLUDE RETURN_EXCLUDING C|
|S17|27–28|chody kchdy|FERRY FERRY C|
|S18|29–30|pchdy chkaiin|STAY LEAVE THERE|
|S19|31–31|odam|THEN THEN|
|S20|32–32|tchdy|THEN THEN|
|S21|33–34|qokas chedy|EXCLUDE RETURN_EXCLUDING G|
|S22|35–35|qokchdy|THEN THEN|
|S23|36–36|qokaiin|THEN THEN|
|S24|37–37|or|THEN THEN|
|S25|38–39|ar alol|FERRY FERRY OTHER_CARGO|
|S26|40–41|keodaiin ols|EXCLUDE RETURN_EXCLUDING G|
|S27|42–43|solkchy chckhy|STAY LEAVE THERE|
|S28|44–44|qokchdy|THEN THEN|
|S29|45–45|qokchdy|THEN THEN|
|S30|46–46|okar|THEN THEN|
|S31|47–48|ar y|FERRY FERRY W|
|S32|49–49|qokchdy|THEN THEN|
|S33|50–50|kar|THEN THEN|
|S34|51–52|ar okain|FERRY FERRY C|
|S35|53–53|ykain|THEN THEN|
|S36|54–57|[sh:{c's}]ear ol kchedy okal|WITH_OUT WITH_TRIP B TAKE_OUT C|
|S37|58–61|qotor cheeor olk[ee:a]dy daiin|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S38|62–63|qoky todalain|FERRY FERRY G|
|S39|64–64|qotal|THEN THEN|
|S40|65–66|kaiin otaiin|STAY LEAVE THERE|
|S41|67–71|otal she ka[r:s] ariin okchedy|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE W|
|S42|72–77|dariin yk ykaiin sheekar otchdy dar|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S43|78–78|kar|THEN THEN|
|S44|79–79|shedain|THEN THEN|
|S45|80–80|taipar|THEN THEN|
|S46|81–84|orolkain ytchdy kchedy ykeey|WITH_OUT WITH_TRIP B TAKE_OUT G|
|S47|85–86|kaiin qokain|STAY LEAVE THERE|
|S48|87–87|ald|THEN THEN|
|S49|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 2; failed eligible prefixes: 14.
- S05 FIXED_TRIP_FAILED; prefix S03:W, S04:empty.
- S25 FIXED_TRIP_FAILED; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:empty, S17:C, S21:empty.
- S25 FIXED_TRIP_FAILED; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:empty, S17:C, S21:C.
- S27 NO_CARGO_FOR_STAY; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:empty, S17:C, S21:W, S25:W, S26:empty.
- S31 FIXED_TRIP_FAILED; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:empty, S17:C, S21:W, S25:W, S26:C.
- S25 FIXED_TRIP_FAILED; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:G, S17:C, S21:empty.
- S25 FIXED_TRIP_FAILED; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:G, S17:C, S21:C.
- S27 NO_CARGO_FOR_STAY; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:G, S17:C, S21:W, S25:W, S26:empty.
- S31 FIXED_TRIP_FAILED; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:G, S17:C, S21:W, S25:W, S26:C.
- S38 FIXED_TRIP_FAILED; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:G, S17:C, S21:W, S25:W, S26:W, S31:W, S34:C, S36:C.
- S27 NO_CARGO_FOR_STAY; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:W, S17:C, S21:empty, S25:W, S26:empty.
- S31 FIXED_TRIP_FAILED; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:W, S17:C, S21:empty, S25:W, S26:C.
- S27 NO_CARGO_FOR_STAY; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:W, S17:C, S21:C, S25:W, S26:empty.
- S34 FIXED_TRIP_FAILED; prefix S03:W, S04:W, S05:W, S06:empty, S12:G, S16:W, S17:C, S21:C, S25:W, S26:W, S31:W.

## FULL08_independent — SUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "FIRST", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair o laiin chefchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–12|sor orsheckhy ockhody|CONVEY CONVEY_OUT NEXT C|
|S04|13–14|shos alol|STAY LEAVE THERE|
|S05|15–15|dy|THEN THEN|
|S06|16–16|kar|THEN THEN|
|S07|17–18|oky daiiin|FERRY FERRY C|
|S08|19–19|okar|THEN THEN|
|S09|20–21|ar okam|STAY LEAVE THERE|
|S10|22–22|tshol|THEN THEN|
|S11|23–23|kar|THEN THEN|
|S12|24–24|sheedy|THEN THEN|
|S13|25–25|okeody|THEN THEN|
|S14|26–31|qokedy chody kchdy pchdy chkaiin odam|PAIR C PAIRED_WITH UNATTENDED G WOULD_BE UNSAFE|
|S15|32–32|tchdy|THEN THEN|
|S16|33–34|qokas chedy|FERRY FERRY G|
|S17|35–35|qokchdy|THEN THEN|
|S18|36–36|qokaiin|THEN THEN|
|S19|37–37|or|THEN THEN|
|S20|38–39|ar alol|STAY LEAVE THERE|
|S21|40–40|keodaiin|THEN THEN|
|S22|41–41|ols|THEN THEN|
|S23|42–43|solkchy chckhy|STAY LEAVE THERE|
|S24|44–44|qokchdy|THEN THEN|
|S25|45–45|qokchdy|THEN THEN|
|S26|46–46|okar|THEN THEN|
|S27|47–48|ar y|STAY LEAVE THERE|
|S28|49–49|qokchdy|THEN THEN|
|S29|50–50|kar|THEN THEN|
|S30|51–52|ar okain|STAY LEAVE THERE|
|S31|53–54|ykain [sh:{c's}]ear|ALONE RETURN ALONE|
|S32|55–57|ol kchedy okal|CONVEY CONVEY_OUT NEXT C|
|S33|58–58|qotor|THEN THEN|
|S34|59–60|cheeor olk[ee:a]dy|EXCLUDE RETURN_EXCLUDING C|
|S35|61–61|daiin|THEN THEN|
|S36|62–63|qoky todalain|FERRY FERRY W|
|S37|64–64|qotal|THEN THEN|
|S38|65–66|kaiin otaiin|STAY LEAVE THERE|
|S39|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S41|78–78|kar|THEN THEN|
|S42|79–80|shedain taipar|ALONE RETURN ALONE|
|S43|81–81|orolkain|THEN THEN|
|S44|82–84|ytchdy kchedy ykeey|CONVEY CONVEY_OUT NEXT G|
|S45|85–86|kaiin qokain|STAY LEAVE THERE|
|S46|87–87|ald|THEN THEN|
|S47|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 0.
Voyages: S03:C → S07:C → S16:G → S31:empty → S32:C → S34:G → S36:W → S42:empty → S44:G.

## FULL09_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–6|dair|THEN THEN|
|S03|7–7|o|THEN THEN|
|S04|8–8|laiin|THEN THEN|
|S05|9–13|chefchdy sor orsheckhy ockhody shos|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE W|
|S06|14–15|alol dy|FERRY FERRY FIRST_CARGO|
|S07|16–16|kar|THEN THEN|
|S08|17–18|oky daiiin|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S09|19–19|okar|THEN THEN|
|S10|20–20|ar|THEN THEN|
|S11|21–21|okam|THEN THEN|
|S12|22–22|tshol|THEN THEN|
|S13|23–23|kar|THEN THEN|
|S14|24–24|sheedy|THEN THEN|
|S15|25–26|okeody qokedy|FERRY FERRY C|
|S16|27–28|chody kchdy|STAY LEAVE THERE|
|S17|29–29|pchdy|THEN THEN|
|S18|30–30|chkaiin|THEN THEN|
|S19|31–34|odam tchdy qokas chedy|RESULT JOINING_RESULT REST_CARGO COLOC FIRST_CARGO|
|S20|35–35|qokchdy|THEN THEN|
|S21|36–37|qokaiin or|EXCLUDE RETURN_EXCLUDING C|
|S22|38–38|ar|THEN THEN|
|S23|39–40|alol keodaiin|FERRY FERRY W|
|S24|41–41|ols|THEN THEN|
|S25|42–43|solkchy chckhy|STAY LEAVE THERE|
|S26|44–44|qokchdy|THEN THEN|
|S27|45–45|qokchdy|THEN THEN|
|S28|46–46|okar|THEN THEN|
|S29|47–47|ar|THEN THEN|
|S30|48–48|y|THEN THEN|
|S31|49–49|qokchdy|THEN THEN|
|S32|50–50|kar|THEN THEN|
|S33|51–51|ar|THEN THEN|
|S34|52–53|okain ykain|STAY LEAVE THERE|
|S35|54–55|[sh:{c's}]ear ol|STAY LEAVE THERE|
|S36|56–56|kchedy|THEN THEN|
|S37|57–57|okal|THEN THEN|
|S38|58–58|qotor|THEN THEN|
|S39|59–59|cheeor|THEN THEN|
|S40|60–61|olk[ee:a]dy daiin|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S41|62–63|qoky todalain|FERRY FERRY C|
|S42|64–64|qotal|THEN THEN|
|S43|65–66|kaiin otaiin|STAY LEAVE THERE|
|S44|67–67|otal|THEN THEN|
|S45|68–69|she ka[r:s]|EXCLUDE RETURN_EXCLUDING C|
|S46|70–71|ariin okchedy|FERRY FERRY FIRST_CARGO|
|S47|72–77|dariin yk ykaiin sheekar otchdy dar|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S48|78–78|kar|THEN THEN|
|S49|79–82|shedain taipar orolkain ytchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S50|83–83|kchedy|THEN THEN|
|S51|84–84|ykeey|THEN THEN|
|S52|85–86|kaiin qokain|STAY LEAVE THERE|
|S53|87–87|ald|THEN THEN|
|S54|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 3.
- S23 FIXED_TRIP_FAILED; prefix S06:W, S08:empty, S15:C, S21:empty.
- S41 FIXED_TRIP_FAILED; prefix S06:W, S08:empty, S15:C, S21:W, S23:W, S40:empty.
- S46 FIXED_TRIP_FAILED; prefix S06:W, S08:empty, S15:C, S21:W, S23:W, S40:C, S41:C, S45:empty.

## FULL10_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–6|dair|THEN THEN|
|S03|7–7|o|THEN THEN|
|S04|8–8|laiin|THEN THEN|
|S05|9–9|chefchdy|THEN THEN|
|S06|10–10|sor|THEN THEN|
|S07|11–12|orsheckhy ockhody|FERRY FERRY G|
|S08|13–13|shos|THEN THEN|
|S09|14–14|alol|THEN THEN|
|S10|15–15|dy|THEN THEN|
|S11|16–17|kar oky|EXCLUDE RETURN_EXCLUDING C|
|S12|18–18|daiiin|THEN THEN|
|S13|19–20|okar ar|FERRY FERRY W|
|S14|21–21|okam|THEN THEN|
|S15|22–22|tshol|THEN THEN|
|S16|23–24|kar sheedy|EXCLUDE RETURN_EXCLUDING W|
|S17|25–26|okeody qokedy|FERRY FERRY C|
|S18|27–31|chody kchdy pchdy chkaiin odam|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE W|
|S19|32–32|tchdy|THEN THEN|
|S20|33–34|qokas chedy|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S21|35–35|qokchdy|THEN THEN|
|S22|36–38|qokaiin or ar|CONVEY CONVEY_OUT NEXT W|
|S23|39–39|alol|THEN THEN|
|S24|40–41|keodaiin ols|EXCLUDE RETURN_EXCLUDING C|
|S25|42–43|solkchy chckhy|STAY LEAVE THERE|
|S26|44–44|qokchdy|THEN THEN|
|S27|45–45|qokchdy|THEN THEN|
|S28|46–47|okar ar|FERRY FERRY W|
|S29|48–48|y|THEN THEN|
|S30|49–49|qokchdy|THEN THEN|
|S31|50–51|kar ar|EXCLUDE RETURN_EXCLUDING W|
|S32|52–53|okain ykain|FERRY FERRY G|
|S33|54–55|[sh:{c's}]ear ol|STAY LEAVE THERE|
|S34|56–56|kchedy|THEN THEN|
|S35|57–57|okal|THEN THEN|
|S36|58–61|qotor cheeor olk[ee:a]dy daiin|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S37|62–63|qoky todalain|FERRY FERRY W|
|S38|64–64|qotal|THEN THEN|
|S39|65–66|kaiin otaiin|STAY LEAVE THERE|
|S40|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S41|73–74|yk ykaiin|FERRY FERRY W|
|S42|75–76|sheekar otchdy|STAY LEAVE THERE|
|S43|77–77|dar|THEN THEN|
|S44|78–79|kar shedain|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S45|80–81|taipar orolkain|FERRY FERRY W|
|S46|82–82|ytchdy|THEN THEN|
|S47|83–83|kchedy|THEN THEN|
|S48|84–84|ykeey|THEN THEN|
|S49|85–86|kaiin qokain|STAY LEAVE THERE|
|S50|87–87|ald|THEN THEN|
|S51|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 3; failed eligible prefixes: 22.
- S22 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:empty, S17:C, S20:empty.
- S22 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:empty, S17:C, S20:C.
- S25 NO_CARGO_FOR_STAY; prefix S07:G, S11:empty, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:empty.
- S28 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:G.
- S32 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:W, S28:W, S31:empty.
- S32 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:W, S28:W, S31:C.
- S45 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:W, S28:W, S31:G, S32:G, S37:W, S41:W, S44:empty.
- S45 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:W, S28:W, S31:G, S32:G, S37:W, S41:W, S44:C.
- S22 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:G, S17:C, S20:empty.
- S22 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:G, S17:C, S20:C.
- S25 NO_CARGO_FOR_STAY; prefix S07:G, S11:empty, S13:W, S16:G, S17:C, S20:W, S22:W, S24:empty.
- S45 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:G, S17:C, S20:W, S22:W, S24:W, S28:W, S31:empty, S32:G, S37:W, S41:W, S44:empty.
- S45 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:G, S17:C, S20:W, S22:W, S24:W, S28:W, S31:empty, S32:G, S37:W, S41:W, S44:C.
- S45 FIXED_TRIP_FAILED; prefix S07:G, S11:empty, S13:W, S16:G, S17:C, S20:W, S22:W, S24:W, S28:W, S31:C, S32:G, S37:W, S41:W, S44:empty.
- S51 FINAL_LOCAL_ASSERTION_FALSE; prefix S07:G, S11:empty, S13:W, S16:G, S17:C, S20:W, S22:W, S24:W, S28:W, S31:C, S32:G, S37:W, S41:W, S44:W, S45:W.
- S22 FIXED_TRIP_FAILED; prefix S07:G, S11:G, S13:W, S16:empty, S17:C, S20:empty.
- S22 FIXED_TRIP_FAILED; prefix S07:G, S11:G, S13:W, S16:empty, S17:C, S20:C.
- S25 NO_CARGO_FOR_STAY; prefix S07:G, S11:G, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:empty.
- S45 FIXED_TRIP_FAILED; prefix S07:G, S11:G, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:W, S28:W, S31:empty, S32:G, S37:W, S41:W, S44:empty.
- S45 FIXED_TRIP_FAILED; prefix S07:G, S11:G, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:W, S28:W, S31:empty, S32:G, S37:W, S41:W, S44:C.
- S45 FIXED_TRIP_FAILED; prefix S07:G, S11:G, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:W, S28:W, S31:C, S32:G, S37:W, S41:W, S44:empty.
- S51 FINAL_LOCAL_ASSERTION_FALSE; prefix S07:G, S11:G, S13:W, S16:empty, S17:C, S20:W, S22:W, S24:W, S28:W, S31:C, S32:G, S37:W, S41:W, S44:W, S45:W.

## FULL10_independent — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkair olfchedy qop[eee:che]dar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair o laiin chefchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–12|sor orsheckhy ockhody|CONVEY CONVEY_OUT NEXT G|
|S04|13–14|shos alol|STAY LEAVE THERE|
|S05|15–15|dy|THEN THEN|
|S06|16–16|kar|THEN THEN|
|S07|17–18|oky daiiin|FERRY FERRY G|
|S08|19–19|okar|THEN THEN|
|S09|20–21|ar okam|STAY LEAVE THERE|
|S10|22–22|tshol|THEN THEN|
|S11|23–23|kar|THEN THEN|
|S12|24–24|sheedy|THEN THEN|
|S13|25–25|okeody|THEN THEN|
|S14|26–31|qokedy chody kchdy pchdy chkaiin odam|PAIR C PAIRED_WITH UNATTENDED G WOULD_BE UNSAFE|
|S15|32–32|tchdy|THEN THEN|
|S16|33–34|qokas chedy|FERRY FERRY FIRST_CARGO|
|S17|35–35|qokchdy|THEN THEN|
|S18|36–36|qokaiin|THEN THEN|
|S19|37–37|or|THEN THEN|
|S20|38–39|ar alol|STAY LEAVE THERE|
|S21|40–40|keodaiin|THEN THEN|
|S22|41–41|ols|THEN THEN|
|S23|42–43|solkchy chckhy|STAY LEAVE THERE|
|S24|44–44|qokchdy|THEN THEN|
|S25|45–45|qokchdy|THEN THEN|
|S26|46–46|okar|THEN THEN|
|S27|47–48|ar y|STAY LEAVE THERE|
|S28|49–49|qokchdy|THEN THEN|
|S29|50–50|kar|THEN THEN|
|S30|51–52|ar okain|STAY LEAVE THERE|
|S31|53–54|ykain [sh:{c's}]ear|ALONE RETURN ALONE|
|S32|55–57|ol kchedy okal|CONVEY CONVEY_OUT NEXT W|
|S33|58–58|qotor|THEN THEN|
|S34|59–60|cheeor olk[ee:a]dy|EXCLUDE RETURN_EXCLUDING G|
|S35|61–61|daiin|THEN THEN|
|S36|62–63|qoky todalain|FERRY FERRY W|
|S37|64–64|qotal|THEN THEN|
|S38|65–66|kaiin otaiin|STAY LEAVE THERE|
|S39|67–72|otal she ka[r:s] ariin okchedy dariin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|73–77|yk ykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S41|78–78|kar|THEN THEN|
|S42|79–80|shedain taipar|ALONE RETURN ALONE|
|S43|81–81|orolkain|THEN THEN|
|S44|82–84|ytchdy kchedy ykeey|CONVEY CONVEY_OUT NEXT C|
|S45|85–86|kaiin qokain|STAY LEAVE THERE|
|S46|87–87|ald|THEN THEN|
|S47|88–93|[a:y]lo[s:r]am solkaiin opalke chckhy darin chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 1.
- S36 FIXED_TRIP_FAILED; prefix S03:G, S07:G, S16:G, S31:empty, S32:W, S34:empty.

## FULL11_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–7|dair olaiin|FERRY FERRY W|
|S03|8–9|chefchdy sor|ALONE RETURN ALONE|
|S04|10–10|orsheckhy|THEN THEN|
|S05|11–12|ockhody shos|FERRY FERRY C|
|S06|13–13|alol|THEN THEN|
|S07|14–14|dy|THEN THEN|
|S08|15–15|kar|THEN THEN|
|S09|16–17|oky daiiin|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S10|18–18|okar|THEN THEN|
|S11|19–19|ar|THEN THEN|
|S12|20–21|okam tshol|FERRY FERRY C|
|S13|22–22|kar|THEN THEN|
|S14|23–23|sheedy|THEN THEN|
|S15|24–25|okeody qokedy|FERRY FERRY C|
|S16|26–27|chody kchdy|FERRY FERRY C|
|S17|28–29|pchdy chkaiin|EXCLUDE RETURN_EXCLUDING G|
|S18|30–30|odam|THEN THEN|
|S19|31–31|tchdy|THEN THEN|
|S20|32–33|qokar chedy|FERRY FERRY G|
|S21|34–34|qokchdy|THEN THEN|
|S22|35–35|qokaiin|THEN THEN|
|S23|36–36|or|THEN THEN|
|S24|37–37|ar|THEN THEN|
|S25|38–38|alol|THEN THEN|
|S26|39–39|keodaiin|THEN THEN|
|S27|40–40|olr|THEN THEN|
|S28|41–42|solkchy chckhy|STAY LEAVE THERE|
|S29|43–43|qokchdy|THEN THEN|
|S30|44–44|qokchdy|THEN THEN|
|S31|45–45|okar|THEN THEN|
|S32|46–46|ar|THEN THEN|
|S33|47–47|y|THEN THEN|
|S34|48–48|qokchdy|THEN THEN|
|S35|49–49|kar|THEN THEN|
|S36|50–50|ar|THEN THEN|
|S37|51–52|okain ykain|EXCLUDE RETURN_EXCLUDING C|
|S38|53–53|ssear|THEN THEN|
|S39|54–59|olkchedy okal qotor cheeor olkady daiin|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|60–61|qoky todalain|FERRY FERRY FIRST_CARGO|
|S41|62–62|qotal|THEN THEN|
|S42|63–64|kaiin otaiin|STAY LEAVE THERE|
|S43|65–66|otal she|ALONE RETURN ALONE|
|S44|67–67|kar|THEN THEN|
|S45|68–69|ariin okchedy|FERRY FERRY C|
|S46|70–73|dariin ykykaiin sheekar otchdy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S47|74–74|dar|THEN THEN|
|S48|75–75|kar|THEN THEN|
|S49|76–76|shelain|THEN THEN|
|S50|77–81|taipar orolkain ytchdy kchedy ykeey|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE W|
|S51|82–83|kaiin qokain|STAY LEAVE THERE|
|S52|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 8.
- S12 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S05:C, S09:empty.
- S40 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S05:C, S09:C, S12:C, S15:C, S16:C, S17:empty, S20:G, S37:empty.
- S40 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S05:C, S09:C, S12:C, S15:C, S16:C, S17:empty, S20:G, S37:G.
- S45 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S05:C, S09:C, S12:C, S15:C, S16:C, S17:empty, S20:G, S37:W, S40:W, S43:empty.
- S40 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S05:C, S09:C, S12:C, S15:C, S16:C, S17:C, S20:G, S37:empty.
- S40 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S05:C, S09:C, S12:C, S15:C, S16:C, S17:C, S20:G, S37:G.
- S45 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S05:C, S09:C, S12:C, S15:C, S16:C, S17:W, S20:G, S37:empty, S40:W, S43:empty.
- S45 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S05:C, S09:C, S12:C, S15:C, S16:C, S17:W, S20:G, S37:G, S40:W, S43:empty.

## FULL12_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–7|dair olaiin|FERRY FERRY W|
|S03|8–9|chefchdy sor|EXCLUDE RETURN_EXCLUDING C|
|S04|10–12|orsheckhy ockhody shos|CONVEY CONVEY_OUT NEXT G|
|S05|13–14|alol dy|STAY LEAVE THERE|
|S06|15–15|kar|THEN THEN|
|S07|16–16|oky|THEN THEN|
|S08|17–17|daiiin|THEN THEN|
|S09|18–18|okar|THEN THEN|
|S10|19–19|ar|THEN THEN|
|S11|20–20|okam|THEN THEN|
|S12|21–21|tshol|THEN THEN|
|S13|22–22|kar|THEN THEN|
|S14|23–23|sheedy|THEN THEN|
|S15|24–25|okeody qokedy|EXCLUDE RETURN_EXCLUDING C|
|S16|26–27|chody kchdy|FERRY FERRY C|
|S17|28–28|pchdy|THEN THEN|
|S18|29–29|chkaiin|THEN THEN|
|S19|30–30|odam|THEN THEN|
|S20|31–31|tchdy|THEN THEN|
|S21|32–33|qokar chedy|FERRY FERRY G|
|S22|34–34|qokchdy|THEN THEN|
|S23|35–36|qokaiin or|FERRY FERRY FIRST_CARGO|
|S24|37–37|ar|THEN THEN|
|S25|38–39|alol keodaiin|STAY LEAVE THERE|
|S26|40–40|olr|THEN THEN|
|S27|41–42|solkchy chckhy|STAY LEAVE THERE|
|S28|43–43|qokchdy|THEN THEN|
|S29|44–44|qokchdy|THEN THEN|
|S30|45–45|okar|THEN THEN|
|S31|46–46|ar|THEN THEN|
|S32|47–47|y|THEN THEN|
|S33|48–48|qokchdy|THEN THEN|
|S34|49–49|kar|THEN THEN|
|S35|50–50|ar|THEN THEN|
|S36|51–52|okain ykain|ALONE RETURN ALONE|
|S37|53–58|ssear olkchedy okal qotor cheeor olkady|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S38|59–59|daiin|THEN THEN|
|S39|60–61|qoky todalain|FERRY FERRY G|
|S40|62–62|qotal|THEN THEN|
|S41|63–64|kaiin otaiin|STAY LEAVE THERE|
|S42|65–66|otal she|STAY LEAVE THERE|
|S43|67–67|kar|THEN THEN|
|S44|68–72|ariin okchedy dariin ykykaiin sheekar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE W|
|S45|73–74|otchdy dar|STAY LEAVE THERE|
|S46|75–75|kar|THEN THEN|
|S47|76–76|shelain|THEN THEN|
|S48|77–80|taipar orolkain ytchdy kchedy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S49|81–81|ykeey|THEN THEN|
|S50|82–83|kaiin qokain|STAY LEAVE THERE|
|S51|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 2; failed eligible prefixes: 3.
- S23 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S15:empty, S16:C, S21:G.
- S21 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S15:G, S16:C.
- S21 FIXED_TRIP_FAILED; prefix S02:W, S03:W, S04:G, S15:G, S16:C.

## FULL13_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "FIRST", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–7|dair olaiin|FERRY FERRY W|
|S03|8–9|chefchdy sor|EXCLUDE RETURN_EXCLUDING C|
|S04|10–11|orsheckhy ockhody|FERRY FERRY G|
|S05|12–13|shos alol|EXCLUDE RETURN_EXCLUDING C|
|S06|14–14|dy|THEN THEN|
|S07|15–15|kar|THEN THEN|
|S08|16–16|oky|THEN THEN|
|S09|17–17|daiiin|THEN THEN|
|S10|18–18|okar|THEN THEN|
|S11|19–20|ar okam|FERRY FERRY C|
|S12|21–21|tshol|THEN THEN|
|S13|22–22|kar|THEN THEN|
|S14|23–23|sheedy|THEN THEN|
|S15|24–26|okeody qokedy chody|WITH_RETURN WITH_TRIP C RETURN|
|S16|27–30|kchdy pchdy chkaiin odam|WITH_OUT WITH_TRIP B TAKE_OUT C|
|S17|31–31|tchdy|THEN THEN|
|S18|32–33|qokar chedy|EXCLUDE RETURN_EXCLUDING G|
|S19|34–34|qokchdy|THEN THEN|
|S20|35–35|qokaiin|THEN THEN|
|S21|36–36|or|THEN THEN|
|S22|37–38|ar alol|FERRY FERRY C|
|S23|39–39|keodaiin|THEN THEN|
|S24|40–40|olr|THEN THEN|
|S25|41–42|solkchy chckhy|STAY LEAVE THERE|
|S26|43–43|qokchdy|THEN THEN|
|S27|44–44|qokchdy|THEN THEN|
|S28|45–45|okar|THEN THEN|
|S29|46–47|ar y|FERRY FERRY C|
|S30|48–48|qokchdy|THEN THEN|
|S31|49–49|kar|THEN THEN|
|S32|50–51|ar okain|FERRY FERRY OTHER_CARGO|
|S33|52–57|ykain ssear olkchedy okal qotor cheeor|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S34|58–59|olkady daiin|ALONE RETURN ALONE|
|S35|60–61|qoky todalain|FERRY FERRY C|
|S36|62–62|qotal|THEN THEN|
|S37|63–64|kaiin otaiin|STAY LEAVE THERE|
|S38|65–66|otal she|ALONE RETURN ALONE|
|S39|67–67|kar|THEN THEN|
|S40|68–68|ariin|THEN THEN|
|S41|69–69|okchedy|THEN THEN|
|S42|70–74|dariin ykykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S43|75–75|kar|THEN THEN|
|S44|76–77|shelain taipar|FERRY FERRY G|
|S45|78–81|orolkain ytchdy kchedy ykeey|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S46|82–83|kaiin qokain|STAY LEAVE THERE|
|S47|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 11.
- S22 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S05:empty, S11:C, S15:C, S16:C, S18:empty.
- S32 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S05:empty, S11:C, S15:C, S16:C, S18:C, S22:C, S29:C.
- S22 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S05:empty, S11:C, S15:C, S16:C, S18:W.
- S22 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S05:G, S11:C, S15:C, S16:C, S18:empty.
- S32 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S05:G, S11:C, S15:C, S16:C, S18:C, S22:C, S29:C.
- S22 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S05:G, S11:C, S15:C, S16:C, S18:W.
- S22 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S05:W, S11:C, S15:C, S16:C, S18:empty.
- S44 FIXED_TRIP_FAILED; prefix S02:W, S03:empty, S04:G, S05:W, S11:C, S15:C, S16:C, S18:C, S22:C, S29:C, S32:W, S34:empty, S35:C, S38:empty.
- S22 FIXED_TRIP_FAILED; prefix S02:W, S03:W, S04:G, S05:empty, S11:C, S15:C, S16:C, S18:empty.
- S44 FIXED_TRIP_FAILED; prefix S02:W, S03:W, S04:G, S05:empty, S11:C, S15:C, S16:C, S18:C, S22:C, S29:C, S32:W, S34:empty, S35:C, S38:empty.
- S22 FIXED_TRIP_FAILED; prefix S02:W, S03:W, S04:G, S05:G, S11:C, S15:C, S16:C, S18:empty.

## FULL14_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "FIRST", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–11|dair olaiin chefchdy sor orsheckhy ockhody|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S03|12–13|shos alol|FERRY FERRY G|
|S04|14–14|dy|THEN THEN|
|S05|15–15|kar|THEN THEN|
|S06|16–17|oky daiiin|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S07|18–18|okar|THEN THEN|
|S08|19–20|ar okam|FERRY FERRY W|
|S09|21–21|tshol|THEN THEN|
|S10|22–22|kar|THEN THEN|
|S11|23–23|sheedy|THEN THEN|
|S12|24–25|okeody qokedy|EXCLUDE RETURN_EXCLUDING C|
|S13|26–26|chody|THEN THEN|
|S14|27–30|kchdy pchdy chkaiin odam|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S15|31–31|tchdy|THEN THEN|
|S16|32–33|qokar chedy|FERRY FERRY G|
|S17|34–34|qokchdy|THEN THEN|
|S18|35–35|qokaiin|THEN THEN|
|S19|36–36|or|THEN THEN|
|S20|37–38|ar alol|FERRY FERRY G|
|S21|39–39|keodaiin|THEN THEN|
|S22|40–40|olr|THEN THEN|
|S23|41–42|solkchy chckhy|STAY LEAVE THERE|
|S24|43–43|qokchdy|THEN THEN|
|S25|44–44|qokchdy|THEN THEN|
|S26|45–45|okar|THEN THEN|
|S27|46–47|ar y|FERRY FERRY C|
|S28|48–48|qokchdy|THEN THEN|
|S29|49–49|kar|THEN THEN|
|S30|50–51|ar okain|FERRY FERRY C|
|S31|52–56|ykain ssear olkchedy okal qotor|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE W|
|S32|57–58|cheeor olkady|FERRY FERRY C|
|S33|59–59|daiin|THEN THEN|
|S34|60–61|qoky todalain|FERRY FERRY C|
|S35|62–62|qotal|THEN THEN|
|S36|63–64|kaiin otaiin|STAY LEAVE THERE|
|S37|65–65|otal|THEN THEN|
|S38|66–66|she|THEN THEN|
|S39|67–67|kar|THEN THEN|
|S40|68–69|ariin okchedy|FERRY FERRY OTHER_CARGO|
|S41|70–71|dariin ykykaiin|ALONE RETURN ALONE|
|S42|72–72|sheekar|THEN THEN|
|S43|73–73|otchdy|THEN THEN|
|S44|74–74|dar|THEN THEN|
|S45|75–75|kar|THEN THEN|
|S46|76–76|shelain|THEN THEN|
|S47|77–79|taipar orolkain ytchdy|CONVEY CONVEY_OUT NEXT C|
|S48|80–81|kchedy ykeey|STAY LEAVE THERE|
|S49|82–83|kaiin qokain|STAY LEAVE THERE|
|S50|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 2.
- S16 FIXED_TRIP_FAILED; prefix S03:G, S06:empty, S08:W, S12:empty.
- S16 FIXED_TRIP_FAILED; prefix S03:G, S06:empty, S08:W, S12:W.

## FULL15_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "OTHER", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–9|dair olaiin chefchdy sor|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S03|10–10|orsheckhy|THEN THEN|
|S04|11–12|ockhody shos|FERRY FERRY W|
|S05|13–14|alol dy|ALONE RETURN ALONE|
|S06|15–15|kar|THEN THEN|
|S07|16–17|oky daiiin|FERRY FERRY G|
|S08|18–19|okar ar|EXCLUDE RETURN_EXCLUDING C|
|S09|20–20|okam|THEN THEN|
|S10|21–21|tshol|THEN THEN|
|S11|22–22|kar|THEN THEN|
|S12|23–23|sheedy|THEN THEN|
|S13|24–25|okeody qokedy|FERRY FERRY C|
|S14|26–28|chody kchdy pchdy|WITH_RETURN WITH_TRIP W RETURN|
|S15|29–29|chkaiin|THEN THEN|
|S16|30–30|odam|THEN THEN|
|S17|31–31|tchdy|THEN THEN|
|S18|32–33|qokar chedy|FERRY FERRY G|
|S19|34–34|qokchdy|THEN THEN|
|S20|35–35|qokaiin|THEN THEN|
|S21|36–38|or ar alol|WITH_RETURN WITH_TRIP C RETURN|
|S22|39–40|keodaiin olr|FERRY FERRY FIRST_CARGO|
|S23|41–42|solkchy chckhy|STAY LEAVE THERE|
|S24|43–43|qokchdy|THEN THEN|
|S25|44–44|qokchdy|THEN THEN|
|S26|45–46|okar ar|EXCLUDE RETURN_EXCLUDING C|
|S27|47–47|y|THEN THEN|
|S28|48–48|qokchdy|THEN THEN|
|S29|49–49|kar|THEN THEN|
|S30|50–55|ar okain ykain ssear olkchedy okal|PAIR C PAIRED_WITH UNATTENDED W WOULD_BE UNSAFE|
|S31|56–56|qotor|THEN THEN|
|S32|57–58|cheeor olkady|COPY LIKEWISE OTHER_CARGO|
|S33|59–59|daiin|THEN THEN|
|S34|60–61|qoky todalain|FERRY FERRY W|
|S35|62–62|qotal|THEN THEN|
|S36|63–64|kaiin otaiin|STAY LEAVE THERE|
|S37|65–66|otal she|STAY LEAVE THERE|
|S38|67–67|kar|THEN THEN|
|S39|68–73|ariin okchedy dariin ykykaiin sheekar otchdy|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S40|74–74|dar|THEN THEN|
|S41|75–75|kar|THEN THEN|
|S42|76–76|shelain|THEN THEN|
|S43|77–81|taipar orolkain ytchdy kchedy ykeey|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE W|
|S44|82–83|kaiin qokain|STAY LEAVE THERE|
|S45|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 2.
- S45 FINAL_LOCAL_ASSERTION_FALSE; prefix S04:W, S05:empty, S07:G, S08:G, S13:C, S14:W, S18:G, S21:C, S22:C, S26:G, S34:W.
- S14 FIXED_TRIP_FAILED; prefix S04:W, S05:empty, S07:G, S08:W, S13:C.

## FULL16_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "OTHER", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–6|dair|THEN THEN|
|S03|7–7|olaiin|THEN THEN|
|S04|8–11|chefchdy sor orsheckhy ockhody|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S05|12–12|shos|THEN THEN|
|S06|13–13|alol|THEN THEN|
|S07|14–14|dy|THEN THEN|
|S08|15–16|kar oky|FERRY FERRY C|
|S09|17–17|daiiin|THEN THEN|
|S10|18–19|okar ar|FERRY FERRY C|
|S11|20–20|okam|THEN THEN|
|S12|21–21|tshol|THEN THEN|
|S13|22–23|kar sheedy|FERRY FERRY FIRST_CARGO|
|S14|24–25|okeody qokedy|EXCLUDE RETURN_EXCLUDING C|
|S15|26–26|chody|THEN THEN|
|S16|27–28|kchdy pchdy|FERRY FERRY G|
|S17|29–30|chkaiin odam|EXCLUDE RETURN_EXCLUDING W|
|S18|31–31|tchdy|THEN THEN|
|S19|32–33|qokar chedy|FERRY FERRY G|
|S20|34–34|qokchdy|THEN THEN|
|S21|35–35|qokaiin|THEN THEN|
|S22|36–37|or ar|EXCLUDE RETURN_EXCLUDING C|
|S23|38–38|alol|THEN THEN|
|S24|39–40|keodaiin olr|FERRY FERRY FIRST_CARGO|
|S25|41–42|solkchy chckhy|STAY LEAVE THERE|
|S26|43–43|qokchdy|THEN THEN|
|S27|44–44|qokchdy|THEN THEN|
|S28|45–46|okar ar|FERRY FERRY C|
|S29|47–47|y|THEN THEN|
|S30|48–48|qokchdy|THEN THEN|
|S31|49–50|kar ar|FERRY FERRY C|
|S32|51–53|okain ykain ssear|WITH_RETURN WITH_TRIP W RETURN|
|S33|54–54|olkchedy|THEN THEN|
|S34|55–55|okal|THEN THEN|
|S35|56–57|qotor cheeor|FERRY FERRY W|
|S36|58–58|olkady|THEN THEN|
|S37|59–59|daiin|THEN THEN|
|S38|60–61|qoky todalain|FERRY FERRY W|
|S39|62–62|qotal|THEN THEN|
|S40|63–64|kaiin otaiin|STAY LEAVE THERE|
|S41|65–66|otal she|FERRY FERRY W|
|S42|67–68|kar ariin|FERRY FERRY W|
|S43|69–74|okchedy dariin ykykaiin sheekar otchdy dar|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S44|75–76|kar shelain|FERRY FERRY W|
|S45|77–81|taipar orolkain ytchdy kchedy ykeey|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S46|82–83|kaiin qokain|STAY LEAVE THERE|
|S47|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 3.
- S19 FIXED_TRIP_FAILED; prefix S08:C, S10:C, S13:C, S14:empty, S16:G, S17:empty.
- S19 FIXED_TRIP_FAILED; prefix S08:C, S10:C, S13:C, S14:empty, S16:G, S17:C.
- S47 FINAL_LOCAL_ASSERTION_FALSE; prefix S08:C, S10:C, S13:C, S14:empty, S16:G, S17:G, S19:G, S22:G, S24:W, S28:C, S31:C, S32:W, S35:W, S38:W, S41:W, S42:W, S44:W.

## FULL17_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "FIRST", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–6|dair|THEN THEN|
|S03|7–8|olaiin chefchdy|FERRY FERRY G|
|S04|9–10|sor orsheckhy|FERRY FERRY G|
|S05|11–12|ockhody shos|FERRY FERRY C|
|S06|13–14|alol dy|ALONE RETURN ALONE|
|S07|15–16|kar oky|FERRY FERRY G|
|S08|17–17|daiiin|THEN THEN|
|S09|18–19|okar ar|FERRY FERRY C|
|S10|20–20|okam|THEN THEN|
|S11|21–21|tshol|THEN THEN|
|S12|22–23|kar sheedy|FERRY FERRY FIRST_CARGO|
|S13|24–25|okeody qokedy|EXCLUDE RETURN_EXCLUDING C|
|S14|26–31|chody kchdy pchdy chkaiin odam tchdy|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S15|32–33|qokar chedy|FERRY FERRY G|
|S16|34–34|qokchdy|THEN THEN|
|S17|35–35|qokaiin|THEN THEN|
|S18|36–38|or ar alol|WITH_RETURN WITH_TRIP C RETURN|
|S19|39–40|keodaiin olr|FERRY FERRY C|
|S20|41–42|solkchy chckhy|STAY LEAVE THERE|
|S21|43–43|qokchdy|THEN THEN|
|S22|44–44|qokchdy|THEN THEN|
|S23|45–46|okar ar|FERRY FERRY C|
|S24|47–47|y|THEN THEN|
|S25|48–48|qokchdy|THEN THEN|
|S26|49–50|kar ar|FERRY FERRY C|
|S27|51–54|okain ykain ssear olkchedy|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S28|55–55|okal|THEN THEN|
|S29|56–58|qotor cheeor olkady|WITH_RETURN WITH_TRIP G RETURN|
|S30|59–59|daiin|THEN THEN|
|S31|60–61|qoky todalain|FERRY FERRY OTHER_CARGO|
|S32|62–62|qotal|THEN THEN|
|S33|63–64|kaiin otaiin|STAY LEAVE THERE|
|S34|65–65|otal|THEN THEN|
|S35|66–66|she|THEN THEN|
|S36|67–68|kar ariin|FERRY FERRY G|
|S37|69–69|okchedy|THEN THEN|
|S38|70–71|dariin ykykaiin|FERRY FERRY OTHER_CARGO|
|S39|72–73|sheekar otchdy|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S40|74–74|dar|THEN THEN|
|S41|75–76|kar shelain|FERRY FERRY W|
|S42|77–81|taipar orolkain ytchdy kchedy ykeey|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE G|
|S43|82–83|kaiin qokain|STAY LEAVE THERE|
|S44|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 2.
- S15 FIXED_TRIP_FAILED; prefix S03:G, S04:G, S05:C, S06:empty, S07:G, S09:C, S12:C, S13:empty.
- S44 FINAL_LOCAL_ASSERTION_FALSE; prefix S03:G, S04:G, S05:C, S06:empty, S07:G, S09:C, S12:C, S13:G, S15:G, S18:C, S19:C, S23:C, S26:C, S29:G, S31:G, S36:G, S38:G, S39:G, S41:W.

## FULL18_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "RECENT", "other": "FIRST", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–6|dair|THEN THEN|
|S03|7–7|olaiin|THEN THEN|
|S04|8–8|chefchdy|THEN THEN|
|S05|9–9|sor|THEN THEN|
|S06|10–10|orsheckhy|THEN THEN|
|S07|11–11|ockhody|THEN THEN|
|S08|12–12|shos|THEN THEN|
|S09|13–13|alol|THEN THEN|
|S10|14–14|dy|THEN THEN|
|S11|15–15|kar|THEN THEN|
|S12|16–17|oky daiiin|FERRY FERRY G|
|S13|18–18|okar|THEN THEN|
|S14|19–19|ar|THEN THEN|
|S15|20–21|okam tshol|EXCLUDE RETURN_EXCLUDING OTHER_CARGO|
|S16|22–22|kar|THEN THEN|
|S17|23–25|sheedy okeody qokedy|CONVEY CONVEY_OUT NEXT C|
|S18|26–26|chody|THEN THEN|
|S19|27–28|kchdy pchdy|STAY LEAVE THERE|
|S20|29–29|chkaiin|THEN THEN|
|S21|30–30|odam|THEN THEN|
|S22|31–31|tchdy|THEN THEN|
|S23|32–33|qokar chedy|EXCLUDE RETURN_EXCLUDING G|
|S24|34–34|qokchdy|THEN THEN|
|S25|35–35|qokaiin|THEN THEN|
|S26|36–36|or|THEN THEN|
|S27|37–37|ar|THEN THEN|
|S28|38–38|alol|THEN THEN|
|S29|39–40|keodaiin olr|FERRY FERRY W|
|S30|41–42|solkchy chckhy|STAY LEAVE THERE|
|S31|43–43|qokchdy|THEN THEN|
|S32|44–44|qokchdy|THEN THEN|
|S33|45–45|okar|THEN THEN|
|S34|46–46|ar|THEN THEN|
|S35|47–47|y|THEN THEN|
|S36|48–48|qokchdy|THEN THEN|
|S37|49–49|kar|THEN THEN|
|S38|50–50|ar|THEN THEN|
|S39|51–52|okain ykain|FERRY FERRY FIRST_CARGO|
|S40|53–53|ssear|THEN THEN|
|S41|54–57|olkchedy okal qotor cheeor|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S42|58–59|olkady daiin|FERRY FERRY FIRST_CARGO|
|S43|60–61|qoky todalain|FERRY FERRY OTHER_CARGO|
|S44|62–62|qotal|THEN THEN|
|S45|63–64|kaiin otaiin|STAY LEAVE THERE|
|S46|65–65|otal|THEN THEN|
|S47|66–66|she|THEN THEN|
|S48|67–67|kar|THEN THEN|
|S49|68–69|ariin okchedy|FERRY FERRY OTHER_CARGO|
|S50|70–74|dariin ykykaiin sheekar otchdy dar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S51|75–75|kar|THEN THEN|
|S52|76–81|shelain taipar orolkain ytchdy kchedy ykeey|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S53|82–83|kaiin qokain|STAY LEAVE THERE|
|S54|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 1.
- S54 FINAL_LOCAL_ASSERTION_FALSE; prefix S12:G, S15:empty, S17:C, S23:C, S29:W, S39:W, S42:W, S43:G, S49:G.

## FULL19_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "GOAL"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–7|dair olaiin|FERRY FERRY G|
|S03|8–8|chefchdy|THEN THEN|
|S04|9–10|sor orsheckhy|ALONE RETURN ALONE|
|S05|11–11|ockhody|THEN THEN|
|S06|12–13|shos alol|FERRY FERRY W|
|S07|14–14|dy|THEN THEN|
|S08|15–15|kar|THEN THEN|
|S09|16–16|oky|THEN THEN|
|S10|17–17|daiiin|THEN THEN|
|S11|18–18|okar|THEN THEN|
|S12|19–20|ar okam|FERRY FERRY FIRST_CARGO|
|S13|21–21|tshol|THEN THEN|
|S14|22–22|kar|THEN THEN|
|S15|23–23|sheedy|THEN THEN|
|S16|24–25|okeody qokedy|FERRY FERRY C|
|S17|26–28|chody kchdy pchdy|WITH_RETURN WITH_TRIP W RETURN|
|S18|29–30|chkaiin odam|FERRY FERRY W|
|S19|31–31|tchdy|THEN THEN|
|S20|32–33|qokar chedy|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S21|34–34|qokchdy|THEN THEN|
|S22|35–35|qokaiin|THEN THEN|
|S23|36–36|or|THEN THEN|
|S24|37–38|ar alol|FERRY FERRY W|
|S25|39–39|keodaiin|THEN THEN|
|S26|40–40|olr|THEN THEN|
|S27|41–42|solkchy chckhy|STAY LEAVE THERE|
|S28|43–43|qokchdy|THEN THEN|
|S29|44–44|qokchdy|THEN THEN|
|S30|45–45|okar|THEN THEN|
|S31|46–47|ar y|FERRY FERRY C|
|S32|48–48|qokchdy|THEN THEN|
|S33|49–49|kar|THEN THEN|
|S34|50–51|ar okain|FERRY FERRY FIRST_CARGO|
|S35|52–52|ykain|THEN THEN|
|S36|53–57|ssear olkchedy okal qotor cheeor|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S37|58–59|olkady daiin|EXCLUDE RETURN_EXCLUDING FIRST_CARGO|
|S38|60–61|qoky todalain|FERRY FERRY C|
|S39|62–62|qotal|THEN THEN|
|S40|63–64|kaiin otaiin|STAY LEAVE THERE|
|S41|65–65|otal|THEN THEN|
|S42|66–66|she|THEN THEN|
|S43|67–67|kar|THEN THEN|
|S44|68–71|ariin okchedy dariin ykykaiin|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S45|72–73|sheekar otchdy|STAY LEAVE THERE|
|S46|74–74|dar|THEN THEN|
|S47|75–75|kar|THEN THEN|
|S48|76–81|shelain taipar orolkain ytchdy kchedy ykeey|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S49|82–83|kaiin qokain|STAY LEAVE THERE|
|S50|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 3.
- S24 FIXED_TRIP_FAILED; prefix S02:G, S04:empty, S06:W, S12:G, S16:C, S17:W, S18:W, S20:empty.
- S24 FIXED_TRIP_FAILED; prefix S02:G, S04:empty, S06:W, S12:G, S16:C, S17:W, S18:W, S20:C.
- S50 FINAL_LOCAL_ASSERTION_FALSE; prefix S02:G, S04:empty, S06:W, S12:G, S16:C, S17:W, S18:W, S20:W, S24:W, S31:C, S34:G, S37:W, S38:C.

## FULL20_primary — INSUFFICIENT

Setting: `{"copy": "FIRST", "exclude": "EXCLUDING", "first": "FIRST", "other": "OTHER", "there": "CURRENT"}`

|Clause|Groups (1-based)|Written complete span|Assumed construction|
|---|---|---|---|
|S01|1–5|psheor olkais olfchedy qopeeedar opchey|INITIAL INIT CARGOS COLOC M HOME|
|S02|6–6|dair|THEN THEN|
|S03|7–7|olaiin|THEN THEN|
|S04|8–8|chefchdy|THEN THEN|
|S05|9–9|sor|THEN THEN|
|S06|10–10|orsheckhy|THEN THEN|
|S07|11–11|ockhody|THEN THEN|
|S08|12–13|shos alol|FERRY FERRY W|
|S09|14–14|dy|THEN THEN|
|S10|15–15|kar|THEN THEN|
|S11|16–17|oky daiiin|ALONE RETURN ALONE|
|S12|18–18|okar|THEN THEN|
|S13|19–20|ar okam|FERRY FERRY C|
|S14|21–21|tshol|THEN THEN|
|S15|22–22|kar|THEN THEN|
|S16|23–23|sheedy|THEN THEN|
|S17|24–25|okeody qokedy|EXCLUDE RETURN_EXCLUDING C|
|S18|26–29|chody kchdy pchdy chkaiin|GOAL GOAL FAR_BANK WITHOUT_HARM HARM|
|S19|30–31|odam tchdy|FERRY FERRY G|
|S20|32–33|qokar chedy|FERRY FERRY FIRST_CARGO|
|S21|34–34|qokchdy|THEN THEN|
|S22|35–36|qokaiin or|STAY LEAVE THERE|
|S23|37–38|ar alol|FERRY FERRY W|
|S24|39–40|keodaiin olr|FERRY FERRY FIRST_CARGO|
|S25|41–42|solkchy chckhy|STAY LEAVE THERE|
|S26|43–43|qokchdy|THEN THEN|
|S27|44–44|qokchdy|THEN THEN|
|S28|45–45|okar|THEN THEN|
|S29|46–47|ar y|FERRY FERRY FIRST_CARGO|
|S30|48–48|qokchdy|THEN THEN|
|S31|49–49|kar|THEN THEN|
|S32|50–51|ar okain|FERRY FERRY FIRST_CARGO|
|S33|52–53|ykain ssear|STAY LEAVE THERE|
|S34|54–55|olkchedy okal|FERRY FERRY W|
|S35|56–56|qotor|THEN THEN|
|S36|57–58|cheeor olkady|EXCLUDE RETURN_EXCLUDING G|
|S37|59–59|daiin|THEN THEN|
|S38|60–61|qoky todalain|FERRY FERRY W|
|S39|62–62|qotal|THEN THEN|
|S40|63–64|kaiin otaiin|STAY LEAVE THERE|
|S41|65–65|otal|THEN THEN|
|S42|66–66|she|THEN THEN|
|S43|67–67|kar|THEN THEN|
|S44|68–72|ariin okchedy dariin ykykaiin sheekar|CAPACITY AT_MOST_ONE BESIDES M EXAMPLE C|
|S45|73–73|otchdy|THEN THEN|
|S46|74–74|dar|THEN THEN|
|S47|75–75|kar|THEN THEN|
|S48|76–81|shelain taipar orolkain ytchdy kchedy ykeey|SAFETY UNSAFE PAIRS FORBIDDEN WHEN WITHOUT_AGENT M|
|S49|82–83|kaiin qokain|STAY LEAVE THERE|
|S50|84–89|aldalosam solkaiin opalke chckhy dario chky|CONCLUSION THUS ALL UNHARMED THERE ATTENDED_BY M|

Successful eligible complete paths: 1; failed eligible prefixes: 3.
- S38 FIXED_TRIP_FAILED; prefix S08:W, S11:empty, S13:C, S17:empty, S19:G, S20:W, S23:W, S24:W, S29:W, S32:W, S34:W, S36:empty.
- S38 FIXED_TRIP_FAILED; prefix S08:W, S11:empty, S13:C, S17:empty, S19:G, S20:W, S23:W, S24:W, S29:W, S32:W, S34:W, S36:C.
- S20 FIXED_TRIP_FAILED; prefix S08:W, S11:empty, S13:C, S17:W, S19:G.
