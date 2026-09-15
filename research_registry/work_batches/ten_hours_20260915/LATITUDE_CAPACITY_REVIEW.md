# Independent latitude-capacity receipt and geometry-packet review

2026-09-15. **PASS for the bounded metadata result and the 3,761-program
enumeration.** Both fixed latitude serializations lack eligible complete
paragraphs in every edition. The immediate worksheet format stops before code
construction or arithmetic fitting. This is a notation-capacity result, not
evidence against astronomy or numerical meaning generally.

The reconstruction read only the six already guarded GDT915 caches in the
current GDT928 scope. No new target scope, source-word search, target-body
display, digit/opcode fit, image opening, contact, or reserve access occurred.
GDT967 was neither run nor modified. No GDT968 was created by this review.

## Independent reconstruction

I checked all eight GDT928 preregistration bindings, then reconstructed the
complete paragraphs directly from the six caches without importing GDT928's
loader or the new capacity script. The independent implementation finds each
paragraph start, its first closing marker before the next start, and requires
consecutive locus numbers. It separately checks each line for at least two
groups, literal `[a-z]+`, consecutive source-group indices and definite internal
seams. Group totals include every group in the complete frame.

All 179 allowed selectors were checked against the inherited allowlist, with
f84-prefixed and f116v selectors excluded. Every complete/literal/nonliteral
total and every bin of the reported literal length histograms agrees exactly.

| Edition | Complete frames | Eligible literal frames | Ineligible frames | Eligible 7 groups | Eligible 12 groups |
|---|---:|---:|---:|---:|---:|
| ZL3b | 659 | 31 | 628 | 0 | 0 |
| IT2a | 690 | 523 | 167 | 0 | 0 |
| RF1b | 0 | 0 | 0 | 0 | 0 |

Every model has zero eligible physical leaves, below its requirement of three.
The sole complete twelve-group frame before literal filtering is ZL3b
`f46r|f46r.14-f46r.15`. It fails **NONLITERAL_GROUP** and **UNDEFINITE_SEAM**.
Only its metadata identifier, length and reasons are reported here; its body
was not displayed. There are no complete seven-group frames in any edition,
and IT2a has no complete twelve-group frame even before literal filtering.

The excluded ZL frame remains unknown for a different treatment of uncertain
characters/seams; it is not a failed numerical calculation. The many other
nonliteral frames likewise remain outside this exact literal channel. RF's
absence of complete boundary-marked paragraphs is missing structural capacity,
not a refutation of content. Different paragraph boundaries, lengths, hidden
arguments or filler would be different models and are not automatic successors.
Alternate readings are versions of one manuscript, not three replications.

## Independent numerical count

The program count concerns an illustrative finite algorithm grid, not 3,761
historically printed source calculations. I enumerated all tuples
`(branch,h,d,e,90,phi)` under the decision's domains and checked distinctness:

| Branch | Rule and permitted observations | Programs |
|---|---|---:|
| NORTH | `d=1..24`, `h=d+1..89`, `e=h-d`, `phi=90-e` | 1,836 |
| SOUTH | `d=1..24`, `h=1..89-d`, `e=h+d`, `phi=90-e` | 1,836 |
| EQUINOX | `d=0`, `h=1..89`, `e=h`, `phi=90-e` | 89 |
| Total | All intermediate and final values lie in `1..89` | **3,761** |

For each nonzero branch, `sum(89-d, d=1..24) = 24*89-300 = 1836`.
The enumerator excludes zero-declination NORTH/SOUTH cases, so they cannot
imitate EQUINOX without exercising opposite signs. The canonical enumeration,
branch order N/S/E, then ascending h/d, compact JSON without trailing newline,
has SHA-256 `730a28cba513a6dd1ba93d4244fd719ce05517e45c32d7ca4c2ef7880e07cb82`.

The seven-instruction sequence has five numeric instructions and two without
operands. FUSED therefore has seven groups; SEPARATE has `5*2+2=12`.
The source's Q=90 interpretation, integer grid, direction meanings and
serialization remain hypotheses. No digit-key completeness, successful
arithmetic recovery, or semantic uniqueness was tested after the metadata stop.

## Bound receipts

| File | SHA-256 |
|---|---|
| `LATITUDE_WORKSHEET_DECISION.md` | `92caf80c8c273c818debe95c52f3766deec22818ebdd6c3bd21926c776595e81` |
| `latitude_capacity.py` | `f934ac328bc67d08588749ff815d99c392c57b65b18b01c4e974ec15b324670d` |
| `LATITUDE_CAPACITY.json` | `b31a05f0bed210db6ec282b314aed12b3ea75fe5778aaa2a4b30275ee555ee88` |

The six input filenames are under
`experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/`:

| Cache | SHA-256 |
|---|---|
| `SOURCE_DISCOVERY_ZL3b.json` | `53223239734cbe655ba7f296a81d70924955bb746beb52e08035e1c4d651f6a2` |
| `SOURCE_EVALUATION_ZL3b.json` | `7ab2cafe31d50b4013682c9b73d867bd36bae9a0a4addc0de509be7be48e44c0` |
| `SOURCE_DISCOVERY_IT2a.json` | `ab7c8bd792365fc9dc1b3b8376f8453719a0003712aeb6caff1fbe211e2ba2fa` |
| `SOURCE_EVALUATION_IT2a.json` | `2c62ef9c6c1cec11fd0e0e383b85190705a6059439163509213df2bd56d0e8c9` |
| `SOURCE_DISCOVERY_RF1b.json` | `90662e53898c7b59d1bfc724e9d49fe8af6acf714fbb99a45262cbe594bf270a` |
| `SOURCE_EVALUATION_RF1b.json` | `ccace49eb471825f70afff673cf8bcb60ec9a41fbb8eb96dfbef1f2fef1ec99c` |

## Reproduce the independent metadata check

Run this Python block from repository root. It retains metadata and eligibility
booleans; it prints no target words and does not import the primary loader.

```python
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, json, re

R = Path.cwd()
P = R / 'experiments/yolo/gdt915_terminal_lr_phrase_transfer'
S = R / 'research_registry/work_batches/ten_hours_20260915'
lock = json.loads((R / 'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/PREREG_LOCK.json').read_text())['files']
for name, digest in lock.items():
    assert hashlib.sha256((R / name).read_bytes()).hexdigest() == digest
allowed = set(json.loads((P / 'src/SPEC.json').read_text())['allowed_selectors'])
assert len(allowed) == 179
assert not any(p.startswith(('f84', 'f116v')) for p in allowed)
reported = json.loads((S / 'LATITUDE_CAPACITY.json').read_text())['panels']
for ed in ('ZL3b', 'IT2a', 'RF1b'):
    pages = defaultdict(list)
    for phase in ('DISCOVERY', 'EVALUATION'):
        data = json.loads((P / 'artifacts' / f'SOURCE_{phase}_{ed}.json').read_text())
        ix = {name: i for i, name in enumerate(data['group_columns'])}
        for raw in data['lines']:
            m = raw['metadata']
            assert m['page'] in allowed
            if m['kind'] != 'P':
                continue
            gs = raw['groups']
            good = len(gs) >= 2
            good &= all(re.fullmatch('[a-z]+', g[ix['ivtff_group_raw']]) is not None for g in gs)
            for left, right in zip(gs, gs[1:]):
                good &= int(right[ix['source_group_index']]) == int(left[ix['source_group_index']]) + 1
                good &= left[ix['right_separator']] == right[ix['left_separator']] == 'DEFINITE_SPACE'
            pages[m['page']].append((int(m['source_row_index']), int(m['locus'].rsplit('.', 1)[1]), m['paragraph_start'] == '1', m['paragraph_end'] == '1', len(gs), bool(good)))
    frames = []
    for page, lines in pages.items():
        lines.sort()
        starts = [i for i, line in enumerate(lines) if line[2]]
        for k, first in enumerate(starts):
            limit = starts[k+1] if k+1 < len(starts) else len(lines)
            last = next((j for j in range(first, limit) if lines[j][3]), None)
            if last is None:
                continue
            block = lines[first:last+1]
            numbers = [line[1] for line in block]
            if numbers != list(range(numbers[0], numbers[0]+len(numbers))):
                continue
            frames.append((sum(line[4] for line in block), all(line[5] for line in block)))
    good = [n for n, eligible in frames if eligible]
    assert len(frames) == reported[ed]['complete']
    assert len(good) == reported[ed]['literal']
    assert len(frames)-len(good) == reported[ed]['nonliteral']
    assert {str(n): v for n, v in Counter(good).items()} == reported[ed]['literal_length_histogram']
    for model, length in (('FUSED', 7), ('SEPARATE', 12)):
        assert length not in good
        assert reported[ed]['models'][model] == dict(paragraphs=0, physical_leaves=[], minimum_three_leaf_capacity=False, rows=[])
    print(ed, len(frames), len(good), 'ZERO_ELIGIBLE_7_AND_12')
programs = []
for branch in 'NSE':
    for h in range(1, 90):
        for d in ([0] if branch == 'E' else range(1, 25)):
            e = h-d if branch == 'N' else h+d if branch == 'S' else h
            phi = 90-e
            if 1 <= e <= 89 and 1 <= phi <= 89:
                programs.append((branch, h, d, e, 90, phi))
assert Counter(p[0] for p in programs) == dict(N=1836, S=1836, E=89)
assert len(programs) == len(set(programs)) == 3761
assert hashlib.sha256(json.dumps(programs, separators=(',', ':')).encode()).hexdigest() == '730a28cba513a6dd1ba93d4244fd719ce05517e45c32d7ca4c2ef7880e07cb82'
print('NUMERICAL_PROGRAMS', len(programs), 'PASS')
```

## Geometry: which current packet is usable?

**GDT871 is the best existing source packet to nominate for a prospective
whole-output review, but no primary packet reviewed here already establishes
an eligible complete geometric construction.** This is a source/architecture
decision, not another image observation. No image was opened in this task.

I checked [the current scope](../../../docs/VOYNICH_DATA_SCOPE.md) and the
actual GDT791, GDT861, GDT867 and GDT871 admission tables. The appropriate
already admitted full originals are:

| Packet | Currently admitted selectors on original | Established observation and unresolved obligation |
|---|---|---|
| GDT871, Yale1006194 | f67r1 and f67r2 | Two complete circular compositions plus distinct horizontal text regions. Includes pointed fields, radial divisions, faces and coloured forms. No complete primitive inventory, seed-role assignment, construction text ownership or metric-error model. |
| GDT871, Yale1006196 | f68r1, f68r2 and f68r3 | Complete shared original with open star fields and a large circular composition. The orientation report does not independently settle exact selector-to-region order or all individual inscription attachments. |

The relevant records are GDT871's
[report](../../../experiments/yolo/gdt871_remaining_shared_diagram_orientation/REPORT.md),
[whole-original observations](../../../experiments/yolo/gdt871_remaining_shared_diagram_orientation/artifacts/OBSERVATION.json),
[image metadata](../../../experiments/yolo/gdt871_remaining_shared_diagram_orientation/artifacts/IMAGE_METADATA.json),
and [admissions](../../../experiments/yolo/gdt871_remaining_shared_diagram_orientation/src/PAGE_ADMISSIONS.tsv).
The image hashes are
`0518312a566ee713a46c9887d8b8b9d7141d14095e360661789c1dad9b5c0d1c`
and `4b0f31d1e08b8f026886aa599232b7dfcd33417b1eef43a44e619c3ebd21faa5`.
They bind existing sources; neither cached image was opened or republished here.

**f57v is not a current image candidate.** Its historical exposure and the
existence of GDT179's provisional role-scaffold primary do not grant current
image access. Missing older Llull/manual report files do not imply that f57v
was unresearched. It is absent from the currently applicable tables checked
above; no f57 image is opened or proposed as a substitute.

GDT392 supplies limited independently observed boundary asymmetries inside the
admitted f67 originals: f67r1 D1 has a decorated sector boundary; f67r2 M1/M2/M3
have dotted boundaries/tail. These can be retained as visual facts. They do not
identify a compass centre, seed segment, construction order or text-to-output
relation. Its absence of an author-visible direction remains unchanged. A
metric construction could in principle remain meaningful modulo a global
reflection and rotation; it must not turn catalogue clockwise order into an
observed instruction order. The old directed-array test stays closed.

RBR002's f67r2 underlayer packet is about retraced writing, not construction
geometry. It retained only two recoverable earlier-ink cases and stopped its
correction route. Its localization initially used a wrong equal-radius
approximation of an elliptical ring. Neither the old localizations nor its
underlayer observations supply exact construction circles or a metric model.
GDT791 provides page/record hierarchy, with deep panel annotation limited to
three biological pages; it does not add a complete geometric census to the
f67/f68 originals. GDT878's named minimal-pair/visible-red-area packet and
GDT213/GDT221's medical-diagram architecture and failed assignment transfer
likewise do not supply this missing output relation. The f69v start/direction
and calendar closures are not reopened.

## A genuinely different geometry question, and its present stop

The concrete source-side mechanism in
[IDEA000125](../../proposals/geometric_construction_program.json) is finite:
JOIN, CIRCLE, INTERSECT, STOP, with prior-object references and two seed points.
Euclid I.1 is a complete small source example: two circles centred on the given
segment's endpoints and two joins from a common intersection produce equal
sides. Its constraint is a constructed metric equality, not the name of a
circle, a star count or radial succession. The previously reviewed complete
source proposition and CMI's medieval witness index support this mathematical
content; they do not supply a Voynich code or owned target output.

Before any new native view, root would need to bind one whole output unit in
GDT871's existing packet and the exact prospective question: does that entire
unit contain an enumerable point/line/circle construction, with a complete
written passage hypothesized to describe it? No label translation is required.
Seed roles can be inferred jointly from a fixed inventory of visible points;
requiring already deciphered point names would be unnecessary. What cannot be
free is a new coordinate for each instruction, target-dependent deletion of
auxiliary primitives, or a new output boundary for each candidate.

The known whole-original descriptions contain faces and coloured/curved forms
outside the four-opcode language. Thus **the entire illustrated original is
not already a demonstrated complete output of that language**. Selecting only
convenient circles while dropping the remaining graphics would lose the whole
output contract. A visibly bounded geometric subunit could be legitimate, but
the existing packets do not yet establish one with all required primitives and
its complete instruction text. If the proposed relation is merely concentric
circles/spokes or their symmetry, the new task changes no meaning decision and
should not be implemented.

The bounded next action, if root chooses it, is a preregistered whole-unit
inspection of **one of the two GDT871 originals**, directed solely at this new
completeness/metric-construction question. A complete figure whose output cannot
be represented stops the specified language; an uncertain or incomplete output
stops capacity without refuting geometry. Only a complete owned output and
bounded passage could justify program construction. A second whole construction
under the same code would then be required before interpreting transfer.

This review does not authorize that view, silently claim a new construction
relation, demand confirmed lexical anchors, or repeat the closed ring and label
tests. At this checkpoint the strongest named packet is GDT871; **target-ready
geometric packets established by this review: zero**.
