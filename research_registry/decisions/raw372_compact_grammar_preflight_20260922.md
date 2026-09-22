# RAW372 compact grammar preflight — whole f83r title/custody/loan account

This is a bounded content preflight for the existing RAW372 offer. It reads the
whole target alignment already stored in
`research_registry/proposals/raw_f83r_title_custody_loan.json` and the complete
W41 report. It assigns no new whole-word meaning, opens no target, reserve or
image source, and changes no registry or global status.

The source offer contains eight lines and 72 groups. Its exact JSON hash is
`0400e17f9483891b8dac47d7459bbda839f010e52d2e0cb4682e22c7e7522142`.
W41 REPORT is retained at hash
`32d02fcc71a98ad7414ac72adb99c4216f7e8cc4760bc041865f1b0c5d509c55`.
The seven fixed whole hypotheses supplied by RAW372 are:

- `shedy` — same asset A;
- `qokaiin` — title holder B;
- `lchedy` — borrower/custody party C;
- `chedy` — permission to use A, as a normative statement;
- `qokeedy` — delivery of custody of A to C;
- `qokedy` — duty to return A, as a normative statement;
- `qoteedy` — title to A remains with B.

These are fixed inputs to the preflight, not confirmed translations. Their
occurrences are 20 positions: `chedy` 5, `qoteedy` 4, `qokaiin` 3, `shedy`
3, `lchedy` 2, `qokedy` 2 and `qokeedy` 1.

## Exact unknown census and repetition pressure

The 72 written groups contain 54 exact types. Seven are the fixed forms above;
47 exact types remain unknown, occupying 52 groups. The unknown type list is:

```text
ar, chary, checkhy, chedchy, cheey, cheg, chepol, chey, chkedy, chkeedy,
daiin, dar, deey, dor, lchs, lo, lpchedy, lsheedy, o, olchedy, olkeedy,
opedy, otedy, pchedal, pchedar, qeeedy, qekaiin, qokal, qokeey, qokshedy,
qoky, qol, qopchedy, qotaiin, qotal, qoty, rchedy, rches, rsheedy, schedy,
shecthedchy, shetar, shey, shol, sol, solshed, tchedy
```

Repeated unknowns provide possible shared valency pressure without providing
lexical values: `chey` occurs twice in f83r.3, `daiin` twice in f83r.3–4,
`qoky` three times in f83r.6–8, and `qotal` twice in f83r.3. Their arguments
remain untyped until a construction supplies them. `qoteedy` is fixed and
occurs at f83r.2:7, f83r.5:9, and twice consecutively at f83r.7:9–10. The
double is therefore a repeated written title-duty assertion candidate, not two
assumed transfers or sales.

W41 supplies a live rival only for the unknown `qoky`: its local T0/H1 account
can connect three markers between a transfer and a later heating, but W41 also
records the .16:5 countercase and four missing recipients. That report does not
license assigning `qoky` here.

## Uniform construction skeleton

A compact account can be stated with four reusable typed constructions. These
are an audit skeleton, not a selected interpretation of the unknown forms.
Unknown groups are opaque terminals `u_i`; they may fill arguments or frame
slots, but no `u_i` receives a value.

Let `A:Asset`, `B:TitleHolder`, `C:CustodyParty`, and `S` be the paragraph
state. The fixed hypotheses contribute these typed predicates:

```text
TITLE(A,B)       = qoteedy
PERMIT(A,C)      = chedy
RETURN_DUE(A,C)  = qokedy
DELIVER(A,C)     = qokeedy
ASSET_REF(A)     = shedy
OWNER_REF(B)     = qokaiin
BORROWER_REF(C)  = lchedy
```

The four constructions are:

1. `REF_FRAME(u*, ref)` has ordered shape `opaque frame → reference`. It
   carries a typed `ASSET_REF(A)`, `OWNER_REF(B)` or `BORROWER_REF(C)` through
   intervening opaque groups without turning those groups into new values.
   Reuse is allowed only when the written reference slot has the same type.

2. `NORMATIVE(m, A, party, scope)` has ordered shape
   `opaque frame → m → typed asset/party arguments → opaque scope`, where
   `m ∈ {TITLE, PERMIT, RETURN_DUE}`. It adds a constraint to `S` and never
   changes custody by itself. `TITLE` and `PERMIT` therefore remain distinct
   relations even when adjacent in one line.

3. `CUSTODY_EVENT(A, C, S)` has ordered shape
   `prior state → DELIVER(A,C) → resulting state`. Its only state equation is

   ```text
   S=(TITLE(A,B), CUSTODY(A,X), RETURN_DUE(A,C))
   --DELIVER(A,C)-->
   S'=(TITLE(A,B), CUSTODY(A,C), RETURN_DUE(A,C)).
   ```

   The equation changes custody while preserving title and the return duty. It
   does not infer a sale, a return, or a new asset.

4. `ASSERT_REPEAT(m, args)` has ordered shape `m(args) m(args)` and produces
   one repeated normative assertion with one typed argument tuple. It is the
   uniform treatment of the exact `qoteedy qoteedy` at f83r.7:9–10; it does not
   multiply assets, title, custody or legal acts. A rival that treats the two
   tokens as two events remains open because no fixed syntax chooses this
   construction.

These four rules are compact and compositional: they use only the seven fixed
hypotheses, preserve unknown terminals, and state the sole physical state
transition as an equation. They do not provide a finite surface writer for all
47 unknown types.

## Demonstrations on distinct written clauses

**f83r.2 (11 groups).** The exact line is

```text
sol cheey qokaiin shol lchs shey qoteedy rches ar chedy dor
```

The skeleton can instantiate `REF_FRAME(sol, cheey, OWNER_REF(B), …)` and
`NORMATIVE(TITLE,A,B, rches/ar/dor)` followed by
`NORMATIVE(PERMIT,A,C, dor)`, while retaining `shol`, `lchs`, `shey`, and the
other groups as opaque. This yields the conditional constraints
`TITLE(A,B) ∧ PERMIT(A,C)` and no custody change. It does not claim that
`lchs`, `dor`, or any other unknown is an actor, operation or connector.

**f83r.4 (9 groups).** The exact line is

```text
qokshedy chedy qokedy chkedy daiin shetar shedy qekaiin chedy
```

A uniform `NORMATIVE` instantiation binds `chedy` to `PERMIT(A,C)` and
`qokedy` to `RETURN_DUE(A,C)`, while `shedy` supplies `ASSET_REF(A)` for the
same tuple. The remaining forms stay opaque. The resulting state constraint is
`PERMIT(A,C) ∧ RETURN_DUE(A,C)`; it does not perform a return and does not
create a second A.

**f83r.6 (9 groups).** The exact line is

```text
schedy chedchy qokal olchedy qokaiin chedy qokeedy lchedy qoky
```

Here the fixed slots support `OWNER_REF(B)`, `PERMIT(A,C)`,
`DELIVER(A,C)`, and `BORROWER_REF(C)` in that written order, with
`schedy/chedchy/qokal/olchedy/qoky` retained as opaque frame or argument
material. `CUSTODY_EVENT` therefore gives the conditional equation
`TITLE(A,B) ∧ CUSTODY(A,C) ∧ RETURN_DUE(A,C)` after the delivery, but only if
its prior state and `A`/`C` arguments are supplied by the surrounding frame.
No unknown is silently chosen as the missing title or return operator.

**f83r.7 (10 groups).** The exact line is

```text
solshed lsheedy qeeedy qoky o qol rsheedy qokedy qoteedy qoteedy
```

The final three fixed terminals fit `NORMATIVE(RETURN_DUE,A,C)` followed by
`ASSERT_REPEAT(TITLE,A,B)`. The double `qoteedy` is held as one repeated
assertion over one tuple, while the preceding seven groups remain opaque.
This is a useful shared-valency opportunity, but it does not decide whether
the repetition is emphasis, serial syntax or two acts.

The four demonstrations show that a small typed account can express title,
permission, custody and return without assigning the 47 unknown types. They do
not show that the exact unknown groups supply the missing arguments, that the
four constructions are the manuscript grammar, or that the paragraph's
physical history is true.

## Decision

A compact construction skeleton is warranted as a bounded preflight because
three distinct lines plus the double repetition can be represented with the
same typed relations and one explicit custody equation. A meaningful whole
semantic development is **not warranted yet**. The genuine obstacles are:

- 47 unknown exact types occupy 52 of 72 groups, so most argument order and
  scope remain opaque;
- the skeleton needs typed antecedents for A, B and C across lines, but repeated
  fixed forms alone do not establish which unknown groups introduce or bind
  them;
- `DELIVER` occurs once, while title/permission/return recur; the proposed
  state transition is therefore conditional on a cross-line binding rather than
  independently recovered;
- the exact `qoteedy qoteedy` repetition has no fixed construction choice;
- W41's `qoky` candidate has a documented countercase and cannot be imported;
- the RAW372 offer itself says all meanings, participants, boundaries and
  provenance are hypothetical and requires a finite writer before fixed
  testing.

Decision: retain this four-rule skeleton as a bounded design constraint, but
defer a whole-reading development or semantic selection until an independently
bounded source or argument-binding preflight supplies typed antecedents without
assigning a new lexical winner. No new lexicon, score, simulator, or result
claim is authorized by this note.
