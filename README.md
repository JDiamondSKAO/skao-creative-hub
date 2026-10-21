# SKAO Creative Hub

The theme behind the **SKAO Creative Hub**: the Communications team's site on Confluence, built with Scroll Viewport, where staff of the Square Kilometre Array Observatory find templates, brand files, slide decks, photos and practical guidance.

This repository holds the theme, the scripts that generate it, a static preview, the test suite and the tools used to set up the Confluence space behind it.

**Status:** live, theme 2.24.8 (October 2026). See [CHANGELOG.md](CHANGELOG.md) for every release and [HANDOVER.md](HANDOVER.md) for where things stand.

## What the Hub does

- **Five sections:** Presentations, Documents, Brand, Photos and video, and How-to guides. An Events section is built but hidden for now.
- **Downloads straight from Confluence.** Files attached to a page and labelled `approved` appear as downloads. All files and Just added list them across the Hub.
- **Search** across pages, files and quick answers to common questions.
- **Photos and video** from the Canto staff media library, shown as a slideshow and linked to the Staff Resources Portal.
- **Share your presentation:** staff send a talk for review, and some become approved slide decks.
- **For new staff:** a first-visit welcome note and a short guided tour.
- **Feedback** from every page, through a form that records the page it came from.
- Light and dark modes, keyboard support and reduced motion throughout.

## How it works

Scroll Viewport renders each Confluence page through one Velocity template, `page.vm`. The template carries the Hub's design and content for every page it knows. Confluence supplies the page IDs, titles, attachments and search.

- `scripts/build.py` and its layer modules generate `page.vm` and a static preview in `docs/`. Both are generated, so edit the scripts, `js/` and `css/`, never the output.
- Pages are known by their Confluence IDs. Pages added later are matched by title (`scripts/interiors.py`, `PLANNED`).
- Links to internal documents are kept out of this public repository. They live in a local `dev/links.json` and are filled in only when a release is packaged.

## Repository layout

| Path | Contents |
|---|---|
| `scripts/` | Build layers, tests, packaging and Confluence tools |
| `js/`, `css/`, `fonts/`, `images/` | Theme scripts, styles and assets |
| `page.vm` | The generated Scroll Viewport template |
| `docs/` | The generated static preview |
| `evidence/interior-route-map.json` | Every page: Confluence ID, Confluence title and Hub title |
| `CHANGELOG.md` | Release notes |
| `HANDOVER.md` | Current state, next steps and local-only files |
| `AGENTS.md` | Working rules for AI coding assistants |

## Getting started

Requires Python 3.11+ (with Pillow for the picture scripts) and Node.js 20+.

```sh
npm install
python3 scripts/build.py
npm test                                        # must exit 0
python3 -m http.server 8766 --directory docs    # static preview at http://127.0.0.1:8766
```

**Local test mode** serves the built Hub as Confluence would, with a small stand-in for the Confluence REST API. Downloads, Just added, search, the slideshow and the announcement bar all work there.

```sh
python3 scripts/dev_fixtures.py    # builds dev/fixtures.json from the local file map
python3 scripts/dev_server.py      # http://127.0.0.1:8767
```

Add `?fresh` to any address to see the Hub as a first-time visitor. `dev/` is local only and never committed.

## Releasing

1. Update the version in `scripts/package.py` and add an entry to `CHANGELOG.md`.
2. Run `python3 scripts/package.py`. It builds `release/skao-creative-hub-v<version>-flat-upload.zip` with the internal links filled in, then rebuilds the committed files without them.
3. In the Scroll Viewport theme editor, upload the nine files from the zip, replacing the old ones.

The release zip contains internal links. Never publish it or attach it to a GitHub release.

## Confluence tools

Each tool asks for a Confluence personal access token. Tokens are typed into the terminal and never stored. None of the tools deletes anything permanently.

| Script | What it does |
|---|---|
| `upload_kit.py` | Gathers every file to attach into one folder per page. With `--upload`, attaches them and labels downloads `approved`. |
| `confluence_text.py` | Writes the Hub's own text into its Confluence pages, creates pages the Hub added later and arranges the page tree. Run it without `--apply` to review first. |
| `confluence_cleanup.py` | Moves pages the Hub no longer uses to the space trash, children first. |
| `canto_sync.py` | Publishes the Canto slideshow (images and a manifest) to the Photography Media page. With `--publish`, sends the last snapshot without Canto. |

## Canto slideshow

`scripts/canto_sync.py` picks approved, credited images of at least 2,000 px from the Canto **Staff media library** folder, and leaves out anything marked as not cleared. It publishes web-sized previews and a manifest as attachments, so staff browsers never talk to Canto.

Editors can pin an image to the slideshow with the Canto tag **Hub feature**. See the script's own notes for how images are chosen and how to run it on a schedule.

## Conventions

- **This repository is public.** Never commit internal links, credentials, personal names or staff photos.
- Write in plain English and follow the SKAO house style. It's the "SKAO slide deck", never "master deck".
- Tests must pass before a release is packaged.

## Licence

The code is MIT licensed. SKAO brand assets (logos, marks, photography and the SKAO name) are © SKA Observatory and are not licensed for reuse. See [LICENSE](LICENSE).
