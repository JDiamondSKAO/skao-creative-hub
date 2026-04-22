# SKAO Creative Hub — Scroll Viewport Theme

The SKAO Creative Hub is an internal Confluence portal for SKA Observatory staff — a central resource for brand guidelines, templates, assets, event support, and creative production tooling. This repository holds the **Scroll Viewport theme** that skins the hub's Confluence space (`CRH`) and a **static GitHub Pages demo** that shows the theme in action without needing Confluence access.

## What's in the repo

```
.
├── page.vm                 Scroll Viewport page template (Apache Velocity)
├── css/                    Theme stylesheets
│   ├── style.css           Main — layout, components, content patterns
│   └── eggs.css            Hidden surprises (easter eggs)
├── js/                     Theme JavaScript
│   ├── main.js             Core behaviours — search, nav, theme toggle, feedback
│   └── eggs.js             Hidden surprises
├── images/                 Theme assets (logo, mark, header background)
├── docs/                   Static GitHub Pages build — serves the public demo
│   ├── index.html          Homepage (demo render)
│   ├── assets/             Copies of css/js/images
│   └── …                   Sample section and leaf pages
├── scripts/                Helpers (content-to-HTML builders, release prep)
└── README.md               This file
```

## What the theme does

Built on Scroll Viewport for Confluence Data Centre, the theme transforms a plain Confluence space into a branded portal:

- **Two-row header** — logo + nav strip, auto-overflows into "More" dropdown if section count ever exceeds 6.
- **Dynamic icon matching** on category cards — contributors renaming pages never breaks the UI.
- **Contextual sidebar** that walks the page tree up to four levels.
- **Ctrl+K search modal** backed by Confluence's CQL REST API.
- **Recent updates grid** auto-populated from the three most recently modified pages.
- **Dark mode** with View Transitions API circular reveal, OS preference detection, localStorage persistence.
- **Accessibility** — skip-to-content, keyboard shortcuts (`?` for help, `D` for dark, `T` for top), WCAG-AA focus rings.
- **Content patterns** — reusable download cards, Canto cards, colour swatches, figures, and related-link grids documented on the in-Confluence **Content Patterns** page.
- **Audience tag strip** — driven by Confluence page labels (`audience-staff`, `audience-partner`, `audience-internal`, `status-draft`, `status-deprecated`).
- **Print stylesheet** for brand-book pages that staff will actually print.

## Running the theme inside Confluence

1. Zip the repo root — include `page.vm`, `css/`, `js/`, `images/`. Exclude `docs/`, `scripts/`, `README.md`.
2. Upload to Scroll Viewport as a custom theme.
3. Attach the theme to the `CRH` Confluence space.
4. Make sure the space home page is set correctly — the theme walks up to it for nav.

## The GitHub Pages demo

`docs/` contains a static-rendered version of the hub, served by GitHub Pages. The demo is generic — no internal content — and is for:

- Showing the theme to external parties (vendors, interviewers, new hires) without Confluence access
- Pressure-testing content patterns before they hit the real space
- Portfolio/documentation

### Limitations of the static build

- **Search** runs against a local JSON index, not Confluence CQL.
- **Recent updates** are hardcoded in the static HTML.
- **"New" badges** based on last-modified dates are stripped (no lastmod data in static files).
- **`$homePage.children` nav generation** is hardcoded in each page.
- **Page feedback widget** links to a demo URL, not the real Jira Service Desk.

These are acceptable for a demo. If the maintenance burden becomes real, rebuild with 11ty or Jekyll using a single nav partial.

## Writing content for the hub

All content authoring follows the **Content Patterns** page inside the Confluence space. Patterns are storage-format snippets that you paste into your page, edit the text, and publish. The theme styles the result automatically.

The pattern source lives at [`../creative-hub/pages/tools-resources/content-patterns.xml`](../creative-hub/pages/tools-resources/content-patterns.xml) in the vault.

## Conventions

- **`crh-` class prefix** — everything. Avoids collisions with Confluence AUI classes.
- **`.content-body` + `.crh-content-body`** on main content containers — the former is Confluence-native, the latter is theme-styled. Both coexist.
- **No inline styles in content pages** — patterns handle this. If you find yourself writing `style="…"`, raise a ticket.
- **Canto is the DAM, Confluence is the wrapper** — never upload brand imagery as page attachments.

## Roadmap / known gaps

- [ ] Image gallery pattern (logo variants, icon sheets)
- [ ] Proper feedback endpoint (currently "No" routes to helpdesk with page context; "Yes" is local only)
- [ ] Search-index generator script for the static build
- [ ] Redirect widget for deprecated-page handling
- [ ] Matter.js 404 lazy-loaded only after user interaction (currently conditional, but still a chunky dep)
- [ ] Consider rebuilding the static demo with 11ty if hand-edited pages exceed ~6

## Licence

The theme **code** (HTML/CSS/JS/VM) — TBD, but intended to be MIT so it can be reused by other SKAO projects and the wider Scroll Viewport community.

The **SKAO brand assets** in `images/` (logos, marks, photography) are © SKA Observatory and are not licensed for reuse outside SKAO contexts.

## Contact

Built and maintained by Joe Diamond, Creative Production Lead at SKAO.
Contributions: raise a Jira Service Desk ticket at the [creative helpdesk](https://jira.skatelescope.org/servicedesk/customer/portal/364) or contact comms@skao.int.
