# Gedächtniskarte für offene Übergänge

An exact close clears item, preparation, measure, source and target. Without a close and under the
same owner, retain only the registers named by the transition card or immediate clause ending.

- H1-S001 -> H1-S002: **mit der aktiven Bereitung weiter:** (ACTIVE_PREPARATION)
- H2-S001 -> H2-S002: **mit demselben Ansatz und Sollmaß weiter:** (ACTIVE_PREPARATION|PRESCRIBED_MEASURE)
- H2-S002 -> H2-S003: **aus demselben Ansatz weiter:** (ACTIVE_PREPARATION)
- H3-S002 -> H3-S003: **mit diesem Materialanteil weiter:** (CURRENT_MATERIAL_SHARE)
- H3-S003 -> H3-S004: **mit diesem Posten auf Sollmaß weiter:** (CURRENT_ITEM|PRESCRIBED_MEASURE)
- H5-S001 -> H5-S002: **vom zielgesetzten Ansatz weiter:** (TARGETED_PREPARATION)
- H5-S003 -> H5-S004: **mit dem eingesetzten Posten weiter:** (CURRENT_ITEM)
- H5-S004 -> H5-S005: **mit dem Auszug am Ziel weiter:** (ACTIVE_EXTRACT|TARGET)
- H5-S005 -> H5-S006: **zum nächsten Posten weiter:** (ACTIVE_SEQUENCE|CURRENT_ITEM)
- B1-S006 -> B1-S007: **am offenen Ziel in die Überführung weiter:** (TARGET|UNFINISHED_TRANSFER)
- B1-S011 -> B1-S012: **mit dem eingesetzten Posten am selben Besitzer weiter:** (CURRENT_ITEM|LOCAL_STATION)
- B1-S014 -> B1-S015: **von der eben gesetzten Quelle weiter:** (SOURCE)
- B3-S011 -> B3-S012: **mit dem aus der Quelle überführten Posten weiter:** (CURRENT_ITEM|SOURCE)
