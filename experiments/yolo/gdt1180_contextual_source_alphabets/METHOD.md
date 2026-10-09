# Executable method

`src/codec.py` trains only declared source tables and implements the complete deterministic encoder/decoder. `src/run.py` verifies frozen hashes, renders every book, checks exact recipe roundtrips and applies inherited metrics. `src/validate.py` rereads persisted text, decodes using only public tables and text, rewrites it, independently counts words/glyphs and verifies decisions. Tables include all global units and every learned row; no plaintext-dependent external boundary metadata is supplied to the decoder.

Source license/provenance: CoReMA University of Graz CC-BY4.0 expanded recipe XML; hashes and origin in1177 projection and1159 SOURCE.json. These are historically exposed controls; complete means the pre-existing editorial projection criterion. No target raw text, images, sealed folios or reserved data are read.
