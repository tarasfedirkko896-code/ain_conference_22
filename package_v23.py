from pathlib import Path
from PIL import Image,ImageChops
import json,zipfile,io
p=Path(__file__).resolve().parents[1]
m=json.loads((p/'base-v22.tmj').read_text());art=Image.open(p/'ain_with_labels_v23.png').convert('RGB');art.load();w,h,t=m['width'],m['height'],32
recon=Image.new('RGB',art.size)
for y in range(0,h,64):
 for x in range(0,w,64):
  i=(y//64)*3+x//64;s=m['tilesets'][i];cw,ch=min(64,w-x),min(64,h-y);name=f'ain-v23-{x//64}-{y//64}.png'
  tile=art.crop((x*t,y*t,(x+cw)*t,(y+ch)*t));tile.save(p/name,compress_level=6);Image.open(p/name).load();s['image']=name;s['name']=f'AIN map with permanent signs {i+1}';recon.paste(Image.open(p/name),(x*t,y*t))
assert ImageChops.difference(recon,art).getbbox() is None
(p/'map-ain-v23.tmj').write_text(json.dumps(m,separators=(',',':')))
assert m['layers']==json.loads((p/'base-v22.tmj').read_text())['layers']
(p/'README-v23.txt').write_text('Завантажте весь вміст папки upload у корінь ain_conference_22.\nMap URL після публікації:\nhttps://tarasfedirkko896-code.github.io/ain_conference_22/map-ain-v23.tmj\n\nУсі 11 написів включені безпосередньо до графіки карти. Глядацька зала замінено на Головна сцена.\nПрямокутна форма зали, усі проходи, колізії та стартові позиції незмінні від v22.\nУсі текстури до 2048×2048. Звук налаштовується окремо у WorkAdventure.\n')
files=['map-ain-v23.tmj']+[s['image'] for s in m['tilesets']]
out=p.parent/'AIN_WorkAdventure_v23_Signs.zip';tmp=out.with_suffix('.tmp')
with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED) as z:
 for name in files:z.write(p/name,'upload/'+name)
 for name in ['README-v23.txt','AIN_v23_labels.jpg','AIN_v23_blocked_zones.jpg','validation-v23.json','tools/build_v23.py','tools/package_v23.py']:z.write(p/name,name)
out.write_bytes(tmp.read_bytes())
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 for name in z.namelist():
  if name.endswith(('.png','.jpg')):Image.open(io.BytesIO(z.read(name))).load()
print('All signs baked into background; collisions unchanged; all packaged images verified;',out.stat().st_size,'bytes')
