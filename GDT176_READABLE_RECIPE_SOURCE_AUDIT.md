# GDT176 source audit — CoReMA semantic recipe roles

The official CoReMA API documents three TEI/XML levels: a hyperdiplomatic
collection transcription, a semantically annotated collection, and derived
single-recipe records.  It specifically defines annotations including
`ingredient`, `tool`, `instruction`, `opener`, and `closer`.  Source API:
<https://gams.uni-graz.at/archive/objects/context:corema/methods/sdef:Context/get?mode=api>.
Semantic model:
<https://gams.uni-graz.at/o:corema.semanticdec>.

CoReMA describes the annotation as a basis for comparing recipe texts across
languages.  The project supplies TEI sources directly and licenses the text
under CC BY 4.0; facsimiles have separate licenses and are not downloaded here.

The frozen recipe-index endpoint is:
<https://gams.uni-graz.at/archive/objects/query:corema.recipeindex/datastreams/RESULT/content>.
It contained 4,252 rows at freeze time.  The exact hash and byte count are in
`gdt176_source_freeze.json`.

The objective source-only rule retained six collection-level annotated TEI
objects.  Their identifiers, public URLs, manuscript date statements, exact
byte hashes, recipe counts, and semantic-tag counts are recorded in
`gdt176_corema_collection_manifest.tsv`.

This source freeze is not a Voynich result.  It authorizes a held-collection
instrument calibration and supplies no Voynich role, lexeme, meaning,
language, plaintext, or translation.  No Voynich table and no f84r row was
opened by the freezer.
