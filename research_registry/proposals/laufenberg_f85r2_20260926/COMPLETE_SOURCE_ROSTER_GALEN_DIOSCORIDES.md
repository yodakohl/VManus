# Complete-source availability: Galen and Dioscorides, 2026-09-27

Two distinct complete-work editions are concretely available. Galen was newly
downloaded; Dioscorides was already cached and has now been inspected as a whole
edition. This is source acquisition/qualification, not a manuscript finding,
concept-frequency result or independent semantic confirmation. The third-work
decision belongs to root's separate roster assessment.

| Work | Actual readable input and boundary | Provenance and limits |
|---|---|---|
| Galen, *On the Natural Faculties* | Complete Brock1916 edition: English Books I.1–17, II.1–9 and III.1–15, followed by the Greek text and a Latin-script transliteration. All41 English chapter anchors, three Greek book markers and the ebook end marker are present. | [Project Gutenberg43383](https://www.gutenberg.org/ebooks/43383), translator Arthur John Brock; London: Heinemann/New York: Putnam. The preface identifies the Greek basis as KühnII as edited by Helmreich1893, with modifications. The catalog states public domain in the USA; the file retains Gutenberg's terms. |
| Dioscorides, *De materia medica* | Complete five-book Wellmann digital edition in polytonic Greek, with prefatory material, critical apparatus and the closing address to Areios. Four main-text gap markers and two apparatus gap markers remain explicitly present. | [Scaife/Perseus edition](https://atlas.perseus.tufts.edu/library/urn:cts:greekLit:tlg0656.tlg001.1st1K-grc1/) and [OpenGreekAndLatin's source file](https://github.com/OpenGreekAndLatin/First1KGreek/blob/master/data/tlg0656/tlg001/tlg0656.tlg001.1st1K-grc1.xml). Harvard College Library digital publication2018; Wellmann's three printed volumes are dated1907/1906/1914 in the TEI header. The digital encoding explicitly carries CC BY-SA4.0. |

Galen's HTML was fetched successfully from the catalog's actual reading link:
[complete HTML](https://www.gutenberg.org/cache/epub/43383/pg43383-images.html).
It contains1,258,731 bytes, SHA256
`d234a983f9c363828a8c71b9b7ae68569548c72cfe2b2691ad5c0409d3609590`.
The filename says “images”, but only HTML bytes were fetched; no images or OCR.
The old102,400-byte `galen3_frame_source.html` was not accepted as a complete
work. Previous Galen excerpts remain prior project exposure.

Dioscorides contains4,424,582 bytes, SHA256
`e2a2175c5ca1c1a2313c5816bc79c7fa1c9103766fcad193356d0c13ce6746bc`.
This exactly matches the existing cache and
[GDT963's provenance](../../../experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE_ORIGIN.json).
No new Dioscorides witness or download is claimed. Its chapter markup contains
nested chapters, duplicate identifiers and numbering irregularities; a direct
children-only extraction would lose text. Main-text gaps have no stated extent.
Whole-work coverage therefore does **not** mean a gap-free, newly collated text.
The file is useful as a qualified complete edition; suitability for a later
strict exhaustive annotation remains a separate decision.

Both are ancient Greek medical works represented by modern editions, rather
than representative fifteenth-century vernacular samples. Galen is an extended
physiological argument; Dioscorides is pharmacological materia medica. Their
distinct authors/work identities prevent counting them as duplicate copies,
but shared medical traditions and possible later borrowing prevent any automatic
claim of statistical independence.

Galen's English, Greek and transliteration count as **one work**. Scaife,
GitHub, cached XML and earlier Dioscorides excerpts also count as **one work**.
Do not concatenate translations, transliteration, apparatus, introductions or
indexes into a future concept-count denominator. A common-language or explicit
cross-language annotation contract is still missing; no such counts were made.

[The receipt](COMPLETE_SOURCE_ROSTER_GALEN_DIOSCORIDES.json) records complete
boundaries, acquisition metadata, hashes, licenses, known gaps and relative
cache paths. Raw files reside only in the self-ignored
`external_cache/complete_source_roster/` folder and are not publication payload.
No Voynich content, image, reserve, contact or new decoder was used. These two
sources alone neither establish a three-work roster nor reopen IDEA607.
