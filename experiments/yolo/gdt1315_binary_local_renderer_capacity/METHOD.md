# GDT1315: local graphical-choice capacity for binary-code survivors

Decision note10October2026. Inclusive budget08:00–08:35UTC covers retrieval,
preparation, implementation, verification and publication; no expansion at deadline.
1314retains2/2/1reader-specific binary partitions but leaves within-class graphical
choice free. The genuinely unknown question is whether a local deterministic
whole-form writer, optionally carrying one bit of state, can make those choices.
This is a new restriction of the surviving family, not a repair of an old failure.

The exact conditional family retains1312's global bit partition and injective
bitword/source-character table. Given a source character, the renderer emits ONE
whole visible group. Its output may depend arbitrarily on previous/current/next
source characters, exact page selector, original group index in the output line,
total original group count of that line, and a hidden
state from a set of sizeS<=2. History may affect that state by ANYdeterministic
update; no transition restriction is needed for a necessary bound. The table may
be arbitrarily large; no claim of compactness is being tested. Source lookahead
one character is permitted. Optional free choice, randomness, longer source
context, paragraph role, preceding visible shape, line number, unbounded counter or other per-event
inputs are outside this family unless included in the stated at-most-two states.
This does not exclude such alternatives or establish native writer complexity.

For a fixed known context, at mostSdifferent whole outputs are possible. Since the
codebook is injective, equality of full bitwords is equality of decoded source
characters regardless of their unknown values. Thus max distinct center rawforms
within an exact context cell is a necessary lower bound onS. It is NOT sufficient
for a realizable state-transition machine. If this bound exceeds2for every surviving
key of a reading, stop the entire specified family for that reading. Otherwise
retain only not-excluded, never claim a successful writer. No larger state cap,
added context fields, source assignment or decoder fit after outcome.

Data: unchanged1233strict groups union1314EDGES, readers separate. Rejoin915original
IDs, rawforms, indices, seams and line metadata. Use only triples at consecutive
original group indices INONEexactlocus with retained groups and definite joining
seams. No skipped/uncertain neighbors, crossing lines, sentinel guess or source
repair. This additionally assumes these three groups are consecutive source
characters; external record boundaries inside triples would change that contract.
Physical line edges are complete-group boundaries as in1314. No new text/image,
rawTSV, reserves, f84/f84r/f116v/f1rbody or historical327/336body.

For each of all2/2/1surviving keys compute three PREDECLARED context levels:
SOURCE=(left,current,right bitwords);
PAGE=(page selector,SOURCE);
LAYOUT=(page selector,original center index,total original line group count,SOURCE).
LAYOUT is the sole primary decision level. SOURCE/PAGE describe how much these
provided contexts reduce the bound; their larger bounds cannot override LAYOUT.
For each level retain cell/type-count histogram, maximum, total cells/occurrences,
number of cells exceeding2, and first lexical maximum-cell witness, all distinct
center forms with an original event witness. Retain EVERYLAYOUTcell exceeding2
and its original IDs. No p-value or independent-replication claim.

Primary keyed sets use bitstrings; independent sort/group verifier uses(length,
integer) codes and independently reconstructs consecutive triples. Validate source
joins, all cells, maximum witnesses and complete conflict artifact. Freeze programs,
protocol and input hashes before native count. Toy fixtures cover a validtwooutput
cell, threeoutput contradiction, changed layout, leading-zero length and missing
original neighbor. No arbitrary meanings, not even provisional ones, assigned.

Predecessors read:1295/1310test ONEvisibleunit per sourceletter with within-word
neighbor allography, not one WHOLEgroup per sourcecharacter.1276tests fixedstem-pair
endings and one binary input, not these codeword-derived sourcecontexts.1313only
constrains decoded runs;1314onlycode inventory. Their original decisions remain.
1314's shape-choice issue motivates this bounded test, not a long decoder project.

Pre-count scope correction after source-free review: paragraph flags are omitted
from ALLreaders, because1073leavesRFparagraphmetadata unscorable. Missing values
are not physicalFalse. Paragraph-role-sensitive rules are therefore explicitly
outside this test; no claim that paragraph effects are controlled. This change
was made before locking or any native count, not after seeing an outcome.
