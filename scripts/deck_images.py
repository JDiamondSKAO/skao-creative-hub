"""Slide pictures for the Standard SKAO template page, from the master deck's own renders.

Reads the slide PNGs the master deck repository renders from PowerPoint (read only) and writes a small
WebP for each picture the page asks for (slidekit.PICTURES: deck-cover.webp and so on) to build/deck/.
They go on the Standard SKAO Template page in Confluence without a label, so the page shows them as
pictures rather than listing them as downloads. The renders carry approved photos with their credits,
so they stay out of this public repository.

Usage: python3 scripts/deck_images.py [folder of slide-NN.png renders]
       (default: "master_deck_renders" in dev/brandbank-map.json)
"""
import json
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slidekit import PICTURES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build' / 'deck'
SIZE = (800, 450)   # twice the widest card, so the pictures stay sharp on a retina screen


def main(argv):
    if argv:
        src = Path(argv[0])
    else:
        spec = json.loads((ROOT / 'dev' / 'brandbank-map.json').read_text())
        src = Path(spec['master_deck_renders'])
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob('deck-*.webp'):
        old.unlink()
    total = 0
    for name, slide in PICTURES.items():
        png = src / f'slide-{slide:02d}.png'
        if not png.exists():
            sys.exit(f'missing {png}: render the deck first, or pass the folder with its slide PNGs')
        with Image.open(png) as im:
            im = im.convert('RGB')
            im.thumbnail(SIZE, Image.LANCZOS)
            out = OUT / f'{name}.webp'
            im.save(out, 'WEBP', quality=82, method=6)
        total += out.stat().st_size
        print(f'{out.name}  slide {slide}  {out.stat().st_size // 1024} KB')
    print(f'{len(PICTURES)} pictures, {total // 1024} KB, in {OUT}')


if __name__ == '__main__':
    main(sys.argv[1:])
