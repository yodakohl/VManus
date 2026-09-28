# GDT1063 method — informed visual exploration

This dossier follows [GDT1062](../gdt1062_schechter_plant_label_source_alignment/REPORT.md)
and the [exposure declaration](PREREGISTRATION.md). It is **not** a blind or
prospectively scored image test. The public decoder's visual descriptions and
three current-turn Voynich images had already been seen before the question was
registered. The four examined pages are the complete intersection of the
GDT1062 table with known image admissions: f2v (GDT623), f9v (GDT844), f11r
and f24v (GDT791). f2v/f29v are read from the already published GDT1059
visual decision; the other three current-turn images were existing cached
copies of admitted canvases. f84/f84r and reserves remain closed.

`src/VISUAL_RECORD.tsv` records all four visual assessments. The botanical
comparators were checked against these primary botanical descriptions:
[Viola tricolor, Flora of North America](https://efloras.org/florataxon.aspx?flora_id=1&taxon_id=250100968),
[Centaurea, RHS](https://www.rhs.org.uk/plants/328403/centaurea-jacea-var-nemoralis/details),
[Tilia, RHS](https://www.rhs.org.uk/plants/18225/tilia-cordata/details),
[Conium, Kew](https://powo.science.kew.org/taxon/urn%3Alsid%3Aipni.org%3Anames%3A840668-1/general-information),
and [Borago, RHS](https://www.rhs.org.uk/plants/borage?type=0). Historical
Voynich image assessment also independently lists f9v as a likely pansy or
violet in [Zandbergen's quire 2 notes](https://mail.voynich.nu/q02/index.html).
The [official f9v canvas](https://collections.library.yale.edu/iiif/2/1006093/full/1600,/0/default.jpg)
is the one previously admitted by GDT844. Prior local f11r morphology is in
V70's ten-page visual inventory; f24v's earlier image metadata are in GDT404.

`src/run.py` joins existing GDT1062 position results, the published GDT1059
Herbal-A head census and the guarded `words profile fochor`; it writes a
compact structural artifact. `src/validate.py` checks those joins and the
four-row visual-record scope. It **cannot validate human botanical likeness**;
the source images and botanical descriptions must be judged directly. No
new decoder, glyph mapping or source transcription rule is built.
