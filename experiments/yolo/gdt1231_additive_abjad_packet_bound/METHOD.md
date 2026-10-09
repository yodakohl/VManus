# GDT1231 — additive letter packets: method

Status: selected, unscored. Root owns selection and analysis. No blindness claim.

The historical al-Qalqashandi example replaces one source letter with a packet
of letters whose numerical values add to its value. Alternatives for the same
value are explicitly permitted. Root inspected IX232–233. The Mafatih al-Ulum
primary table supplies the28 positive values; its modern edition and source
limits are recorded separately. This is an explicit reconstruction, not an
identified Voynich alphabet or language.

Positive motivation: a human can execute the rule by addition; it carries actual
letters and permits alternative written forms without a giant word dictionary.
The strongest relevant predecessor is GDT882: all fixed nonzero constant sums
of complete literal lines failed. Its source units and constant-line target are
different; it is not reopened. GDT969 fixes a23-group arithmetic programme and
failed; IDEA110/GDT880 tested a between-group total relation with insufficient
capacity. Those remain closed. No prior proposed continuation is reused.

Unknown: can any fixed positive assignment from the complete abjad value table
make every already selected strict-interior manual-packet form encode one valid
source-letter value? That necessary condition is meaning-free. If contradicted,
this exact simple packet interpretation stops. If compatible, only arithmetic
capacity survives; message framing, reversible writer choices, source literacy,
word frequency and directed sign structure still need justification. No full
writer is built and no statistical fit is claimed.

Use the fixed existing manual packet (12 loci,36 complete alternate-reader lines,
297 raw groups), with the filter in SPEC.json. Selection of those examples predates
this model and deliberately includes frequent, rare and long forms; it is not
random or independent confirmation. Alternate readings are tested separately.
No fixed common key is demanded across disagreeing readers. Strict interior
spaces avoid assuming that every physical line edge is a packet boundary.

Each of the22 working signs gets one value in A={1..9,10..90 by10,100..900 by100,
1000}; equal values for distinct signs are allowed. Every retained group sum must
lie in A. This relaxed class contains all injective22-sign substitutions using
that table. No fixed order or exactly-two-sign condition is added. Full source
word/punctuation framing is not supplied by the historic example and is not
silently inferred from a later subsection about another cipher.

Run Z3 as a constraint finder. For UNSAT, retain a deletion-reduced core and
certify it through a separately implemented finite-domain CSP search using exact
integer set arithmetic, with an explicit branching certificate. A validator
rebuilds words/counts from the owned packet and replays the certificate using
its own support calculation; it does not accept an UNSAT label as a proof.
For SAT, independently sum all word constraints under the witness. Fixtures
include positive, inconsistent and repeated-sign coefficient cases. Incomplete
certificate or timeout is inconclusive, not an exclusion. No new native query.

The inclusive work budget is60min,10:41:37–11:41:37UTC, counting source review,
preparation, implementation, validation and local closure. Per-reader limits:
90s solver,30s core reduction,180s independent search. At deadline stop expansion
and record actual uncertainty. Do not automatically repair this writer or add
corpora. Work stays local under the user's4Oct checkpoint exception.
