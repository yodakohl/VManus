# EBA001 external evidence acquisition targets

Date: 2026-08-13

This ranking works backwards from observations that make currently
indistinguishable physical or semantic hypotheses predict different outcomes.
It is not a list of additional correlations and it does not authorize another
decoder over the existing transcription.

## 1. Raw 365-nm f17r and f116v capture triplets — executed

- **Candidate:** the six exact public Lazarus/RIT 16-bit TIFF capture products bound in
  `results/eba001_raw_directional_msi_inventory.json`.
- **Currently ambiguous hypotheses:** a faint registered marginal trace exists
  independently in the source TIFF captures, versus it is a single-capture
  transient or processed-composite-only artifact.
- **New observable:** persistence at corresponding apparent manuscript coordinates across
  three separately timed file-labelled `MB365UV` captures while gross mounting
  and edge shadow patterns change.
- **Predictions:** a source-stable trace appears at corresponding coordinates
  in all three; a one-capture or processing artifact does not.
- **Distinguishing power:** yes for those narrow alternatives. It does not
  identify absorptance or ink and does not exclude static relief or fixed
  shadow.
- **Provenance:** high. Public 2014 TIFF capture products, object IDs, embedded
  TIFF `DateTime` values, byte hashes, and technical metadata are frozen. Release description:
  `https://manuscriptroadtrip.wordpress.com/2024/09/08/multispectral-imaging-and-the-voynich-manuscript/`.
- **Expected information gain:** medium. It removes a physical-state ambiguity
  upstream of palaeographic interpretation.
- **Acquisition cost:** low; approximately 600 MB and a deterministic render.
- **Outcome / kill:** both targets are three-capture-stable dark traces with
  mechanism unresolved. Absence from any source capture would have killed the
  processed-image observation as a repeatable physical lead.

## 2. Beinecke f1r pre-/early-post-chemical archival rotographs

- **Candidate:** exact pre-treatment JPEG
  `https://proto57.wordpress.com/wp-content/uploads/2013/07/f1r_before_chemicals_beinecke_2013.jpg`
  and early-post-treatment JPEG
  `https://proto57.wordpress.com/wp-content/uploads/2013/07/signature-early-after-chemicals.jpg`;
  provenance pages `https://proto57.wordpress.com/2013/07/14/new-look-at-the-de-tepencz-signature/`
  and `https://proto57.wordpress.com/2014/11/14/you-say-tspenencz-i-say-topenencz/`.
- **Currently ambiguous hypotheses:** a disputed f1r trace predates Voynich's
  chemical intervention, versus it was created/reconfigured by that treatment
  or later handling.
- **New observable:** the same physical trace in a claimed pre-treatment
  archival state, compared with early post-treatment and modern MSI.
- **Predictions:** an original trace must already exist in the pre-treatment
  image; a treatment-created trace must be absent or physically different.
- **Distinguishing power:** high for chronology if Beinecke authenticates the
  archival print and image geometry; zero lexical information by itself.
- **Provenance:** medium now (blog-mediated photographs of material reportedly
  found in the Beinecke Voynich Papers); high only after record-level Beinecke
  confirmation. Exact public pre-image metadata: 3024×4032, 1,464,669 bytes,
  SHA-256 `0b6d57368360b13e0d7696cb2ed036b96efc8c8098e058dc7619f40b254c9a0f`.
- **Expected information gain:** high for an intervention chronology, low for
  translation unless the recovered trace is independently readable and
  physically paired.
- **Acquisition cost:** low public download; medium institutional provenance
  request.
- **Kill:** inability to establish that the print is pre-treatment, or image
  quality insufficient to register the disputed trace.

## 3. Complete 2009 McCrone annexes and 2025 f1r/f1v XRF maps

- **Candidate:** an **unconfirmed-asset request** for sample-site micrographs
  and spectra named publicly as
  `McCronemicrographs (003).pdf`, `McCroneSpectraScans1-4.pdf`, and
  `McCroneSpectraScans 4-20.pdf`, plus the 2025 spatial XRF maps/report for f1r
  and f1v. Public records:
  `https://www.voynich.ninja/thread-4964.html` and
  `https://www.youtube.com/watch?v=nH28ltqYIyo`.
- **Currently ambiguous hypotheses:** adjacent plain/Voynich-style strokes are
  one material intervention, versus materially distinct interventions; stains
  obscure rather than create the underlying f1r marks.
- **New observable:** photographed sample identity and elemental/spectral
  response of explicitly localized strokes and altered parchment.
- **Predictions:** a common intervention predicts indistinguishable localized
  response within instrument precision; distinct interventions predict a
  reproducible material separation.  Either result still requires visible
  relational ownership before semantic transfer.
- **Distinguishing power:** high for material grouping, conditional for
  chronology, low for semantics alone.
- **Provenance:** potentially high if obtained from Yale/McCrone native annexes;
  current anonymous access is incomplete or registration-gated, so the asset is
  not evidence until delivered and bound.
- **Expected information gain:** high because it can collapse writer/layer
  alternatives rather than add text correlations.
- **Acquisition cost:** medium: request the annexes and final XRF package from
  Yale/project authors with exact sample-site metadata.
- **Kill:** sample sites do not touch the relevant strokes, lack photographs,
  or chemistry cannot distinguish them.

## 4. Native Rosettes f85v+f86r multispectral bands

- **Candidate:** an **unconfirmed-capture request** for the Rosettes capture
  reportedly made in 2014 and reproduced
  in the 2016 facsimile but not in the public Drive. Inventory source:
  `https://www.voynich.nu/gallery.html`.
- **Currently ambiguous hypotheses:** faint/paint-covered Rosettes structures
  are genuine authorial connections or writing states, versus show-through,
  offset, pigment response, or damage.
- **New observable:** raw aligned spectral bands with capture metadata for the
  complete foldout.
- **Predictions:** genuine underlying ink persists with a coherent spectral
  signature and non-mirrored geometry; show-through/offset predicts matching
  reverse/facing geometry; pigment/damage predicts different band response.
- **Distinguishing power:** potentially high for topology and layer order, but
  semantic value depends on revealing a forced readable legend or start/order
  marker.
- **Provenance:** currently low discovery provenance (a secondary gallery
  report with no institutional capture ID); potentially high only if a native
  file and metadata are supplied by Yale/Lazarus/RIT.
- **Expected information gain:** high because Rosettes has several otherwise
  unresolved relations and a single acquisition could create multiple new
  observables.
- **Acquisition cost:** medium institutional request; zero new manuscript
  exposure if existing files can be released.
- **Kill:** only processed illustrations survive, no native metadata, or no new
  connection/readable relation appears.

## 5. Chester Beatty T 402 f7v 28-section lunar wheel — killed screen

- **Candidate:** a screened but **killed** Chester Beatty T 402, f7v
  comparator, official object
  `https://viewer.cbl.ie/viewer/object/T_402/`, canvas
  `https://viewer.cbl.ie/viewer/api/v1/records/T_402/pages/16/canvas/`, and
  public Minorsky catalogue
  `https://chesterbeatty.ie/assets/uploads/2018/11/Turkish-Manuscripts-and-Miniatures_Part1.pdf`.
- **Currently ambiguous hypotheses:** Voynich 28-slot systems encode a
  physically ordered astronomical/calendar state, versus another cyclic or
  nonsemantic register whose orientation is freely permutable.
- **New observable:** a source-only diplomatic 28-row table fixing day,
  direction/start, owned inscription, and moonrise-hour/phase value in a
  readable near-contemporary wheel.
- **Predictions:** a topology-matched system predicts transfer only after start,
  direction, and long/short slot class are fixed; a generic 28-count analogy
  fails those constraints.
- **Distinguishing power:** presently insufficient. T 402 has a genuine
  28-wedge wheel, but no public 28-row human transcription was found, its
  uniform wedges may be non-isomorphic to a Voynich alternating 14+14
  structure, and f69v has no author-visible start/direction. A readable source
  origin therefore would not stop a free cross-manuscript rotation/reflection.
- **Provenance:** high: official IIIF and institutional catalogue; full image
  4302×6240, SHA-256
  `8abc1751a1c27d69d84a0b3067aef9950e8a422ab6462b824e609c2c755908dd`.
- **Expected information gain:** zero for current Voynich alignment because the
  target-side phase is free; medium document-practice value only after a
  qualified source-only transcription.
- **Acquisition cost:** medium specialist diplomacy, low image access.
- **Kill:** the current candidate is killed as a Voynich alignment unless an
  independent target start/direction is first found; it is also killed if the
  target's alternating physical slot class is mandatory and absent from T 402.

## Constraint from the executed acquisition

The new observation has the required adversarial form:

```text
H_SOURCE_CAPTURE_STABLE_TRACE           -> same trace in all three source captures
H_SINGLE_CAPTURE_OR_PROCESSING_ARTIFACT -> absent/inconsistent in at least one
observed                                -> same trace at corresponding coordinates
```

Thus only the single-capture/transient and processed-composite-only alternatives
are rejected. The visible capture-specific mounting/edge shadows are also not a
complete explanation of the target traces. Static relief, fixed shadow,
fluorescence response, stain, and ink remain open. The next acquisition must
attack chemistry, chronology, or authenticated illumination geometry; another
text model would not use this new information.

## Public physical-layer inventory by modality

This compact inventory distinguishes physical data layers from websites.  An
item marked unavailable is an acquisition target, not evidence already used.

| folio / object | institution or source | modality | raw or processed | public state (2026-08-13) | already used in VManus? | new physical information |
|---|---|---|---|---|---|---|
| Complete MS 408 | Yale Beinecke | ordinary-light IIIF JPEG | processed 8-bit derivative | public, 213 canvases | yes | no new layer |
| f1r, f8r, f17r, f26r, f47r, f70v1, f71r, f93r, f102v1, f116v | Lazarus Project / RIT | multispectral bands labelled 365–940 nm; some transmission | public 16-bit TIFF capture products | public Drive | only the six f17r/f116v MB365UV bodies used by EBA001; other bodies unconsumed | yes, band-specific response and repeat-capture evidence; lamp geometry not documented here |
| same ten folios | Lazarus Project / RIT | pseudocolour/PCA/MNF-style displays | processed JPEGs | public Drive | yes, prior MSI worth screens | no additional raw layer beyond the above |
| f1r before treatment | Beinecke Voynich Papers via Rich SantaColoma | historical rotograph, likely orthochromatic | derivative handheld JPEG of archival print | public, record-level catalogue provenance not yet confirmed | no visual pass | yes, pre-treatment chronology |
| f1r early after treatment | Beinecke Voynich Papers via Rich SantaColoma | historical ordinary-light print | derivative rephotographed crop | public, record-level catalogue provenance not yet confirmed | no visual pass | yes as chronological comparison |
| about twenty McCrone sample sites | Yale / McCrone Associates | photomicrographs and instrument spectra | analytical annex PDFs | named in public forum; anonymous outbound file link unavailable | no | yes, localized composition if sample photographs bind sites |
| f1r/f1v | Yale / 2025 materiality project | spatial XRF elemental maps | processed maps plus underlying spectra/report | lecture-visible; final package not public | no | yes, elemental distribution and chemical-treatment boundary |
| f85v+f86r Rosettes | Yale / Lazarus / RIT | multispectral capture | native status unknown; one reproduction reported | capture reported, public native file not located | no | yes, foldout layer/topology evidence |
| selected 2009 areas including reported f1r/f17r views | Yale / McCrone-related publicity | UV/IR photography | original status unknown | omitted originals not located | no | potentially, but provenance insufficient |
| complete manuscript | early NYPL/Voynich photostat set | historical ordinary-light/photostat | archival prints | reported restricted/uncatalogued, not downloadable | no systematic pass | yes, earlier physical states and cropping |
