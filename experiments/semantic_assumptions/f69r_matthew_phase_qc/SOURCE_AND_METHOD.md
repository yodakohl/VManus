# f69r / Matthew Paris 12-of-16 phase QC

Date: 2026-08-09

This is a post-hoc human geometry quality-control audit, not a lexical target
test. It uses no OCR, automated vision, image embedding, or machine-generated
caption.

Frozen descriptive inputs:

- The human f69r catalogue and direct scan inspection give four unpainted
  cardinal axes, four green diagonal spokes, and eight blue spokes flanking
  the cardinal axes.
- British Library Cotton MS Nero D I ff.185r-v are catalogued as wind
  diagrams. The reproduced Matthew Paris construction places four principal
  directions and eight collateral positions in a sixteen-point frame, leaving
  the four diagonals unused.

For a schematic clockwise sixteen-position coordinate with North = 0:

- f69r blank = `{0,4,8,12}`, green = `{2,6,10,14}`, blue = all odd positions;
- Matthew principal = `{0,4,8,12}`, collateral = all odd positions, unused =
  `{2,6,10,14}`.

The only calculation enumerates all 32 rotations/reflections and asks how many
map Matthew `principal/collateral/unused` to f69r
`green/blue/blank`. The expected answer is eight. Consequently the class
layout is exact after a 45-degree phase change but cannot choose a start,
handedness, outer-text ownership, or direction name.

Sources:

- https://www.voynich.nu/q10/index.html#f69r
- https://www.voynich.com/folios/color/069r.jpg
- https://searcharchives.bl.uk/catalog/040-001102706
- https://commons.wikimedia.org/wiki/File:Matthew_Paris_12-to-16-wind_compass.jpg
