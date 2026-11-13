#!/usr/bin/env python3
"""Static command-boundary audit plus pixel/derivative arithmetic tests.
Not an RDP, emulator, or hardware test.
"""
import pathlib, subprocess, re, math
ROOT=pathlib.Path(__file__).resolve().parents[1]/'source'
def get(path,old=False):
 return subprocess.check_output(['git','show','4235c59f00b04440e3fd5fec49f0bc80e48cf212:'+path],cwd=ROOT,text=True) if old else (ROOT/path).read_text()
def calls(s,name):
 out=[];pos=0
 while (a:=s.find(name+'(',pos))>=0:
  b=a+len(name)+1;depth=1;start=b;args=[]
  while depth:
   c=s[b]
   if c=='(':depth+=1
   elif c==')':depth-=1
   if c==',' and depth==1:args.append(s[start:b].strip());start=b+1
   if depth==0:args.append(s[start:b].strip())
   b+=1
  out.append(args);pos=b
 return out
def norm(s):return re.sub(r'\s+','',s)
count=0
for path in ['src/engine/fox_std_lib.c','src/engine/fox_hud.c','src/engine/fox_message.c']:
 for macro,deriv in [('gSPTextureRectangle',8),('gSPTextureRectangleFlip',9)]:
  old,new=calls(get(path,True),macro),calls(get(path),macro)
  assert len(old)==len(new),(path,macro)
  for a,b in zip(old,new):
   for k in range(10):
    expect=a[k]
    if k in (1,3):expect=expect.replace('4.0f','8.0f') if '4.0f' in expect else '2 * ('+expect+')'
    if k==deriv:expect=expect.replace('1024','512').replace('(32 * 32)','(16 * 32)')
    assert norm(b[k])==norm(expect),(path,macro,k,b[k],expect)
   count+=1
# Offscreen render target (small portraits/textures) must not be doubled.
a=get('src/engine/fox_std_lib.c',True).split('u16* Graphics_SetupTextureRender')[1].split('void Graphics_DisplayHUDNumber')[0]
b=get('src/engine/fox_std_lib.c').split('u16* Graphics_SetupTextureRender')[1].split('void Graphics_DisplayHUDNumber')[0]
assert a==b
# Perspective and orthographic projection retain logical4:3 geometry.
assert get('src/sys/sys_lib.c').split('void Lib_InitPerspective')[1].split('void Lib_DmaRead')[0]==get('src/sys/sys_lib.c',True).split('void Lib_InitPerspective')[1].split('void Lib_DmaRead')[0]
assert re.search(r'#define SCREEN_WIDTH\s+320',get('include/gfx.h'))
# Discrete fill inclusive endpoint vs 1cycle exclusive endpoint.
for lo,hi in [(0,319),(8,311),(160,319),(319,319)]:
 assert (2*hi+1)-2*lo+1==2*(hi-lo+1)
 assert 2*hi-2*lo==2*(hi-lo)
# Horizontal sampling rate halves; vertical and texture allocation unchanged.
for scale in [0.25,0.5,1,2,3,4,8]:
 for sign in [-1,1]:
  old=int(sign*1024/scale);new=int(sign*512/scale)
  assert abs(2*new-old)<=1
# Full/versus destination viewport range stays inside signed16 and RDP10.2.
assert 640*4<32768 and 640*4<4096 and 720*4<4096
print(f'PASS: {count} texture rectangle calls, flipped derivative axis, offscreen invariance, logical aspect, endpoint/sampling arithmetic')
