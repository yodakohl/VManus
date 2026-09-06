"""Bounded classic-TIFF metadata inventory; no image library or raster decoding."""
import argparse,base64,hashlib,json,os,struct,urllib.request
from pathlib import Path
E=Path(__file__).resolve().parents[1]
TYPE_INFO={1:('BYTE',1),2:('ASCII',1),3:('SHORT',2),4:('LONG',4),5:('RATIONAL',8),6:('SBYTE',1),7:('UNDEFINED',1),8:('SSHORT',2),9:('SLONG',4),10:('SRATIONAL',8),11:('FLOAT',4),12:('DOUBLE',8),13:('IFD',4),16:('LONG8',8),17:('SLONG8',8),18:('IFD8',8)}
POINTERS={330:'SubIFD',34665:'ExifIFD',40965:'InteropIFD'}
GPS=34853
STRUCTURAL={273,279,324,325,513,514}
LIMITS=dict(max_payload_bytes=1048576,max_total_payload_bytes=8388608,max_ifds=128,max_entries=10000)
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n'
def write(p,x):p.parent.mkdir(exist_ok=True);p.write_text(enc(x))
def overlap(start,size,ranges):return any(start<b and start+size>a for a,b in ranges)
def decode(raw,t,order):
 if t==2:return dict(text=raw.rstrip(b'\0').decode('utf-8',errors='replace'),raw_base64=base64.b64encode(raw).decode())
 codes={1:'B',3:'H',4:'I',6:'b',8:'h',9:'i',11:'f',12:'d',13:'I',16:'Q',17:'q',18:'Q'}
 if t in codes:
  values=list(struct.unpack(order+codes[t]*(len(raw)//TYPE_INFO[t][1]),raw));return dict(values=[v if not isinstance(v,float) or __import__('math').isfinite(v) else repr(v) for v in values])
 if t in [5,10]:
  values=struct.unpack(order+('I' if t==5 else 'i')*(len(raw)//4),raw);return dict(rationals=[list(values[i:i+2]) for i in range(0,len(values),2)])
 return dict(raw_base64=base64.b64encode(raw).decode())
def parse_tiff(path):
 size=path.stat().st_size;reads=[];rasters=[];entries=[];directories=[];seen=set();payload_used=0;blocked=[]
 with path.open('rb') as f:
  def read_at(offset,n):
   if offset<0 or n<0 or offset+n>size:raise ValueError('TIFF metadata bounds violation')
   if overlap(offset,n,rasters):raise ValueError('Metadata structure overlaps declared raster')
   f.seek(offset);data=f.read(n)
   if len(data)!=n:raise ValueError('Short metadata read')
   reads.append((offset,n));return data
  header=read_at(0,8);byte_order=header[:2].decode('ascii');assert byte_order in ['II','MM'],'Unsupported TIFF byte order';order='<' if byte_order=='II' else '>';magic,first=struct.unpack(order+'HI',header[2:]);assert magic==42,'Only classic TIFF42 supported; BigTIFF is not silently parsed'
  def entry_payload(e,structural=False):
   nonlocal payload_used
   if e['tag_id']==GPS:return None,'SKIPPED_GPS'
   if e['payload_size'] is None:return None,'OPAQUE_TYPE'
   n=e['payload_size']
   if n>LIMITS['max_payload_bytes'] or payload_used+n>LIMITS['max_total_payload_bytes']:return None,'SKIPPED_LIMIT'
   if n<=4:data=e['_inline'][:n]
   else:
    offset=e['_value_offset']
    if overlap(offset,n,rasters):return None,'SKIPPED_RASTER_OVERLAP'
    data=read_at(offset,n)
   payload_used+=n;return data,'READ'
  def visit(offset,namespace,root_chain=False):
   if not offset:return
   if offset in seen:raise ValueError('Repeated or cyclic IFD pointer')
   if len(seen)>=LIMITS['max_ifds']:raise ValueError('IFD count limit')
   seen.add(offset);n=struct.unpack(order+'H',read_at(offset,2))[0]
   if len(entries)+n>LIMITS['max_entries']:raise ValueError('IFD entry count limit')
   directory=read_at(offset+2,n*12+4);local=[]
   for i in range(n):
    part=directory[i*12:i*12+12];tag,t,count=struct.unpack(order+'HHI',part[:8]);info=TYPE_INFO.get(t);e=dict(namespace=namespace,ifd_offset=offset,entry_index=i,tag_id=tag,type_id=t,type_name=info[0] if info else 'UNKNOWN',count=count,payload_size=count*info[1] if info else None,_inline=part[8:12],_value_offset=struct.unpack(order+'I',part[8:12])[0]);local.append(e)
   if len({e['tag_id'] for e in local})!=len(local):raise ValueError('Duplicate tag IDs within IFD')
   directories.append(dict(namespace=namespace,offset=offset,root_chain=root_chain,entries=n));entries.extend(local)
   # Read strip/tile offset arrays and lengths as metadata, never the referenced bytes.
   structural_values={}
   for e in local:
    if e['tag_id'] in STRUCTURAL:
     data,status=entry_payload(e,True)
     if status!='READ' or e['type_id'] not in [3,4,13,16,18]:raise ValueError('Cannot establish raster ranges from structural tags')
     structural_values[e['tag_id']]=decode(data,e['type_id'],order)['values'];e['_raw']=data
   for offsets,lengths in [(273,279),(324,325),(513,514)]:
    if offsets in structural_values or lengths in structural_values:
     if offsets not in structural_values or lengths not in structural_values or len(structural_values[offsets])!=len(structural_values[lengths]):raise ValueError('Incomplete raster-range pair')
     for start,length in zip(structural_values[offsets],structural_values[lengths]):
      if start<0 or length<0 or start+length>size:raise ValueError('Invalid raster range')
      if overlap(start,length,[(p,p+n) for p,n in reads]):raise ValueError('Previously read metadata overlaps declared raster')
      rasters.append((start,start+length))
   for e in local:
    if e['tag_id'] in POINTERS:
     data,status=entry_payload(e,True)
     if status!='READ' or e['type_id'] not in [4,13,16,18]:blocked.append(dict(namespace=namespace,tag_id=e['tag_id'],reason='UNTRAVERSED_IFD_POINTER'));continue
     e['_raw']=data
     for i,child in enumerate(decode(data,e['type_id'],order)['values']):visit(child,namespace+'/'+POINTERS[e['tag_id']]+'['+str(i)+']')
   nxt=struct.unpack(order+'I',directory[n*12:n*12+4])[0]
   if nxt:visit(nxt,namespace+'/next',root_chain)
  visit(first,'IFD0',True)
  public=[];private=[]
  for e in entries:
   if '_raw' in e:data,status=e['_raw'],'READ'
   else:data,status=entry_payload(e)
   d={k:v for k,v in e.items() if not k.startswith('_')};d.update(payload_sha256=hashlib.sha256(data).hexdigest() if data is not None else None,status=status,opaque_payload=e['type_id'] in [7] or e['type_id'] not in TYPE_INFO or e['tag_id']>=32768 and e['tag_id'] not in POINTERS and e['tag_id']!=GPS);public.append(d)
   private.append(dict(descriptor=d,value=decode(data,e['type_id'],order) if data is not None else None))
  metadata_only=not any(overlap(start,n,rasters) for start,n in reads);assert metadata_only
  out=dict(format='CLASSIC_TIFF',byte_order=byte_order,root_ifd_count=sum(d['root_chain'] for d in directories),ifd_count=len(directories),tags=public,raster_ranges_count=len(rasters),limits=LIMITS,opaque_or_skipped_metadata=bool(blocked) or any(d['opaque_payload'] or d['status'] not in ['READ','SKIPPED_GPS'] for d in public),untraversed_pointers=blocked,pixel_decoded=False,raster_payload_read=False)
  return out,dict(tags=private,directories=directories,raster_ranges=rasters,metadata_read_ranges=reads)
def controls():
 folder=E/'runtime';folder.mkdir(exist_ok=True);path=folder/'synthetic_metadata_only.tif';b=bytearray(512);b[:8]=b'II'+struct.pack('<HI',42,8)
 def ifd(offset,rows):
  struct.pack_into('<H',b,offset,len(rows))
  for i,(tag,t,count,value) in enumerate(rows):struct.pack_into('<HHI',b,offset+2+12*i,tag,t,count);b[offset+10+12*i:offset+14+12*i]=value if isinstance(value,bytes) else struct.pack('<I',value)
  struct.pack_into('<I',b,offset+2+12*len(rows),0)
 ifd(8,[(256,4,1,2),(257,4,1,2),(258,3,1,16),(277,3,1,1),(270,2,6,300),(273,4,1,400),(279,4,1,8),(34665,4,1,160),(34853,4,1,450),(330,4,1,260)])
 ifd(160,[(65000,7,4,b'ABCD'),(40965,4,1,220)]);ifd(220,[(1,2,4,b'R98\0')]);ifd(260,[(305,2,8,320)]);b[300:306]=b'hello\0';b[320:328]=b'fixture\0';b[400:408]=b'RASTER!!';b[450:458]=b'GPS!!!!!';path.write_bytes(b);pub,priv=parse_tiff(path);assert pub['ifd_count']==4 and pub['root_ifd_count']==1 and pub['raster_payload_read'] is False;assert any(t['tag_id']==65000 and t['opaque_payload'] for t in pub['tags']);assert next(t for t in pub['tags'] if t['tag_id']==34853)['status']=='SKIPPED_GPS';assert all(not overlap(start,n,[(400,408),(450,458)]) for start,n in priv['metadata_read_ranges']);assert any(t['value'] and t['value'].get('text')=='hello' for t in priv['tags']);return dict(status='PASS',classic_nested_ifd=True,ascii=True,opaque_tag=True,gps_values_not_read=True,raster_not_read=True)
def acquire(q):
 destination=E/'runtime'/q['filename'];destination.parent.mkdir(exist_ok=True)
 if not destination.exists():
  partial=destination.with_suffix(destination.suffix+'.partial');request=urllib.request.Request(q['source_url'],headers={'User-Agent':'VManus-GDT869/1.0'})
  with urllib.request.urlopen(request,timeout=90) as response:
   if not response.geturl().startswith('https://drive.usercontent.google.com/'):raise ValueError('Unexpected source redirect')
   with partial.open('xb') as target:
    count=0
    while block:=response.read(1048576):
     count+=len(block)
     if count>q['size']:raise ValueError('Download exceeds frozen source size')
     target.write(block)
  partial.replace(destination)
 digest=hashlib.sha256();count=0
 with destination.open('rb') as source:
  while block:=source.read(1048576):digest.update(block);count+=len(block)
 assert count==q['size'] and digest.hexdigest()==q['sha256'],'Frozen source identity mismatch';return destination

def main():
 p=argparse.ArgumentParser();p.add_argument('--controls',action='store_true');p.add_argument('--run',action='store_true');args=p.parse_args()
 if args.controls:result=controls();write(E/'artifacts/CONTROLS.json',result);print(enc(result));return
 if not args.run:p.error('Explicit --run required after public GO')
 s=json.loads((E/'src/SPEC.json').read_text());assert len(s['files'])==3 and all(q['folio']=='f17r' and '17r+MB365UV_' in q['filename'] for q in s['files']);assert len({q['filename'] for q in s['files']})==3;public=[];private=[]
 for q in s['files']:
  path=acquire(q);pub,priv=parse_tiff(path);pub.update({k:q[k] for k in ['filename','folio','file_id','sha256','size']});private.append(dict(filename=q['filename'],metadata=priv));public.append(pub)
  values={t['descriptor']['tag_id']:t['value'] for t in priv['tags'] if t['descriptor']['namespace']=='IFD0'}
  for tag,key in [(256,'width'),(257,'height'),(258,'bits'),(277,'samples')]:assert values[tag]['values']==[s['expected_tiff'][key]],'Unexpected TIFF geometry'
  assert pub['root_ifd_count']==s['expected_tiff']['pages'],'Unexpected TIFF page count'
 write(E/'runtime/PRIVATE_METADATA.json',dict(files=private));write(E/'artifacts/INVENTORY.json',dict(files=public,pixel_decoded=False,raster_payload_read=False));print(enc(dict(status='METADATA_INVENTORY_COMPLETE_MANUAL_ASSESSMENT_PENDING',files=len(public),tags=sum(len(f['tags']) for f in public))))
if __name__=='__main__':main()
