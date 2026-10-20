"""Pictures for Designs to reuse, from the reusable event assets and the merchandise folder.

The theme shows each design with a picture attached to the Designs to reuse page under a fixed
name (design-roller-banners.webp and so on, see DESIGNS in interiors.py). This script makes those
files from the print files, so they can be uploaded as they are. It only reads the source folders.
The pictures go to build/designs/, which stays out of Git; local test mode serves them from there.

The folders come from dev/brandbank-map.json: "event_assets" (the reusable event assets folder; if
it isn't named, the folder three up from "events_guide") and "root" (its 04_MERCHANDISE folder).

  python3 scripts/design_images.py
"""
import json
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build' / 'designs'
SIZE = (900, 600)  # 3:2, twice the size a picture is shown at
Image.MAX_IMAGE_PIXELS = None  # print files are large

def A(src, knock=False, cut=None):
 """One print file: knock clears a white background (mock-ups, renders); cut keeps a part
 of it, as (left, top, right, bottom) fractions."""
 return {'src': src, 'knock': knock, 'cut': cut}

# Picture name: how it's made. 'photo' fills the frame from a crop of the source (fractions);
# 'art' lays print files side by side at the same height, each with a soft shadow.
# Sources starting merch/ are in the merchandise folder; the rest are reusable event assets. A * in
# the file name takes the first match.
DESIGNS = {
 # Cropped so the visitor at the left edge is out of the picture.
 'design-iau-ga-2024': ('photo', 'STANDS/SKAO_PAVILION/MAIN/SKAO_PAV-6.jpg', (0.09, 0.04, 1, 0.94)),
 'design-korea-walls': ('art', [A('STANDS/SKA_KOREA/FINALS/SKA_KOREA_ARTWORK/SCIENCE_WALL/SKA_SCIENCE_KOREA_STAND_950x2500MM_OL.pdf'),
                                A('STANDS/SKA_KOREA/FINALS/SKA_KOREA_ARTWORK/DUSK_WALL/SKA_DUSK_KOREA_STAND_950x2500MM_OL.pdf')]),
 'design-gazebo': ('art', [A('BANNER_SYSTEMS/GAZEBOS/SKA_LOW/FINALS/SKAO_Gazebo_Australia_v1.jpg', knock=True)]),
 'design-stretch-walls': ('art', [A('BANNER_SYSTEMS/STRETCH_WALLS_FABRILUX/5000mm_x_2250mm/SKAO_GENERIC/FINALS/SKAO_Stretch_walls_5m_v2.pdf')]),
 'design-roller-banners': ('art', [A('BANNER_SYSTEMS/ROLLER_BANNERS/850mm_x_2110mm/SKAO_GENERIC/FINALS/SKAO_ROLLER_BANNER_850mm_x_2110+300mm_op.pdf'),
                                   A('BANNER_SYSTEMS/ROLLER_BANNERS/1000mm_x_2290mm/SKAO_GENERIC/FINALS/SKAO_BANNER_1000x2290mm.pdf'),
                                   A('BANNER_SYSTEMS/ROLLER_BANNERS/1500mm_x_2110mm/SKAO_GENERIC/FINALS/SKAO_ROLLER_BANNER_1500mm_x_2110+300mm.pdf')]),
 'design-wide-banners': ('art', [A('BANNER_SYSTEMS/CP-26-002_WIDE_BANNER_1500x2010mm/FINALS/CP-26-002_SKAO_WIDE_BANNER_1500x2010mm.pdf'),
                                 A('BANNER_SYSTEMS/CP-26-002_WIDE_BANNER_1500x2010mm/FINALS/CP-26-002_SKA-MID_LOW_WIDE_BANNER_1500x2010mm.pdf')]),
 'design-wall-banners': ('art', [A('BANNER_SYSTEMS/WALL_BANNERS/2000mm_x_2250mm/MID_LOW_INFOGRAPHIC/FINALS/SKA_Low_Mid_Infographic_2000mm_x_2250mm.pdf'),
                                 A('BANNER_SYSTEMS/WALL_BANNERS/1200mm_x_2000mm/SKAO_GENERIC/FINALS/SKAO_Banner_1200x2000mm_OP.pdf')]),
 # The flag sizes printed under the flags are left out.
 'design-teardrop-flags': ('art', [A('BANNER_SYSTEMS/TEARDROP_BANNERS/SKAO_GENERIC/FINALS/SKAO_Teardrop_Banner_nocutter.pdf', knock=True, cut=(0, 0, 1, 0.86))]),
 'design-sarao': ('art', [A('PARTNER_COBRANDS/SARAO/FINALS/SKAO-SARAO_3000mm_Wall.pdf'), A('PARTNER_COBRANDS/SARAO/FINALS/SKAO-SARAO_850x2050mm.pdf')]),
 'design-cetc': ('art', [A('PARTNER_COBRANDS/CETC/FINALS/*.pdf')]),
 'design-ngvla': ('art', [A('PARTNER_COBRANDS/NGVLA/FINALS/SKAO_Vancouver_Banner_2960x2280mm_v3.pdf')]),
 # The cover only: the schedule beside it names the speakers.
 'design-programmes': ('art', [A('EVENT_COLLATERAL/PROGRAMME_EXAMPLES/21255_VLBI Conference Programme.jpg', cut=(0, 0, 0.42, 1))]),
 'design-pi-planning': ('art', [A('PI_PLANNING/PI23/SKAO_LOGO_PI24_CO-LOCATION.png', knock=True)]),
 'design-stickers': ('art', [A('merch/SKAO/STICKERS/FINALS/SKAO Sticker - pictorial.png'), A('merch/SKAO/STICKERS/FINALS/SKAO Sticker - logo.png')]),
 'design-lanyards': ('art', [A('merch/SKAO/PROMOTIONAL_ITEMS/LANYARD/DEVELOPMENT/LANYARD_MOCKUP.png', knock=True)]),
 'design-coasters': ('art', [A('merch/SKAO/PROMOTIONAL_ITEMS/SKAO_COASTERS/FINALS/SKAO_COASTER_OL_TIME.pdf', knock=True),
                             A('merch/SKAO/PROMOTIONAL_ITEMS/SKAO_COASTERS/FINALS/SKAO_COASTER_OL_SCIENCE.pdf', knock=True)]),
 'design-notepads': ('art', [A('merch/SKAO/STATIONERY/A5_PAD/FINALS/SKAO_A5_NOTEPAD_BLEED.pdf'), A('merch/SKAO/STATIONERY/A7_POST_ITS/FINALS/SKAO_A7_POSTIT.pdf')]),
 # The FRONT and BACK labels under the shirts are left out.
 'design-t-shirts': ('art', [A('merch/SKAO/APPAREL/SCIENCE_IS_FOR_EVERYONE/25773_SKAO T-shirts_pride2023_mockup_FINAL.pdf', knock=True, cut=(0, 0, 1, 0.88))]),
}

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
 a = im.getchannel('A').filter(ImageFilter.GaussianBlur(0.7))
 im.putalpha(a)
 return im

def art(items, margin=40, gap=26):
 """Print files side by side at the same height, centred, each with a soft shadow."""
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

def photo(path, box):
 """A photo cropped to fill the 3:2 frame."""
 im = crop(load(path).convert('RGB'), box)
 ratio = SIZE[0] / SIZE[1]
 if im.width / im.height > ratio:
  w = round(im.height * ratio); im = im.crop(((im.width - w) // 2, 0, (im.width - w) // 2 + w, im.height))
 else:
  h = round(im.width / ratio); im = im.crop((0, (im.height - h) // 2, im.width, (im.height - h) // 2 + h))
 return im.resize(SIZE, Image.LANCZOS)

def main():
 spec = json.loads((ROOT / 'dev' / 'brandbank-map.json').read_text())
 events = Path(spec.get('event_assets') or Path(spec['events_guide']).parents[2])
 merch = Path(spec['root']) / '04_MERCHANDISE'
 def where(src):
  path = merch / src[len('merch/'):] if src.startswith('merch/') else events / src
  return sorted(path.parent.glob(path.name))[0] if '*' in path.name else path
 OUT.mkdir(parents=True, exist_ok=True)
 for name, (kind, *rest) in DESIGNS.items():
  if kind == 'photo':
   im = photo(where(rest[0]), rest[1])
  else:
   im = art([{**it, 'path': where(it['src'])} for it in rest[0]])
  im.save(OUT / f'{name}.webp', quality=86, method=6)
  print(name)

if __name__ == '__main__':
 main()
