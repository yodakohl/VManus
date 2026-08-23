# Rotstiftbuch des Meisters

Vier Fehlerarten werden je achtmal geübt. Die rote Atomfolge ist absichtlich
falsch; es wird keine neue Manuskriptoberfläche gezeichnet.

## GRADE_CHANGE

- H1-S001: `DCHE+Y | CTH+OR | AR | PARTITION+TY | OS | AIR | OT+TY+OL | OK+Y | AIIN | E+TY` → falsch `DCHE+Y | CTH+OR | AR | PARTITION+TY | OS | AIR | OT+TY+OL | OK+Y | AIIN | EE+TY`; kurz wird länger.
- H4-S003: `Y+AIIN | CHEO+AR | CHK+EE+Y | OL+CLOSE` → falsch `Y+AIIN | CHEO+AR | CHK+E+Y | OL+CLOSE`; länger wird kurz.
- H5-S003: `SH | HO | KCH+E+Y | OK+OK+Y` → falsch `SH | HO | KCH+EE+Y | OK+OK+Y`; kurz wird länger.
- B1-S001: `OK+E+CLOSE` → falsch `OK+EE+CLOSE`; kurz wird länger.
- B1-S004: `CHD+Y | OL | SHED+E+CLOSE` → falsch `CHD+Y | OL | SHED+EE+CLOSE`; kurz wird länger.
- B1-S008: `Y | OL | CHK+E+Y | OL | SHED+E+CLOSE` → falsch `Y | OL | CHK+EE+Y | OL | SHED+E+CLOSE`; kurz wird länger.
- B1-S009: `OK+E+CLOSE` → falsch `OK+EE+CLOSE`; kurz wird länger.
- B1-S010: `OK+E+CLOSE` → falsch `OK+EE+CLOSE`; kurz wird länger.

## Y_CLOSE_CONFUSION

- H1-S001: `DCHE+Y | CTH+OR | AR | PARTITION+TY | OS | AIR | OT+TY+OL | OK+Y | AIIN | E+TY` → falsch `DCHE+CLOSE | CTH+OR | AR | PARTITION+TY | OS | AIR | OT+TY+OL | OK+Y | AIIN | E+TY`; laufender Posten wird zum Schrittabschluss.
- H1-S002: `OK+Y | OT+OL | OL | CTH+Y` → falsch `OK+CLOSE | OT+OL | OL | CTH+Y`; laufender Posten wird zum Schrittabschluss.
- H2-S001: `Y+CHEO+OR | CTH+Y | OR | CTH+AIIN | CTH+OL+Y | Y | Y | AIIN | Y` → falsch `Y+CHEO+OR | CTH+CLOSE | OR | CTH+AIIN | CTH+OL+Y | Y | Y | AIIN | Y`; laufender Posten wird zum Schrittabschluss.
- H2-S003: `Y+KCH+OR | OR | OR | Y | IIN | Y | HO+AIIN` → falsch `Y+KCH+OR | OR | OR | CLOSE | IIN | Y | HO+AIIN`; laufender Posten wird zum Schrittabschluss.
- H3-S001: `HO+L | HO+AL | CFH+Y | SH+AIIN | CPH+Y | CHEEY | HO+CLOSE` → falsch `HO+L | HO+AL | CFH+CLOSE | SH+AIIN | CPH+Y | CHEEY | HO+CLOSE`; laufender Posten wird zum Schrittabschluss.
- H3-S003: `PREV+OL | Y | KCH+Y | Y | AIIN` → falsch `PREV+OL | CLOSE | KCH+Y | Y | AIIN`; laufender Posten wird zum Schrittabschluss.
- H3-S004: `OT+Y | OK+OL | CTH+Y | Y` → falsch `OT+CLOSE | OK+OL | CTH+Y | Y`; laufender Posten wird zum Schrittabschluss.
- H4-S002: `AIIN | CHD+Y | AL+AM` → falsch `AIIN | CHD+CLOSE | AL+AM`; laufender Posten wird zum Schrittabschluss.

## AL_AR_SWAP

- H1-S001: `DCHE+Y | CTH+OR | AR | PARTITION+TY | OS | AIR | OT+TY+OL | OK+Y | AIIN | E+TY` → falsch `DCHE+Y | CTH+OR | AL | PARTITION+TY | OS | AIR | OT+TY+OL | OK+Y | AIIN | E+TY`; Quelle wird Ziel.
- H2-S002: `OT+OR | OR | OT+OL | OL | OL+OR | OL | AIIN | AR` → falsch `OT+OR | OR | OT+OL | OL | OL+OR | OL | AIIN | AL`; Quelle wird Ziel.
- H3-S001: `HO+L | HO+AL | CFH+Y | SH+AIIN | CPH+Y | CHEEY | HO+CLOSE` → falsch `HO+L | HO+AR | CFH+Y | SH+AIIN | CPH+Y | CHEEY | HO+CLOSE`; Ziel wird Quelle.
- H4-S002: `AIIN | CHD+Y | AL+AM` → falsch `AIIN | CHD+Y | AR+AM`; Ziel wird Quelle.
- H4-S003: `Y+AIIN | CHEO+AR | CHK+EE+Y | OL+CLOSE` → falsch `Y+AIIN | CHEO+AL | CHK+EE+Y | OL+CLOSE`; Quelle wird Ziel.
- H4-S004: `AIIN | OK+AL | OL+CTH+Y | OR | Y | OR+AIN` → falsch `AIIN | OK+AR | OL+CTH+Y | OR | Y | OR+AIN`; Ziel wird Quelle.
- H5-S001: `HO+OR | HO | HO+AL+Y | AIIN | HO | KCH+OL | OT+OR | OK+Y | AL` → falsch `HO+OR | HO | HO+AR+Y | AIIN | HO | KCH+OL | OT+OR | OK+Y | AL`; Ziel wird Quelle.
- H5-S004: `OK+Y | OK+CHEO | KCH+AL` → falsch `OK+Y | OK+CHEO | KCH+AR`; Ziel wird Quelle.

## DROP_DUPLICATE_REORDER

- H1-S001: `DCHE+Y | CTH+OR | AR | PARTITION+TY | OS | AIR | OT+TY+OL | OK+Y | AIIN | E+TY` → falsch `CTH+OR | DCHE+Y | AR | PARTITION+TY | OS | AIR | OT+TY+OL | OK+Y | AIIN | E+TY`; die ersten beiden Arbeitsschritte tauschen ihre Reihenfolge.
- H1-S002: `OK+Y | OT+OL | OL | CTH+Y` → falsch `OT+OL | OK+Y | OL | CTH+Y`; die ersten beiden Arbeitsschritte tauschen ihre Reihenfolge.
- H2-S001: `Y+CHEO+OR | CTH+Y | OR | CTH+AIIN | CTH+OL+Y | Y | Y | AIIN | Y` → falsch `CTH+Y | Y+CHEO+OR | OR | CTH+AIIN | CTH+OL+Y | Y | Y | AIIN | Y`; die ersten beiden Arbeitsschritte tauschen ihre Reihenfolge.
- H2-S002: `OT+OR | OR | OT+OL | OL | OL+OR | OL | AIIN | AR` → falsch `OR | OT+OR | OT+OL | OL | OL+OR | OL | AIIN | AR`; die ersten beiden Arbeitsschritte tauschen ihre Reihenfolge.
- H2-S003: `Y+KCH+OR | OR | OR | Y | IIN | Y | HO+AIIN` → falsch `OR | Y+KCH+OR | OR | Y | IIN | Y | HO+AIIN`; die ersten beiden Arbeitsschritte tauschen ihre Reihenfolge.
- H3-S001: `HO+L | HO+AL | CFH+Y | SH+AIIN | CPH+Y | CHEEY | HO+CLOSE` → falsch `HO+AL | HO+L | CFH+Y | SH+AIIN | CPH+Y | CHEEY | HO+CLOSE`; die ersten beiden Arbeitsschritte tauschen ihre Reihenfolge.
- H3-S003: `PREV+OL | Y | KCH+Y | Y | AIIN` → falsch `Y | PREV+OL | KCH+Y | Y | AIIN`; die ersten beiden Arbeitsschritte tauschen ihre Reihenfolge.
- H3-S004: `OT+Y | OK+OL | CTH+Y | Y` → falsch `OK+OL | OT+Y | CTH+Y | Y`; die ersten beiden Arbeitsschritte tauschen ihre Reihenfolge.
