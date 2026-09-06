# GDT869 — Embedded capture metadata, f17r only

Question: do unexported TIFF metadata explicitly assign illumination to the
three already known f17r MB365UV captures? EBA001 exported only eleven fields;
the known public imaging README directs readers to image properties. This is
an exploratory metadata inventory, not a new visual or decipherment experiment.
The duplicate screen returned no prior full-tag audit; the primary EBA001
acquisition script confirms the limited field export.

Freeze the three URLs, byte counts and SHA256 values in src/SPEC.json before
fetching or opening their metadata. Inspect metadata only: enumerate classic
TIFF image directories and reachable ordinary EXIF/SubIFD/interoperability
directories, with entry type/count/byte size/hash. Do not decode pixels, render,
crop, OCR, inspect GPS values, or retrieve another manuscript folio. Unknown
private fields remain disclosed as opaque when no defensible interpretation
exists. A parser stop is an instrument limitation, never evidence of absence.

Full metadata values remain in ignored runtime for local review. Public outputs
contain structural descriptors and hashes; publish only a concise, privacy-
checked description of scientifically relevant illumination fields. Do not
publish camera/host identifiers, private paths, private machine metadata or
unrelated payloads. No full source image/PDF mirrors are published.

Root manually assesses readable metadata after acquisition. Positive evidence
requires an explicit capture-specific lighting label or geometry. Image
orientation, sequence number, wavelength and exposure duration alone do not
assign lamp direction. Absence means only no assignment in actually decoded
metadata; unexplained opaque fields prevent an exhaustive absence claim.
Independent validation verifies exact source bytes, reachable tag inventory,
and parser controls; it cannot validate the semantics of an unknown vendor blob.

A documented assignment would support deciding whether a later physically
motivated contrast is feasible. No assignment closes this metadata route;
opaque payloads identify a specific remaining documentation need. None permits
ink, chronology, hand, character, word, language or meaning claims. The README's
reported calibration and pseudocolor processing are not proof that these raw
files have received either operation.

Budget: selection/scaffold began10:45:58UTC. Stop this pass by11:15UTC, including
publication, or record the exact unresolved instrument/source limit. No automatic
image reinterpretation or alternate-capture hunt follows. Runner and independent
validator controls must pass before frozen source acquisition. No targets have
been opened during protocol preparation.
