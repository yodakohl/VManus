from pathlib import Path
import argparse
import hashlib
import json
from PIL import Image

parser = argparse.ArgumentParser(description="Reproduce exact admitted f82r analytical crops; no download or enhancement.")
parser.add_argument("image", type=Path, help="Existing admitted JPEG matching SOURCE.json")
args = parser.parse_args()
root = Path(__file__).resolve().parent
receipt = json.loads((root / "SOURCE.json").read_text())
raw = args.image.read_bytes()
assert hashlib.sha256(raw).hexdigest() == receipt["source"]["sha256"]
image = Image.open(args.image)
assert image.size == (receipt["source"]["width"], receipt["source"]["height"])
for crop in receipt["crops"]:
    result = image.crop(tuple(crop["box"]))
    result.save(root / crop["file"])
    assert result.size == (crop["width"], crop["height"])
print("Exact crops regenerated; no visual judgment or meaning validated.")
