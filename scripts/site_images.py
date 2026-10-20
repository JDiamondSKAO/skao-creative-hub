"""Telescope photos for Site progress and the two site pages, from the SKAO image bank.

Each site page carries its photo as an attachment called site-photo.jpg: the site page shows it
as a banner, and Site progress shows it on that telescope's tile. This script makes web-sized
copies in build/site/low/ and build/site/mid/, which stay out of Git; local test mode serves them.

The image bank folder is named in dev/brandbank-map.json as "image_bank".

  python3 scripts/site_images.py
"""
import json
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build' / 'site'
# Official images: SKA-Low antennas at dusk, SKA-Mid dishes at night.
PHOTOS = {'low': 'SKA-LOW/OFFICIAL_IMAGES/IMG_2506.JPG', 'mid': 'SKA-MID/OFFICIAL_IMAGES/SKAO-Mid_UK23304.jpg'}
WIDTH = 1800

def main():
 bank = Path(json.loads((ROOT / 'dev' / 'brandbank-map.json').read_text())['image_bank'])
 for site, rel in PHOTOS.items():
  im = ImageOps.exif_transpose(Image.open(bank / rel)).convert('RGB')
  im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
  (OUT / site).mkdir(parents=True, exist_ok=True)
  path = OUT / site / 'site-photo.jpg'
  im.save(path, quality=80, optimize=True, progressive=True)
  print(f'{site}/site-photo.jpg  {im.size[0]}x{im.size[1]}  {path.stat().st_size // 1024} KB')

if __name__ == '__main__':
 main()
