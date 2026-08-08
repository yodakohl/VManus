# Initial bare-carrier state system

Decision: **INITIAL_BARE_CARRIER_STATE_SYSTEM_CONFIRMED_QUALIFIED**.

## Carrier-wide correction

The S/Q missing corner is not S-specific. q is overwhelmingly attached to the first parsed unit: ZL3b 5288/5321 first (99.379816%; noninitial=33); IT2a 5284/5317 first (99.379349%; noninitial=33); RF1b 5286/5323 first (99.304903%; noninitial=37). Rare exceptions are exported, so this is not an absolute spelling ban.

| carrier | odd ZL strata | z | family p | discovered | all-panel confirmed |
|---|---:|---:|---:|---:|---:|
| d | 91 | 11.416 | 5.74213e-29 | True | True |
| k | 21 | 2.270 | 0.203806 | False | False |
| l | 29 | 1.464 | 0.937064 | False | False |
| o | 18 | 2.265 | 0.200217 | False | False |
| ok | 22 | 0.684 | 1 | False | False |
| ol | 32 | 1.566 | 0.766189 | False | False |
| ot | 25 | 3.195 | 0.013691 | True | False |
| s | 42 | 10.157 | 2.82958e-22 | True | True |
| t | 51 | 9.841 | 1.07159e-21 | True | True |

Frozen all-panel line-entry carriers: **d, s, t**. The bare-d carrier is not the BOUND_D selector.

## Paragraph-state split

| reading | split | role-conditioned strata | T open/cont | D+S open/cont | z | exact p |
|---|---|---:|---:|---:|---:|---:|
| ZL3b | odd | 13 | 15/4 | 1/24 | 4.350 | 5.78704e-06 |
| ZL3b | even | 18 | 21/3 | 0/22 | 4.606 | 6.78168e-07 |
| IT2a | odd | 15 | 18/5 | 1/24 | 4.393 | 2.89352e-06 |
| IT2a | even | 19 | 21/4 | 1/22 | 4.255 | 8.13802e-06 |

Largest four-panel Bonferroni p=3.25521e-05; paragraph plant p=5.78704e-06, pass=True.

Corrected structural reading: `[PARAGRAPH-OPENING-ASSOCIATED BARE-T CARRIER + BASE]` contrasts with `[CONTINUATION-LINE-ENTRY-ASSOCIATED BARE-D/BARE-S CARRIER + BASE]`. q is a word-edge state used in confirmed selector environments. These are positional constructions, not START/CONTINUE words and not evidence for a negative marker.

This supersedes the interpretation of the missing s+q corner as a special S/Q semantic or operator interaction. It does not supersede S's independently measured continuation-line preference.

Runtime: 34.56 s; cached text only, image decodes: 0.
