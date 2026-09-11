# Native source artifacts

IMAGE_RECEIPT.json binds the official full JPEG URL, dimensions and hash. Download that unchanged URL to runtime/f106v.jpg to repeat pixel checks. A_CONTEXT.png and A_FULL_PARAGRAPH.png are source-native pixel crops; JSON receipts give coordinates. OBSERVER_B_crop.png is a byte-identical copy of the independently frozen runtime crop referenced in observer B's packet; that original packet is unchanged. Reproduction may copy it back to runtime/OBSERVER_B_crop.png. No enhancement or generated strokes.

Run src/run.py to reconcile the frozen17-group packets, then src/validate.py. These programs check source/packaging and the registered decision, not palaeographic truth. Credit: Beinecke Rare Book and Manuscript Library, Yale University, MS408, f106v.
