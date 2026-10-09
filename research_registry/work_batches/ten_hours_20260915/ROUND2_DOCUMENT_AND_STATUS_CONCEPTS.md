# Round 2: source-specific document and status mechanisms

**Status:** `SOURCE_ONLY_UNREVIEWED`, 2026-09-15. This note deepens existing raw cards `IDEA000333` and `IDEA000335`; it adds no new card, opens no Voynich target text/image, and runs no test. The route and all target gates remain unchanged.

## 1. Documentary transfer with a scoped protection and procuration chain (`IDEA000333`)

**Primary source.** Electronic Sawyer S 454, A.D. 924 x 939, “King Athelstan to the burgesses of Malmesbury; grant of privileges and 5 hides near Norton, Wilts.” The site gives Latin, a translation, and metadata for the witnesses. Source: [Electronic Sawyer S 454](https://esawyer.lib.cam.ac.uk/charter/454.html). The site notes that one listed manuscript witness is a seventeenth-century copy; the charter’s date range and transmission qualification remain part of the source limits.

**Complete bounded chain.** The source first has Athelstan grant, for himself and his successors, to the burgesses and their successors: (a) taxes and free customs, preserved as under Edward and without diminution; (b) a command to those under his power not to injure them, with release from named burdens/claims; (c) royal heath of five hides near Norton, granted because of their assistance against the Danes. It then closes the act: the charter is made with the king’s sign, attested by Edmund (his brother), and made with the counsel of Wolsin (chancellor), Odo (treasurer), and Godwine. The final sentence identifies Godwine, bearer of the king’s standard, as the person who obtained this for the burgesses.

**Meaning hypothesis D1: typed documentary act.** A source-derived parser would represent `issuer → beneficiary → right/object`, then a protection/restriction scoped to that beneficiary, then attestation and a procurator/agent closure. The five-hide grant and the customs grant share beneficiary and issuer but have different objects and grounds. The terminal Godwine clause links an agent back to the beneficiaries.

**Meaning hypothesis D2: administrative list/report.** The same visible sequence could be a list of privileges, burdens, land, names, and an explanatory note. Names at the end are metadata or historical commentary; no witness or procurator relation is required, and the protection clause need not scope over both grants.

**Smallest different target consequence.** On an already admitted complete-paragraph object, D1 predicts a reusable participant relation spanning at least two acts (the same recipient linked to distinct objects) plus a terminal attestation/agent relation whose scope points back to that recipient. D2 predicts independent fields: object clauses may occur without a beneficiary carry, and terminal names need not link to earlier arguments. The distinction is a cross-clause argument graph and scope relation, not equality of whole word forms. No target instance was inspected here.

**Assumption cost and failure.** Paragraph boundaries and a terminal-name/attestation role would need to be fixed by an existing source-bound analysis. A Herbal paragraph may contain no documentary act, and a final material/result field could mimic a witness closure. If no repeated participant relation or scoped protection/agent link can be fixed without English glosses, this remains a historical register rival only. `IDEA000034` and `IDEA000066` are nearest exception/scope predecessors; they are not treated as positive evidence.

## 2. Institutional status machine with a permission branch and persistent repair (`IDEA000335`)

**Primary source.** Rule of Benedict, chapter 43, “On Those Who Come Late to the Work of God or to Table,” in the Order of Saint Benedict’s archived text. Source: [OSB Rule of Benedict, chapter 43](https://archive.osb.org/rb/text/rbemjo2.html). The web text is Leonard J. Doyle’s modern English translation from the Latin, revised/adapted for the page; the source status is therefore a translated witness, not a claim about a Voynich lexicon.

**Complete bounded chain.** The chapter has one general trigger—failure to come when the signal/verse calls—and several domains:

1. At the night office, arriving after the Gloria of Psalm 94 removes the person from the usual choir place and puts them last or in a place where the abbot and all can see them. They remain there through the office and then make public satisfaction; entering the oratory prevents loss of the whole office and is intended to correct future conduct.
2. At the day Hours, arrival after the verse and Gloria of the first Psalm again means last place. The late person cannot join the choir until satisfaction, **unless** the abbot pardons and permits it; the text immediately preserves the duty to make satisfaction even under that permission.
3. At table, lateness is corrected through a first/second-time threshold; persistent failure excludes the person from the common table, separates them from the group, makes them eat alone, and removes their wine portion until satisfaction and amendment. A similar penalty applies to absence from the post-meal verse.
4. A person who refuses something offered by the Superior receives nothing later until proper satisfaction.

**Meaning hypothesis S1: persistent actor-state transition.** A formal content model carries an actor from trigger → visible demotion/separation → repair/satisfaction → restored participation. The abbot’s permission is a bounded branch that changes re-entry timing but does not delete the repair edge. The table branch adds a counted recurrence threshold and a deprivation state; the refusal branch reuses the same repair condition with a different trigger.

**Meaning hypothesis S2: independent procedural penalties.** The chapter may instead be a set of local instructions: late arrival, choir placement, table exclusion, and refusal each have their own penalty. “Satisfaction” can be a repeated conventional phrase without a carried actor state; the permission clause may simply replace the normal choir restriction.

**Smallest different target consequence.** S1 predicts a repeated repair relation that closes multiple trigger domains, with the permission branch altering only one intermediate edge and leaving the terminal repair obligation. It also predicts that a recurrence threshold changes status (common table → separation) rather than merely repeating an action. S2 predicts no cross-domain state carry: each penalty can stand alone, and permission may cancel the downstream repair requirement. The distinguishing object is a linked trigger/status/repair/exception graph, not a same-word claim. No target paragraph or candidate form was inspected.

**Assumption cost and failure.** The target must expose complete ordered records and a role-bearing exception/repair structure. Without an independently fixed actor or scope relation, any ordered procedure can be relabelled as status change. The strongest failure is that the manuscript has operational entries with no institutional persistence; then S1 cannot beat S2. `IDEA000034` and `IDEA000066` remain realistic scope/exception rivals, and the source does not make them false.

## Why these two additions are materially distinct

The charter requires a **participant/object/scope/attestation** graph whose terminal names certify an act. Benedict requires an **actor/state/time/repair** graph in which an exception preserves a later obligation across several trigger domains. Both produce connected hypothetical readings without assigning English meanings, while differing from Meum’s material/preparation/result branch. A future exploratory parser could test either only after fixing the source-derived relation schema and choosing an already admitted complete-paragraph endpoint; a positive structural fit would remain exploratory and would not certify translation.
