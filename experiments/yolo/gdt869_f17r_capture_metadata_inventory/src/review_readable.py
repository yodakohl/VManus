"""Post-extraction descriptive projection; not a changed preregistered test.

Reads only the ignored metadata output, never TIFF/raster bytes. Public values
are restricted to a spectral acquisition field and two literal lighting labels.
No vendor payload, host/path/camera identifier or unrelated IPTC field is emitted.
"""
import json,struct
from pathlib import Path
E=Path(__file__).resolve().parents[1]
source=json.loads((E/'runtime/PRIVATE_METADATA.json').read_text())
rows=[]
for f in source['files']:
    by={t['descriptor']['tag_id']:t for t in f['metadata']['tags']}
    spectral=by[34852]['value']['text'].strip()
    import re
    assert re.fullmatch(r'(\(MB365UV, (?:7\.450|10\.000)s, 100\.0w\)\s*){1,2}',spectral)
    vals=by[33723]['value']['values'];raw=struct.pack('<'+'I'*len(vals),*vals)
    position=0;caption=None;records=0
    while position+5<=len(raw) and raw[position]==28:
        record,dataset=raw[position+1:position+3]
        size=int.from_bytes(raw[position+3:position+5],'big')
        if size&32768 or position+5+size>len(raw):break
        value=raw[position+5:position+5+size]
        if (record,dataset)==(2,120):
            assert value==b'Main banks\nTransmissive\n'
            caption=['Main banks','Transmissive']
        records+=1;position+=5+size
    assert caption is not None
    rows.append(dict(filename=f['filename'],spectral_tag=34852,spectral_text=spectral,
                     iptc_tag=33723,iptc_record=2,iptc_dataset=120,caption_lines=caption,
                     parsed_iptc_records=records,iptc_trailing_bytes=len(raw)-position,
                     source_tag_hashes={str(t):by[t]['descriptor']['payload_sha256'] for t in (34852,33723)},
                     vendor_metadata_not_fully_decoded=[37407,37408]))
result=dict(status='READABLE_ACQUISITION_FIELDS_DESCRIBED',files=rows,
            post_extraction_projection=True,explicit_capture_direction_assignment=False,
            limitation='Same generic caption in all three captures; no assignment of entry to lamp direction. Vendor fields remain partly opaque. Repeated spectral entry does not establish two lamps.')
(E/'artifacts/READABLE_FIELDS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('Three privacy-restricted acquisition metadata descriptions written')
