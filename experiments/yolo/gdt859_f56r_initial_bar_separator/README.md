# GDT859 f56r initial upper bar

Completed post-discovery native/source audit. See REPORT and METHOD.

For reproduction, the exact original JPEG must exist at
`docs/visual_overview/runtime/1006184.jpg` (runtime cache, not published).
Download source: https://collections.library.yale.edu/iiif/2/1006184/full/full/0/default.jpg
Validator checks SHA256 d81272aa14671b1b6672fe7556c15ac177c734685d9ef7448237a2cc08dc899d,
2375075 bytes and dimensions2793×3707; missing or changed bytes fail.

Result: native A/B both judge AB connected and BC disconnected. All three
readings retain a definite separator between their first two stored groups.
These are separate descriptions; software establishes no ordinal alignment.
Complete lines, including @167/@168 entities, are in artifacts/SOURCE_LINES.json.

Reproduction:

```
python3 experiments/yolo/gdt859_f56r_initial_bar_separator/src/run.py
python3 experiments/yolo/gdt859_f56r_initial_bar_separator/src/validate.py
python3 experiments/yolo/gdt859_f56r_initial_bar_separator/src/run.py --check
python3 experiments/yolo/gdt859_f56r_initial_bar_separator/src/bind.py
```

Native observations are recorded inputs, not reproduced software vision.
