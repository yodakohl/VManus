# IDEA479: independent reference and complete-statement review

2026-09-22, completed within the 16:21 UTC review limit. This is a bounded
primary-source audit of an already exposed RAW, not a new corpus test. The RAW,
GDT599 and all predecessor bytes remain unchanged.

**Decision:** the three reported complete statements and their BODY source
pointers are accurate. S441 contradicts the explicitly strengthened conjunction
of physical body identity, one unchanged bath, consecutive actual actions and
strict outside-to-inside entry. It does not contradict GDT599's original
object-completion contract. S442 is the predeclared countercase to collapsing
every BODY SH→K chain into entry into the same bath. No new meaning is confirmed.

## What the old reference model actually commits

GDT599 METHOD, “Auswahlfolge” and “Referenzform”, deliberately render a left
source anaphorically as *derselbe/dieselbe/dasselbe*. Model `REFERENCE_CARD_SPECS`
and `DETERMINERS` (lines 107–142) make this an explicit rendering rule, not a
coincidence of two BODY labels. T05 chooses the nearest compatible history
entry, copies its `object_class` and `lemma`, sets `ANAPHORIC`, and records its
specific `source_governor_key` (lines 710–724). In the retained German reading,
“denselben Körper” therefore intends discourse coreference to that earlier
object mention. Calling the old output merely an unrelated repeated type would
understate this declared reading.

The executable record is narrower than a physical state model. `state_entry`
(lines 395–408) stores class, lemma, source governor/action/event, host index,
channel and role. It does not carry an enduring individual identifier or the
earlier pointer recursively inside that state; each new entry receives the
current host's governor. The separate output pointers permit reconstructing a
mention chain. There is no body-to-bath relation, unique bath identity, time,
occupancy bit or transition precondition. History resets at OT/DY (lines
487–510); action-Q can commit a new STATION result, but this is a participant
completion mechanism, not proof of a body's physical movement. METHOD's unique
`host_ordinal_global` is provenance identity, not an individual patient ID.

Thus three levels must remain distinct: (1) exact old mention provenance and
anaphoric wording; (2) their intended same-object discourse interpretation;
(3) IDEA479's added interpretation as the same physical individual acting in
one real bath through consecutive times. The last level is not independently
entailed or validated by the old program. Neither equal BODY types nor equal
owner descriptions unify distinct own/default objects across statements.

The BODY-conditioned renderer inserts “Nimm … heraus” and “Bringe … ein”
(`insert_object`, lines 314–338). It does not stipulate that entry is a partial
OUT→IN operation. Strict entry, as opposed to setting a destination or another
permitted interpretation of “einbringen”, is another added semantic premise.

## Complete admitted units and exact consequences

All 14 hosts, including all four controls, and all 10 actions were inspected.
The authorizations cover only S402 on f81r and S441/S442 on f81v. The complete
reader corroborates them at lines 613–616 and 757–764.

**S402, hosts 3290–3293:** “Halte den Körper im Bad auf Grad I. Nimm denselben
Körper heraus. Bringe denselben Körper auf Grad I ein. Schließe den Arbeitsgang.”

The SH object is `DEFINITE / DEFAULT:BODY`. CH
`ACTION:G407-E2783@3:CH` points to `ACTION:G407-E2783@1:SH`; K
`ACTION:G407-E2783@4:K` points to that CH. Both are `Q01_LEFT_ANAPHORIC` and
`T05_LEFT_COMPATIBLE_STATE`. Conditional on physical x and unchanged B, HOLD
requires and retains IN, REMOVE gives OUT, and ENTRY gives IN. Both strict and
idempotent entry satisfy this local chain. This is a compatibility example,
not evidence selecting either interpretation.

**S441, hosts 3481–3484:** “Wende die Anwendungsportion von der Ausgangsstation
oder aus dem Ausgangsbecken an. Halte den Körper im Bad auf Grad I. Bringe
denselben Körper auf Grad II ein. Schließe den Arbeitsgang.”

The initial P remains `PORTION / DEFAULT:P:PORTION`, with its source modifier;
it is not silently removed or identified with BODY. SH
`ACTION:G407-E2925@1:SH` has written Y, BODY and source
`HOST:G407-E2925:RUNNING:G407-E2925@3`. The adjacent K
`ACTION:G407-E2926@1:K` is BODY/anaphoric and points exactly to that SH. There
is no intervening host or written K destination change. Grades I and II remain
different; a grade change by itself does not supply a new bath.

Under the added same-x/same-B/actual-chronology premises, SH leaves IN while
strict K requires OUT: contradiction at this adjacent pair. The preceding P
needs no invented no-op interpretation because SH itself establishes the state
immediately before K. Idempotent destination assignment avoids this particular
conflict; different destination and nonconsecutive/habitual/normative readings
remain rivals. This does not establish complete physical executability of all
S441 clauses or select one rival as the manuscript's meaning.

**S442, hosts 3485–3490:** “Halte den Körper im Bad auf Grad I. Bringe denselben
Körper an der Stations-Arbeitsstelle, zur Zielstation oder ins Zielbecken und
von der Ausgangsstation oder aus dem Ausgangsbecken ein. Fahre im selben
Arbeitsgang fort. Setze denselben Körper ein. Behandle denselben Körper.
Schließe den Arbeitsgang.”

SH is `DEFAULT:BODY`. K `ACTION:G407-E2927@3:K` points to
`ACTION:G407-E2927@1:SH`, exactly as a same-object discourse link, but its full
written source/destination/working-place packet survives in both upstream and
completed clauses. The subsequent P `ACTION:G407-E2931@1:P` points to K; CHD
`ACTION:G407-E2931@2:CHD` retains its earlier SH pointer. OL and DY are retained.

Consequently the K cannot be flattened into an unspecified re-entry into the
same B. A movement from A to distinct B can remain strict entry into B while
the body was previously in A. The packet does not itself prove A≠B or identify
either with the preceding implicit bath, and its alternatives must not be
silently resolved. S442 is therefore a countercase to the blanket diagnostic,
not a demonstrated successful whole physical execution. Later P/CHD effects
remain unbound; neither can be omitted to claim a complete result.

## What the predecessor checks do and do not add

GDT590 fixes a hypothetical host-conditioned BODY/STATION distinction (52/92
versus 40/92), not a physical identity or bath address. Its image review
explicitly rejects a 4/4 body confirmation. GDT591 finds all 14 within-statement
BODY/STATION role changes at a new SH governor, preserving source ownership.
That is role/host continuity; its conclusion explicitly disclaims confirmed
image chronology, patients, treatments and lexical meanings. Its “remote”
carrier terminology means a different source event, not a physical distance.

GDT584's statement-wide governor attachment is a reason to preserve S442's
entire directional packet. Its inherited statement units and OT/DY rendering
are not independently established historical sentences or a clock. None of
these reports supplies the missing same-bath or actual-time premise. Shared
owner labels such as “gemeinsames zweireihiges Badfeld” do not do so either.

The useful outcome is a precise conditional content restriction: the full old
S441 wording cannot also receive *all* the new strict-entry commitments. It is
not a new failure of the historical GDT599 decision, a manuscript-level
rejection of K, or an independent semantic confirmation. No enlarged search,
simulator, local exception, changed glossary or new image is warranted here.

## Evidence and access receipt

The action TSV was independently queried with the guarded `statement_id`
selector allowing only `G407-S402`, `G407-S441`, `G407-S442`: 10 selected rows.
Root's guarded full-column host packet supplies all 14 hosts. Root reported
that the complete-statement TSV guard rejected its quoted multiline row shape;
that guard was not bypassed here. Only the exact three corresponding reader
sections were read as corroboration. No other manuscript unit was opened.

SHA-256 values checked:

| Input | SHA-256 |
|---|---|
| Frozen RAW `raw_body_bath_strict_entry_reference_20260921.json` | `7023ac1b365d43b56b6106d94cda0b8db10272aee6e9369ad17dc3278d32fc86` |
| GDT599 METHOD | `e974ce05ab58a73d914c50c35cbd32c64e23612ae535930c8c09ef8827058e93` |
| GDT599 model.py | `9b62ea3bbb928acbac7f691bbd9be94619e26d0dae09323a808761f3f13476f8` |
| GDT599 1443-action edition | `7f430e61dee99a5b7a87b701a0db761e7d308e190e4a55a8354da65af431fe23` |
| GDT599 313-statement TSV, hash only | `a347128f5aba4ba9fdacff1fe69519dbcf55f016040779b1ef687a0804682263` |
| `raw479_complete_hosts_20260922.tsv` | `f09df572568c0303303b8a969cce42c67659b2975dc3a046de4ca45508c2c913` |
| `raw479_complete_actions_20260922.tsv` | `f096ae63a16f588ffc849adc251e986b9a152ae9d505478c7d02c7ef28705226` |
| GDT590 REPORT | `4a7e02c40e14295dccae781ecff231c5e1d6032a7a1c4c67cccc68b9a5e88ac5` |
| GDT591 REPORT | `db2b32d000fa8fc93059251a2bc04a428b7ee7b9fcb58f6a913b1e9aaeb40cdd` |
| GDT584 REPORT | `85bc1d98666014d6c0ca230d0260f9b9ff892b389e53b16fb192a4a5c02980ec` |

The legacy hashes match the frozen RAW's stated dependencies. No source claim
correction was required; the distinction between inherited reference wording
and added physical execution assumptions is essential to interpreting it.
