"""Covers for the decks and templates shown as cards (Approved slide decks, Partner templates).

A card shows a picture attached to the same page under the file's own name: Template.pptx and
Template.jpg. This script makes those pictures from the files themselves with Quick Look (macOS),
so they can be uploaded as they are. They go to build/covers/<page>/, which stays out of Git;
local test mode attaches them (scripts/dev_fixtures.py).

Which files get a cover comes from dev/brandbank-map.json: examples marked "cover", and the
"covers" list for files matched by the page patterns. "slide" picks another slide than the first
(PowerPoint only), for templates that open on a notes slide.

  python3 scripts/cover_images.py
"""
import json, re, subprocess, tempfile, zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build' / 'covers'
SIZE = (1280, 720)

def first_slide(path, slide, tmp):
    """A copy of a PowerPoint file that opens on the given slide, for Quick Look to render."""
    copy = Path(tmp) / path.name
    with zipfile.ZipFile(path) as src, zipfile.ZipFile(copy, 'w', zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == 'ppt/presentation.xml':
                xml = data.decode('utf8')
                ids = re.findall(r'<p:sldId [^>]*/>', xml)
                pick = ids[slide - 1]
                xml = xml.replace(pick, '', 1).replace(ids[0], pick + ids[0], 1)
                data = xml.encode('utf8')
            dst.writestr(item, data)
    return copy

def render(path, slide=1):
    with tempfile.TemporaryDirectory() as tmp:
        src = first_slide(path, slide, tmp) if slide > 1 and path.suffix.lower() == '.pptx' else path
        subprocess.run(['qlmanage', '-t', '-s', str(SIZE[0]), '-o', tmp, str(src)], check=True, capture_output=True, timeout=600)
        made = Path(tmp) / (src.name + '.png')
        if not made.exists(): raise SystemExit(f'Quick Look made no picture for {path.name}')
        im = Image.open(made).convert('RGB')
    # Fill a 16:9 frame, as the card shows it.
    ratio = SIZE[0] / SIZE[1]
    if im.width / im.height > ratio:
        w = round(im.height * ratio); im = im.crop(((im.width - w) // 2, 0, (im.width - w) // 2 + w, im.height))
    else:
        h = round(im.width / ratio); im = im.crop((0, (im.height - h) // 2, im.width, (im.height - h) // 2 + h))
    return im.resize(SIZE, Image.LANCZOS)

def main():
    spec = json.loads((ROOT / 'dev' / 'brandbank-map.json').read_text())
    jobs = []
    for ex in spec.get('examples', []):
        if ex.get('cover'):
            base = Path(spec[ex.get('root', 'root')])
            found = sorted(p for p in base.glob(ex['from']) if p.is_file())
            if found: jobs.append((ex['page'], found[0], Path(ex['title']).stem, ex.get('slide', 1)))
    for c in spec.get('covers', []):
        base = Path(spec[c.get('root', 'root')])
        found = sorted(p for p in base.glob(c['file']) if p.is_file())
        if found: jobs.append((c['page'], found[0], found[0].stem, c.get('slide', 1)))
    for page, path, name, slide in jobs:
        out = OUT / page.replace('.html', '')
        out.mkdir(parents=True, exist_ok=True)
        render(path, slide).save(out / f'{name}.jpg', quality=84, optimize=True, progressive=True)
        print(f'{page}: {name}.jpg')

if __name__ == '__main__':
    main()
