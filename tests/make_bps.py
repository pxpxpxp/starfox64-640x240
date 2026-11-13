import pathlib,zlib,struct
r=pathlib.Path(__file__).resolve().parents[1];s=(r/'inputs/Star Fox 64 (USA) (Rev 1).z64').read_bytes();t=(r/'source/build/starfox64.us.rev1.z64').read_bytes()
def num(n):
 o=bytearray()
 while True:
  x=n&127;n>>=7
  if not n:o.append(x|128);return o
  o.append(x);n-=1
p=bytearray(b'BPS1')+num(len(s))+num(len(t))+num(0);cursor=0;sourcepos=0;copies=0
# Reuse unchanged compressed DMA payloads at their new location.
for i in range(64):
 _,sa,sb,_=struct.unpack_from('>IIII',s,0xde480+16*i)
 _,ta,tb,_=struct.unpack_from('>IIII',t,0xde710+16*i)
 assert cursor<=ta<tb<=len(t)
 if ta>cursor:p+=num(((ta-cursor-1)<<2)|1)+t[cursor:ta]
 if s[sa:sb]==t[ta:tb]:
  p+=num(((tb-ta-1)<<2)|2);delta=sa-sourcepos;p+=num((abs(delta)<<1)|(delta<0));sourcepos=sb;copies+=1
 else:p+=num(((tb-ta-1)<<2)|1)+t[ta:tb]
 cursor=tb
if cursor<len(t):p+=num(((len(t)-cursor-1)<<2)|1)+t[cursor:]
p+=struct.pack('<II',zlib.crc32(s),zlib.crc32(t));p+=struct.pack('<I',zlib.crc32(p))
(r/'Star_Fox_64_Native_640x240_PVM_E01.bps').write_bytes(p)
# Independent generic BPS decoder; validates all checksum fields.
pos=4
def read():
 global pos
 n=0;shift=1
 while True:
  x=p[pos];pos+=1;n+=(x&127)*shift
  if x&128:return n
  shift<<=7;n+=shift
assert read()==len(s) and read()==len(t);meta=read();pos+=meta;out=bytearray();sr=tr=0
while len(out)<len(t):
 v=read();n=(v>>2)+1;action=v&3
 if action==0:out+=s[len(out):len(out)+n]
 elif action==1:out+=p[pos:pos+n];pos+=n
 elif action==2:
  v=read();sr+=-(v>>1) if v&1 else v>>1;out+=s[sr:sr+n];sr+=n
 else:
  v=read();tr+=-(v>>1) if v&1 else v>>1
  for _ in range(n):out.append(out[tr]);tr+=1
assert bytes(out)==t and pos==len(p)-12
assert struct.unpack('<III',p[-12:])==(zlib.crc32(s),zlib.crc32(out),zlib.crc32(p[:-4]))
print('PASS BPS roundtrip + 3 CRCs; bytes',len(p),'unchanged payload copies',copies)
