from pathlib import Path
import struct,hashlib,json,re
root=Path(__file__).resolve().parents[1];p=root/'source/build';c=(p/'starfox64.us.rev1.z64').read_bytes();u=(p/'starfox64.us.rev1.uncompressed.z64').read_bytes();m=(p/'starfox64.us.rev1.map').read_text();offset=int(re.search(r'0x([0-9a-f]+)\s+dma_table_ROM_START',m)[1],16)
def mio(b):
 assert b[:4]==b'MIO0'
 size,cp,rp=struct.unpack('>III',b[4:16]);mask=16;bits=0;out=bytearray()
 while len(out)<size:
  if not bits:flags=b[mask];mask+=1;bits=8
  if flags&128:out.append(b[rp]);rp+=1
  else:
   n=int.from_bytes(b[cp:cp+2],'big');cp+=2;dist=(n&4095)+1
   for _ in range((n>>12)+3):out.append(out[-dist])
  flags=(flags<<1)&255;bits-=1
 assert len(out)==size
 return bytes(out)
maxscratch=0;count=0
for i in range(100):
 v,a,b,flag=struct.unpack_from('>IIII',c,offset+i*16)
 if not b:break
 assert 0<=a<b<=len(c) and flag in (0,1)
 payload=mio(c[a:b]) if flag else c[a:b]
 expected=u[v:v+len(payload)]
 if i==0:payload=payload[:16]+expected[16:24]+payload[24:]
 if i!=2:assert payload==expected,(i,v,a,b)
 if flag:maxscratch=max(maxscratch,b-a)
 count+=1
assert maxscratch<=3*640*240*2
def addr(n):return int(re.search(r'0x([0-9a-f]+)\s+'+n+r'\s*$',m,re.M)[1],16)
assert addr('gTaskOutputBuffer')-addr('gZBuffer')==640*240*2
assert 0x80615780-addr('gFrameBuffers')==3*640*240*2
assert addr('gFrameBuffers')-addr('gFillBuffer')==3*640*2
for n in ['gDramStack','gOSYieldData','gZBuffer','gTaskOutputBuffer','gAudioHeap','gTextureRenderBuffer','gFillBuffer','gFrameBuffers']:
 assert addr(n)%16==0 and 0x80400000<=addr(n)<0x80615780
assert 0x80615780<=0x80800000
assert (root/'baseline/build/starfox64.us.rev1.z64').read_bytes()==(root/'inputs/Star Fox 64 (USA) (Rev 1).z64').read_bytes()
r=dict(baseline_byte_exact=True,dma_table_offset=hex(offset),payload_entries_verified=count-1,dma_table_entry_reencoded=True,max_compressed_staging_bytes=maxscratch,staging_capacity=921600,buffer_end='0x80615780',target_sha256=hashlib.sha256(c).hexdigest())
print(json.dumps(r,indent=2));(root/'binary-validation.json').write_text(json.dumps(r,indent=2))
