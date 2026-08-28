#!/usr/bin/env python3
"""Human-smoothed reader channel for the fixed twenty GDT582 passages."""

EDITORIAL_PARAGRAPHS = {
    "G407-S002": (
        "Arbeite an der Arbeitsstelle in Arbeitsform vom Ausgangsgefäß her. Lass ruhen und fahre im selben Gang fort. "
        "Entnimm Arbeitsgut und bring es dort in Arbeitsform ein. Lass ruhen, sondere aus und entnimm ein Flüssigkeitsmaß "
        "in Feinform. Lass das Arbeitsgut in Arbeitsform an der Arbeitsstelle aus der Quelle ruhen; halte äußeres und inneres "
        "Gut gemeinsam auf Stufe I. Lass die Arbeitsform abschließend ruhen und schließe den Gang."
    ),
    "G407-S003": (
        "Setze Arbeitsgut in Arbeitsform an und entnimm es. Beginne danach einen neuen Gang und entnimm weiter. Entnimm "
        "nochmals in Arbeitsform und bring Arbeitsgut und Portion auf die eingestellte beziehungsweise temperierte Bedingung. "
        "Entnimm die Ansatzeinheit, gib in Arbeitsform zu und sondere ein Flüssigkeitsmaß aus. Lass die Form ruhen, sondere "
        "erneut aus, entnimm in Feinform und fahre fort. Lass die Arbeitsform ruhen und schließe."
    ),
    "G515-S042": (
        "Temperiere in Arbeitsform, entnimm und bring Arbeitsgut auf Stufe II ein. Fahre an der Arbeitsstelle fort; gib zu, "
        "entnimm und setze das Gut dort auf Stufe I an. Lass den Ansatz ruhen und bring als Neuansatz ein Flüssigkeitsmaß ein. "
        "Gib das Arbeitsgut am Arbeitsweg zu und sondere es im zweiten Durchgang aus. Setze es an der Arbeitsstelle an, lass "
        "es dort im zweiten Durchgang ruhen und prüfe die bezeichnete Stufe. Gib das Gut zum Ziel, lass ruhen, gib erneut zu "
        "und setze an. Lass auf Stufe I ruhen und gib entlang des Arbeitswegs zu. Entnimm dann aus dem Ausgangsgefäß in einen "
        "neuen Gang, setze auf Stufe II an, lass an der Arbeitsstelle ruhen und gib in Arbeitsform weiter zu. Entnimm, gib auf "
        "Stufe I zu, lass ruhen, entnimm und temperiere. Übernimm diese Einstellung für beide Zielstellen, lass auf Stufe I "
        "ruhen und schließe."
    ),
    "G515-S043": (
        "Entnimm auf Stufe I, stelle die Bedingung an der Hauptstelle ein und prüfe. Lass die Arbeitsform auf Stufe I an der "
        "Arbeitsstelle ruhen. Lass weiter ruhen, setze das Arbeitsgut auf der bezeichneten Stufe aus dem Ausgangsgefäß an und "
        "prüfe beide Arbeitsstellen. Lass den Ansatz ruhen; lass ihn danach auf Stufe I in Arbeitsform im Zielgefäß und "
        "anschließend weiter an der Arbeitsstelle ruhen. Setze das Gut an und arbeite es auf, bring es in Arbeitsform ein und "
        "eröffne damit den nächsten Gang. Bearbeite es auf der bezeichneten Stufe, prüfe, lass es auf Stufe II an der Endstelle "
        "ruhen, gib aus dem Ausgangsgefäß zu und schließe."
    ),
    "G407-S010": (
        "Erwärme den Ansatz und lass ihn im selben Arbeitsgang weiterziehen. Lass die Zubereitung am Ziel- oder "
        "Auffanggefäß stehen. Zieh die feine Pflanzencharge ab und lass Pflanzencharge und Auszug beziehungsweise Arbeitsmaß "
        "zusammen ziehen. Nimm die Charge heraus und bring sie wieder ein; lass sie auf Stufe I ziehen. Temperiere abschließend "
        "und zieh die Zubereitung ab, dann schließe den Arbeitsgang."
    ),
    "G407-S013": (
        "Temperiere eine Pflanzen- oder Arbeitseinheit und zieh sie an der Pflanzenarbeitsstelle ab; nimm dabei Auszug "
        "beziehungsweise Arbeitsmaß. Beginne einen neuen Gang und zieh weiter ab. Setze eine Pflanzencharge an, setze die "
        "Einheit ebenfalls an und zieh sie in Zubereitungsform auf der Verarbeitungsstufe ab. Entnimm die Charge und gib sie "
        "an der Arbeitsstelle zu. Setze die Charge dort weiter in Zubereitungsform an und schließe den Gang."
    ),
    "G407-S020": (
        "Fahre fort: Entnimm an der Pflanzenarbeitsstelle und gib die Charge entlang des Verarbeitungswegs zu. Setze die "
        "Pflanzencharge zweimal an, den zweiten Ansatz in Zubereitungsform an der Arbeitsstelle aus dem Ausgangsmaterial. "
        "Entnimm abschließend und gib in Zubereitungsform zu, dann schließe."
    ),
    "G407-S028": (
        "Fahre im selben Gang mit dem Auszug oder Arbeitsmaß fort, das zum folgenden Ansatz gehört. Setze den Pflanzenansatz "
        "an und zieh eine Pflanzen- oder Arbeitseinheit ab. Entnimm, gib weiter zu, führe den Gang in Zubereitungsform fort "
        "und schließe."
    ),
    "G407-S041": (
        "Trage an der unteren Ringstelle in doppelter Eintragsform ein und fahre fort. Wähle einen Sektoranteil und die "
        "Ringposition an der unteren Zielposition. Wähle dieselbe Position in Eintragsform auf Ringstufe II; die Auswahl gilt "
        "an der unteren Ringstelle in Eintragsform auf der Feinstufe. Fahre fort und schließe."
    ),
    "G407-S045": (
        "Wähle den Positionswert in Eintragsform und fahre im selben Gang fort; führe denselben Gang anschließend noch einmal weiter."
    ),
    "G407-S052": (
        "Halte die Ringposition fest, trage sie ein und lies sie ab. Stelle die abgelesene Position auf Ringstufe II ein. Lies "
        "sie erneut und beginne danach auf Stufe II einen neuen Gang. Lies weiter, setze ein und führe fort. Lies auf Stufe I "
        "ab und markiere in Eintragsform. Setze in Eintragsform ein, lies auf Stufe II ab und fahre fort. Beginne mit der "
        "Sektoreinheit einen neuen Gang. Lies in Eintragsform ab, lies nochmals und stelle die Position auf Stufe III ein. "
        "Trage ein und lies zur Zielposition ab. Stelle in Eintragsform ein, lies ab und wähle in Eintragsform aus. Beginne "
        "erneut, lies über den Ringkontakt, trage auf Stufe III ein und schließe."
    ),
    "G407-S061": (
        "Für die Zielposition: Beginne auf Ringstufe II mit der Ringposition einen neuen Gang und berechne sie zur "
        "Zielposition. Beginne danach nochmals auf Ringstufe II und schließe."
    ),
    "G407-S082": (
        "Führe den Stationsansatz zu, behandle ihn und führe ihn aus der Ausgangsstation beziehungsweise dem Ausgangsbecken "
        "erneut zu. Beschicke ihn auf Stufe II und anschließend vom Ausgangsbecken her; führe den Ansatz zu und behandle ihn. "
        "Beginne danach vom Ausgangsbecken her einen neuen Gang, halte den Ansatz im Bad auf Stufe I und schließe."
    ),
    "G407-S083": (
        "Halte die Anwendungsportion als Stationsansatz auf Stufe I über den Stationskontakt oder die Leitung im Bad. Leite "
        "sie um und halte sie auf Stufe I weiter. Führe den Gang fort und schließe."
    ),
    "G407-S086": (
        "Halte den Stationsansatz auf Stufe I im Bad. Führe ihn aus dem Ausgangsbecken zu, lass ihn ab und führe ihn auf "
        "Stufe I wieder zu. Prüfe die Anwendungsportion. Fahre fort, halte sie auf Stufe II im Stationsgang und schließe."
    ),
    "G407-S193": (
        "Bring eine Becken- oder Körpereinheit ein beziehungsweise wende sie an. Beginne einen neuen Gang, lass ab und "
        "beschicke die Einheit. Lass den Stationsansatz zuerst in Anwendungsform und danach in Feinform ab; bring ihn in "
        "Anwendungsform ein und halte ihn an der Stationsstelle. Fahre mit der Anwendung fort. Zweimal: Lass zweimal ab und "
        "bring den Stationsansatz wieder ein. Bring ihn in Anwendungsform ein und halte ihn auf Stufe I. Beginne einen neuen "
        "Ansatz, bring ihn in Anwendungsform ein und halte ihn an der Arbeitsstelle. Wende ihn in Anwendungsform an und "
        "behandle den Stationsansatz. Teile eine Anwendungsportion ab und leite den Ansatz an der Hauptstation um. Halte ihn "
        "auf Stufe I im Bad und schließe."
    ),
    "G407-S649": (
        "Gib die Drogencharge in Arzneiform an der Hauptstelle zu. Entnimm und gib sie im selben Gang hinein. Zieh die äußere "
        "und die innere Gefäßeinheit ab. Gib die Charge über den Gefäßkontakt hinein und entnimm sie auf Stufe I in "
        "Arzneiform. Beginne einen neuen Gang, entnimm weiter und schließe."
    ),
    "G407-S651": (
        "Gib aus dem Ausgangsgefäß in Arzneiform auf Stufe II hinein. Lass die Drogencharge auf Stufe I ziehen und setze den "
        "Ansatz an. Gib die Charge auf Stufe II weiter zu. Entnimm, temperiere und fahre fort. Gib die Charge an der "
        "Arbeitsstelle hinein und führe den Gang weiter. Trenne ab, setze den Ansatz erneut an und schließe."
    ),
    "G407-S657": (
        "Gib die Drogencharge in Arzneiform hinein und gib dieselbe Charge auf Stufe I zu. Fahre an der Drogenarbeitsstelle "
        "mit dem Dosis- oder Mengenmaß fort. Beginne danach auf Stufe I in Arzneiform einen neuen Gang und schließe."
    ),
    "G407-S659": (
        "Gib die Drogencharge und eine Gefäß- oder Arbeitseinheit auf Stufe II zu. Entnimm Material der Oberklasse und gib "
        "die Charge zu. Beginne einen neuen Gang und führe ihn fort. Lass auf Stufe II ziehen und fahre weiter. Entnimm die "
        "Charge auf Stufe I in Arzneiform. Beginne anschließend in Arzneiform den nächsten Gang und schließe."
    ),
}
