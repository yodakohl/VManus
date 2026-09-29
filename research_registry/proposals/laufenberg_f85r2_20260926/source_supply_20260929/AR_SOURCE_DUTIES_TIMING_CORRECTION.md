# AR source-duty timestamp and ordering correction

This note preserves the original source-duty files and corrects the reliability of their timing statement. It does not alter or replace them.

`AR_SOURCE_DUTIES.md` says “Frozen 2026-09-29 18:42 UTC” and says the freeze preceded any target group/profile reading. That embedded time is impossible to reconcile with the root's contemporaneous clock report: root reports observing the files already present by 18:40:20 UTC. The files' current filesystem mtimes are `2026-09-29 20:39:04.469832676 +0200` (MD) and `20:39:04.470119220 +0200` (JSON), which display as 18:39:04 UTC, but filesystem metadata is corroborating evidence only; neither that timestamp nor an exact creation second is certified here.

The carried task summary says this agent wrote the original source-duty files in the prior work phase before target/profile inspection. Their filesystem mtimes display as 18:39:04 UTC, corroborating (but not proving to the second) creation before this agent's 18:40:14 clock call and ensuing target/profile inspection. Root independently confirms seeing the files by 18:40:20 UTC; that receipt alone would not establish existence before 18:40:14.

A separate later tool sequence in this agent's current context returned 18:40:14, then opened `AR_W_PROFILES.json`, extracted target W18–23 ZL groups, read target word-prior rows, and only afterward reopened `AR_SOURCE_DUTIES.md` and the AQ reports. Thus target/profile content was inspected before the **reopening** of the duties file, not before the source-duty file was authored. The inherited context records earlier AQ-report reading before target inspection; exact times are unavailable. No lexical assignment had been made at the target/profile-inspection stage; AR_AUTHOR values were authored after the duties text was read.

The supportable ordering is therefore: the agent authored the duties file before target/profile access according to carried work context, with mtimes corroborating that sequence; the agent later reopened/read the duties file after target/profile inspection; and no target value was assigned until after reading the frozen duties. The original embedded 18:42 UTC time is erroneous and must not be used as an exact freeze timestamp. No exact second is invented to reconcile it.

Original files and unchanged SHA-256:

- `AR_SOURCE_DUTIES.md`: `df465e4cbbd4863e34725cdc867719ab06d15918c75c68f08ac71eb1d83bac57`
- `AR_SOURCE_DUTIES.json`: `2a60580691fff14bde1125227cd345de2c664bce91969340c5bebfd0e7318d99`
