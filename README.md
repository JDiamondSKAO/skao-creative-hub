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
