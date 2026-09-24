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

## Canto showcase

Photos and video shows a gallery of the Canto **Staff media library** folder, and Telescope imagery, Hero images and Event photography show matching albums. Staff browsers never talk to Canto: `scripts/canto_sync.py` copies web-sized previews and a manifest (`canto-showcase.json`) into attachments on one Hub page, and the theme reads them from Confluence. Tiles open the asset in Canto.

```sh
export CANTO_DOMAIN=skao CANTO_API_KEY=...            # or CANTO_APP_ID / CANTO_APP_SECRET
export CANTO_FOLDER_PATH="Staff media library"
python3 scripts/canto_sync.py --dry-run --out build/canto   # check what would be published
python3 scripts/canto_sync.py --dry-run --env dev/canto.env   # same, reading settings from a local file (dev/ is not in Git)
export CONFLUENCE_BASE=https://confluence.skatelescope.org CONFLUENCE_TOKEN=... CONFLUENCE_PAGE_ID=381891718
python3 scripts/canto_sync.py                               # publish to the Photos and video page
```

- Run it on a schedule (for example daily) or from a Canto webhook. Keep credentials in the scheduler's secrets, never in this repository.
- Only images in albums under the folder are published. Thumbnails are resized to 640 px and stripped of embedded metadata (including location).
- `CANTO_ASSET_URL` and `CANTO_ALBUM_URL` set where tiles link (defaults: `https://{domain}.canto.global/asset/{id}` and `/album/{id}`). Use portal links if staff reach Canto through the SKAO Library portal.
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
