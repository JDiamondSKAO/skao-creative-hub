"""Pictures of the event kit for Stands and merchandise, from the Events Production Manual's files.

The theme shows each kit item with a picture attached to the Stands and merchandise page
under a fixed name (kit-pull-up-banners.webp and so on, see KIT). This script makes those
files from the manual's product renders, so they can be uploaded as they are. They go to
build/kit/, which stays out of Git; local test mode serves them from there.

The manual's folder is named in dev/brandbank-map.json as "events_guide".

  python3 scripts/kit_images.py
"""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build' / 'kit'
SIZE = (900, 600)  # 3:2, twice the size a picture is shown at

# Picture name: the manual's file it comes from (or the page of the manual for the pull-up photo).
KIT = {
 'kit-pull-up-banners': ('manual', 11),
 'kit-fabrilux-3m': 'LINKS/BANNERS_CONFIGS/3M_BANNER/3M_BANNER_1.png',
 'kit-fabrilux-2m': 'LINKS/BANNERS_CONFIGS/2M_BANNER/2M_BANNER_1.png',
 'kit-kiosk': 'LINKS/BANNERS_CONFIGS/TABLE/TABLE.png',
 'kit-table-cloths': 'LINKS/BANNERS_CONFIGS/TABLE/SKAO_TABLE_CLOTH.pdf',
}
MANUAL = 'FINALS/BROCHURE/SKAO Events Production Manual (version 1).pdf'

def fit(im, margin=0.04):
 """A cut-out product, trimmed to what is drawn and centred on a clear 3:2 canvas."""
 im = im.convert('RGBA')
 im = im.crop(im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox())
 w, h = SIZE[0] * (1 - 2 * margin), SIZE[1] * (1 - 2 * margin)
 scale = min(w / im.width, h / im.height)
 im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
 out = Image.new('RGBA', SIZE, (0, 0, 0, 0))
 out.alpha_composite(im, ((SIZE[0] - im.width) // 2, (SIZE[1] - im.height) // 2))
 return out

def cover(im):
 """A photo cropped to fill the 3:2 canvas."""
 im = im.convert('RGB')
 ratio = SIZE[0] / SIZE[1]
 if im.width / im.height > ratio:
  w = round(im.height * ratio); im = im.crop(((im.width - w) // 2, 0, (im.width - w) // 2 + w, im.height))
 else:
  h = round(im.width / ratio); im = im.crop((0, (im.height - h) // 2, im.width, (im.height - h) // 2 + h))
 return im.resize(SIZE, Image.LANCZOS)

def pdf_pages(path, dpi=110):
 import subprocess, tempfile
 with tempfile.TemporaryDirectory() as tmp:
  subprocess.run(['pdftoppm', '-r', str(dpi), '-png', str(path), f'{tmp}/p'], check=True)
  return [Image.open(p).convert('RGB') for p in sorted(Path(tmp).glob('p*.png'))]

def cloths(path):
 """The two table cloth designs side by side, each with a soft edge so the white one reads."""
 from PIL import ImageFilter
 pages = pdf_pages(path)
 gap, margin = 20, 30
 w = (SIZE[0] - 2 * margin - gap) // 2
 out = Image.new('RGBA', SIZE, (0, 0, 0, 0))
 for i, page in enumerate(pages[:2]):
  page = page.resize((w, round(page.height * w / page.width)), Image.LANCZOS)
  x, y = margin + i * (w + gap), (SIZE[1] - page.height) // 2
  shadow = Image.new('RGBA', SIZE, (0, 0, 0, 0))
  shadow.paste((13, 29, 44, 60), (x, y + 6, x + page.width, y + page.height + 6))
  out.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))
  out.paste(page, (x, y))
 return out

def main():
 spec = json.loads((ROOT / 'dev' / 'brandbank-map.json').read_text())
 guide = Path(spec['events_guide'])
 OUT.mkdir(parents=True, exist_ok=True)
 for name, source in KIT.items():
  if isinstance(source, tuple):
   from pypdf import PdfReader
   page = PdfReader(guide / MANUAL).pages[source[1] - 1]
   im = cover(max(page.images, key=lambda i: i.image.width * i.image.height).image)
  elif source.endswith('.pdf'):
   im = cloths(guide / source)
  else:
   im = fit(Image.open(guide / source))
  im.save(OUT / f'{name}.webp', quality=86, method=6)
  print(f'{name}.webp  {(OUT / f"{name}.webp").stat().st_size // 1024} KB')

if __name__ == '__main__':
 main()
