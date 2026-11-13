from pathlib import Path
import struct
root=Path(__file__).resolve().parents[1]
for name in ['inputs/Star Fox 64 (USA) (Rev 1).z64','source/build/starfox64.us.rev1.z64']:
 b=(root/name).read_bytes();a=[0xf8ca4ddc]*6
 for (x,) in struct.iter_unpack('>I',b[4096:1052672]):
  if (a[5]+x)>0xffffffff:a[3]=(a[3]+1)&0xffffffff
  a[5]=(a[5]+x)&0xffffffff;a[2]^=x
  n=x&31;r=((x<<n)|(x>>(32-n)))&0xffffffff
  a[4]=(a[4]+r)&0xffffffff;a[1]^=r if a[1]>x else a[5]^x;a[0]=(a[0]+(a[4]^x))&0xffffffff
 crc=(a[5]^a[3]^a[2],a[4]^a[1]^a[0]);assert crc==struct.unpack_from('>II',b,16),(name,crc)
 print('PASS CIC6102',name,*(hex(x) for x in crc))
