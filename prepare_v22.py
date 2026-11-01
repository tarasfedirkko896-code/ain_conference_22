from pathlib import Path
from copy import deepcopy
from collections import deque
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json
p=Path(__file__).resolve().parents[1]
old=json.loads((p/'base-v21.tmj').read_text());m=deepcopy(old)
original=Image.open(p/'ain_conference_v15.png').convert('RGB')
edit=Image.open(p.parent/'generated_images/exec-d18cf369-3d6d-4c02-ba75-21340bfb8a51.png').convert('RGB').resize(original.size,Image.Resampling.LANCZOS)
# Only consume the generated architectural section. Existing branding and all other art remain exact.
mask=Image.new('L',original.size);d=ImageDraw.Draw(mask)
for box in [(420,128,860,344),(380,176,900,240)]:d.rectangle(tuple(v*4 for v in box),fill=255)
art=Image.composite(edit,original,mask);art.save(p/'ain_conference_v22.png',compress_level=6)
assert ImageChops.difference(art,original).getbbox()
# All pixels outside edited architecture are unchanged, including original ROZETKA asset.
assert Image.composite(ImageChops.difference(art,original),Image.new('RGB',art.size),ImageChops.invert(mask)).getbbox() is None
w,h,t=m['width'],m['height'],32;first=1;sets=[]
for y in range(0,h,64):
 for x in range(0,w,64):
  cw,ch=min(64,w-x),min(64,h-y);name=f'ain-v22-{x//64}-{y//64}.png';art.crop((x*t,y*t,(x+cw)*t,(y+ch)*t)).save(p/name,compress_level=6)
  sets.append({'firstgid':first,'name':f'AIN rectangular auditorium {len(sets)+1}','tilewidth':32,'tileheight':32,'tilecount':cw*ch,'columns':cw,'image':name,'imagewidth':cw*t,'imageheight':ch*t,'margin':0,'spacing':0});first+=cw*ch
m['tilesets']=sets+old['tilesets'][6:]
a=next(l['data'] for l in m['layers'] if l['name']=='Collisions');gid=m['tilesets'][6]['firstgid']
for y in range(h):
 for x in range(w):
  if mask.getpixel((x*32+16,y*32+16)):a[y*w+x]=0
# New straight side rails and front boundary with three existing doorways.
blocks=[(452,176,463,296),(816,176,827,296),(440,272,463,344),(816,272,839,344),(479,298,515,332),(562,298,609,332),(671,298,718,332),(765,298,801,332)]
for x1,y1,x2,y2 in blocks:
 for y in range(h):
  for x in range(w):
   if x1<=x*8+4<=x2 and y1<=y*8+4<=y2:a[y*w+x]=gid
# Design rectangle covers all seat rows and the central aisle; excludes side booths.
zone={'name':'Глядацька зала','x':464*4,'y':176*4,'width':352*4,'height':120*4,'design_coordinates':{'x':464,'y':176,'width':352,'height':120},'purpose':'Reference for drawing the audience area in WorkAdventure; does not activate audio automatically.'}
(p/'audience-zone-v22.json').write_text(json.dumps(zone,ensure_ascii=False,indent=2))
start=next(l['data'] for l in m['layers'] if l['name']=='start');q=deque([next(i for i,v in enumerate(start) if v)]);seen=set()
while q:
 i=q.popleft()
 if i in seen or a[i]:continue
 seen.add(i);x,y=i%w,i//w
 for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
  xx,yy=x+dx,y+dy
  if 0<=xx<w and 0<=yy<h:q.append(yy*w+xx)
for y in range(22,37):
 for x in range(58,102):assert y*w+x in seen,(x,y)
for name,(x,y) in json.loads((p/'geometry-v15.json').read_text())['checkpoints'].items():assert int(y/8)*w+int(x/8) in seen,name
(p/'base-v22.tmj').write_text(json.dumps(m,separators=(',',':')))
report={'rectangular_audience_all_tiles_reachable':True,'previous_route_checkpoints_reachable':True,'outside_artwork_unchanged':True,'audio_area_requires_editor_setup':True}
(p/'collision-changes-v22.json').write_text(json.dumps(report,indent=2))
# Setup diagram separate from the actual map artwork.
preview=art.resize((1600,960),Image.Resampling.LANCZOS).convert('RGBA');shade=Image.new('RGBA',preview.size);sd=ImageDraw.Draw(shade)
r=(580,220,1020,370);sd.rectangle(r,fill=(19,226,202,65),outline=(120,255,235,255),width=4)
preview=Image.alpha_composite(preview,shade);sheet=Image.new('RGB',(1600,1050),'#111b2b');sheet.paste(preview,(0,90));dd=ImageDraw.Draw(sheet);fp='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
dd.text((24,12),'ЗОНА СЛУХАЧІВ — ОДИН ПРЯМОКУТНИК',font=ImageFont.truetype(fp,25),fill='white')
dd.text((24,51),'Виділи всю бірюзову область: обидва блоки сидінь і центральний прохід.',font=ImageFont.truetype(fp,19),fill='#a9eee4');sheet.save(p/'AIN_v22_audience_zone.jpg',quality=90,optimize=True)
print(report)
