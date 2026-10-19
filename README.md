# SKAO Creative Hub v2

Staging redesign for the Creative Hub Scroll Sites theme, with a static preview of the homepage and 60 interior pages.

## Local preview

Requires Python 3. From the repository root:

```sh
python3 scripts/build.py
python3 -m http.server 8766 --directory docs
```

Open http://127.0.0.1:8766/. The preview includes proposed guidance and links to staff services. Resource availability notices do not represent released files.

## Checks

Requires Node.js compatible with jsdom 29:

```sh
npm install
npm test
```

Checks cover every interior template route, local links, search behaviour, request draft handling and theme switching. Browser testing is also required for visual changes.

## Local test mode (simulated Confluence)

The static preview can't show features that depend on Confluence: downloads from approved attachments, the Just added strip, the announcement banner and Confluence search. Local test mode serves the built Hub in its Confluence mode with a small stand-in for the Confluence REST API.

```sh
python3 scripts/build.py
python3 scripts/dev_fixtures.py        # reads dev/brandbank-map.json, writes dev/fixtures.json
python3 scripts/dev_server.py          # http://127.0.0.1:8767
python3 scripts/dev_server.py --no-approved      # nothing labelled "approved": fallbacks
python3 scripts/dev_server.py --no-announcement  # no announcement banner
```

`dev/` is excluded from Git. The map points at local files, which are streamed on download and never copied into the repository.

## Files on a page

- **Resource pages** (templates, logos, the Brand Book and similar) list the files attached to their Confluence page and labelled `approved`, grouped by the rules in `brandkit.DOWNLOAD_GROUPS`.
- **Pages people keep current themselves** (Recent talks, SKA-Low progress, SKA-Mid progress) list every file attached to the page, newest first, with no label needed. A file name starting with the year and month (`2026-10 Name Event.pptx`) shows that month. Staff need permission to add attachments to those pages.
- **Links to internal documents** (status slides, forms, policies) are named in `scripts/links.py`, but their addresses live in `dev/links.json`, which is not in Git: this repo is public and some of those documents open for anyone with the link. `scripts/package.py` builds the release with them and then rebuilds the committed files without them; local test mode fills them in as it serves each page. A name with no address shows as "link to follow" in the preview, and the production theme leaves the content that depends on it out.

## Canto showcase

Photos and video shows a slideshow of the Canto **Staff media library** folder, and Video and animation shows matching video albums. Staff browsers never talk to Canto: `scripts/canto_sync.py` copies web-sized previews and a manifest (`canto-showcase.json`) into attachments on one Hub page, and the theme reads them from Confluence.

```sh
export CANTO_DOMAIN=skao CANTO_APP_ID=... CANTO_APP_SECRET=...   # or CANTO_API_KEY (a generated token)
export CANTO_FOLDER_PATH="Staff media library"
python3 scripts/canto_sync.py --dry-run --out build/canto   # check what would be published
python3 scripts/canto_sync.py --dry-run --env dev/canto.env   # same, reading settings from a local file (dev/ is not in Git)
export CONFLUENCE_BASE=https://confluence.skatelescope.org CONFLUENCE_TOKEN=... CONFLUENCE_PAGE_ID=381891718
python3 scripts/canto_sync.py                               # publish to the Photos and video page
```

- Run it on a schedule (for example daily) or from a Canto webhook. Keep credentials in the scheduler's secrets, never in this repository.
- **What is shown.** Only approved, credited assets of at least 2,000 px (videos only in video collections), and never anything whose description or tags say it is not cleared (for example "heritage review", "pending", "embargo", "draft"). Collections come from the folder structure (SKA-Low, SKA-Mid, Hero shots, Events 2026…); collections with fewer than 3 suitable assets are left out.
- **How it is chosen.** Assets are scored on description quality, tags, landscape shape, resolution, recency and strong subjects (aerials, dishes, stations, night sky), with weak subjects (vehicles, offices, screenshots) lower. No more than a few per album, one per numbered frame sequence, one per title, identical files and visually near-identical images once. People-tagged assets rank lower outside Events.
- **Highlights.** The Photos and video slideshow is a separate pick across the image collections: images without people, at most 1 composite, 2 night skies, 3 aerials and 2 artist impressions.
- **Editorial control in Canto.** Tag an asset **Hub feature** to pin it to Highlights. Add the **People** keyword where people are the subject (canto-metadata-assistant's people detection can apply it). Keep titles and descriptions meaningful; file-like names fall back to the first sentence of the description.
- **View only.** The Hub shows the images as a slideshow (autoplay, pause, previous and next; still for reduced motion) so staff can see what is in Canto; the "Open the Canto library" button under it opens the library, or the album on a topic page. Images are resized to 1280 px and stripped of embedded metadata (including location).
- The manifest still records each asset's link in the private **SKAO Staff** portal (`/v/SKAOStaff/album/{album}?column=image&id=…`), and every general Canto link on the Hub opens the portal. Staff sign in as Consumers with access to that portal only (self-registration with their SKAO email, or SSO later). `CANTO_PORTAL=library` switches tiles to the main Canto library over the asset's album (`/album/{album}?column=image&id=…`), and album links open `/album/{id}`. Override with `CANTO_ASSET_URL`, `CANTO_ALBUM_URL` and `CANTO_FOLDER_URL`. Portal links (`/v/SKAOLibrary/…`) don't work here because the staff folder isn't shared to that portal.
- Albums appear on topic pages when their name contains the page's keywords (`CANTO_STRIPS` in `scripts/polish.py`).
- Local test mode uses the real dry-run output in `build/canto` when it exists (rerun `scripts/dev_fixtures.py` after a dry run), otherwise stand-in albums from local images (`canto_standin` in `dev/brandbank-map.json`).

## Build packages

```sh
python3 scripts/package.py
python3 scripts/staging_files.py
```

Generated archives and flat staging upload files are written under `release/` and excluded from Git. Building or pushing this branch does not assign the theme to a live Confluence site.

## Working conventions

- Make changes on the redesign branch and commit coherent reviewed batches.
- Rebuild previews and run the checks before pushing.
- Keep private research, project ledgers, transcripts and deployment evidence outside the public repository.
- Theme-rendered review copy must be reconciled with canonical Confluence content before rollout, so search and displayed text agree.
- Staff access and resource release readiness require separate verification.

The request helper prepares local text only; users submit requests through the linked helpdesk. Media browsing and contribution routes are distinct. Presentations remain in the Hub and media remains in Canto.
