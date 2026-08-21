# V22 selection — f69 is a repeated-rule schedule, not alternating polarity

Date: 2026-08-22

Status: **contradiction-driven repair of the speculative translation**.

## Hard correction

V21 inherited the convenient rule:

```text
odd radial position  = favour the application
even radial position = withhold the application
```

That rule is incompatible with exact visible recurrence. Complete entry
`okeod` occurs at stations 11, 15 and 24. The first two occupy LONG/odd slots;
the third occupies a SHORT/even slot. Alternating polarity would make one exact
entry mean both “favour” and “withhold.”

The polarity is therefore **not carried by LONG/SHORT position**. LONG/SHORT is
now treated as graphic capacity or alternating entry template.

## Selected 28-rule reading

V22 restores the already existing R2 medical-rule lexicon, which was designed
around exact repeated entry identity. Every radial position keeps a concrete
default, for example:

| station | visible entry | selected rule |
|---:|---|---|
| 1 | `okeey sar` | favourable for a warm bath, especially after sunset |
| 2 | `okeo dy` | use a cool washing, then stop |
| 3 | `ochoyk` | avoid bloodletting |
| 6 | `oeesy` | rest and give no purge |
| 9 | `otody` | avoid a hot bath |
| 11, 15, 24 | `okeod` | favourable for bathing |
| 20 | `sarydy` | avoid a second application |
| 25 | `okodchy` | strain the herbal liquor |
| 28 | `oar alys` | observe the mansion; withhold treatment if weak |

All 28 entries are listed in `V22_F69_28_RULES.tsv`. The three `okeod`
occurrences have one meaning even though they cross layout parity.

## Revised Astro workflow

```text
f67r2  select the governing body-sector safety condition
f68r1  identify a lunar station spatially
f69v   retrieve that station's concrete medical rule
```

The correction improves f69 internally but does not repair the missing f68→f69
index. There is still no visible common start, direction or exact label mapping.
A conventional learned mansion index remains necessary for the combined-tool
reading.

## Scope

Thirty-three visible tokens making up the 28 radial entries are revised in the
complete 569-entry dictionary and 776-event ledger. The 107 circular prose
tokens on f69 and all other pages remain unchanged. The medical actions are
still aggressive working guesses; exact recurrence merely rejects the former
alternating-polarity shortcut. No Voynich label has been decoded into a known
word, and f84/f84r remained sealed.
