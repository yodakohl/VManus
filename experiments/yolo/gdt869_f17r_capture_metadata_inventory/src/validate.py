#!/usr/bin/env python3
"""Independent TIFF directory metadata validator. No raster decoder is used."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct

EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[2]
GPS = 34853
WIDTHS = {1:1, 2:1, 3:2, 4:4, 5:8, 6:1, 7:1, 8:2, 9:4, 10:8, 11:4, 12:8, 13:4, 16:8, 17:8, 18:8}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def parse_directories(stream, length, pointers=(330, 34665, 40965)):
    """Read TIFF headers, directory entries and non-GPS metadata values only.

    Raster offsets are never followed. Directory/payload bounds are checked.
    Internal metadata bytes are returned to the caller, never printed here.
    """
    def take(offset, count):
        require(0 <= offset <= length and 0 <= count <= length-offset, 'TIFF metadata bounds')
        stream.seek(offset)
        data = stream.read(count)
        require(len(data) == count, 'truncated TIFF metadata')
        return data
    marker = take(0, 2)
    require(marker in (b'II', b'MM'), 'TIFF byte order')
    endian = '<' if marker == b'II' else '>'
    def number(data, kind):
        return struct.unpack(endian + kind, data)[0]
    magic = number(take(2, 2), 'H')
    require(magic in (42, 43), 'TIFF magic')
    big = magic == 43
    if big:
        require(number(take(4, 2), 'H') == 8 and number(take(6, 2), 'H') == 0, 'BigTIFF header')
        start = number(take(8, 8), 'Q'); cell, count_size, entry_size = 8, 8, 20
    else:
        start = number(take(4, 4), 'I'); cell, count_size, entry_size = 4, 2, 12
    result, queue, visited = [], [(start, 'IFD0')], set()
    while queue:
        offset, label = queue.pop(0)
        if not offset:
            continue
        require(offset not in visited, 'cyclic/shared TIFF directory pointer')
        visited.add(offset)
        require(len(visited) <= 128, 'too many TIFF directories')
        n = number(take(offset, count_size), 'Q' if big else 'H')
        require(n <= 10000, 'too many TIFF tags')
        take(offset + count_size, n * entry_size + cell)
        entries = []
        for i in range(n):
            position = offset + count_size + i * entry_size
            entry = take(position, entry_size)
            tag, typ = struct.unpack(endian + 'HH', entry[:4])
            count = number(entry[4:12] if big else entry[4:8], 'Q' if big else 'I')
            slot = entry[-cell:]
            require(typ in WIDTHS, 'unsupported TIFF field type')
            size = count * WIDTHS[typ]
            require(size <= length, 'TIFF tag payload exceeds file')
            data_offset = position + entry_size-cell if size <= cell else number(slot, 'Q' if big else 'I')
            payload = None if tag == GPS else take(data_offset, size)
            row = {'ifd': label, 'ifd_offset': offset, 'tag': tag, 'type': typ, 'count': count,
                   'payload_bytes': size, 'inline': size <= cell, 'payload': payload, 'data_offset': data_offset}
            entries.append(row)
            if tag in pointers:
                require(typ in (3, 4, 13, 16, 18), 'non-integer IFD pointer')
                width = WIDTHS[typ]; fmt = {2:'H', 4:'I', 8:'Q'}[width]
                for j in range(count):
                    dest = number(payload[j*width:(j+1)*width], fmt)
                    if dest:
                        queue.append((dest, label + '/' + str(tag) + '[' + str(j) + ']'))
        result.extend(entries)
        nxt = number(take(offset + count_size + n * entry_size, cell), 'Q' if big else 'I')
        if nxt:
            queue.append((nxt, label + '/next'))
    return {'byte_order': marker.decode(), 'big_tiff': big, 'entries': result, 'ifd_count': len(visited)}


def numeric_values(row, byte_order):
    formats = {1:'B', 3:'H', 4:'I', 6:'b', 8:'h', 9:'i', 11:'f', 12:'d', 13:'I', 16:'Q', 17:'q', 18:'Q'}
    require(row['type'] in formats and row['payload'] is not None, 'numeric metadata type')
    return list(struct.unpack(('<' if byte_order == 'II' else '>') + formats[row['type']]*row['count'], row['payload']))


def controls():
    # Classic little-endian, real TIFF directory; GPS points outside the fixture.
    # Successful parsing proves the GPS pointer was not followed.
    tags = [(256,4,1,7), (257,4,1,9), (258,3,1,16), (277,3,1,1), (34853,4,1,999999)]
    content = b'II' + struct.pack('<HIH',42,8,len(tags))
    for tag, typ, count, value in tags:
        content += struct.pack('<HHI',tag,typ,count) + (struct.pack('<H',value)+b'\0\0' if typ==3 else struct.pack('<I',value))
    content += struct.pack('<I',0)
    parsed = parse_directories(io.BytesIO(content), len(content))
    require(parsed['ifd_count'] == 1 and len(parsed['entries']) == 5, 'synthetic TIFF inventory')
    by = {r['tag']:r for r in parsed['entries']}
    require(numeric_values(by[256], 'II') == [7] and numeric_values(by[257], 'II') == [9], 'synthetic dimensions')
    require(by[GPS]['payload'] is None, 'GPS payload excluded')
    # Big-endian classic header exercises a different byte order.
    be = b'MM' + struct.pack('>HIH',42,8,1) + struct.pack('>HHII',256,4,1,11) + struct.pack('>I',0)
    require(numeric_values(parse_directories(io.BytesIO(be),len(be))['entries'][0], 'MM') == [11], 'big-endian fixture')
    try:
        parse_directories(io.BytesIO(content[:-3]), len(content)-3)
    except ValueError:
        pass
    else:
        raise AssertionError('truncated TIFF accepted')
    public, dimensions = inventory_scan(io.BytesIO(content),len(content))
    require(dimensions[256]==[7] and dimensions[257]==[9] and next(t for t in public['tags'] if t['tag_id']==GPS)['status']=='SKIPPED_GPS', 'actual scanner synthetic fixture')
    require(inventory_scan(io.BytesIO(be),len(be))[1][256]==[11], 'actual scanner big-endian fixture')
    nested = bytearray(512)
    nested[:8] = b'II' + struct.pack('<HI',42,8)
    fixture_tags = [(256,4,1,7),(257,4,1,9),(258,3,1,16),(277,3,1,1),
                    (273,4,1,400),(279,4,1,8),(34665,4,1,160),(34853,4,1,450),(270,2,8,400)]
    struct.pack_into('<H',nested,8,len(fixture_tags))
    for i, values in enumerate(fixture_tags):
        struct.pack_into('<HHII',nested,10+i*12,*values)
    struct.pack_into('<H',nested,160,1)
    struct.pack_into('<HHI',nested,162,65000,7,4)
    nested[170:174]=b'ABCD'
    nested[400:408]=b'RASTER!!'; nested[450:458]=b'GPS!!!!!'
    inv,_ = inventory_scan(io.BytesIO(nested),len(nested))
    require(inv['ifd_count']==2 and inv['root_ifd_count']==1 and inv['raster_ranges_count']==1, 'nested raster directory fixture')
    require(next(t for t in inv['tags'] if t['tag_id']==270)['status']=='SKIPPED_RASTER_OVERLAP', 'raster-pointing metadata must not be read')
    require(next(t for t in inv['tags'] if t['tag_id']==65000)['opaque_payload'] is True, 'opaque private descriptor')
    print(json.dumps({'status':'CONTROLS_PASS','source':'SYNTHETIC_TIFF_METADATA_ONLY','pixel_decode':False},sort_keys=True))


TYPE_NAMES = dict(zip([1,2,3,4,5,6,7,8,9,10,11,12,13,16,17,18], ['BYTE','ASCII','SHORT','LONG','RATIONAL','SBYTE','UNDEFINED','SSHORT','SLONG','SRATIONAL','FLOAT','DOUBLE','IFD','LONG8','SLONG8','IFD8']))
POINTER_NAMES = {330:'SubIFD',34665:'ExifIFD',40965:'InteropIFD'}
CAPS = {'max_payload_bytes':1048576,'max_total_payload_bytes':8388608,'max_ifds':128,'max_entries':10000}


def inventory_scan(stream, length):
    reads, raster, visited, entries, blocked = [], [], set(), [], []
    roots, payload_used = 0, 0
    def overlaps(start, size, ranges):
        return any(start < stop and start + size > begin for begin, stop in ranges)
    def take(offset, count):
        require(0 <= offset <= length and 0 <= count <= length-offset, 'metadata bounds')
        require(not overlaps(offset,count,raster), 'metadata overlaps raster')
        stream.seek(offset); value=stream.read(count)
        require(len(value)==count, 'metadata truncated')
        reads.append((offset,offset+count))
        return value
    header=take(0,8)
    require(header[:2] in (b'II',b'MM'), 'TIFF byte order')
    order='<' if header[:2]==b'II' else '>'
    magic, initial=struct.unpack(order+'HI',header[2:])
    require(magic==42, 'only classic TIFF permitted')
    def integers(raw, typ):
        code={3:'H',4:'I',13:'I',16:'Q',18:'Q'}[typ]
        return struct.unpack(order+code*(len(raw)//WIDTHS[typ]),raw)
    def payload(entry):
        nonlocal payload_used
        d=entry['descriptor']; n=d['payload_size']
        if d['tag_id']==GPS:return None,'SKIPPED_GPS'
        if n is None:return None,'OPAQUE_TYPE'
        if n>CAPS['max_payload_bytes'] or payload_used+n>CAPS['max_total_payload_bytes']:return None,'SKIPPED_LIMIT'
        if n<=4:value=entry['cell'][:n]
        else:
            if overlaps(entry['offset'],n,raster):return None,'SKIPPED_RASTER_OVERLAP'
            value=take(entry['offset'],n)
        payload_used+=n
        return value,'READ'
    def directory(offset,name,is_root):
        nonlocal roots
        if offset==0:return
        require(offset not in visited and len(visited)<CAPS['max_ifds'], 'duplicate/cyclic/excess IFD')
        visited.add(offset); roots+=int(is_root)
        n=struct.unpack(order+'H',take(offset,2))[0]
        require(len(entries)+n<=CAPS['max_entries'], 'entry limit')
        raw=take(offset+2,n*12+4); local=[]
        for i in range(n):
            cell=raw[12*i:12*i+12]; tag,typ,count=struct.unpack(order+'HHI',cell[:8])
            d={'namespace':name,'ifd_offset':offset,'entry_index':i,'tag_id':tag,'type_id':typ,
               'type_name':TYPE_NAMES.get(typ,'UNKNOWN'),'count':count,'payload_size':count*WIDTHS[typ] if typ in WIDTHS else None}
            local.append({'descriptor':d,'cell':cell[8:],'offset':struct.unpack(order+'I',cell[8:])[0]})
        require(len({e['descriptor']['tag_id'] for e in local})==n,'duplicate IFD tag')
        entries.extend(local); structural={}
        for e in local:
            d=e['descriptor']
            if d['tag_id'] in (273,279,324,325,513,514):
                raw_value,status=payload(e)
                require(status=='READ' and d['type_id'] in (3,4,13,16,18),'unreadable raster structure')
                e['cached']=raw_value; structural[d['tag_id']]=integers(raw_value,d['type_id'])
        for offset_tag,count_tag in ((273,279),(324,325),(513,514)):
            if offset_tag in structural or count_tag in structural:
                require(offset_tag in structural and count_tag in structural and len(structural[offset_tag])==len(structural[count_tag]),'unpaired raster ranges')
                for begin,size in zip(structural[offset_tag],structural[count_tag]):
                    require(begin+size<=length and not overlaps(begin,size,reads),'invalid raster range or already read raster')
                    raster.append((begin,begin+size))
        for e in local:
            d=e['descriptor']; tag=d['tag_id']
            if tag in POINTER_NAMES:
                raw_value,status=payload(e)
                if status!='READ' or d['type_id'] not in (4,13,16,18):
                    blocked.append({'namespace':name,'tag_id':tag,'reason':'UNTRAVERSED_IFD_POINTER'})
                else:
                    e['cached']=raw_value
                    for i,child in enumerate(integers(raw_value,d['type_id'])):
                        directory(child,name+'/'+POINTER_NAMES[tag]+'['+str(i)+']',False)
        nxt=struct.unpack(order+'I',raw[-4:])[0]
        if nxt:directory(nxt,name+'/next',is_root)
    directory(initial,'IFD0',True)
    tags=[]; dimensions={}
    for e in entries:
        d=dict(e['descriptor'])
        value,status=(e['cached'],'READ') if 'cached' in e else payload(e)
        d.update({'payload_sha256':hashlib.sha256(value).hexdigest() if value is not None else None,
                  'status':status,'opaque_payload':d['type_id']==7 or d['type_id'] not in WIDTHS or d['tag_id']>=32768 and d['tag_id'] not in POINTER_NAMES and d['tag_id']!=GPS})
        tags.append(d)
        if d['namespace']=='IFD0' and d['tag_id'] in (256,257,258,277):
            require(value is not None and d['type_id'] in (3,4,13,16,18),'geometry payload type')
            dimensions[d['tag_id']]=list(integers(value,d['type_id']))
    require(not any(overlaps(a,b-a,raster) for a,b in reads),'raster was read')
    return {'format':'CLASSIC_TIFF','byte_order':header[:2].decode(),'root_ifd_count':roots,'ifd_count':len(visited),
            'tags':tags,'raster_ranges_count':len(raster),'limits':CAPS,
            'opaque_or_skipped_metadata':bool(blocked) or any(t['opaque_payload'] or t['status'] not in ('READ','SKIPPED_GPS') for t in tags),
            'untraversed_pointers':blocked,'pixel_decoded':False,'raster_payload_read':False},dimensions


def validate():
    verify_lock(); spec=read(EXP/'src/SPEC.json')
    registered=spec['files']; names=[q['filename'] for q in registered]
    require(len(names)==len(set(names))==3,'exact three-file allowance')
    require(all(q['folio']=='f17r' and q['filename'].startswith('Voynich_17r+MB365UV_') and q['filename'].endswith('_F.tif') for q in registered),'f17r-only source scope')
    require(set(names)=={'Voynich_17r+MB365UV_007_F.tif','Voynich_17r+MB365UV_029_F.tif','Voynich_17r+MB365UV_037_F.tif'},'fixed three captures')
    expected=[]
    for q in registered:
        path=EXP/'runtime'/q['filename']
        require(path.stat().st_size==q['size'] and digest(path)==q['sha256'],'frozen original source identity')
        require(q['source_url']=='https://drive.usercontent.google.com/download?id='+q['file_id']+'&export=download&confirm=t','frozen original source URL')
        with path.open('rb') as stream: inventory,dimensions=inventory_scan(stream,q['size'])
        for tag,name in ((256,'width'),(257,'height'),(258,'bits'),(277,'samples')):
            require(dimensions[tag]==[spec['expected_tiff'][name]],'registered TIFF dimensions/bits/samples')
        require(inventory['root_ifd_count']==spec['expected_tiff']['pages'],'registered root IFD count')
        inventory.update({k:q[k] for k in ('filename','folio','file_id','sha256','size')})
        expected.append(inventory)
    require(read(EXP/'artifacts/INVENTORY.json')=={'files':expected,'pixel_decoded':False,'raster_payload_read':False},'independent exact metadata inventory parity')
    return {'status':'PASS','files':3,'tag_descriptors':sum(len(f['tags']) for f in expected),
            'source_hashes_and_dimensions_checked':True,'independent_binary_metadata_parse':True,
            'GPS_payload_read':False,'pixel_decode':False,'raster_payload_read':False,'private_values_published':False,
            'claim_ceiling':spec['claim_ceiling'],'limitation':'Software validates metadata descriptors and source bytes, not physical illumination, image content or the manual assessment.'}


def verify_lock():
    lock = read(EXP / 'src/PREREG_LOCK.json')
    require(isinstance(lock, dict) and bool(lock), 'empty preregistration lock')
    required = {str((EXP / p).relative_to(ROOT)) for p in ('METHOD.md','src/SPEC.json','src/run.py','src/validate.py')}
    require(required <= set(lock), 'incomplete executable lock')
    for name, expected in lock.items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), 'invalid locked path')
        require(digest(path) == expected, 'locked file digest mismatch')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--controls', action='store_true')
    parser.add_argument('--no-write', action='store_true')
    args = parser.parse_args()
    if args.controls:
        controls()
        return 0
    try:
        result = validate()
    except (ValueError, KeyError, OSError, TypeError, struct.error) as exc:
        result = {'status':'FAIL','reason':str(exc),'pixel_decode':False,'private_values_published':False}
    payload = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if not args.no_write:
        (EXP / 'artifacts/VALIDATION.json').write_text(payload)
    print(payload, end='')
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
