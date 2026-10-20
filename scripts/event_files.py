"""Downloads for Print and giveaway files: print-ready designs from past SKAO events, each with a cover.

Each entry below becomes one card on the Print and giveaway files page. The card's download is a print
file, or a ZIP when a design comes in several sizes or versions, named for the card ("Roller banners.zip").
Its cover is a picture of the design under the same name ("Roller banners.webp"), which the page shows on
the card (brandkit.DOWNLOAD_VIEW 'cards'). Upload the downloads with the label "approved" and the covers
with no label. Everything goes to build/event-files/, which stays out of Git; local test mode serves it
from there. The script only reads the source folders.

The folders come from dev/brandbank-map.json: "event_assets" (the reusable event assets folder; if
it isn't named, the folder three up from "events_guide") and "root" (its 04_MERCHANDISE folder).

  python3 scripts/event_files.py
"""
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build' / 'event-files'
SIZE = (960, 540)  # 16:9, the shape of a download card's cover
Image.MAX_IMAGE_PIXELS = None  # print files are large

def A(src, knock=False, cut=None):
 """A picture for a cover: knock clears a white background (mock-ups, renders); cut keeps a part
 of it, as (left, top, right, bottom) fractions."""
 return {'src': src, 'knock': knock, 'cut': cut}

# Card name: (the files in its download as (name inside, source), its cover's pictures, space around them;
# MARGINS below sets the space).
# Sources starting merch/ are in the merchandise folder; the rest are reusable event assets. A * takes
# every match, under its own name. One file is offered as it is; several go in a ZIP.
B = 'BANNER_SYSTEMS/'
EVENT_FILES = {
 'Roller banners': ([('Roller banner 85 x 211 cm.pdf', B + 'ROLLER_BANNERS/850mm_x_2110mm/SKAO_GENERIC/FINALS/SKAO_ROLLER_BANNER_850mm_x_2110+300mm_op.pdf'),
                     ('Roller banner 100 x 229 cm.pdf', B + 'ROLLER_BANNERS/1000mm_x_2290mm/SKAO_GENERIC/FINALS/SKAO_BANNER_1000x2290mm.pdf'),
                     ('Roller banner 150 x 211 cm.pdf', B + 'ROLLER_BANNERS/1500mm_x_2110mm/SKAO_GENERIC/FINALS/SKAO_ROLLER_BANNER_1500mm_x_2110+300mm.pdf')], None, 32),
 'Stretch walls': ([('Stretch wall 1.5 x 2.25 m.pdf', B + 'STRETCH_WALLS_FABRILUX/1500mm_x_2250mm/SKAO_GENERIC/FINALS/SKAO_Stretch_walls_1500mm_v3.pdf'),
                    ('Stretch wall 5 x 2.25 m.pdf', B + 'STRETCH_WALLS_FABRILUX/5000mm_x_2250mm/SKAO_GENERIC/FINALS/SKAO_Stretch_walls_5m_v2.pdf')], [1], 40),
 'Wide banners': ([('Wide banner 1.5 x 2 m, SKAO.pdf', B + 'CP-26-002_WIDE_BANNER_1500x2010mm/FINALS/CP-26-002_SKAO_WIDE_BANNER_1500x2010mm.pdf'),
                   ('Wide banner 1.5 x 2 m, SKA-Mid and SKA-Low.pdf', B + 'CP-26-002_WIDE_BANNER_1500x2010mm/FINALS/CP-26-002_SKA-MID_LOW_WIDE_BANNER_1500x2010mm.pdf')], None, 32),
 'Wall banners': ([('Wall banner 2 x 2.25 m, SKA-Mid and SKA-Low.pdf', B + 'WALL_BANNERS/2000mm_x_2250mm/MID_LOW_INFOGRAPHIC/FINALS/SKA_Low_Mid_Infographic_2000mm_x_2250mm.pdf'),
                   ('Wall banner 2 x 2 m, SKA-Mid and SKA-Low.pdf', B + 'WALL_BANNERS/2000mm_x_2000mm/MID_LOW_INFOGRAPHIC/FINALS/SKAO_2X2M_BANNER_.pdf'),
                   ('Wall banner 1.2 x 2 m, SKAO.pdf', B + 'WALL_BANNERS/1200mm_x_2000mm/SKAO_GENERIC/FINALS/SKAO_Banner_1200x2000mm_OP.pdf')], [0, 2], 32),
 # The flag sizes printed under the flags are left off the cover.
 'Teardrop flags': ([('Teardrop flags.pdf', B + 'TEARDROP_BANNERS/SKAO_GENERIC/FINALS/SKAO_Teardrop_Banner_nocutter.pdf'),
                     ('Teardrop flags with cutter guide.pdf', B + 'TEARDROP_BANNERS/SKAO_GENERIC/FINALS/SKAO_Teardrop_Banner_cutter.pdf')],
                    [A(B + 'TEARDROP_BANNERS/SKAO_GENERIC/FINALS/SKAO_Teardrop_Banner_nocutter.pdf', knock=True, cut=(0, 0, 1, 0.86))], 32),
 'Gazebo': ([('Gazebo.pdf', B + 'GAZEBOS/SKA_LOW/FINALS/SKAO Gazebo_Australia_Flat_Opt_1.pdf')],
            [A(B + 'GAZEBOS/SKA_LOW/FINALS/SKAO_Gazebo_Australia_v1.jpg', knock=True)], 32),
 'Stickers': ([('Sticker, logo.pdf', 'merch/SKAO/PROMOTIONAL_ITEMS/STICKERS/FINALS/SKAO_STICKERS_OL_PRINT_LOGO.pdf'),
               ('Sticker, star.pdf', 'merch/SKAO/PROMOTIONAL_ITEMS/STICKERS/FINALS/SKAO_STICKERS_OL_PRINT_PICTORIAL.pdf'),
               ('Sticker, science.pdf', 'merch/SKAO/PROMOTIONAL_ITEMS/STICKERS/FINALS/SKAO_STICKERS_OL_PRINT_SCIENCE.pdf'),
               ('Sticker, time machine.pdf', 'merch/SKAO/PROMOTIONAL_ITEMS/STICKERS/FINALS/SKAO_STICKERS_OL_PRINT_TIMEM.pdf')],
              [A('merch/SKAO/STICKERS/FINALS/SKAO Sticker - pictorial.png'), A('merch/SKAO/STICKERS/FINALS/SKAO Sticker - logo.png')], 80),
 'Lanyards': ([('Lanyard, SKAO.pdf', 'merch/SKAO/PROMOTIONAL_ITEMS/LANYARD/FINALS/LANYARD_950x20MM.pdf'),
               ('Lanyard, science.pdf', 'merch/SKAO/PROMOTIONAL_ITEMS/LANYARD/FINALS/SKAO_SCIENCE_LANYARD_20MM.pdf')],
              [A('merch/SKAO/PROMOTIONAL_ITEMS/LANYARD/DEVELOPMENT/LANYARD_MOCKUP.png', knock=True)], 24),
 'Coasters': ([('Coaster, time machine.pdf', 'merch/SKAO/PROMOTIONAL_ITEMS/SKAO_COASTERS/FINALS/SKAO_COASTER_OL_TIME.pdf'),
               ('Coaster, science is for everyone.pdf', 'merch/SKAO/PROMOTIONAL_ITEMS/SKAO_COASTERS/FINALS/SKAO_COASTER_OL_SCIENCE.pdf'),
               ('Coaster, star.pdf', 'merch/SKAO/PROMOTIONAL_ITEMS/COASTER/FINALS/94MM_PICTORIAL_COASTER_BLEED.pdf')],
              [A('merch/SKAO/PROMOTIONAL_ITEMS/SKAO_COASTERS/FINALS/SKAO_COASTER_OL_TIME.pdf', knock=True),
               A('merch/SKAO/PROMOTIONAL_ITEMS/SKAO_COASTERS/FINALS/SKAO_COASTER_OL_SCIENCE.pdf', knock=True)], 40),
 'Notepads and sticky notes': ([('Notepad A5.pdf', 'merch/SKAO/STATIONERY/A5_PAD/FINALS/SKAO_A5_NOTEPAD_BLEED.pdf'),
                                ('Sticky notes A7.pdf', 'merch/SKAO/STATIONERY/A7_POST_ITS/FINALS/SKAO_A7_POSTIT.pdf')], [0], 44),
 'SKAO and SARAO': ([('SKAO and SARAO wall 3 m.pdf', 'PARTNER_COBRANDS/SARAO/FINALS/SKAO-SARAO_3000mm_Wall.pdf'),
                     ('SKAO and SARAO roller banner 85 x 205 cm.pdf', 'PARTNER_COBRANDS/SARAO/FINALS/SKAO-SARAO_850x2050mm.pdf'),
                     ('SKAO and SARAO 13 x 42 cm.pdf', 'PARTNER_COBRANDS/SARAO/FINALS/SKAO-SARAO_130x420mm.pdf')], [0, 1], 32),
 'SKAO and CETC': ([('SKAO and CETC.pdf', 'PARTNER_COBRANDS/CETC/FINALS/*.pdf')], None, 32),
 # The co-branded roller banner (137 MB) stays out: ask for it.
 'SKAO and ngVLA': ([('SKAO and ngVLA banner 2.96 x 2.28 m.pdf', 'PARTNER_COBRANDS/NGVLA/FINALS/SKAO_Vancouver_Banner_2960x2280mm_v3.pdf'),
                     ('SKAO banner 2.96 x 2.28 m.pdf', 'PARTNER_COBRANDS/NGVLA/FINALS/SKAO_Vancouver_Banner_2960x2280mm_SKAO_ONLY.pdf'),
                     ('SKAO banner 2.48 x 2.29 m.pdf', 'PARTNER_COBRANDS/NGVLA/FINALS/SKAO_Vancouver_Banner_2480x2290mm_SKAO_ONLY.pdf'),
                     ('SKAO roller banner.pdf', 'PARTNER_COBRANDS/NGVLA/FINALS/SKAO_Vancouver_Roller_Banner_SKAO_ONLY.pdf')], [0], 32),
 'PI planning logos': ([(None, 'PI_PLANNING/*/*.png'), (None, 'PI_PLANNING/*/*.pdf'), (None, 'PI_PLANNING/PI23/FOR_PRINT/*.pdf')],
                       [A('PI_PLANNING/PI23/SKAO_LOGO_PI24_CO-LOCATION.pdf')], 120),  # on its white sheet, so it reads in dark mode too
}

# Space around each cover's pictures (pixels at 960 x 540): small, so every cover reads at a similar size.
MARGINS = {'Roller banners': 18, 'Stretch walls': 28, 'Wide banners': 18, 'Wall banners': 18, 'Teardrop flags': 20, 'Gazebo': 20,
 'Stickers': 56, 'Lanyards': 16, 'Coasters': 22, 'Notepads and sticky notes': 22, 'SKAO and SARAO': 20, 'SKAO and CETC': 18,
 'SKAO and ngVLA': 18, 'PI planning logos': 70}

def pdf_page(path, side=1600):
 """Page 1 of a print file, trimmed to its finished size (no bleed or crop marks)."""
 from pypdf import PdfReader
 page = PdfReader(str(path)).pages[0]
 with tempfile.TemporaryDirectory() as tmp:
  subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-scale-to', str(side), '-png', str(path), f'{tmp}/p'], check=True, capture_output=True)
  im = Image.open(sorted(Path(tmp).glob('p*.png'))[0]); im.load()
 if page.get('/Rotate', 0) % 180: return im  # turned pages keep their full sheet
 mb, tb = page.mediabox, page.trimbox
 w, h = float(mb.width), float(mb.height)
 box = ((float(tb.left) - float(mb.left)) / w, (float(mb.top) - float(tb.top)) / h,
        (float(tb.right) - float(mb.left)) / w, (float(mb.top) - float(tb.bottom)) / h)
 return crop(im, box)

def crop(im, box):
 l, t, r, b = box
 return im.crop((round(l * im.width), round(t * im.height), round(r * im.width), round(b * im.height)))

def load(path):
 if path.suffix.lower() == '.pdf': return pdf_page(path)
 im = Image.open(path)
 if im.format == 'JPEG': im.draft('RGB', (1600, 1600))
 im.load()
 im.thumbnail((1600, 1600))
 return im

def knock_white(im):
 """Clear the white background around a mock-up, working in from the corners."""
 im = im.convert('RGBA')
 for xy in [(0, 0), (im.width - 1, 0), (0, im.height - 1), (im.width - 1, im.height - 1)]:
  if sum(im.getpixel(xy)[:3]) > 3 * 235: ImageDraw.floodfill(im, xy, (255, 255, 255, 0), thresh=60)
 im.putalpha(im.getchannel('A').filter(ImageFilter.GaussianBlur(0.7)))
 return im

def art(items, margin=32, gap=24):
 """Pictures side by side at the same height, centred, each with a soft shadow."""
 ims = []
 for it in items:
  im = load(it['path'])
  if it['cut']: im = crop(im, it['cut'])
  ims.append((im.convert('RGBA'), it['knock']))
 ratio = sum(im.width / im.height for im, _ in ims)
 h = min(SIZE[1] - 2 * margin, (SIZE[0] - 2 * margin - gap * (len(ims) - 1)) / ratio)
 out = Image.new('RGBA', SIZE, (0, 0, 0, 0))
 x = round((SIZE[0] - (ratio * h + gap * (len(ims) - 1))) / 2)
 for im, knock in ims:
  im = im.resize((round(im.width * h / im.height), round(h)), Image.LANCZOS)
  if knock: im = knock_white(im)
  y = (SIZE[1] - im.height) // 2
  shadow = Image.new('RGBA', SIZE, (0, 0, 0, 0))
  shadow.paste((13, 29, 44, 70), (x, y + 8), im.getchannel('A'))
  out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(11)))
  out.alpha_composite(im, (x, y))
  x += im.width + gap
 return out

def main():
 spec = json.loads((ROOT / 'dev' / 'brandbank-map.json').read_text())
 events = Path(spec.get('event_assets') or Path(spec['events_guide']).parents[2])
 merch = Path(spec['root']) / '04_MERCHANDISE'
 def where(src):
  path = merch / src[len('merch/'):] if src.startswith('merch/') else events / src
  if '*' not in str(path): return [path]
  return sorted(p for p in path.parent.parent.glob(path.parent.name + '/' + path.name) if p.is_file()) if '*' in path.parent.name \
   else sorted(p for p in path.parent.glob(path.name) if p.is_file())
 if OUT.exists(): shutil.rmtree(OUT)
 OUT.mkdir(parents=True)
 for name, (files, cover, margin) in EVENT_FILES.items():
  found = [(inner or p.name, p) for inner, src in files for p in where(src)]
  if len(found) == 1:
   inner, path = found[0]
   shutil.copyfile(path, OUT / (name + path.suffix.lower()))
  else:
   with zipfile.ZipFile(OUT / (name + '.zip'), 'w', zipfile.ZIP_STORED) as z:
    for inner, path in found: z.write(path, inner)
  # The cover: the listed pictures, or the files themselves (all of them, or those at the given places).
  pics = cover if cover and isinstance(cover[0], dict) else [A(files[i][1]) for i in (cover or range(len(files)))]
  art([{**it, 'path': where(it['src'])[0]} for it in pics], MARGINS.get(name, margin)).save(OUT / (name + '.webp'), quality=86, method=6)
  print(f'{name}: {len(found)} file{"s" if len(found) > 1 else ""}')

if __name__ == '__main__':
 main()
