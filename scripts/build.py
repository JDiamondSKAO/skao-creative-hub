#!/usr/bin/env python3
"""
Creative Hub — static site builder.

Stamps out the docs/ folder from a single shared shell (header, nav, footer,
scripts) plus a per-page body. Keeps docs/ in sync with the theme without
touching 10 near-identical HTML files by hand.

Usage:
    python3 scripts/build.py              # build all pages
    python3 scripts/build.py --help       # usage
    python3 scripts/build.py --list       # show pages that will be built

Pages are defined in PAGES below. Each page has a slug (output folder),
title, section (drives the active nav link), breadcrumbs, and a body
fragment (the main article content). The shell wraps the body in the
standard header / sidebar / main / footer scaffold.

The homepage has its own layout (crh-home body class, hero, category
grid) and is kept in docs/index.html as a hand-written file — it's too
structurally different to template well.
"""
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
import argparse
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS = REPO_ROOT / "docs"


# ---------------------------------------------------------------------------
# PAGE MODEL
# ---------------------------------------------------------------------------

@dataclass
class SidebarLink:
    title: str
    href: str
    active: bool = False
    children: List["SidebarLink"] = field(default_factory=list)


@dataclass
class Crumb:
    title: str
    href: str


@dataclass
class PageNavLink:
    label: str          # "Previous" or "Next"
    title: str
    href: str


@dataclass
class Page:
    slug: str                               # output folder under docs/
    title: str
    section: str                            # one of SECTIONS keys
    breadcrumbs: List[Crumb]
    body: str                               # HTML fragment, drops into <article>
    is_leaf: bool = True                    # leaf pages get feedback widget
    sidebar: List[SidebarLink] = field(default_factory=list)
    prev: Optional[PageNavLink] = None
    next: Optional[PageNavLink] = None
    audience_tags: List[str] = field(default_factory=list)
    description: str = ""


# ---------------------------------------------------------------------------
# SHARED FRAGMENTS (header, footer, modals — identical across all pages)
# ---------------------------------------------------------------------------

SECTIONS = {
    "home":               ("Home",                 "../index.html"),
    "whats-new":          ("What\u2019s New",       "../whats-new/"),
    "brand-guidelines":   ("Brand Guidelines",     "../brand-guidelines/"),
    "templates-assets":   ("Templates &amp; Assets","../templates-assets/"),
    "how-to-work-with-us":("How To Work With Us",  "../how-to-work-with-us/"),
    "events-support":     ("Events Support",       "../events-support/"),
    "tools-resources":    ("Tools &amp; Resources", "../tools-resources/"),
}


def head(title: str, depth: int, description: str = "") -> str:
    """depth = how many levels deep (1 = docs/foo/, 2 = docs/foo/bar/). Used to prefix asset paths."""
    up = "../" * depth
    desc = description or "SKAO Creative Hub — a Scroll Viewport theme for SKA Observatory's internal creative production portal."
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} &mdash; SKAO Creative Hub</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/css/style.css?v=3">
<link rel="stylesheet" href="{up}assets/css/eggs.css?v=3">
<script>
(function(){{try{{var s=localStorage.getItem('crh-theme');if(s==='dark'){{document.documentElement.classList.add('dark')}}else if(!s&&window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches){{document.documentElement.classList.add('dark')}}}}catch(e){{}}}})();
</script>
</head>"""


def header(active_section: str, depth: int) -> str:
    """Main site header with nav strip. active_section drives the active link class."""
    up = "../" * depth
    nav_items = []
    for key, (label, _) in SECTIONS.items():
        if key == "home":
            href = f"{up}index.html"
        else:
            href = f"{up}{key}/"
        active_cls = " crh-nav-active" if key == active_section else ""
        if key == "home":
            nav_items.append(f'<li><a href="{href}" class="crh-nav-link{active_cls}"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg> Home</a></li>')
        else:
            nav_items.append(f'<li><a href="{href}" class="crh-nav-link{active_cls}">{label}</a></li>')
    nav_html = "\n        ".join(nav_items)
    return f"""
<a href="#main-content" class="skip-to-content">Skip to main content</a>
<div class="crh-progress-bar" id="crhProgressBar" role="progressbar" aria-hidden="true"></div>

<div class="crh-search-modal" id="searchModal" role="dialog" aria-modal="true" style="display:none;">
  <div class="crh-search-modal-backdrop" id="searchBackdrop"></div>
  <div class="crh-search-modal-dialog">
    <div class="crh-search-modal-header">
      <h2 class="crh-search-modal-title">Search the Creative Hub</h2>
      <button class="crh-search-modal-close" id="closeSearchModal" aria-label="Close search">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </div>
    <form class="crh-search-form" id="searchForm" role="search">
      <div class="crh-search-input-wrapper">
        <svg class="crh-search-input-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="text" id="searchInput" class="crh-search-input" placeholder="Search..." autocomplete="off">
      </div>
    </form>
    <div class="crh-search-results" id="searchResults">
      <div class="crh-search-empty"><p>Search is live in Confluence. Disabled in this static demo.</p></div>
    </div>
  </div>
</div>

<header class="crh-header">
  <div class="crh-header-bg"></div>
  <div class="crh-header-overlay"></div>
  <div class="crh-header-bar">
    <div class="crh-header-inner">
      <a href="{up}index.html" class="crh-brand-link" aria-label="SKAO Creative Hub Home">
        <img src="{up}assets/images/skao-logo-white.png" alt="SKAO Logo" class="crh-logo-img">
        <span class="crh-site-title">Creative Hub</span>
      </a>
      <div class="crh-header-actions">
        <button class="crh-theme-toggle" id="themeToggle" aria-label="Toggle dark mode" title="Toggle dark mode">
          <svg class="crh-theme-icon-light" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          <svg class="crh-theme-icon-dark" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        </button>
      </div>
    </div>
  </div>
  <nav class="crh-nav-strip" aria-label="Main navigation">
    <div class="crh-nav-strip-inner">
      <ul class="crh-nav-list">
        {nav_html}
      </ul>
    </div>
  </nav>
</header>
"""


def footer(depth: int) -> str:
    up = "../" * depth
    return f"""
<footer class="crh-footer">
  <div class="crh-footer-inner">
    <div class="crh-footer-columns">
      <div class="crh-footer-column">
        <h4>About SKAO</h4>
        <ul>
          <li><a href="https://skao.int/about" target="_blank" rel="noopener">About Us</a></li>
          <li><a href="https://skao.int/careers" target="_blank" rel="noopener">Careers</a></li>
          <li><a href="https://skao.int/news" target="_blank" rel="noopener">News</a></li>
          <li><a href="https://skao.int/contact" target="_blank" rel="noopener">Contact</a></li>
        </ul>
      </div>
      <div class="crh-footer-column">
        <h4>Hub Sections</h4>
        <ul>
          <li><a href="{up}whats-new/">What&rsquo;s New</a></li>
          <li><a href="{up}brand-guidelines/">Brand Guidelines</a></li>
          <li><a href="{up}templates-assets/">Templates &amp; Assets</a></li>
          <li><a href="{up}how-to-work-with-us/">How To Work With Us</a></li>
          <li><a href="{up}events-support/">Events Support</a></li>
          <li><a href="{up}tools-resources/">Tools &amp; Resources</a></li>
        </ul>
      </div>
      <div class="crh-footer-column">
        <h4>Quick Links</h4>
        <ul>
          <li><a href="https://skao.canto.global/v/SKAOLibrary?from_main_library" target="_blank" rel="noopener">Canto DAM</a></li>
          <li><a href="https://fonts.google.com/noto/specimen/Noto+Sans" target="_blank" rel="noopener">Brand Fonts</a></li>
          <li><a href="https://github.com/JDiamondSKAO/skao-creative-hub" target="_blank" rel="noopener">Source on GitHub</a></li>
        </ul>
      </div>
      <div class="crh-footer-column">
        <h4>Support</h4>
        <ul>
          <li><a href="https://jira.skatelescope.org/servicedesk/customer/portal/364" target="_blank" rel="noopener">Creative Helpdesk</a></li>
          <li><a href="https://jira.skatelescope.org/servicedesk/customer/portal/298" target="_blank" rel="noopener">HSSE Helpdesk</a></li>
          <li><a href="mailto:comms@skao.int">comms@skao.int</a></li>
        </ul>
      </div>
    </div>
    <div class="crh-footer-bottom">
      <p class="crh-footer-copyright">&copy; 2026 SKA Observatory. Static demo build. Source on <a href="https://github.com/JDiamondSKAO/skao-creative-hub" target="_blank" rel="noopener" style="color:rgba(255,255,255,0.75);text-decoration:underline;">GitHub</a>.</p>
      <button class="crh-footer-easter-egg" id="footerStar" aria-label="Secret surprise" title="\u2b50">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path d="M10 1.5l3 6h6.5l-5.2 4 2 6.5L10 15l-5.3 4 2-6.5L.5 7.5H7l3-6z"/></svg>
      </button>
    </div>
  </div>
</footer>
<button class="crh-back-to-top" id="backToTop" aria-label="Back to top" title="Back to top">
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="18 15 12 9 6 15"/></svg>
</button>
<script src="{up}assets/js/main.js?v=3"></script>
<script src="{up}assets/js/eggs.js?v=3"></script>
</body>
</html>"""


def render_breadcrumbs(crumbs: List[Crumb], current: str) -> str:
    parts = []
    for c in crumbs:
        parts.append(f'<a href="{c.href}" class="crh-breadcrumb-link">{c.title}</a><svg class="crh-breadcrumb-sep" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>')
    parts.append(f'<span class="crh-breadcrumb-current">{current}</span>')
    return '\n'.join(parts)


def render_sidebar(links: List[SidebarLink], section_title: str, section_href: str) -> str:
    if not links:
        return '<aside class="crh-sidebar" id="sidebarPanel"><div class="crh-sidebar-inner"></div></aside>'
    items = []
    for link in links:
        active_cls = " crh-sidebar-active" if link.active else ""
        open_cls = " crh-sidebar-open" if link.active or any(c.active for c in link.children) else ""
        item = f'<li class="crh-sidebar-item{open_cls}"><a href="{link.href}" class="crh-sidebar-link{active_cls}">{link.title}</a>'
        if link.children and (link.active or any(c.active for c in link.children)):
            child_items = []
            for child in link.children:
                child_active = " crh-sidebar-active" if child.active else ""
                child_items.append(f'<li><a href="{child.href}" class="crh-sidebar-link crh-sidebar-leaf{child_active}">{child.title}</a></li>')
            item += f'<ul class="crh-sidebar-grandchildren">{"".join(child_items)}</ul>'
        item += '</li>'
        items.append(item)
    return f"""<aside class="crh-sidebar" id="sidebarPanel">
  <div class="crh-sidebar-inner">
    <nav class="crh-sidebar-nav" aria-label="Section navigation">
      <a href="{section_href}" class="crh-sidebar-section-link">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
        {section_title}
      </a>
      <ul class="crh-sidebar-tree">
        {"".join(items)}
      </ul>
    </nav>
  </div>
</aside>"""


def render_audience_strip(tags: List[str]) -> str:
    if not tags:
        return ""
    variants = {
        "staff":      ("For staff",      ""),
        "partner":    ("Partner-safe",   "partner"),
        "internal":   ("Internal only",  "internal"),
        "draft":      ("Draft",          "draft"),
        "deprecated": ("Deprecated",     "deprecated"),
    }
    items = []
    for t in tags:
        if t in variants:
            label, variant = variants[t]
            attr = f' data-variant="{variant}"' if variant else ''
            items.append(f'<li><span class="crh-audience-tag"{attr}>{label}</span></li>')
    return f'<ul class="crh-audience-strip" aria-label="Page audience and status">{"".join(items)}</ul>'


def render_feedback() -> str:
    return """<div class="crh-feedback-widget" id="pageFeedback">
  <div class="crh-feedback-question">
    <span class="crh-feedback-label">Was this page helpful?</span>
    <div class="crh-feedback-buttons">
      <button class="crh-feedback-btn crh-feedback-yes" data-vote="yes" aria-label="Yes, helpful"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3H14z"/><path d="M7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"/></svg> Yes</button>
      <button class="crh-feedback-btn crh-feedback-no" data-vote="no" aria-label="No, not helpful"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3H10z"/><path d="M17 2h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"/></svg> No</button>
    </div>
  </div>
  <div class="crh-feedback-thanks" id="pfThanks" style="display:none;">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
    <span>Thank you for your feedback!</span>
  </div>
</div>"""


def render_page_nav(prev: Optional[PageNavLink], next_: Optional[PageNavLink]) -> str:
    if not prev and not next_:
        return ""
    prev_html = f'<a href="{prev.href}" class="crh-nav-button"><span class="crh-nav-label">Previous</span><span class="crh-nav-title">{prev.title}</span></a>' if prev else ""
    next_html = f'<a href="{next_.href}" class="crh-nav-button"><span class="crh-nav-label">Next</span><span class="crh-nav-title">{next_.title}</span></a>' if next_ else ""
    return f'<nav class="crh-page-nav"><div class="crh-nav-prev">{prev_html}</div><div class="crh-nav-next">{next_html}</div></nav>'


def render_page(p: Page) -> str:
    depth = p.slug.count("/") + 1
    section_label, section_href = SECTIONS.get(p.section, (p.section, f"{'../' * depth}{p.section}/"))
    sidebar_html = render_sidebar(p.sidebar, section_label, section_href)
    breadcrumb_html = render_breadcrumbs(p.breadcrumbs, p.title)
    tag_strip_html = render_audience_strip(p.audience_tags)
    feedback_html = render_feedback() if p.is_leaf else ""
    page_nav_html = render_page_nav(p.prev, p.next)

    return f"""{head(p.title, depth, p.description)}
<body>
{header(p.section, depth)}
<div class="crh-layout">
  {sidebar_html}
  <button class="crh-sidebar-toggle" id="sidebarToggle" aria-label="Open navigation panel">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
  </button>
  <main id="main-content" class="crh-main">
    <article class="crh-content">
      <nav class="crh-breadcrumbs" aria-label="Breadcrumb">
        {breadcrumb_html}
      </nav>
      {tag_strip_html}
      <h1 class="crh-page-title">{p.title}</h1>
      <div class="crh-article-meta">
        <span class="crh-article-date">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
          <span class="crh-article-date-text">Demo content</span>
        </span>
      </div>
      <div class="crh-content-body content-body">
        {p.body}
      </div>
      {feedback_html}
      {page_nav_html}
    </article>
  </main>
</div>
{footer(depth)}"""


# ---------------------------------------------------------------------------
# SIDEBARS (per section — all leaf pages in a section share the same sidebar)
# ---------------------------------------------------------------------------

def brand_sidebar(active_slug: str = "") -> List[SidebarLink]:
    return [
        SidebarLink("Logo Usage",  "../logo-usage/",  active=(active_slug == "logo-usage")),
        SidebarLink("Colour Palette", "../colour-palette/", active=(active_slug == "colour-palette")),
    ]


def templates_sidebar(active_slug: str = "") -> List[SidebarLink]:
    return [
        SidebarLink("Letterhead", "../letterhead/", active=(active_slug == "letterhead")),
    ]


def tools_sidebar(active_slug: str = "") -> List[SidebarLink]:
    return [
        SidebarLink("Content Patterns", "../content-patterns/", active=(active_slug == "content-patterns")),
    ]


# ---------------------------------------------------------------------------
# PAGE DEFINITIONS
# ---------------------------------------------------------------------------

def section_child_grid(cards: List[tuple]) -> str:
    """cards = [(href, title, description_or_None), ...]"""
    items = []
    for href, title, desc in cards:
        desc_html = f'<p class="crh-child-card-desc">{desc}</p>' if desc else ""
        items.append(f"""<a href="{href}" class="crh-child-card">
          <div class="crh-child-card-content">
            <h3 class="crh-child-card-title">{title}</h3>
            {desc_html}
          </div>
          <span class="crh-child-card-arrow"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></span>
        </a>""")
    return f"""<div class="crh-child-pages">
  <h2 class="crh-child-pages-heading">Pages in this section</h2>
  <div class="crh-child-grid">
    {"".join(items)}
  </div>
</div>"""


def empty_state(title: str, body: str) -> str:
    return f"""<div class="crh-empty-state">
  <h3>{title}</h3>
  <p>{body}</p>
</div>"""


PAGES: List[Page] = [

    # -------- WHAT'S NEW --------
    Page(
        slug="whats-new",
        title="What\u2019s New",
        section="whats-new",
        breadcrumbs=[Crumb("Home", "../index.html")],
        is_leaf=False,
        audience_tags=["staff"],
        body="""<p>Welcome to the Creative Hub changelog. Latest additions, changes, and announcements across the hub — new resources, updated guidelines, and improvements to how we work together.</p>

<h3>March 2026</h3>
<ul>
  <li>Creative Hub restructure completed — cleaner navigation, merged Templates &amp; Assets section.</li>
  <li>Brand Guidelines section expanded with co-branding guidance and updated tone-of-voice examples.</li>
  <li>New Templates &amp; Assets section consolidates logos, brand templates, presentation decks, and print files in one place.</li>
  <li>Events Support section updated with 2026&ndash;2027 event calendar and lead time guidance.</li>
</ul>

<h3>Coming next</h3>
<ul>
  <li>Expanded video production guidelines and asset templates.</li>
  <li>Animation and motion design best practices section.</li>
  <li>Case studies and project examples from recent SKAO campaigns.</li>
</ul>

<div class="crh-related-grid">
  <a href="../brand-guidelines/">Brand Guidelines</a>
  <a href="../templates-assets/">Templates &amp; Assets</a>
  <a href="../tools-resources/content-patterns/">Content Patterns</a>
</div>""",
    ),

    # -------- BRAND GUIDELINES --------
    Page(
        slug="brand-guidelines",
        title="Brand Guidelines",
        section="brand-guidelines",
        breadcrumbs=[Crumb("Home", "../index.html")],
        is_leaf=False,
        audience_tags=["staff"],
        body=f"""<p>The SKAO brand represents 16 member countries united in building the world&rsquo;s largest radio telescope. Maintaining a consistent, professional visual identity across all communications strengthens our standing as a world-class scientific organisation.</p>

<p>This section provides guidance on SKAO brand standards to ensure clarity and consistency across all your work.</p>

<div class="confluence-information-macro confluence-information-macro-information">
  <div class="confluence-information-macro-body"><p><strong>The Brand Book is the foundational document for all SKAO branding.</strong> It covers brand values, visual identity, logo construction, colour palette, typography, imagery guidelines, and real-world application examples.</p></div>
</div>

<h2>What this section covers</h2>
<ul>
  <li><strong>Logo Usage</strong> &mdash; primary and secondary logos, clear space, sizing, and placement rules.</li>
  <li><strong>Colour Palette</strong> &mdash; SKAO primary and secondary colours with RGB, HEX, and Pantone specifications.</li>
</ul>

{section_child_grid([
    ("logo-usage/",     "Logo Usage",     "Primary and secondary logos, clear space, sizing, placement rules."),
    ("colour-palette/", "Colour Palette", "Primary and secondary colours with RGB, HEX, and Pantone specifications."),
])}""",
    ),

    Page(
        slug="brand-guidelines/logo-usage",
        title="Logo Usage",
        section="brand-guidelines",
        breadcrumbs=[Crumb("Home", "../../index.html"), Crumb("Brand Guidelines", "../")],
        sidebar=brand_sidebar("logo-usage"),
        audience_tags=["staff", "partner"],
        prev=None,
        next=PageNavLink("Next", "Colour Palette", "../colour-palette/"),
        body="""<p>The SKAO logo is the most recognisable element of our visual identity. Correct use across materials is the single most important brand rule &mdash; everything else follows from it.</p>

<h3>Logo variants</h3>
<ul>
  <li><strong>Primary</strong> &mdash; full colour on white or very light backgrounds.</li>
  <li><strong>Reverse</strong> &mdash; white logo on dark or coloured backgrounds.</li>
  <li><strong>Monochrome</strong> &mdash; black for single-colour print (e.g. internal memos, faxes).</li>
  <li><strong>Stacked</strong> &mdash; for narrow spaces where the horizontal version doesn&rsquo;t fit.</li>
</ul>

<h3>Clear space</h3>
<p>Always maintain clear space around the logo equal to the height of the &ldquo;S&rdquo; in &ldquo;SKAO&rdquo;. Nothing should encroach on this space &mdash; no text, images, borders, or other elements.</p>

<figure class="crh-figure">
  <div style="background:linear-gradient(135deg,#9333ea,#C8247E,#003366);aspect-ratio:16/9;border-radius:10px;display:flex;align-items:center;justify-content:center;"><img src="../../assets/images/skao-logo-white.png" alt="SKAO logo on brand gradient" style="height:80px;" class="no-dim"></div>
  <figcaption>The SKAO primary logo on the brand gradient. Use this combination for hero sections and landing pages.<cite>SKAO Brand</cite></figcaption>
</figure>

<h3>Download the logo pack</h3>
<p>All logo variants live in Canto. Please use the latest files &mdash; older variants (pre-2024) are deprecated.</p>

<a class="crh-canto-card" href="https://skao.canto.global/" target="_blank" rel="noopener">
  <span class="crh-canto-badge">Canto</span>
  <span class="crh-canto-title">SKAO Logo &mdash; Primary Pack</span>
  <span class="crh-canto-desc">EPS, SVG, PNG (colour, white, black, stacked). 12 files. Updated March 2026.</span>
  <span class="crh-canto-arrow">Open in Canto &rarr;</span>
</a>

<div class="crh-download-card">
  <div class="crh-download-icon" data-type="zip"></div>
  <div class="crh-download-meta">
    <strong class="crh-download-name">skao-logo-pack-2026.zip</strong>
    <span class="crh-download-detail">ZIP archive &middot; 2.4 MB &middot; 12 files</span>
  </div>
  <a class="crh-download-btn" href="#demo" onclick="alert('Demo build \u2014 no actual file. In the live hub, this downloads from Confluence attachments.');return false;">Download</a>
</div>

<div class="crh-download-card">
  <div class="crh-download-icon" data-type="pdf"></div>
  <div class="crh-download-meta">
    <strong class="crh-download-name">Logo-Usage-Guidelines.pdf</strong>
    <span class="crh-download-detail">PDF &middot; 340 KB &middot; 8 pages</span>
  </div>
  <a class="crh-download-btn" href="#demo" onclick="alert('Demo build \u2014 no actual file.');return false;">Download</a>
</div>

<h3>Do and don\u2019t</h3>
<ul>
  <li><strong>Do</strong> maintain clear space equal to the height of the &ldquo;S&rdquo;.</li>
  <li><strong>Do</strong> use the reverse logo on dark backgrounds for contrast.</li>
  <li><strong>Don\u2019t</strong> stretch, skew, or rotate the logo.</li>
  <li><strong>Don\u2019t</strong> place the logo on busy or low-contrast backgrounds.</li>
  <li><strong>Don\u2019t</strong> recreate the logo &mdash; always use the official files.</li>
</ul>

<h3>Related pages</h3>
<div class="crh-related-grid">
  <a href="../colour-palette/">Colour Palette</a>
  <a href="../../templates-assets/">Templates &amp; Assets</a>
  <a href="../../tools-resources/content-patterns/">Content Patterns</a>
</div>""",
    ),

    Page(
        slug="brand-guidelines/colour-palette",
        title="Colour Palette",
        section="brand-guidelines",
        breadcrumbs=[Crumb("Home", "../../index.html"), Crumb("Brand Guidelines", "../")],
        sidebar=brand_sidebar("colour-palette"),
        audience_tags=["staff", "partner"],
        prev=PageNavLink("Previous", "Logo Usage", "../logo-usage/"),
        next=None,
        body="""<p>The SKAO colour palette carries the brand across every touchpoint &mdash; from web to print to exhibitions. Consistent application is the fastest way to make any piece of work feel unmistakably SKAO.</p>

<h3>Primary palette</h3>
<p>The three-colour gradient that appears in our header treatments. Use in full when branding moments matter. Individual colours may be used as accents or solids.</p>

<div class="crh-swatch-grid">
  <figure class="crh-swatch" data-hex="#9333ea">
    <span class="crh-swatch-chip" style="background:#9333ea;"></span>
    <figcaption>
      <strong>SKAO Purple</strong>
      <span>#9333EA \u00b7 RGB 147 51 234 \u00b7 PMS 2592 C</span>
    </figcaption>
  </figure>
  <figure class="crh-swatch" data-hex="#C8247E">
    <span class="crh-swatch-chip" style="background:#C8247E;"></span>
    <figcaption>
      <strong>SKAO Magenta</strong>
      <span>#C8247E \u00b7 RGB 200 36 126 \u00b7 PMS 227 C</span>
    </figcaption>
  </figure>
  <figure class="crh-swatch" data-hex="#003366">
    <span class="crh-swatch-chip" style="background:#003366;"></span>
    <figcaption>
      <strong>SKAO Navy</strong>
      <span>#003366 \u00b7 RGB 0 51 102 \u00b7 PMS 540 C</span>
    </figcaption>
  </figure>
</div>

<h3>Neutrals</h3>
<p>For body text, UI chrome, and content backgrounds. Use the lightest slates for page backgrounds in light mode and the deepest for dark mode.</p>

<div class="crh-swatch-grid">
  <figure class="crh-swatch"><span class="crh-swatch-chip" style="background:#0f172a;"></span><figcaption><strong>Slate 900</strong><span>#0F172A \u00b7 Body text</span></figcaption></figure>
  <figure class="crh-swatch"><span class="crh-swatch-chip" style="background:#475569;"></span><figcaption><strong>Slate 600</strong><span>#475569 \u00b7 Secondary text</span></figcaption></figure>
  <figure class="crh-swatch"><span class="crh-swatch-chip" style="background:#cbd5e1;"></span><figcaption><strong>Slate 300</strong><span>#CBD5E1 \u00b7 Borders</span></figcaption></figure>
  <figure class="crh-swatch"><span class="crh-swatch-chip" style="background:#f8fafc;border:1px solid #e2e8f0;"></span><figcaption><strong>Slate 50</strong><span>#F8FAFC \u00b7 Surfaces</span></figcaption></figure>
</div>

<h3>Usage guidance</h3>
<ul>
  <li>Use <strong>Purple</strong> as the primary accent on buttons, links, and interactive states.</li>
  <li>Use <strong>Magenta</strong> for campaign moments, highlights, and emotional emphasis.</li>
  <li>Use <strong>Navy</strong> as the grounding colour in typography-heavy contexts &mdash; letterheads, reports, publications.</li>
  <li>Never set body text in Purple or Magenta &mdash; contrast fails WCAG at body sizes.</li>
  <li>Always test colour combinations against WCAG AA contrast minimums (4.5:1 for body, 3:1 for large text).</li>
</ul>

<h3>Related pages</h3>
<div class="crh-related-grid">
  <a href="../logo-usage/">Logo Usage</a>
  <a href="../../tools-resources/">Accessibility Guidelines</a>
</div>""",
    ),

    # -------- TEMPLATES & ASSETS --------
    Page(
        slug="templates-assets",
        title="Templates &amp; Assets",
        section="templates-assets",
        breadcrumbs=[Crumb("Home", "../index.html")],
        is_leaf=False,
        audience_tags=["staff"],
        body=f"""<p>Ready-to-use templates, design assets, and media resources for creating professional SKAO-branded materials. Whether you&rsquo;re drafting a memo, preparing a conference presentation, or editing event video, you&rsquo;ll find what you need here.</p>

<p>Most image assets are stored and managed through our <strong>Canto Digital Asset Management</strong> system. If you need access to Canto or have trouble finding something, contact the creative production team at <a href="mailto:comms@skao.int">comms@skao.int</a>.</p>

<h2>What&rsquo;s here</h2>
<ul>
  <li><strong>Document Templates</strong> &mdash; Word templates for letterheads, report layouts, memo formats, and briefing documents.</li>
  <li><strong>Slide Decks</strong> &mdash; PowerPoint templates and a curated library of pre-made presentations to adapt.</li>
  <li><strong>Photography &amp; Media</strong> &mdash; Curated image collections via Canto.</li>
  <li><strong>Video &amp; Animation</strong> &mdash; Explainer animations, B-roll footage, event recordings.</li>
  <li><strong>Logos &amp; Icons</strong> &mdash; Official SKAO logo files in multiple formats and variants.</li>
  <li><strong>Print Materials</strong> &mdash; Business cards, pull-up banners, exhibition panels, posters, and leaflets.</li>
</ul>

{section_child_grid([
    ("letterhead/",  "Letterhead",  "Official letterhead template for formal correspondence."),
])}

{empty_state("More templates landing soon", "In the live hub, additional sub-sections (Slide Decks, Photography, Video, Logos, Print) each have their own landing page with curated downloads.")}""",
    ),

    Page(
        slug="templates-assets/letterhead",
        title="Letterhead",
        section="templates-assets",
        breadcrumbs=[Crumb("Home", "../../index.html"), Crumb("Templates & Assets", "../")],
        sidebar=templates_sidebar("letterhead"),
        audience_tags=["staff"],
        body="""<p>Official letterhead for formal correspondence from SKA Observatory. Includes SKAO logo, registered address, and pre-formatted text styles.</p>

<h3>What&rsquo;s included</h3>
<ul>
  <li>SKAO logo (header)</li>
  <li>Registered address and contact details</li>
  <li>Pre-formatted body text styles</li>
  <li>Footer with department/contact information</li>
  <li>Page breaks configured for multi-page letters</li>
</ul>

<h3>Download</h3>
<div class="crh-download-card">
  <div class="crh-download-icon" data-type="docx"></div>
  <div class="crh-download-meta">
    <strong class="crh-download-name">SKAO-Letterhead.docx</strong>
    <span class="crh-download-detail">Microsoft Word \u00b7 48 KB \u00b7 v1.2</span>
  </div>
  <a class="crh-download-btn" href="#demo" onclick="alert('Demo build \u2014 no actual file. In the live hub this downloads from Confluence attachments.');return false;">Download</a>
</div>

<h3>Usage guidelines</h3>
<ul>
  <li>Do not modify logo placement or size.</li>
  <li>Use standard fonts and styles provided.</li>
  <li>Maintain 1-inch margins on all sides.</li>
  <li>Update sender details in the footer before sending.</li>
</ul>

<h3>Related</h3>
<div class="crh-related-grid">
  <a href="../../brand-guidelines/logo-usage/">Logo Usage</a>
  <a href="../../brand-guidelines/colour-palette/">Colour Palette</a>
  <a href="../../tools-resources/content-patterns/">Content Patterns</a>
</div>""",
    ),

    # -------- HOW TO WORK WITH US --------
    Page(
        slug="how-to-work-with-us",
        title="How To Work With Us",
        section="how-to-work-with-us",
        breadcrumbs=[Crumb("Home", "../index.html")],
        is_leaf=False,
        audience_tags=["staff", "partner"],
        body=f"""<p>Everything you need to know about commissioning creative work at SKAO &mdash; from submitting a request to receiving the final asset.</p>

<h2>Quick links</h2>
<ul>
  <li><strong>Creative Helpdesk</strong> &mdash; <a href="https://jira.skatelescope.org/servicedesk/customer/portal/364" target="_blank" rel="noopener">Submit a request on Jira Service Desk</a>. Response within 2 working days.</li>
  <li><strong>Email</strong> &mdash; <a href="mailto:comms@skao.int">comms@skao.int</a> for simple questions.</li>
</ul>

<h2>Typical turnaround times</h2>
<ul>
  <li>Minor updates (logo swap, copy edit): 2\u20135 working days</li>
  <li>New slide deck or poster: 1\u20132 weeks</li>
  <li>Publication (Contact, Annual Report): 4\u20138 weeks</li>
  <li>Events / exhibitions: 6\u201312 weeks</li>
  <li>Video / animation: 8\u201316 weeks</li>
</ul>

{empty_state("Section under construction", "In the live hub, this section expands into FAQ, Self-Service Guides, Submitting a Request, and SLA pages.")}""",
    ),

    # -------- EVENTS SUPPORT --------
    Page(
        slug="events-support",
        title="Events Support",
        section="events-support",
        breadcrumbs=[Crumb("Home", "../index.html")],
        is_leaf=False,
        audience_tags=["staff"],
        body=f"""<p>Stand design, merchandise, checklists, and health &amp; safety guidance for SKAO events, conferences, and exhibitions.</p>

<h2>Key upcoming events</h2>
<ul>
  <li>APRIM 2026 &mdash; Hong Kong, May/Jun</li>
  <li>EAS 2026 &mdash; summer</li>
  <li>IAU GA 2027 &mdash; Rome</li>
  <li>AAS 2027 &mdash; early</li>
</ul>

{empty_state("Section under construction", "In the live hub, this section expands into Event Planning Checklist, Health &amp; Safety, Merchandise and Giveaways, and Vendor Directory pages.")}""",
    ),

    # -------- TOOLS & RESOURCES --------
    Page(
        slug="tools-resources",
        title="Tools &amp; Resources",
        section="tools-resources",
        breadcrumbs=[Crumb("Home", "../index.html")],
        is_leaf=False,
        audience_tags=["staff"],
        body=f"""<p>Access Canto, download fonts, find accessibility guidance, and use the Creative Hub&rsquo;s authoring patterns.</p>

<h2>External tools</h2>
<ul>
  <li><a href="https://skao.canto.global/v/SKAOLibrary?from_main_library" target="_blank" rel="noopener">Canto DAM</a> &mdash; digital asset management for SKAO imagery.</li>
  <li><a href="https://fonts.google.com/noto/specimen/Noto+Sans" target="_blank" rel="noopener">Noto Sans</a> &mdash; SKAO&rsquo;s primary typeface.</li>
  <li><a href="https://jira.skatelescope.org/servicedesk/customer/portal/364" target="_blank" rel="noopener">Creative Helpdesk</a> &mdash; Jira Service Desk for requests.</li>
</ul>

{section_child_grid([
    ("content-patterns/",  "Content Patterns",  "Copy-paste Confluence storage-format snippets for all hub content types."),
])}""",
    ),

    # -------- CONTENT PATTERNS (the bonus showcase page) --------
    Page(
        slug="tools-resources/content-patterns",
        title="Content Patterns",
        section="tools-resources",
        breadcrumbs=[Crumb("Home", "../../index.html"), Crumb("Tools & Resources", "../")],
        sidebar=tools_sidebar("content-patterns"),
        audience_tags=["staff"],
        body="""<p>Every pattern on this page has a copy-ready Confluence storage-format snippet (see the full reference inside Confluence). This static demo shows each one <em>in its rendered form</em> so you can see how the theme styles them before writing any content.</p>

<h2>1. Download cards</h2>
<p>For any downloadable file &mdash; Word templates, PowerPoint decks, PDF briefs. Icon auto-selects from <code>data-type</code>.</p>

<div class="crh-download-card">
  <div class="crh-download-icon" data-type="docx"></div>
  <div class="crh-download-meta">
    <strong class="crh-download-name">SKAO-Letterhead.docx</strong>
    <span class="crh-download-detail">Microsoft Word \u00b7 48 KB \u00b7 v1.2</span>
  </div>
  <a class="crh-download-btn" href="#demo" onclick="return false;">Download</a>
</div>

<div class="crh-download-card">
  <div class="crh-download-icon" data-type="pptx"></div>
  <div class="crh-download-meta">
    <strong class="crh-download-name">SKAO-Standard-Deck.pptx</strong>
    <span class="crh-download-detail">PowerPoint \u00b7 4.2 MB \u00b7 16:9 widescreen</span>
  </div>
  <a class="crh-download-btn" href="#demo" onclick="return false;">Download</a>
</div>

<div class="crh-download-card">
  <div class="crh-download-icon" data-type="pdf"></div>
  <div class="crh-download-meta">
    <strong class="crh-download-name">SKAO-Brand-Book-v1.2.pdf</strong>
    <span class="crh-download-detail">PDF \u00b7 12.8 MB \u00b7 64 pages</span>
  </div>
  <a class="crh-download-btn" href="#demo" onclick="return false;">Download</a>
</div>

<h2>2. Canto asset card</h2>
<p>Use when the asset lives in Canto. Don&rsquo;t paste raw Canto links &mdash; this card makes the destination obvious.</p>

<a class="crh-canto-card" href="https://skao.canto.global/" target="_blank" rel="noopener">
  <span class="crh-canto-badge">Canto</span>
  <span class="crh-canto-title">SKAO Logo &mdash; Primary Pack</span>
  <span class="crh-canto-desc">EPS, SVG, PNG (colour, white, black, stacked). 12 files.</span>
  <span class="crh-canto-arrow">Open in Canto &rarr;</span>
</a>

<h2>3. Colour swatch grid</h2>
<p>For Brand Guidelines colour pages. Hex, RGB, and Pantone inline.</p>

<div class="crh-swatch-grid">
  <figure class="crh-swatch"><span class="crh-swatch-chip" style="background:#9333ea;"></span><figcaption><strong>SKAO Purple</strong><span>#9333EA</span></figcaption></figure>
  <figure class="crh-swatch"><span class="crh-swatch-chip" style="background:#C8247E;"></span><figcaption><strong>SKAO Magenta</strong><span>#C8247E</span></figcaption></figure>
  <figure class="crh-swatch"><span class="crh-swatch-chip" style="background:#003366;"></span><figcaption><strong>SKAO Navy</strong><span>#003366</span></figcaption></figure>
</div>

<h2>4. Figure with caption and credit</h2>

<figure class="crh-figure">
  <div style="background:linear-gradient(135deg,#9333ea,#C8247E,#003366);aspect-ratio:16/9;border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:1.5rem;">Image placeholder</div>
  <figcaption>The SKA-Mid site in South Africa&rsquo;s Karoo region at dusk.<cite>SKAO / SARAO</cite></figcaption>
</figure>

<h2>5. Related links grid</h2>
<p>For cross-linking to 3&ndash;6 related pages. Use at the end of a page.</p>

<div class="crh-related-grid">
  <a href="../../brand-guidelines/logo-usage/">Logo Usage</a>
  <a href="../../brand-guidelines/colour-palette/">Colour Palette</a>
  <a href="../../templates-assets/letterhead/">Letterhead</a>
  <a href="../../whats-new/">What\u2019s New</a>
</div>

<h2>6. Callout boxes</h2>
<p>Four standard callouts already styled by the theme. Use the Confluence macro picker &mdash; no custom class needed.</p>

<div class="confluence-information-macro confluence-information-macro-information"><div class="confluence-information-macro-body"><p><strong>Info.</strong> Use for orientation &mdash; context the reader needs before continuing.</p></div></div>

<div class="confluence-information-macro confluence-information-macro-tip"><div class="confluence-information-macro-body"><p><strong>Tip.</strong> Use for time-savers &mdash; shortcuts, faster workflows.</p></div></div>

<div class="confluence-information-macro confluence-information-macro-note"><div class="confluence-information-macro-body"><p><strong>Note.</strong> Use for things to be aware of &mdash; version changes, archive pointers.</p></div></div>

<div class="confluence-information-macro confluence-information-macro-warning"><div class="confluence-information-macro-body"><p><strong>Warning.</strong> Reserve for real consequences &mdash; legal, HSSE, brand compliance.</p></div></div>

<h2>7. Audience tag strip</h2>
<p>Driven by Confluence page labels at the top of every page. You&rsquo;ll see them rendered just under the breadcrumbs, above the page title. This page is tagged <code>For staff</code>.</p>

<h2>Rules of thumb</h2>
<ul>
  <li><strong>One scroll per leaf page.</strong> If you need two, it&rsquo;s two pages.</li>
  <li><strong>One callout per page, ideally zero.</strong> Every extra callout reduces the impact of the one that matters.</li>
  <li><strong>Labels before categories.</strong> Page labels are the only thing that makes filtered search work.</li>
  <li><strong>Canto is the DAM, not Confluence.</strong> Don&rsquo;t upload brand imagery as page attachments.</li>
  <li><strong>Write for the reader who&rsquo;s lost, tired, and in a hurry.</strong> Lead with the answer. Put context below.</li>
</ul>""",
    ),
]


# ---------------------------------------------------------------------------
# 404 PAGE (lives at docs/404.html, outside the standard layout)
# ---------------------------------------------------------------------------

FOUR_O_FOUR = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Page Not Found &mdash; SKAO Creative Hub</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/skao-creative-hub/assets/css/style.css">
<script>
(function(){try{var s=localStorage.getItem('crh-theme');if(s==='dark'){document.documentElement.classList.add('dark')}}catch(e){}})();
</script>
</head>
<body>
<div class="nf-container">
  <div class="nf-content">
    <h1 class="nf-title">404</h1>
    <p class="nf-subtitle">Page Not Found</p>
    <p class="nf-text">The page you\u2019re looking for has drifted into the creative void.</p>
    <div class="nf-actions">
      <a href="/skao-creative-hub/" class="nf-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:6px;"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        Return to Hub
      </a>
      <a href="https://github.com/JDiamondSKAO/skao-creative-hub" target="_blank" rel="noopener" class="nf-btn nf-btn-outline">
        View source on GitHub
      </a>
    </div>
  </div>
</div>
</body>
</html>"""


# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------

def build():
    count = 0
    for page in PAGES:
        out_dir = DOCS / page.slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "index.html"
        out_path.write_text(render_page(page), encoding="utf-8")
        count += 1
        print(f"  wrote  docs/{page.slug}/index.html")

    # 404
    (DOCS / "404.html").write_text(FOUR_O_FOUR, encoding="utf-8")
    count += 1
    print(f"  wrote  docs/404.html")

    print(f"\nBuilt {count} pages.")


def list_pages():
    for p in PAGES:
        print(f"  {p.slug:50s}  [{p.section}]")
    print("  404.html")


def main():
    parser = argparse.ArgumentParser(description="Build the static Creative Hub demo pages.")
    parser.add_argument("--list", action="store_true", help="List pages that would be built without writing.")
    args = parser.parse_args()

    if args.list:
        list_pages()
        return
    build()


if __name__ == "__main__":
    main()
