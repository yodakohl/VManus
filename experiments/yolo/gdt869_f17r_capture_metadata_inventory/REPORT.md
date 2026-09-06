# GDT869 — Acquisition fields found; direction remains unresolved

**UNRESOLVED_OPAQUE_METADATA.** All three exact f17r sources authenticated;
144metadata descriptors independently reconstructed with exact parity. Each
file contains48tags across the principal directory and one EXIF directory.
No pixels were decoded or displayed; no f116v source was accessed.

The additional fields carry information absent from EBA001's eleven-field
export. EXIF tag34852 contains two identical MB365UV entries at7.450seconds
and100.0w for capture007, and one entry at10.000seconds and100.0w for each of
029 and037. These are literal recorded values: duplicated entries do not prove
two lamps, and the unit label does not establish measured radiometric power.
IPTC tag33723, record2/dataset120, contains the same two generic lines in all
three files: Main banks and Transmissive. It supplies no per-capture direction
assignment. READABLE_FIELDS.json retains just these relevant descriptions.

These entries do not resolve the lighting geometry needed for the proposed
material contrast. Vendor fields37407/37408 contain binary data and structured
fixed-width textual content which was not fully decoded. Some content is private
machine metadata and was deliberately omitted. Therefore this is **not** an
exhaustive claim that the files contain no further capture information. The
source gap is now specific: an authoritative interpretation of those vendor
fields or a capture-number-to-lighting map is needed. No automatic vendor decoder,
new image hunt or trace regrading follows this pass.

The EBA001 repeat-capture dark-trace result is unchanged. These additional
metadata do not establish ink, absorption, relief, chronology, hand, character,
reading, language or meaning. The known imaging README reports calibration and
pseudocolor preparation; neither its wording nor these metadata proves that the
three selected products are radiometrically comparable.

## Reproduction and limits

Preregistration0374dd55 was public before source acquisition at10:59:57UTC.
Frozen runner/validator controls passed; run `src/run.py --run`, then
`src/validate.py` from the repository via their experiment-relative paths.
Both use metadata-only readers and authenticate the fixed source bytes.
Download originals only into ignored runtime. INVENTORY.json contains no decoded
payload values; all full private metadata stay in runtime/PRIVATE_METADATA.json.
The public descriptor hashes permit source checking without republishing payloads.

After extraction, root inspected readable fields and added review_readable.py to
reproduce a privacy-restricted descriptive projection. This script is explicitly
post-extraction, not part of the original executable preregistration lock and
not a new confirmatory test. Its narrow field selection is disclosed rather
than represented as an exhaustive vendor decoder. The IPTC scan consumes26records
and leaves2trailing bytes per file; no complete-container interpretation is claimed.
An independent post-extraction review confirms the selected caption fields
exactly and spectral text after trimming one trailing space per file. Its
READABLE_VALIDATION.json is descriptive, not preregistered semantic validation.
The frozen validator checks source/metadata fidelity, not the manual lighting
interpretation. Original files and source PDF remain uncommitted.

Selection began10:45:58UTC; the first metadata inventory completed about11:00UTC.
The implementation/publication overhead is included in the11:15UTC pass budget.
Source credit: Lazarus Project, RIT Chester F. Carlson Center for Imaging Science;
Beinecke MS408,f17r. Technical README source/hash in the bound documentation note.
