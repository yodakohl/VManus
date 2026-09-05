# Calibration annotation visual review

Status: coordinates selected independently from RGB source inspection; no classifier outputs consulted.

Annotator: `visual_A`. Scope: twelve fixed calibration tiles from f76r and f77r in `TILES.json`, four ink and four paper centerpixels per tile (96 labels). Coordinates are native tile-local integer x/y values. The image center represented by an integer coordinate occupies its corresponding native pixel; the display uses four display pixels per native pixel and a 48-pixel outside margin.

I directly inspected all twelve unchanged RGB coordinate plates at 4x nearest-neighbor magnification. I selected clear centers of main-text strokes and nearby visibly blank parchment, including ordinary visible background texture. I did not inspect classifier features, calculate brightness/threshold statistics, or access held annotation files. The page sources had previously been visually admitted; no extra page was accessed.

I then rendered and directly inspected all twelve coordinate overlays, using hollow rings that leave the selected center visible. Five initially estimated coordinates were moved after this visual QC, before scoring; the exact changes appear below. This is annotation-coordinate correction, not a classifier-informed selection. A separate reviewer must still inspect the final overlays before scoring.

Labels concern selected unequivocal centerpixels only. They do not label an entire 3x3 neighborhood, recover faded ink or stroke edges, estimate image-wide mask performance, or validate pen-state measurement. The four ink points in each tile span multiple visually separate glyph shapes. The paper points were chosen in the same local writing field. No nominal selected point was excluded for classifier behavior; uncertain visual regions were avoided as described below. Every tile had capacity for the prescribed eight clear centerpixels.

| Tile | Visual uncertainty exclusions and coordinate QC |
|---|---|
| f76r_B1L | Avoided thin upper-left loops, bottom-edge traces and mixed stroke boundaries; selected broad interiors across three rows. |
| f76r_B1R | Avoided upper-right faint diagonal trace, small central speck and uncertain stroke margins; retained nearby textured paper. |
| f76r_B2L | Avoided clipped edge marks and the narrow descending tips; selected broad loops and upright portions, with local textured paper. |
| f76r_B2R | Avoided faint descending trace near upper middle and thin left/bottom hook margins; no uncertain-paper points selected. Coordinate-overlay QC moved I3 from(136,110) to(138,110) into the upright interior and I4 from(92,175) to(86,174) away from the narrow rightward tip. |
| f76r_B3L | Avoided tiny edge-clipped marks, long narrow descending stroke and weak inter-glyph joins; labels describe only unequivocal centers. Coordinate-overlay QC moved I2 from(90,95) to(85,95), moving out of the gap between uprights into the left stroke. |
| f76r_B3R | Avoided thin descending upper-right connector, uncertain bottom-edge joins and narrow loop edges. Coordinate-overlay QC moved I2 from(104,42) to(102,42), moving from the upright margin into its interior. |
| f77r_B1L | Avoided weak upper loop, narrow diagonal continuation and clipped lower glyphs; parchment texture remains in selected paper pixels. |
| f77r_B1R | Avoided thin diagonal connectors and uncertain rightmost clipped stroke; spread core labels across separate glyphs and rows. Coordinate-overlay QC moved I1 from(34,58) to(29,59), moving from the loop opening into its left stroke. |
| f77r_B2L | Avoided thin long vertical descenders and clipped top/bottom forms; selected centers of four distinct main-text shapes. |
| f77r_B2R | Avoided faint descending tail near upper right and thin diagonal middle-lower connector; paper labels are away from ambiguous margins. |
| f77r_B3L | Avoided hairline descenders and the crossing of two thin lower-left trajectories; selected broad main-text interiors. |
| f77r_B3R | Avoided faint upper-right descending tail, isolated lower-middle short mark and thin lower hooks; paper examples include visible texture. |

No uncertain candidate inventory with individually proposed coordinates preceded the clear-point selection; therefore the regional exclusions above are the actual visual record, not a retrospective list of rejected scored samples. These manually selected obvious points are a restricted prerequisite assay, not a random sample of parchment or writing.
