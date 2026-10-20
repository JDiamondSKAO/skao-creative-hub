"use strict";
document.documentElement.classList.add("js");
document.addEventListener("DOMContentLoaded", () => {
  const $ = (s) => document.querySelector(s),
    $$ = (s) => [...document.querySelectorAll(s)];
  // Links that leave the Hub (another site, another Confluence space, Confluence's own screens) open in a
  // new tab, so the Hub stays open behind them. Hub pages and downloads open in place, so Back still works.
  const leavesHub = (a) => {
    if (a.hasAttribute("download") || a.hasAttribute("target")) return false;
    let u; try { u = new URL(a.getAttribute("href") || "", location.href); } catch { return false; }
    if (!/^https?:$/.test(u.protocol)) return false;
    if (u.origin !== location.origin) return true;
    if (u.pathname.includes("/download/")) return false;
    const space = u.pathname.match(/\/(?:display|spaces)\/([^/]+)/);
    return (space && space[1].toUpperCase() !== "CRH") || /\/pages\/viewpageattachments\.action$/.test(u.pathname);
  };
  const newTab = (a) => {
    a.target = "_blank"; a.rel = (a.rel + " noopener").trim();
    a.setAttribute("aria-describedby", ((a.getAttribute("aria-describedby") || "") + " newTabHint").trim());
  };
  const tabHint = document.createElement("span"); tabHint.id = "newTabHint"; tabHint.hidden = true; tabHint.textContent = "Opens in a new tab";
  document.body.append(tabHint);
  $$("a[href]").forEach((a) => { if (leavesHub(a)) newTab(a); });
  // Links added later (search results, downloads, the slideshow) are caught as they are used.
  document.addEventListener("click", (e) => { const a = e.target.closest?.("a[href]"); if (a && leavesHub(a)) newTab(a); }, true);
  const motion = $("#motionToggle");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (motion) {
    motion.hidden = reducedMotion.matches;
    reducedMotion.addEventListener?.("change", () => { motion.hidden = reducedMotion.matches; });
    motion.addEventListener("click", () => {
      const paused = document.documentElement.classList.toggle("header-motion-paused");
      motion.setAttribute("aria-pressed", String(paused));
      motion.setAttribute("aria-label", paused ? "Resume header animation" : "Pause header animation");
      motion.title = paused ? "Resume header animation" : "Pause header animation";
    });
  }
  const navItems = $$("#mainNav a");
  const currentPath = location.pathname.replace(/\/$/, "");
  [...navItems, ...$$(".sidebar a:not(#toc a)")].forEach(a => {
    if (new URL(a.href).pathname.replace(/\/$/, "") === currentPath) a.setAttribute("aria-current", "page");
  });
  if ($(".start-hero")) navItems[0]?.setAttribute("aria-current", "page");
  // On a page inside a section, mark that section in the top menu.
  const sectionHome = $(".section-nav a.section-home");
  if (sectionHome) {
    const home = new URL(sectionHome.href).pathname.replace(/\/$/, "");
    navItems.forEach((a) => {
      if (!a.hasAttribute("aria-current") && new URL(a.href).pathname.replace(/\/$/, "") === home) a.setAttribute("aria-current", "true");
    });
  }
  // One underline slides to the link under the pointer or focus, then settles back on the current section.
  const topNav = $("#mainNav"), bar = topNav?.querySelector(".nav-indicator");
  if (bar) {
    const home = () => topNav.querySelector("a[aria-current]");
    const place = (a) => {
      if (!a || !a.offsetWidth) { topNav.classList.remove("has-mark"); return; }
      if (!topNav.classList.contains("has-mark")) {
        topNav.classList.add("no-slide");
        setTimeout(() => topNav.classList.remove("no-slide"), 50);
      }
      topNav.style.setProperty("--mark-x", a.offsetLeft + "px");
      topNav.style.setProperty("--mark-w", a.offsetWidth + "px");
      topNav.classList.add("has-mark");
      topNav.classList.toggle("mark-away", a !== home());
    };
    navItems.forEach((a) => {
      a.addEventListener("pointerenter", () => place(a));
      a.addEventListener("focus", () => place(a));
    });
    topNav.addEventListener("pointerleave", () => place(home()));
    topNav.addEventListener("focusout", (e) => { if (!topNav.contains(e.relatedTarget)) place(home()); });
    const settle = () => place(home());
    if ("ResizeObserver" in window) new ResizeObserver(settle).observe(topNav);
    document.fonts?.ready.then(settle);
    settle();
  }
  const menu = $("#menuButton"),
    nav = $("#mainNav");
  menu?.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    menu.setAttribute("aria-expanded", String(open));
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && nav?.classList.contains("open")) {
      nav.classList.remove("open");
      menu.setAttribute("aria-expanded", "false");
      menu.focus();
    }
  });
  const dialog = $("#searchDialog"),
    input = $("#searchInput"),
    results = $("#searchResults"),
    message = $("#searchStatus");
  let opener,
    timer,
    controller,
    serial = 0,
    index;
  function openSearch(e) {
    opener = e?.currentTarget || document.activeElement;
    dialog.showModal();
    showRecent();
    input.focus();
    input.select();
  }
  $$("[data-search]").forEach((b) => b.addEventListener("click", openSearch));
  $$("[data-hub-search]").forEach((form) => form.addEventListener("submit", (e) => {
    e.preventDefault(); openSearch({currentTarget: form.querySelector("input")});
    input.value = form.querySelector("input").value; form.querySelector("input").value = ""; search();
  }));
  $("#closeSearch")?.addEventListener("click", () => dialog.close());
  dialog?.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {e.preventDefault(); e.stopPropagation(); dialog.close();}
  }, true);
  dialog?.addEventListener("close", () => {
    controller?.abort();
    serial++;
    opener?.focus();
  });
  document.addEventListener("keydown", (e) => {
    // "/" opens search too, unless you are typing somewhere.
    if (e.key === "/" && !e.ctrlKey && !e.metaKey && !e.altKey && !dialog.open && !e.target.closest?.("input, textarea, select, [contenteditable]")) {
      e.preventDefault(); openSearch(); return;
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
      e.preventDefault();
      dialog.open ? dialog.close() : openSearch();
    }
  });
  function safeLink(value) {
    try {
      const u = new URL(value, location.href);
      return ["https:", "http:"].includes(u.protocol) &&
        u.origin === location.origin
        ? u.href
        : null;
    } catch {
      return null;
    }
  }
  function cqlLiteral(s) {
    return s
      .replace(/\\/g, "\\\\")
      .replace(/"/g, '\\"')
      .replace(/[\u0000-\u001f]/g, " ");
  }
  // Staff use many words for the same thing; expand each term to its group.
  const SYNONYMS = [
    ["slides", "slide", "presentation", "presentations", "deck", "decks", "ppt", "pptx", "powerpoint", "keynote", "talk"],
    ["logo", "logos", "artwork", "icon", "icons", "lockup", "emblem"],
    ["colour", "colours", "color", "colors", "palette", "hex", "rgb"],
    ["font", "fonts", "typeface", "typography", "noto"],
    ["photo", "photos", "photography", "image", "images", "picture", "pictures", "canto"],
    ["video", "videos", "film", "footage", "b-roll", "broll", "animation", "recording"],
    ["template", "templates"],
    ["signature", "signatures", "email"],
    ["letterhead", "letterheads", "letter"],
    ["poster", "posters", "print", "printing", "banner"],
    ["request", "brief", "commission", "helpdesk", "jira", "help"],
    ["event", "events", "stand", "booth", "exhibition", "conference"],
    ["merchandise", "merch", "giveaway", "giveaways", "swag"],
    ["firefly", "ai", "generative"],
    ["accessibility", "accessible", "a11y", "contrast", "alt"],
    ["partner", "co-branding", "cobranding", "csiro", "sarao"],
    ["business", "card", "cards"],
  ];
  const expand = (term) => {
    const alts = new Set([term]);
    if (term.length >= 2)
      SYNONYMS.forEach((g) => {
        if (g.includes(term) || (term.length >= 4 && g.some((w) => w.startsWith(term)))) g.forEach((w) => alts.add(w));
      });
    return [...alts];
  };
  // Plain questions work too: filler words are dropped unless nothing else is left.
  const FILLER = new Set("a an the and or of to in on at for from with about is are be can could do does did get find need want where what which who how when why i we you my our me it its this that there any some please should would have has".split(" "));
  const terms = (q) => {
    const all = q.toLowerCase().split(/[^\p{L}\p{N}-]+/u).filter((t) => t.length > 1);
    const kept = all.filter((t) => !FILLER.has(t));
    return kept.length ? kept : all;
  };
  const escapeRe = (t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const slugify = (t) => t.toLowerCase().replace(/[^\p{L}\p{N}]+/gu, "-").replace(/^-+|-+$/g, "").slice(0, 60) || "section";
  function rank(rows, q) {
    const words = terms(q), phrase = q.toLowerCase().trim();
    if (!words.length) return [];
    return rows
      .map((r) => {
        const title = (r.title || "").toLowerCase(), excerpt = (r.excerpt || "").toLowerCase(), body = (r.keywords || "").toLowerCase();
        let score = title === phrase ? 40 : title.startsWith(phrase) ? 20 : title.includes(phrase) ? 15 : 0;
        const hits = [];
        for (const w of words) {
          let best = 0, hit = w;
          for (const alt of expand(w)) {
            const weight = alt === w ? 1 : 0.8;
            const re = new RegExp("(^|[^\\p{L}\\p{N}])" + escapeRe(alt), "u");
            const s = re.test(title) ? 10 : title.includes(alt) ? 6 : excerpt.includes(alt) ? 3 : body.includes(alt) ? 1 : 0;
            if (s * weight > best) { best = s * weight; hit = alt; }
          }
          if (!best) return null;
          score += best;
          hits.push(hit);
        }
        return { ...r, score, hits };
      })
      .filter(Boolean)
      .sort((a, b) => b.score - a.score || a.title.length - b.title.length);
  }
  // Build text with <mark> around matches, using DOM nodes only.
  function highlight(el, text, hits) {
    if (!hits?.length) { el.textContent = text; return; }
    const re = new RegExp("((?<![\\p{L}\\p{N}])(?:" + hits.map(escapeRe).join("|") + "))", "giu");
    text.split(re).forEach((part, i) => {
      if (!part) return;
      if (i % 2) { const m = document.createElement("mark"); m.textContent = part; el.append(m); }
      else el.append(part);
    });
  }
  function snippet(r) {
    const excerpt = r.excerpt || "";
    const lowTitle = (r.title + " " + excerpt).toLowerCase();
    const missing = (r.hits || []).find((h) => !lowTitle.includes(h));
    const body = r.keywords || "";
    if (!missing || !body) return excerpt;
    const at = body.toLowerCase().indexOf(missing);
    if (at < 0) return excerpt;
    const from = Math.max(0, body.lastIndexOf(" ", Math.max(0, at - 50)));
    return (from ? "…" : "") + body.slice(from, at + 90).trim() + "…";
  }
  // Ready-written answers to common questions sit above the results.
  let answerCard = null;
  function findAnswer(q) {
    const words = terms(q);
    if (!words.length || words.length > 6) return null;
    let best = null, bestHits = 0;
    $$("#hubAnswers a").forEach((a) => {
      const keys = (a.dataset.keys || "").split(" ");
      const hits = words.filter((w) => expand(w).some((alt) => keys.some((k) => k === alt || (alt.length >= 4 && k.startsWith(alt)) || (k.length >= 4 && alt.startsWith(k))))).length;
      if (hits > bestHits) { best = a; bestHits = hits; }
    });
    return best;
  }
  function showAnswer(q) {
    const a = findAnswer(q), href = a && safeLink(a.href);
    answerCard = null;
    if (!a || !href) return;
    const card = document.createElement("a"), label = document.createElement("span"), question = document.createElement("strong"), text = document.createElement("small"), go = document.createElement("em");
    card.className = "search-answer"; card.href = href;
    label.className = "result-group"; label.textContent = "Quick answer";
    question.textContent = a.dataset.question || "";
    text.textContent = a.dataset.answer || "";
    go.textContent = "Open " + a.textContent.trim() + " →";
    card.append(label, question, text, go);
    answerCard = card;
  }
  function renderRows(rows) {
    results.replaceChildren(...(answerCard ? [answerCard] : []));
    let count = 0;
    rows.forEach((r) => {
      const href = safeLink(r.href);
      if (!href || count >= 12) return;
      const a = document.createElement("a"),
        label = document.createElement("strong"),
        desc = document.createElement("small");
      a.href = href;
      if (r.group) {
        const g = document.createElement("span");
        g.className = "result-group";
        g.textContent = r.group;
        a.append(g);
      }
      highlight(label, r.title, r.hits);
      highlight(desc, snippet(r), r.hits);
      a.append(label, desc);
      results.append(a);
      count++;
    });
    return count;
  }
  // Pages the theme knows about are matched instantly by title.
  const localRoutes = () =>
    $$("#hubRoutes a[data-page-id]").map((a) => ({ id: a.dataset.pageId, title: a.textContent.trim(), href: a.href, excerpt: "" }));
  let rendered = "";
  async function search() {
    controller?.abort();
    const id = ++serial;
    const q = input.value.trim();
    rendered = "";
    suggest.hidden = q.length >= 2;
    if (q.length < 2) {
      answerCard = null;
      results.replaceChildren();
      message.textContent = "";
      return;
    }
    message.textContent = "Searching…";
    showAnswer(q);
    if (answerCard) results.replaceChildren(answerCard);
    controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 10000);
    try {
      let rows;
      if (document.body.dataset.mode === "preview") {
        if (!index) {
          const res = await fetch("search-index.json", {
            signal: controller.signal,
          });
          if (!res.ok) throw Error("unavailable");
          index = await res.json();
        }
        rows = rank(index, q);
      } else {
        // Show the Hub's page titles, which can differ from the Confluence page names.
        let labels = {};
        try { labels = JSON.parse($("#hubTitles")?.textContent || "{}"); } catch {}
        const local = rank(localRoutes().map((r) => ({ ...r, title: labels[r.id] || r.title })), q);
        if (local.length) { results.replaceChildren(); renderRows(local); }
        const ctx = document.body.dataset.context || "";
        const alts = [q, ...terms(q).flatMap(expand)].filter((v, i, all) => all.indexOf(v) === i).slice(0, 8);
        const cql =
          'type=page AND space="CRH" AND (' +
          alts.map((t) => 'title~"' + cqlLiteral(t) + '" OR text~"' + cqlLiteral(t) + '"').join(" OR ") +
          ")";
        // Approved files whose names match, shown after the pages that hold them.
        const fileWords = terms(q).flatMap(expand).filter((v, i, all) => all.indexOf(v) === i).slice(0, 6);
        const filesFound = fetch(ctx + "/rest/api/content/search?" + new URLSearchParams({ cql: 'type=attachment AND space="CRH" AND label="approved" AND (' + fileWords.map((t) => 'title~"' + cqlLiteral(t) + '"').join(" OR ") + ")", limit: "8", expand: "container" }), { credentials: "same-origin", headers: { Accept: "application/json" }, signal: controller.signal })
          .then((r) => (r.ok ? r.json() : { results: [] })).catch(() => ({ results: [] }));
        const res = await fetch(
          ctx +
            "/rest/api/content/search?" +
            new URLSearchParams({ cql, limit: "20", expand: "ancestors" }),
          {
            credentials: "same-origin",
            headers: { Accept: "application/json" },
            signal: controller.signal,
          },
        );
        if (res.status === 401 || res.status === 403)
          throw Error(
            "Please sign in to Confluence to search these resources.",
          );
        if (!res.ok)
          throw Error(
            "Search is unavailable. Browse the resource categories or try again.",
          );
        const data = await res.json();
        const routes = new Map($$("#hubRoutes a[data-page-id]").map(a => [a.dataset.pageId, a]));
        const remote = (data.results || []).map((r) => ({
          title: labels[String(r.id)] || r.title,
          excerpt: (r.ancestors || []).map((a) => a.title).join(" / "),
          href: routes.get(String(r.id))?.href || ctx + (r._links?.webui || "/pages/viewpage.action?pageId=" + encodeURIComponent(r.id)),
          hits: terms(q),
        }));
        // Title matches first, whatever order the API returns; everything Confluence found stays listed.
        const wanted = terms(q).flatMap(expand);
        const titleScore = (r) => wanted.filter((t) => r.title.toLowerCase().includes(t)).length;
        remote.forEach((r, i) => { r.order = i; });
        remote.sort((a, b) => titleScore(b) - titleScore(a) || a.order - b.order);
        const seen = new Set(local.map((r) => r.href));
        const files = ((await filesFound).results || []).filter((f) => !/^canto-|\.json$/i.test(f.title || "")).slice(0, 4).map((f) => {
          const page = String(f.container?.id || ""), ext = ((f.title || "").match(/\.([a-z0-9]+)$/i) || [])[1];
          return {
            title: String(f.title || "").replace(/\.[a-z0-9]+$/i, "").replace(/[_]+/g, " ").trim(),
            excerpt: "On " + (labels[page] || f.container?.title || "a Hub page"),
            href: (routes.get(page)?.href || ctx + (f.container?._links?.webui || "")) + "#downloads",
            group: ext ? ext.toUpperCase() + " file" : "File",
            hits: terms(q),
          };
        });
        rows = [...local, ...remote.filter((r) => !seen.has(r.href))].slice(0, 12 - files.length).concat(files);
      }
      if (id !== serial || !dialog.open) return;
      const count = renderRows(rows);
      rendered = count ? q : "";
      message.textContent = count
        ? `${count} result${count === 1 ? "" : "s"}.` + (matchMedia("(pointer: fine)").matches ? " Use ↑ ↓ to move, Enter to open." : "")
        : answerCard ? "" : "No matching pages. Try another word or browse all resources.";
    } catch (e) {
      if (id === serial && dialog.open)
        message.textContent =
          e.name === "AbortError"
            ? "Search took too long. Try again or browse the resources."
            : e.message === "unavailable"
              ? "Search is unavailable. Browse the resources below."
              : e.message;
    } finally {
      clearTimeout(timeout);
    }
  }
  // Recently viewed pages stay in this browser only.
  const RECENT = "crh-recent";
  const readRecent = () => { try { return JSON.parse(localStorage.getItem(RECENT) || "[]").filter((r) => r && r.title && safeLink(r.href)); } catch { return []; } };
  const pageTitle = $(".page-head h1")?.textContent.trim();
  if (pageTitle) {
    try {
      const here = location.href.split("#")[0];
      localStorage.setItem(RECENT, JSON.stringify([{ title: pageTitle, href: here }, ...readRecent().filter((r) => r.href !== here)].slice(0, 5)));
    } catch {}
  }
  const suggest = $("#searchSuggest") || document.createElement("div");
  function showRecent() {
    const list = $("#recentList"), wrap = $("#recentPages");
    if (!list || !wrap) return;
    const here = location.href.split("#")[0];
    const items = readRecent().filter((r) => r.href !== here).slice(0, 4);
    list.replaceChildren(...items.map((r) => { const a = document.createElement("a"); a.href = safeLink(r.href); a.textContent = r.title; return a; }));
    wrap.hidden = !items.length;
  }
  dialog?.addEventListener("keydown", (e) => {
    if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
    const links = [...(suggest.hidden ? results : suggest).querySelectorAll("a")];
    if (!links.length) return;
    e.preventDefault();
    const at = links.indexOf(document.activeElement);
    if (e.key === "ArrowUp" && at <= 0) { input.focus(); return; }
    links[e.key === "ArrowDown" ? Math.min(at + 1, links.length - 1) : at - 1].focus();
  });
  input?.addEventListener("input", () => {
    clearTimeout(timer);
    controller?.abort();
    serial++;
    rendered = "";
    if (input.value.trim().length < 2) { search(); return; }
    timer = setTimeout(search, 180);
  });
  $("#searchForm")?.addEventListener("submit", (e) => {
    e.preventDefault();
    clearTimeout(timer);
    const first = results.querySelector("a");
    if (rendered && rendered === input.value.trim() && first) { location.href = first.href; return; }
    search();
  });
  // Latest files: every approved file in the Hub and the site teams' progress slides, newest first,
  // grouped by month. Each file names the page it is on and that page's Hub section.
  async function loadFeed(box) {
    const list = box.querySelector("[data-feed-list]"), chipBox = box.querySelector(".type-chips");
    const search = box.querySelector("#fileFilter"), status = box.querySelector("#feedStatus"), empty = box.querySelector("#feedEmpty");
    const read = (key, fallback) => { try { return JSON.parse(box.dataset[key] || "null") || fallback; } catch { return fallback; } };
    const pages = read("pages", {}), sections = new Map(read("sections", [])), sitePages = read("sitePages", []);
    const preview = document.body.dataset.mode === "preview", ctx = document.body.dataset.context || "";
    const note = (text) => { const p = document.createElement("p"); p.className = "feed-note"; p.textContent = text; list.replaceChildren(p); };
    const placeOf = (id, title) => pages["i:" + id] || pages["t:" + String(title || "").toLowerCase()] || null;
    const routeHref = (id) => { const a = $$("#hubRoutes a").find((x) => x.dataset.pageId === String(id)); return a ? safeLink(a.getAttribute("href")) : null; };
    const toRow = (f, site) => {
      const title = String(f.title || ""), href = preview ? null : safeLink(ctx + (f._links?.download || ""));
      if (!preview && !href) return null;
      const id = String(f.container?.id || ""), at = placeOf(id, f.container?.title);
      const base = title.replace(/\.[a-z0-9]+$/i, "").replace(/_+/g, " ").replace(/\s+/g, " ").trim();
      const dm = base.match(/^(\d{4})[-. ]?(\d{2})(?:[-. ]?\d{2})?[\s-]+(.+)$/);
      const webui = f.container?._links?.webui;
      return {
        href, name: dm ? dm[3].trim() : base, title, ext: (title.match(/\.([a-z0-9]+)$/i)?.[1] || "file").toLowerCase(),
        when: Date.parse(f.version?.when || "") || 0, updated: Number(f.version?.number) > 1, size: f.extensions?.fileSize,
        type: at?.[0] || "", page: at?.[1] || String(f.container?.title || ""),
        pageHref: preview ? null : (webui ? safeLink(ctx + webui) : routeHref(id)), downloads: !site,
      };
    };
    let rows = [];
    if (preview) {
      const day = 864e5, now = Date.now();
      rows = [
        { title: "SKAO_PPT_Unrestricted.pptx", container: { title: "Standard SKAO template" }, version: { when: new Date(now - 2 * day).toISOString() }, extensions: { fileSize: 3.4 * 1048576 } },
        { title: "2026-10 SKA-Low progress.pptx", container: { title: "SKA-Low progress" }, version: { when: new Date(now - 5 * day).toISOString() }, extensions: { fileSize: 12.6 * 1048576 } },
        { title: "SKAO_Letterhead_UNRESTRICTED.docx", container: { title: "Letterheads" }, version: { when: new Date(now - 9 * day).toISOString(), number: 2 }, extensions: { fileSize: 143 * 1024 } },
        { title: "SKAO_SRCnet_logo_colour_rgb.png", container: { title: "Partner logos" }, version: { when: new Date(now - 41 * day).toISOString() }, extensions: { fileSize: 62 * 1024 } },
      ].map((f) => toRow(f, false));
    } else {
      try {
        const res = await fetch(ctx + "/rest/api/content/search?" + new URLSearchParams({ cql: 'type=attachment AND space="CRH" AND label="approved" ORDER BY lastmodified DESC', limit: "200", expand: "container,version" }), { credentials: "same-origin", headers: { Accept: "application/json" } });
        if (!res.ok) throw Error(String(res.status));
        const approved = (await res.json()).results || [];
        // Progress slides need no label: the site teams add them to their own pages.
        const decks = await Promise.all(sitePages.map((id) => attachmentsOf(id, ctx).then((fs) => fs.filter((f) => !/^canto-|^site-photo\.|\.json$/i.test(String(f.title || ""))).map((f) => ({ ...f, container: { id } }))).catch(() => [])));
        const seen = new Set();
        rows = [...approved.map((f) => toRow(f, false)), ...decks.flat().map((f) => toRow(f, true))].filter((r) => r && !seen.has(r.href) && seen.add(r.href));
      } catch (e) {
        note(e.message === "401" || e.message === "403" ? "Sign in to Confluence to see the latest files." : "The latest files could not be loaded.");
        return;
      }
    }
    rows.sort((x, y) => y.when - x.when);
    if (!rows.length) { note("No new files yet. Files appear here as soon as they are approved."); return; }
    const monthOf = (t) => { const d = new Date(t); return MONTHS[d.getMonth()] + " " + d.getFullYear(); };
    const day = (t) => { try { return new Intl.DateTimeFormat("en-GB", new Date(t).getFullYear() === new Date().getFullYear() ? { day: "numeric", month: "short" } : { day: "numeric", month: "short", year: "numeric" }).format(t); } catch { return ""; } };
    const months = new Map();
    rows.forEach((r) => { const k = r.when ? monthOf(r.when) : "Earlier"; if (!months.has(k)) months.set(k, []); months.get(k).push(r); });
    list.replaceChildren(...[...months].map(([label, items]) => {
      const sec = document.createElement("section"); sec.className = "feed-month";
      const h = document.createElement("h2"), count = document.createElement("span");
      h.textContent = label; count.textContent = items.length + (items.length === 1 ? " file" : " files"); h.append(count);
      const ul = document.createElement("ul"); ul.className = "feed-list";
      const batches = new Map();
      items.forEach((r) => { const k = r.page + "|" + new Date(r.when).toDateString(); if (!batches.has(k)) batches.set(k, []); batches.get(k).push(r); });
      batches.forEach((group) => { if (group.length >= 3) ul.append(batch(group)); else group.forEach((r) => ul.append(row(r))); });
      sec.append(h, ul); return sec;
    }));
    // One file: its type, name, page and section, when it was added, and a download button.
    function row(r, inBatch) {
      const li = document.createElement("li"); li.className = inBatch ? "feed-file" : "feed-row"; li.dataset.type = r.type || "other";
      const badge = document.createElement("span"); badge.className = "file-badge"; badge.dataset.ext = r.ext; badge.textContent = r.ext.toUpperCase().slice(0, 4);
      const text = document.createElement("span"); text.className = "feed-text";
      const name = document.createElement("strong"); name.className = "feed-name"; name.textContent = r.name;
      const where = document.createElement("span"); where.className = "feed-where";
      const page = document.createElement(r.pageHref ? "a" : "span"); page.textContent = r.page || "Creative Hub";
      if (r.pageHref) page.href = r.pageHref + (r.downloads ? "#downloads" : "");
      where.append(page);
      if (sections.has(r.type)) { const s2 = document.createElement("span"); s2.className = "feed-section"; s2.textContent = sections.get(r.type); where.append(s2); }
      text.append(name, where);
      const when = document.createElement("span"); when.className = "feed-when"; when.textContent = r.when ? (r.updated ? "Updated " : "Added ") + day(r.when) : "";
      const get = document.createElement("a"); get.className = "dl-file";
      if (r.href) { get.href = r.href; get.setAttribute("download", ""); get.title = r.title; } else get.setAttribute("aria-disabled", "true");
      get.setAttribute("aria-label", `Download ${r.name}, ${r.ext.toUpperCase()}${size(r.size) ? ", " + size(r.size) : ""}`);
      const b = document.createElement("b"); b.textContent = "Download"; const small = document.createElement("small"); small.textContent = size(r.size);
      get.append(b, small);
      if (inBatch) li.append(badge, name, get); else li.append(badge, text, when, get);
      if (preview && !inBatch) { const tag = document.createElement("span"); tag.className = "example-tag"; tag.textContent = "Example"; name.append(tag); }
      return li;
    }
    // Several files added to one page on the same day: one row, with the files listed underneath on request.
    function batch(group) {
      const r = group[0], li = row({ ...r, name: group.length + (group.every((x) => x.updated) ? " updated files" : " new files") });
      li.classList.add("feed-batch");
      const tally = group.reduce((t, x) => ({ ...t, [x.ext]: (t[x.ext] || 0) + 1 }), {}), common = Object.keys(tally).sort((x, y) => tally[y] - tally[x])[0];
      const badge = li.querySelector(".file-badge"); badge.dataset.ext = common; badge.textContent = common.toUpperCase().slice(0, 4); badge.classList.add("is-stack");
      li.querySelector(".example-tag")?.remove();
      const list = document.createElement("ul"); list.className = "feed-sub"; list.hidden = true; list.id = "batch-" + Math.random().toString(36).slice(2, 9);
      group.forEach((x) => list.append(row(x, true)));
      const toggle = document.createElement("button"); toggle.type = "button"; toggle.className = "feed-toggle";
      toggle.setAttribute("aria-expanded", "false"); toggle.setAttribute("aria-controls", list.id);
      const label = () => { toggle.textContent = list.hidden ? "Show files" : "Hide files"; };
      toggle.addEventListener("click", () => { list.hidden = !list.hidden; li.dataset.userOpen = String(!list.hidden); toggle.setAttribute("aria-expanded", String(!list.hidden)); label(); });
      label();
      li.querySelector(".dl-file").replaceWith(toggle);
      li.append(list);
      return li;
    }
    // Section filters for the sections that have files, in the Hub's own order.
    let type = "all";
    const counts = rows.reduce((m, r) => m.set(r.type, (m.get(r.type) || 0) + 1), new Map());
    const chip = (key, label, n) => {
      const b = document.createElement("button"); b.type = "button"; b.dataset.typeFilter = key; b.setAttribute("aria-pressed", String(key === "all"));
      const c = document.createElement("span"); c.textContent = n; b.append(label + " ", c);
      b.addEventListener("click", () => { type = key; chipBox.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); apply(); });
      return b;
    };
    const present = [...sections].filter(([key]) => counts.get(key));
    if (present.length > 1) { chipBox.replaceChildren(chip("all", "All", rows.length), ...present.map(([key, label]) => chip(key, label, counts.get(key)))); chipBox.hidden = false; }
    function apply() {
      const words = terms(search?.value || "");
      const fits = (hay) => words.every((w) => expand(w).some((alt) => hay.includes(alt)));
      let n = 0;
      list.querySelectorAll(".feed-row").forEach((li) => {
        const inType = type === "all" || li.dataset.type === type;
        if (!li.classList.contains("feed-batch")) { const match = inType && fits(li.textContent.toLowerCase()); li.hidden = !match; if (match) n++; return; }
        // A folded group matches on its page and section, or on any of its files, which then show.
        const head = li.querySelector(".feed-text").textContent.toLowerCase(), sub = li.querySelector(".feed-sub"), files = [...sub.children];
        let shown = 0;
        files.forEach((f) => { const match = inType && fits(head + " " + f.textContent.toLowerCase()); f.hidden = !match; if (match) shown++; });
        li.hidden = !shown; n += shown;
        const open = (words.length && shown) || li.dataset.userOpen === "true";
        sub.hidden = !open; li.querySelector(".feed-toggle").setAttribute("aria-expanded", String(!!open)); li.querySelector(".feed-toggle").textContent = open ? "Hide files" : "Show files";
      });
      list.querySelectorAll(".feed-month").forEach((m) => { m.hidden = !m.querySelector(".feed-row:not([hidden])"); });
      if (status) status.textContent = n === rows.length ? "" : `Showing ${n} of ${rows.length} files.`;
      if (empty) empty.hidden = n > 0;
    }
    search?.addEventListener("input", apply);
    box.querySelector("#clearFeed")?.addEventListener("click", () => {
      if (search) search.value = ""; type = "all";
      chipBox.querySelectorAll("button").forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.typeFilter === "all")));
      apply(); search?.focus();
    });
  }
  // Homepage search box hands over to the full search dialog as you type.
  const hero = $("#heroSearch");
  hero?.addEventListener("input", () => {
    if (!hero.value) return;
    openSearch({ currentTarget: hero });
    input.value = hero.value;
    hero.value = "";
    input.dispatchEvent(new Event("input"));
  });
  // Sidebar: only the group holding this page stays open.
  const groups = $$(".section-nav details.nav-group");
  if (groups.some((g) => g.querySelector("a[aria-current]"))) groups.forEach((g) => { g.open = !!g.querySelector("a[aria-current]"); });
  // Pages with several questions get one control to open or close them all.
  const body = $(".content-body");
  const questions = body ? [...body.querySelectorAll(":scope > details.guidance-detail, :scope > .help-answers > details.guidance-detail")] : [];
  if (questions.length >= 3) {
    const toggle = document.createElement("button");
    toggle.type = "button"; toggle.className = "expand-all";
    const label = () => { toggle.textContent = questions.every((d) => d.open) ? "Collapse all" : "Expand all"; };
    toggle.addEventListener("click", () => { const open = !questions.every((d) => d.open); questions.forEach((d) => { d.open = open; }); label(); });
    questions.forEach((d) => d.addEventListener("toggle", label));
    label();
    questions[0].before(toggle);
  }
  // Links to a collapsed section open it.
  const openTarget = (id) => { const d = id && document.getElementById(id); if (d && d.tagName === "DETAILS") { d.open = true; return d; } };
  $$("[data-open-details]").forEach((a) => a.addEventListener("click", (e) => {
    const d = openTarget(a.hash.slice(1));
    if (!d) return;
    e.preventDefault();
    d.scrollIntoView({ behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "start" });
    d.querySelector("input, textarea")?.focus({ preventScroll: true });
  }));
  openTarget(location.hash.slice(1));
  addEventListener("hashchange", () => openTarget(location.hash.slice(1)));
  // Announcement: the newest Hub page labelled "announcement". Dismissal lasts until that page changes.
  const banner = $("#announcement");
  if (banner) loadAnnouncement(banner);
  async function loadAnnouncement(el) {
    const link = $("#announcementLink"), KEY = "crh-announce-dismissed";
    let item;
    if (document.body.dataset.mode === "preview") {
      item = { key: "example:1", title: "Example announcement: the newest Hub page labelled “announcement” appears here", href: link.href };
    } else {
      try {
        const ctx = document.body.dataset.context || "";
        const cql = 'type=page AND space="CRH" AND label="announcement" ORDER BY lastmodified DESC';
        const res = await fetch(ctx + "/rest/api/content/search?" + new URLSearchParams({ cql, limit: "1", expand: "version" }), { credentials: "same-origin", headers: { Accept: "application/json" } });
        if (!res.ok) return;
        const r = ((await res.json()).results || [])[0];
        if (!r || !r.title) return;
        item = { key: String(r.id) + ":" + String(r.version?.number || ""), title: String(r.title), href: ctx + (r._links?.webui || "/pages/viewpage.action?pageId=" + encodeURIComponent(r.id)) };
      } catch { return; }
    }
    try { if (localStorage.getItem(KEY) === item.key) return; } catch {}
    link.textContent = item.title;
    const href = safeLink(item.href);
    if (href) link.href = href;
    const still = matchMedia("(prefers-reduced-motion: reduce)").matches || !el.animate;
    const grow = (from, to, done) => {
      const h = el.scrollHeight + "px";
      el.style.overflow = "hidden";
      el.animate([{ height: from ? h : "0px", opacity: from }, { height: to ? h : "0px", opacity: to }], { duration: to ? 320 : 220, easing: "cubic-bezier(.16,1,.3,1)" })
        .finished.then(() => { el.style.overflow = ""; done?.(); });
    };
    el.hidden = false;
    if (!still) grow(0, 1);
    el.querySelector(".announce-close").addEventListener("click", () => {
      if (still) el.hidden = true; else grow(1, 0, () => { el.hidden = true; });
      try { localStorage.setItem(KEY, item.key); } catch {}
      (document.querySelector("#main-content") || document.body).focus?.({ preventScroll: true });
    });
  }
  // First visit: a short welcome that says the Hub is new and still growing, with a way to send feedback.
  // It shows once per browser; Beta · Share feedback in the header stays for later.
  const welcome = $("#welcomeDialog"), WELCOME = "crh-welcome-1";
  if (welcome) {
    const remember = () => { try { localStorage.setItem(WELCOME, "1"); } catch {} };
    let seen = true;
    try { seen = localStorage.getItem(WELCOME) === "1"; } catch {}
    welcome.querySelectorAll("[data-welcome-close]").forEach((b) => b.addEventListener("click", () => welcome.close()));
    welcome.addEventListener("close", remember);
    welcome.querySelector("a[href]")?.addEventListener("click", () => { remember(); welcome.close(); });
    welcome.addEventListener("click", (e) => { if (e.target === welcome) welcome.close(); });
    if (!seen && document.body.dataset.mode !== "preview" && typeof welcome.showModal === "function")
      setTimeout(() => { if (!document.querySelector("dialog[open]")) welcome.showModal(); }, 700);
  }
  // The feedback form (Airtable) opens with this page filled in, so we know where feedback came from.
  // While Share feedback still points at the helpdesk, the links stay as they are.
  if (pageTitle) $$("a[data-feedback]").forEach((l) => {
    try {
      const u = new URL(l.href);
      if (u.hostname !== "airtable.com") return;
      u.searchParams.set("prefill_Page", pageTitle);
      l.href = u.href;
    } catch {}
  });
  // Files uploaded to a Hub page and labelled "approved" become its downloads.
  refreshAvailability();
  async function refreshAvailability() {
    const panel = $(".asset-panel[data-page-id]"), pageId = panel?.dataset.pageId || document.body.dataset.pageId;
    if (!panel && !pageId) return;
    if ($("[data-attachments], [data-deck-library]")) return; // these pages list their files themselves
    const slot = panel?.querySelector("[data-downloads]");
    if (document.body.dataset.mode === "preview") {
      if (slot) {
        const p = document.createElement("p"); p.className = "downloads-note";
        p.textContent = "Preview: in Confluence, files attached to this page and labelled “approved” are listed here as downloads.";
        slot.replaceChildren(p); slot.hidden = false;
      }
      return;
    }
    const ctx = document.body.dataset.context || "";
    let files = [];
    try {
      const cql = 'type=attachment AND space="CRH" AND label="approved" ORDER BY title';
      const res = await fetch(ctx + "/rest/api/content/search?" + new URLSearchParams({ cql, limit: "200", expand: "container,version" }), { credentials: "same-origin", headers: { Accept: "application/json" } });
      if (!res.ok) return;
      files = (await res.json()).results || [];
    } catch { return; }
    const byPage = new Map();
    files.forEach((f) => { const id = String(f.container?.id || ""); if (id) byPage.set(id, [...(byPage.get(id) || []), f]); });
    const mine = pageId ? byPage.get(String(pageId)) : null;
    if (!mine?.length) return;
    // Cards show a cover: a picture attached to the page under the file's own name.
    const view = $("[data-dl-groups]")?.dataset.dlView || "list";
    const pictures = view === "cards" && pageId ? await attachmentsOf(pageId, ctx).catch(() => []) : [];
    const section = renderDownloads(mine, ctx, pictures);
    if (!section) return;
    // Links from "Just added" point at #downloads, which only exists once the files have loaded.
    const arrive = () => { if (location.hash === "#downloads") section.scrollIntoView({ block: "start", behavior: reducedMotion.matches ? "auto" : "smooth" }); };
    if (!panel) {
      const slot = $(".content-body > [data-downloads-slot]"), intro = $(".content-body > .task-intro");
      if (slot) slot.replaceWith(section); else if (intro) intro.after(section); else $(".content-body")?.prepend(section);
      arrive();
      return;
    }
    panel.querySelectorAll('.how-to-get, [data-fact=versions], [data-fact=sizes], [data-fact="partner versions"], [data-fact=planned]').forEach((el) => el.remove());
    release(panel, mine.filter((f) => safeLink(ctx + (f._links?.download || ""))), view);
    panel.after(section);
    beside(section, view);
    arrive();
  }
  // Release details on the main card, read from the approved files: the newest upload date and,
  // when every file agrees on it, the version (from the file names, or Confluence's own count).
  function release(panel, files, view = "list") {
    const fact = (key, value) => { const el = panel.querySelector(`[data-fact="${key}"]`); if (!el) return; if (value) el.querySelector("dd").textContent = value; el.hidden = !el.querySelector("dd").textContent; };
    const times = files.map((f) => Date.parse(f.version?.when || "")).filter((t) => !isNaN(t));
    let updated = "";
    if (times.length) try { updated = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "long", year: "numeric" }).format(new Date(Math.max(...times))); } catch {}
    const one = (list) => list.length === files.length && new Set(list).size === 1 ? list[0] : "";
    const named = one(files.map((f) => (String(f.title || "").match(/(?:^|[\s_-])v(\d+(?:\.\d+)?)(?=[\s_.-]|$)/i) || [])[1]).filter(Boolean));
    const counted = one(files.map((f) => String(f.version?.number || "")).filter(Boolean));
    fact("version", view === "list" && (named || counted) ? "Version " + (named || counted) : "");
    fact("updated", updated);
    fact("approved", "");
  }
  // "Before you use the file" sits beside a list of downloads as a card. Cards and logo tiles need the
  // width, so there the checks follow them as a band.
  function beside(section, view = "list") {
    const read = $$(".content-body > .reading-section").find((r) => r.querySelector("h2")?.textContent.trim() === "Before you use the file");
    if (!read) return;
    if (view !== "list") { read.classList.add("dl-checks"); read.querySelector("h2").className = "rail-title"; section.after(read); return; }
    const wrap = document.createElement("div"); wrap.className = "dl-layout";
    const card = document.createElement("aside"); card.className = "dl-aside"; card.setAttribute("aria-labelledby", "beforeUse");
    const h = read.querySelector("h2"); h.id = "beforeUse"; h.className = "rail-title";
    card.append(...read.childNodes);
    section.replaceWith(wrap); wrap.append(section, card); read.remove();
  }
  // The site progress pages list every file the site team adds, newest first: no "approved" label is
  // needed, so adding a file is the whole job. "2026-10 SKA-Low progress.pptx" reads as "SKA-Low
  // progress", given October 2026. Photos, Canto thumbnails, data files and off-site links are left out.
  const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  function pageFiles(files, ctx) {
    return files.filter((f) => !/^canto-|^site-photo\.|\.json$/i.test(String(f.title || ""))).map((f) => {
      const title = String(f.title || ""), ext = (title.match(/\.([a-z0-9]+)$/i)?.[1] || "file").toLowerCase();
      const href = safeLink(ctx + (f._links?.download || ""));
      const base = title.replace(/\.[a-z0-9]+$/i, "").replace(/_+/g, " ").trim();
      const dm = base.match(/^(\d{4})[-. ]?(\d{2})(?:[-. ]?\d{2})?[\s-]+(.+)$/);
      const month = dm && +dm[2] >= 1 && +dm[2] <= 12 ? MONTHS[+dm[2] - 1] + " " + dm[1] : "";
      return { title, ext, href, name: dm ? dm[3].trim() : base, month, when: Date.parse(f.version?.when || "") || 0, size: f.extensions?.fileSize };
    }).filter((r) => r.href).sort((x, y) => y.when - x.when);
  }
  const fmt = (t) => { try { return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric" }).format(new Date(t)); } catch { return ""; } };
  const size = (n) => !n ? "" : n > 1073741824 ? (n / 1073741824).toFixed(1) + " GB" : n > 1048576 ? (n / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1024)) + " KB";
  async function attachmentsOf(pageId, ctx, expand = "version") {
    const res = await fetch(ctx + "/rest/api/content/" + encodeURIComponent(pageId) + "/child/attachment?" + new URLSearchParams({ limit: "200", expand }), { credentials: "same-origin", headers: { Accept: "application/json" } });
    if (!res.ok) throw new Error(String(res.status));
    return (await res.json()).results || [];
  }
  // Each site page carries its telescope photo as site-photo.jpg. Construction overview shows it on
  // that telescope's tile with the month of the newest slides; the site page shows it as a banner.
  const isPhoto = (f) => /^site-photo\.(jpe?g|png|webp)$/i.test(String(f.title || ""));
  function showPhoto(slot, files, ctx) {
    const f = files.find(isPhoto), href = f && safeLink(ctx + (f._links?.download || ""));
    if (!slot || !href) return;
    const img = new Image(); img.alt = ""; img.decoding = "async";
    img.onload = () => { slot.hidden = false; slot.classList.add("has-photo"); };
    img.src = href; slot.append(img);
  }
  $$("[data-site-page]").forEach(async (tile) => {
    if (document.body.dataset.mode === "preview") return;
    const ctx = document.body.dataset.context || "";
    let files = [];
    try { files = await attachmentsOf(tile.dataset.sitePage, ctx); } catch { return; }
    showPhoto(tile.querySelector(".scope-photo"), files, ctx);
    const newest = pageFiles(files, ctx)[0], line = tile.querySelector("[data-latest-line]");
    if (newest && line) line.textContent = "Latest slides: " + (newest.month || fmt(newest.when));
  });
  const fileList = $("[data-site-files]");
  if (fileList) loadSitePage(fileList);
  const feedBox = $("[data-file-feed]");
  if (feedBox) loadFeed(feedBox);
  const deckBox = $("[data-deck-library]");
  if (deckBox) loadDecks(deckBox);
  // Approved slide decks: every approved deck on the page, newest first, each with its cover, its details and
  // a preview. Communications writes the details in the attachment's comment in Confluence, as
  // "Speaker: … · Event: … · Audience: … · Slides: … · Classification: …" (one per line works too).
  async function loadDecks(box) {
    const list = box.querySelector("[data-deck-list]"), chipBox = box.querySelector(".type-chips"), search = $("#deckFilter"), sort = $("#deckSort");
    const status = $("#deckStatus"), empty = $("#deckEmpty"), pageId = document.body.dataset.pageId, ctx = document.body.dataset.context || "";
    const preview = document.body.dataset.mode === "preview";
    const note = (text) => { const li = document.createElement("li"); li.className = "deck-note"; li.textContent = text; list.replaceChildren(li); };
    let rules = [];
    try { rules = JSON.parse($("[data-dl-groups]")?.dataset.dlGroups || "[]").map((r) => ({ ...r, re: new RegExp(r.match, "i") })); } catch {}
    let files = [];
    if (preview) {
      const at = (y, m) => new Date(Date.UTC(y, m - 1, 15)).toISOString();
      files = [
        { title: "2026-09 About the SKAO.pptx", version: { when: at(2026, 9), by: { displayName: "Communications" } }, extensions: { fileSize: 48e6, comment: "Speaker: Example speaker · Event: Example conference · Audience: General public · Slides: 24 · Classification: Unrestricted" } },
        { title: "2026-06 Construction progress, both sites.pptx", version: { when: at(2026, 6), by: { displayName: "Communications" } }, extensions: { fileSize: 120e6, comment: "Event: Example briefing · Slides: 18" } },
      ];
    } else {
      if (!pageId) return;
      try { files = await attachmentsOf(pageId, ctx, "version,metadata.labels"); } catch { note("The decks could not be loaded."); return; }
    }
    const IMAGE = /\.(png|jpe?g|webp)$/i, baseOf = (t) => String(t || "").replace(/\.[a-z0-9]+$/i, "").toLowerCase();
    const labelled = files.some((f) => Array.isArray(f.metadata?.labels?.results));
    const approved = (f) => preview || !labelled || (f.metadata?.labels?.results || []).some((l) => l.name === "approved");
    const covers = new Map();
    files.forEach((f) => { const href = safeLink(ctx + (f._links?.download || "")); if (href && IMAGE.test(String(f.title || ""))) covers.set(baseOf(f.title), href); });
    // "Key: value" details from the attachment comment.
    const KEYS = { speaker: "speaker", speakers: "speaker", presenter: "speaker", by: "speaker", "made by": "made", author: "made", owner: "made", event: "event", audience: "audience", slides: "slides", classification: "classification", topic: "topic", title: "title", date: "date" };
    const details = (comment) => {
      const out = {};
      String(comment || "").split(/\n|\s+[·|]\s+|\s*;\s*/).forEach((part) => { const m = part.match(/^\s*([a-z ]+?)\s*:\s*(.+?)\s*$/i); if (m && KEYS[m[1].toLowerCase()]) out[KEYS[m[1].toLowerCase()]] = m[2]; });
      return out;
    };
    const CLASSES = ["Strictly Confidential", "Confidential", "For Project Use", "SKAO Staff Only", "Staff Resources", "Unrestricted"];
    const TONES = ["#c2185b", "#0b7bb5", "#c26a1b", "#2f8a5b", "#7c3aed", "#5b6475"];
    const topics = [...new Set(rules.map((r) => r.group))];
    const decks = files.filter((f) => !IMAGE.test(String(f.title || "")) && approved(f)).map((f) => {
      const title = String(f.title || ""), href = preview ? null : safeLink(ctx + (f._links?.download || ""));
      if (!preview && !href) return null;
      const info = details(f.extensions?.comment || f.metadata?.comment);
      const base = title.replace(/\.[a-z0-9]+$/i, "").replace(/_+/g, " ").replace(/\s+/g, " ").trim();
      const dm = base.match(/^(\d{4})[-. ]?(\d{2})(?:[-. ]?\d{2})?[\s-]+(.+)$/);
      const added = Date.parse(f.version?.when || "") || 0;
      const when = dm && +dm[2] >= 1 && +dm[2] <= 12 ? Date.UTC(+dm[1], +dm[2] - 1, 15) : Date.parse(info.date || "") || added;
      let name = info.title || (dm ? dm[3].trim() : base);
      // "A journey through time, de Laeter Colloquium" reads "A journey through time" when the event line names the colloquium.
      const eventName = String(info.event || "").split(",")[0].trim();
      if (eventName) name = name.replace(new RegExp("\\s*[,–—-]\\s*" + escapeRe(eventName) + "\\s*$", "i"), "").trim() || name;
      const topic = info.topic || rules.find((r) => r.re.test(title))?.group || "Other decks";
      const ext = (title.match(/\.([a-z0-9]+)$/i)?.[1] || "file").toLowerCase();
      const id = String(f.id || "").replace(/^att/, "");
      return { title, href, name, when, added, topic, ext, info, id, size: f.extensions?.fileSize, updated: Number(f.version?.number) > 1, by: f.version?.by?.displayName || "",
        classification: info.classification || CLASSES.find((c) => new RegExp("(^|[\\s_-])" + c.replace(/ /g, "[\\s_-]+") + "($|[\\s_.-])", "i").test(base)) || "",
        cover: covers.get(baseOf(title)) || "", preview: !preview && id && pageId ? location.pathname + "?preview=/" + encodeURIComponent(pageId) + "/" + encodeURIComponent(id) + "/" + encodeURIComponent(title) : "" };
    }).filter(Boolean);
    if (!decks.length) { note("No approved decks yet. They appear here as soon as Communications approves them."); return; }
    const toneOf = (topic) => TONES[(topics.indexOf(topic) + TONES.length) % TONES.length] || TONES[TONES.length - 1];
    const month = (t) => { const d = new Date(t); return MONTHS[d.getUTCMonth()] + " " + d.getUTCFullYear(); };
    const KINDS = { pptx: "PowerPoint", ppt: "PowerPoint", potx: "PowerPoint", key: "Keynote", pdf: "PDF" };
    const rows = decks.map((d) => {
      const li = document.createElement("li"); li.className = "deck"; li.dataset.topic = d.topic; li.style.setProperty("--c", toneOf(d.topic));
      const make = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
      // The cover: the picture attached under the deck's own name, or a title slide in the topic's colour.
      const cover = make(d.preview ? "a" : "div", "deck-cover");
      if (d.preview) { cover.href = d.preview; cover.setAttribute("aria-label", "Preview " + d.name); }
      const slide = make("span", "deck-slide"); slide.setAttribute("aria-hidden", "true");
      slide.append(make("small", "", "SKA Observatory"), make("i"), make("i")); cover.append(slide);
      if (d.cover) { const img = new Image(); img.alt = ""; img.decoding = "async"; img.loading = "lazy"; img.onload = () => cover.classList.add("has-image"); img.src = d.cover; cover.append(img); }
      if (d.preview) cover.append(make("span", "deck-peek", "Preview"));
      // What the talk is: its topic, its title, then where and when it was given.
      const body = make("div", "deck-body"), kicker = make("p", "deck-kicker");
      kicker.append(make("span", "deck-topic", d.topic));
      if (preview) kicker.append(make("span", "example-tag", "Example"));
      body.append(kicker, make("h3", "deck-title", d.name));
      const where = [d.info.event, d.when ? month(d.when) : ""].filter(Boolean).join(" · ");
      if (where) body.append(make("p", "deck-event", where));
      // Who gave it, who it was for, who made it, how long it is and who may see it, always in that order.
      const facts = make("dl", "deck-facts");
      const fact = (label, value, cls) => { if (!value) return; const div = make("div", cls); div.append(make("dt", "", label), make("dd", "", value)); facts.append(div); };
      fact("Speaker", d.info.speaker); fact("Audience", d.info.audience); fact("Made by", d.info.made);
      fact("Slides", d.info.slides); fact("Classification", d.classification, "is-class");
      if (facts.children.length) body.append(facts);
      // The file and what you can do with it, in a strip along the bottom of every card.
      const foot = make("div", "deck-foot"), file = make("p", "deck-file"), actions = make("div", "deck-actions");
      file.append(make("strong", "", [KINDS[d.ext] || d.ext.toUpperCase(), size(d.size)].filter(Boolean).join(" · ")));
      if (d.added) file.append(make("span", "", (d.updated ? "Updated " : "Added ") + fmt(d.added)));
      if (d.preview) { const pv = make("a", "button secondary deck-preview", "Preview"); pv.href = d.preview; pv.setAttribute("aria-label", `Preview ${d.name} in Confluence`); actions.append(pv); }
      const get = make("a", "button deck-download", "Download");
      if (d.href) { get.href = d.href; get.setAttribute("download", ""); get.title = d.title; } else get.setAttribute("aria-disabled", "true");
      get.setAttribute("aria-label", `Download ${d.name}, ${KINDS[d.ext] || d.ext.toUpperCase()}${size(d.size) ? ", " + size(d.size) : ""}`);
      actions.append(get); foot.append(file, actions);
      li.append(cover, body, foot);
      li._deck = d; return li;
    });
    // Topic filters (only when there is more than one), search and sort.
    let topic = "all";
    const present = topics.concat(["Other decks"]).filter((t) => decks.some((d) => d.topic === t));
    if (present.length > 1) {
      const chip = (key, label, n) => {
        const b = document.createElement("button"); b.type = "button"; b.dataset.topicFilter = key; b.setAttribute("aria-pressed", String(key === "all"));
        if (key !== "all") b.style.setProperty("--c", toneOf(key));
        const c = document.createElement("span"); c.textContent = n; b.append(label + " ", c);
        b.addEventListener("click", () => { topic = key; chipBox.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", String(x === b))); apply(); });
        return b;
      };
      chipBox.replaceChildren(chip("all", "All", decks.length), ...present.map((t) => chip(t, t, decks.filter((d) => d.topic === t).length)));
      chipBox.hidden = false;
    }
    function apply() {
      const words = terms(search?.value || "");
      const order = sort?.value || "new";
      const sorted = [...rows].sort((a, b) => order === "az" ? a._deck.name.localeCompare(b._deck.name) : order === "old" ? a._deck.when - b._deck.when : b._deck.when - a._deck.when);
      let n = 0;
      sorted.forEach((li) => {
        const hay = li.textContent.toLowerCase();
        const match = (topic === "all" || li.dataset.topic === topic) && words.every((w) => expand(w).some((alt) => hay.includes(alt)));
        li.hidden = !match; if (match) n++;
      });
      list.replaceChildren(...sorted);
      if (status) status.textContent = n === rows.length ? (rows.length === 1 ? "1 deck" : rows.length + " decks") : `Showing ${n} of ${rows.length} decks`;
      if (empty) empty.hidden = n > 0;
    }
    search?.addEventListener("input", apply);
    sort?.addEventListener("change", apply);
    $("#clearDecks")?.addEventListener("click", () => {
      if (search) search.value = ""; topic = "all";
      chipBox.querySelectorAll("button").forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.topicFilter === "all")));
      apply(); search?.focus();
    });
    apply();
  }
  // Earlier decks: a month tile, the deck and its details, and a download button. Long lists show the
  // six newest first, with a button for the rest.
  function deckList(rows) {
    const ol = document.createElement("ol"); ol.className = "deck-list";
    rows.forEach((r, i) => {
      const li = document.createElement("li"); li.className = "deck-row";
      const d = new Date(r.when), [m, y] = r.month ? r.month.split(" ") : [r.when ? MONTHS[d.getMonth()] : "", r.when ? String(d.getFullYear()) : ""];
      const date = document.createElement("span"); date.className = "deck-date"; date.setAttribute("aria-hidden", "true");
      const mb = document.createElement("b"), yb = document.createElement("small"); mb.textContent = (m || "").slice(0, 3); yb.textContent = y || ""; date.append(mb, yb);
      const text = document.createElement("span"); text.className = "deck-text";
      const name = document.createElement("strong"); name.textContent = r.name;
      const meta = document.createElement("span"); meta.textContent = [r.month, r.ext.toUpperCase(), size(r.size), r.when && "added " + fmt(r.when)].filter(Boolean).join(" · ");
      text.append(name, meta);
      const a = document.createElement("a"); a.className = "deck-get"; a.href = r.href; a.setAttribute("download", ""); a.title = r.title;
      a.setAttribute("aria-label", `Download ${r.name}${r.month ? ", " + r.month : ""}, ${r.ext.toUpperCase()}${size(r.size) ? ", " + size(r.size) : ""}`);
      a.textContent = "Download";
      li.append(date, text, a);
      if (i >= 6 && rows.length > 8) li.hidden = true;
      ol.append(li);
    });
    if (rows.length <= 8) return ol;
    const wrap = document.createElement("div"), more = document.createElement("button");
    more.type = "button"; more.className = "button secondary deck-more"; more.textContent = `Show all ${rows.length} earlier decks`;
    more.addEventListener("click", () => { ol.querySelectorAll(".deck-row[hidden]").forEach((li) => { li.hidden = false; }); more.remove(); });
    wrap.append(ol, more); return wrap;
  }
  // SKA-Low and SKA-Mid progress: the newest deck leads in the telescope panel, earlier decks follow.
  async function loadSitePage(box) {
    const hero = $("[data-site-hero]"), pageId = document.body.dataset.pageId, ctx = document.body.dataset.context || "";
    if (!hero || !pageId || document.body.dataset.mode === "preview") return;
    let files = [];
    try { files = await attachmentsOf(pageId, ctx); } catch { return; }
    showPhoto(hero.querySelector("[data-site-photo]"), files, ctx);
    const rows = pageFiles(files, ctx), title = hero.querySelector("[data-hero-title]"), meta = hero.querySelector("[data-hero-meta]");
    if (!rows.length) { title.textContent = "No slides yet"; meta.textContent = hero.dataset.empty || ""; return; }
    const r = rows[0], a = document.createElement("a");
    title.textContent = r.month || fmt(r.when);
    const file = document.createElement("span"); file.className = "site-hero-file"; file.textContent = r.name;
    const details = document.createElement("span"); details.textContent = [r.ext.toUpperCase(), size(r.size), r.when && "added " + fmt(r.when)].filter(Boolean).join(" · ");
    meta.replaceChildren(file, details);
    a.className = "button on-dark"; a.href = r.href; a.setAttribute("download", ""); a.title = r.title; a.textContent = "Download slides";
    hero.querySelector("[data-hero-actions]").replaceChildren(a);
    if (rows.length < 2) return;
    box.querySelector("[data-attachment-list]").replaceChildren(deckList(rows.slice(1)));
    const count = box.querySelector("[data-file-count]"); if (count) count.textContent = rows.length - 1 + (rows.length === 2 ? " deck" : " decks");
    box.hidden = false;
  }
  // The event kit: each item's picture is a file attached to the page under a fixed name
  // (kit-fabrilux-3m.webp and so on). Until it's there, an outline of the item shows instead.
  const kitBox = $("[data-kit]");
  if (kitBox && document.body.dataset.mode !== "preview") loadKit(kitBox);
  async function loadKit(box) {
    const pageId = document.body.dataset.pageId, ctx = document.body.dataset.context || "";
    if (!pageId) return;
    let files = [];
    try {
      const res = await fetch(ctx + "/rest/api/content/" + encodeURIComponent(pageId) + "/child/attachment?" + new URLSearchParams({ limit: "200" }), { credentials: "same-origin", headers: { Accept: "application/json" } });
      if (!res.ok) return;
      files = (await res.json()).results || [];
    } catch { return; }
    box.querySelectorAll("[data-kit-image]").forEach((slot) => {
      const name = slot.dataset.kitImage.toLowerCase();
      const file = files.find((f) => String(f.title || "").toLowerCase().replace(/\.(webp|png|jpe?g)$/, "") === name && /\.(webp|png|jpe?g)$/i.test(f.title));
      const href = file && safeLink(ctx + (file._links?.download || ""));
      if (!href) return;
      const img = new Image(); img.alt = ""; img.decoding = "async";
      img.onload = () => slot.classList.add("has-image");
      img.src = href; slot.append(img);
    });
  }
  // Downloads grouped by the choice people are making: classification, office, partner, then file type.
  // A page shows them as a list (the default), as cards with a cover (decks and templates) or as logo
  // tiles with a preview (brandkit.DOWNLOAD_VIEW).
  function renderDownloads(files, ctx, pictures = []) {
    const CLASSES = ["Unrestricted", "Staff Resources", "SKAO Staff Only", "For Project Use", "Confidential", "Strictly Confidential"];
    const KINDS = [["Templates", /^(pptx?|potx|key|docx?|dotx)$/], ["Guides and PDFs", /^pdf$/], ["ZIP packs", /^zip$/], ["Video", /^(mp4|mov|m4v)$/], ["Motion templates", /^mogrt$/], ["Artwork", /^(ai|eps|indd|psd|svg)$/], ["Images", /^(png|jpe?g|gif|webp)$/]];
    const FORMAT_ORDER = ["pptx", "potx", "key", "docx", "dotx", "pdf", "ai", "eps", "svg", "png", "jpg", "zip", "mp4", "mov", "mogrt"];
    const FORMAT_NAMES = { pptx: "PowerPoint", ppt: "PowerPoint", potx: "PowerPoint", key: "Keynote", docx: "Word", doc: "Word", dotx: "Word", pdf: "PDF", zip: "ZIP" };
    const view = $("[data-dl-groups]")?.dataset.dlView || "list";
    const partnerPage = /co-branding|partner/i.test($(".page-head h1")?.textContent || "");
    let rules = [];
    try { rules = JSON.parse($("[data-dl-groups]")?.dataset.dlGroups || "[]").map((r) => ({ ...r, re: new RegExp(r.match, "i"), cut: r.strip ? new RegExp(r.strip, "gi") : null })); } catch { rules = []; }
    const pattern = (label) => new RegExp("(^|[\\s_-])" + label.replace(/ /g, "[\\s_-]+") + "($|[\\s_.-])", "i");
    const tidy = (label) => {
      let t = label.replace(/_+/g, " ").replace(/\s+/g, " ").trim();
      if (t && t === t.toUpperCase()) t = t.toLowerCase();
      t = t.charAt(0).toUpperCase() + t.slice(1);
      return t.replace(/\b(skao|sarao|csiro|rcn|pdf|ska)\b/gi, (m) => m.toUpperCase()).replace(/\bsrcnet\b/gi, "SRCNet")
        .replace(/\b([a-z]{2,3})src\b/gi, (m, c) => c.toLowerCase() + "SRC").replace(/\ba([0-5])\b/gi, "A$1");
    };
    // Words that name the brand or the file type rather than the version.
    const NOISE = new Set(["skao", "ska", "template", "templates", "letterhead", "wordletterhead", "ppt", "logofiles", "signature", "file", "files"]);
    // Split joined words ("KeynoteTemplate") but keep codes such as "ukSRC" whole.
    const words = (base) => tidy(base.replace(/PowerPoint/g, "Powerpoint").replace(/([a-z])([A-Z][a-z])/g, "$1 $2").replace(/[()]/g, " ")).split(" ").filter((w) => /[\p{L}\p{N}]/u.test(w));
    // On cards, a picture attached under a deck's own name (Deck.pptx and Deck.jpg) is its cover, not a download.
    const IMAGE = /\.(png|jpe?g|webp)$/i, baseOf = (t) => String(t || "").replace(/\.[a-z0-9]+$/i, "").toLowerCase();
    const covers = new Map();
    if (view === "cards") {
      const named = new Set(files.filter((f) => !IMAGE.test(String(f.title || ""))).map((f) => baseOf(f.title)));
      [...pictures, ...files].forEach((f) => { const href = safeLink(ctx + (f._links?.download || "")); if (href && IMAGE.test(String(f.title || "")) && named.has(baseOf(f.title))) covers.set(baseOf(f.title), href); });
      files = files.filter((f) => !(IMAGE.test(String(f.title || "")) && covers.has(baseOf(f.title))));
    }
    const variants = new Map();
    files.forEach((f) => {
      const title = String(f.title || ""), ext = (title.match(/\.([a-z0-9]+)$/i)?.[1] || "").toLowerCase();
      const href = safeLink(ctx + (f._links?.download || ""));
      if (!href) return;
      const base = title.replace(/\.[a-z0-9]+$/i, "");
      const w = words(base), key = w.filter((x) => !/^(keynote|powerpoint)$/i.test(x)).join(" ").toLowerCase();
      if (!variants.has(key)) variants.set(key, { base, words: w.filter((x) => !/^(keynote|powerpoint)$/i.test(x)), files: [] });
      variants.get(key).files.push({ title, ext, href, size: size(f.extensions?.fileSize), when: Date.parse(f.version?.when || "") || 0 });
    });
    if (!variants.size) return null;
    [...variants.values()].forEach((v) => {
      v.cls = [...CLASSES].sort((x, y) => y.length - x.length).find((c) => pattern(c).test(v.base));
      const kinds = [...new Set(v.files.map((i) => KINDS.find(([, re]) => re.test(i.ext))?.[0] || "Other files"))];
      v.group = kinds.length > 1 ? "Files" : kinds[0];
      v.rule = v.cls ? null : rules.find((r) => v.files.some((i) => r.re.test(i.title)));
      if (v.cls) v.group = "By information classification";
      else if (v.rule) v.group = v.rule.group;
      else if (!partnerPage && /\b(sarao|csiro|srcnet|rcn)\b|[a-z]src\b/i.test(v.words.join(" "))) v.group = "Partner versions";
      else if (v.group === "Templates" && /office|landscape|portrait/i.test(v.base)) v.group = "By office and layout";
    });
    // A page's own group names come first; one may share a name with a file type ("Templates"), so each name is listed once.
    const ORDER = [...new Set(["By information classification", ...rules.map((r) => r.group), "By office and layout", "Files", ...KINDS.map(([k]) => k), "Other files", "Partner versions"])];
    const groups = ORDER.map((name) => [name, [...variants.values()].filter((v) => v.group === name)]).filter(([, g]) => g.length);
    const total = [...variants.values()].reduce((n, v) => n + v.files.length, 0);
    const section = document.createElement("section"); section.className = "downloads"; section.id = "downloads"; section.setAttribute("aria-labelledby", "downloadsHeading");
    const head = document.createElement("div"); head.className = "downloads-head";
    const h2 = document.createElement("h2"); h2.id = "downloadsHeading"; h2.textContent = "Downloads";
    const count = document.createElement("p"); count.textContent = total + (total === 1 ? " file" : " files");
    head.append(h2, count); section.append(head);
    const wrap = document.createElement("div"); wrap.className = "dl-groups" + (groups.length > 1 && view === "list" ? " multi" : "") + (view === "list" ? "" : " " + view);
    // One download button per format, in a set order.
    const chip = (row, i, friendly, bare) => {
      const kind = (friendly && FORMAT_NAMES[i.ext]) || (i.ext || "file").toUpperCase();
      const a = document.createElement("a"); a.className = "dl-file"; a.href = i.href; a.setAttribute("download", ""); a.title = i.title;
      a.setAttribute("aria-label", `Download ${row.label}, ${kind}${i.size ? ", " + i.size : ""}`);
      const b = document.createElement("b"); b.textContent = kind; b.dataset.ext = i.ext;
      const small = document.createElement("small"); small.textContent = i.size;
      a.append(b); if (!bare) a.append(small); return a;
    };
    const inOrder = (row) => row.files.sort((x, y) => (FORMAT_ORDER.indexOf(x.ext) + 99) % 99 - (FORMAT_ORDER.indexOf(y.ext) + 99) % 99);
    // Decks and templates: a cover (or the title, set as a slide), the month from a "2026-10" prefix, and a button per format.
    let tone = -1;  // each group of cards gets the next colour, starting from the brand's navy and magenta
    const cards = (list) => {
      tone++;
      const ul = document.createElement("ul"); ul.className = "file-cards";
      // Newest first: by the month in the file name, else by when it was added.
      const dated = (row) => { const m = row.base.match(/^(\d{4})[-. ]?(\d{2})/); return m ? Date.UTC(+m[1], +m[2] - 1, 28) : Math.max(...row.files.map((i) => i.when)); };
      [...list].sort((x, y) => dated(y) - dated(x)).forEach((row) => {
        const base = row.base.replace(/_+/g, " ").replace(/\s+/g, " ").trim(), dm = base.match(/^(\d{4})[-. ]?(\d{2})(?:[-. ]?\d{2})?[\s-]+(.+)$/);
        const month = dm && +dm[2] >= 1 && +dm[2] <= 12 ? MONTHS[+dm[2] - 1] + " " + dm[1] : "";
        row.label = row.rule?.label || (dm ? dm[3].trim() : base);
        const li = document.createElement("li"); li.className = "file-card";
        const cover = document.createElement("div"); cover.className = "file-cover"; cover.setAttribute("aria-hidden", "true");
        const type = document.createElement("span"), brand = document.createElement("small");
        type.className = "cover-type"; brand.textContent = "SKA Observatory"; type.append(brand, document.createElement("i"), document.createElement("i")); cover.append(type);
        cover.dataset.tone = String(tone % 4);
        const pic = row.files.map((i) => covers.get(baseOf(i.title))).find(Boolean);
        if (pic) { const img = new Image(); img.alt = ""; img.decoding = "async"; img.loading = "lazy"; img.onload = () => cover.classList.add("has-image"); img.src = pic; cover.append(img); }
        const body = document.createElement("div"); body.className = "file-card-body";
        if (month) { const k = document.createElement("p"); k.className = "file-card-kicker"; k.textContent = month; body.append(k); }
        const h = document.createElement("h4"); h.className = "file-card-title"; h.textContent = row.label; body.append(h);
        if (row.rule?.desc) { const d = document.createElement("p"); d.className = "file-card-desc"; d.textContent = row.rule.desc; body.append(d); }
        const get = document.createElement("p"); get.className = "file-card-files"; inOrder(row).forEach((i) => get.append(chip(row, i, true)));
        body.append(get); li.append(cover, body); ul.append(li);
      });
      return ul;
    };
    // Logos: the PNG as a preview (white versions on navy), or the centre's code for a regional pack.
    const COUNTRIES = { aus: "Australia", ca: "Canada", ch: "Switzerland", cn: "China", de: "Germany", es: "Spain", fr: "France", in: "India", it: "Italy", jp: "Japan", kr: "Republic of Korea", nl: "Netherlands", pt: "Portugal", se: "Sweden", uk: "United Kingdom", za: "South Africa" };
    const tiles = (list) => {
      const ul = document.createElement("ul"); ul.className = "logo-tiles";
      if (list.every((row) => /^[a-z]{2,3}SRC$/.test(row.label))) ul.classList.add("packs");
      list.forEach((row) => {
        const code = row.label.match(/^([a-z]{2,3})SRC$/);
        if (!code) row.label = row.label.replace(/^colou?r$/i, "Full colour");
        const li = document.createElement("li"); li.className = "logo-tile" + (code ? " is-pack" : "");
        if (/white/i.test(row.base)) li.dataset.tone = "dark";
        const look = document.createElement("div"); look.className = "logo-preview"; look.setAttribute("aria-hidden", "true");
        const png = row.files.find((i) => i.ext === "png");
        if (png) { const img = new Image(); img.alt = ""; img.decoding = "async"; img.loading = "lazy"; img.onload = () => look.classList.add("has-image"); img.src = png.href; look.append(img); }
        else if (code) { const t = document.createElement("span"), b = document.createElement("b"); t.className = "logo-code"; b.textContent = "SRC"; t.append(code[1], b); look.append(t); }
        const body = document.createElement("div"); body.className = "logo-tile-body";
        const name = document.createElement("strong"); name.textContent = row.label; body.append(name);
        if (code && COUNTRIES[code[1]]) { const c = document.createElement("small"); c.textContent = COUNTRIES[code[1]]; body.append(c); }
        const get = document.createElement("span"); get.className = "dl-files"; inOrder(row).forEach((i) => get.append(chip(row, i, false, !code)));
        body.append(get); li.append(look, body); ul.append(li);
      });
      return ul;
    };
    groups.forEach(([name, list]) => {
      // Drop words every version in the group shares, when they are brand/type words or the group is large enough.
      let lead = 0, tail = 0;
      // Named groups keep their descriptive words ("Logo flare statement 1"); only brand and type words go.
      const rule = list[0].rule, strippable = (word) => NOISE.has(word.toLowerCase()) || (!rule && list.length >= 3);
      const at = (v, i) => v.words[i]?.toLowerCase();
      if (list.length > 1) {
        while (list.every((v) => v.words.length - lead - tail > 1 && at(v, lead) === at(list[0], lead)) && strippable(list[0].words[lead])) lead++;
        while (list.every((v) => v.words.length - lead - tail > 1 && at(v, v.words.length - 1 - tail) === at(list[0], list[0].words.length - 1 - tail)) && strippable(list[0].words[list[0].words.length - 1 - tail])) tail++;
      }
      list.forEach((v, n) => {
        let label = v.cls || v.rule?.label || v.words.slice(lead, v.words.length - tail).join(" ") || tidy(v.base);
        if (v.rule?.cut && !v.rule.label) label = label.replace(v.rule.cut, " ").replace(/\s+/g, " ").trim() || tidy(v.base);
        v.label = /^[a-z]+(\s|$)/.test(label) ? label.charAt(0).toUpperCase() + label.slice(1) : label;
        v.rank = v.cls ? CLASSES.indexOf(v.cls) : n;
      });
      const g = document.createElement("section"); g.className = "dl-group";
      if (list[0].rule?.site) g.dataset.site = list[0].rule.site;
      if (groups.length > 1) {
        const h3 = document.createElement("h3"); h3.textContent = name; g.append(h3);
        const note = list[0].rule?.note;
        if (note) { const n = document.createElement("p"); n.className = "dl-note"; n.textContent = note; g.append(n); }
      }
      list.sort((x, y) => x.rank - y.rank);
      if (view === "cards") g.append(cards(list));
      else if (view === "logos") g.append(tiles(list));
      else {
        const ul = document.createElement("ul");
        list.forEach((row) => {
          const li = document.createElement("li"); li.className = "dl-row";
          const label = document.createElement("span"); label.className = "dl-label"; label.textContent = row.label;
          const formats = document.createElement("span"); formats.className = "dl-files";
          inOrder(row).forEach((i) => formats.append(chip(row, i, false)));
          li.append(label, formats); ul.append(li);
        });
        g.append(ul);
      }
      wrap.append(g);
    });
    section.append(wrap);
    return section;
  }
  // Canto showcase: images synced from the staff media folder into a Hub page's attachments.
  loadCanto();
  async function loadCanto() {
    const slots = $$("[data-canto]");
    if (!slots.length || document.body.dataset.mode === "preview") return;
    const ctx = document.body.dataset.context || "";
    const CANTO = /^https:\/\/[a-z0-9-]+\.canto\.global\//i;
    let manifest;
    try {
      const cql = 'type=attachment AND space="CRH" AND title="canto-showcase.json"';
      const res = await fetch(ctx + "/rest/api/content/search?" + new URLSearchParams({ cql, limit: "1" }), { credentials: "same-origin", headers: { Accept: "application/json" } });
      if (!res.ok) return;
      const hit = ((await res.json()).results || [])[0];
      const url = hit && safeLink(ctx + (hit._links?.download || ""));
      if (!url) return;
      const m = await fetch(url, { credentials: "same-origin" });
      if (!m.ok) return;
      manifest = await m.json();
    } catch { return; }
    const asset = (a) => {
      const src = typeof a?.src === "string" && a.src.startsWith("/download/attachments/") ? safeLink(ctx + a.src) : null;
      const href = typeof a?.href === "string" && CANTO.test(a.href) ? a.href : null;
      return src && href ? { src, href, title: String(a.title || "Untitled"), alt: String(a.alt || a.title || ""), credit: String(a.credit || ""), video: a.kind === "video", w: Number(a.width) || 0, h: Number(a.height) || 0 } : null;
    };
    const albums = (Array.isArray(manifest?.albums) ? manifest.albums : []).map((al) => ({
      name: String(al.name || "Album"), path: String(al.path || al.name || "Album"), count: Number(al.count) || 0,
      href: typeof al.href === "string" && CANTO.test(al.href) ? al.href : null,
      assets: (Array.isArray(al.assets) ? al.assets : []).map(asset).filter(Boolean),
    })).filter((al) => al.assets.length);
    if (!albums.length) return;
    const folderHref = typeof manifest.href === "string" && CANTO.test(manifest.href) ? manifest.href : null;
    if (folderHref) $$(".canto-gallery .canto-open").forEach((a) => { a.href = folderHref; });
    const curated = (Array.isArray(manifest?.highlights) ? manifest.highlights : []).map(asset).filter(Boolean);
    // Drop the folder levels every album shares, so tabs read "Telescopes" rather than "Asset library - Staff / Telescopes".
    const parts = albums.map((al) => al.path.split(" / "));
    let shared = 0;
    while (parts.every((p) => p.length - shared > 1 && p[shared] === parts[0][shared])) shared++;
    albums.forEach((al, i) => { al.path = parts[i].slice(shared).join(" / ") || al.name; });
    // View-only slideshow: it shows what is in the library; opening Canto is the button beside it.
    const slideshow = (slot, list) => {
      const stage = slot.querySelector(".show-stage"), ul = slot.querySelector(".show-slides"), dots = slot.querySelector(".show-dots");
      const play = slot.querySelector(".show-play"), items = list.slice(0, 12);
      let at = 0, timer = null, paused = reducedMotion.matches || items.length < 2;
      const slides = items.map((a, i) => {
        const li = document.createElement("li"), img = document.createElement("img"), cap = document.createElement("p");
        li.className = "show-slide"; li.setAttribute("aria-roledescription", "slide"); li.setAttribute("aria-label", `${i + 1} of ${items.length}`);
        // Large images: only the first two load straight away, the rest just before they show.
        if (i < 2) img.src = a.src; else img.dataset.src = a.src;
        img.alt = a.alt || a.title; img.decoding = "async";
        if (a.w && a.h) { img.width = a.w; img.height = a.h; }
        cap.className = "show-caption";
        const t = document.createElement("strong"); t.textContent = a.title; cap.append(t);
        if (a.video) { const v = document.createElement("span"); v.className = "show-kind"; v.textContent = "Video"; cap.prepend(v); }
        if (a.credit) { const c = document.createElement("small"); c.textContent = /^(©|\(c\)|credit)/i.test(a.credit) ? a.credit : "© " + a.credit; cap.append(c); }
        li.append(img, cap); return li;
      });
      ul.replaceChildren(...slides);
      const marks = items.map((a, i) => {
        const b = document.createElement("button"); b.type = "button"; b.setAttribute("aria-label", `Show image ${i + 1}: ${a.title}`);
        b.addEventListener("click", () => { show(i); stop(true); }); return b;
      });
      dots.replaceChildren(...marks); dots.hidden = items.length < 2;
      slot.querySelectorAll(".show-prev, .show-next, .show-play").forEach((b) => { b.hidden = items.length < 2; });
      function show(i) {
        at = (i + items.length) % items.length;
        slides.forEach((li, n) => { const on = n === at; li.classList.toggle("is-on", on); li.setAttribute("aria-hidden", String(!on)); });
        marks.forEach((b, n) => b.setAttribute("aria-current", n === at ? "true" : "false"));
        [at, (at + 1) % items.length].forEach((n) => { const img = slides[n].querySelector("img"); if (img.dataset.src) { img.src = img.dataset.src; delete img.dataset.src; } });
      }
      const tick = () => { clearTimeout(timer); if (!paused && !hold) timer = setTimeout(() => { show(at + 1); tick(); }, 5200); };
      let hold = false;
      function stop(byUser) { if (byUser) paused = true; clearTimeout(timer); sync(); }
      function sync() {
        play.setAttribute("aria-pressed", String(paused)); play.setAttribute("aria-label", paused ? "Play slideshow" : "Pause slideshow");
        stage.classList.toggle("is-paused", paused);
        ul.setAttribute("aria-live", paused ? "polite" : "off");
      }
      play.addEventListener("click", () => { paused = !paused; sync(); if (!paused) { show(at + 1); tick(); } else clearTimeout(timer); });
      slot.querySelector(".show-prev").addEventListener("click", () => { show(at - 1); stop(true); });
      slot.querySelector(".show-next").addEventListener("click", () => { show(at + 1); stop(true); });
      // Hovering or tabbing into the slideshow holds it on the current image.
      stage.addEventListener("pointerenter", () => { hold = true; clearTimeout(timer); });
      stage.addEventListener("pointerleave", () => { hold = false; tick(); });
      slot.addEventListener("focusin", () => { hold = true; clearTimeout(timer); });
      slot.addEventListener("focusout", (e) => { if (!slot.contains(e.relatedTarget)) { hold = false; tick(); } });
      document.addEventListener("visibilitychange", () => { hold = document.hidden; tick(); });
      show(0); sync(); tick();
    };
    // The page's "Open the Canto library" button moves under the slideshow, so it sits with what it opens.
    const dock = (slot, href) => {
      const btn = $(".content-body > .task-intro > a.button[href*='canto.global']");
      const foot = slot.querySelector(".show-foot");
      if (btn && foot) { if (href) btn.href = href; btn.target = "_blank"; btn.rel = "noopener"; foot.append(btn); }
      else if (foot && href) {
        const a = document.createElement("a"); a.className = "button"; a.href = href; a.target = "_blank"; a.rel = "noopener";
        a.innerHTML = 'Open the Canto library <span class="arr arr-out" aria-hidden="true">↗</span>'; foot.append(a);
      }
    };
    slots.forEach((slot) => {
      const words = (slot.dataset.canto || "").toLowerCase().split(/\s+/).filter(Boolean);
      const matches = words.length ? albums.filter((al) => words.some((w) => new RegExp("(^|[^a-z0-9])" + escapeRe(w) + "([^a-z0-9]|$)", "i").test(al.path + " " + al.name))) : albums;
      if (!matches.length) return;
      let list, href;
      if (slot.classList.contains("wide")) {
        // The best of the library: curated highlights, else photos from the image collections in turn (not events or reels).
        const showcase = matches.filter((al) => !/\b(events?|videos?)\b/i.test(al.name));
        const source = showcase.length ? showcase : matches, all = [], seen = new Set();
        const take = (wantVideo) => { for (let i = 0; all.length < 12 && source.some((al) => al.assets[i]); i++) source.forEach((al) => { const a = al.assets[i]; if (a && a.video === wantVideo && !seen.has(a.src) && all.length < 12) { seen.add(a.src); all.push(a); } }); };
        if (curated.length >= 4) curated.slice(0, 12).forEach((a) => { if (!seen.has(a.src)) { seen.add(a.src); all.push(a); } });
        else { take(false); take(true); }
        list = all; href = folderHref;
      } else {
        const al = matches[0];
        list = matches.flatMap((m) => m.assets.filter((a) => !a.video)).concat(matches.flatMap((m) => m.assets.filter((a) => a.video)));
        href = (matches.length === 1 && al.href) || folderHref;
        const h = slot.querySelector("h2"); if (h && matches.length === 1) h.textContent = "In the staff media library: " + al.path;
      }
      if (!list.length) return;
      slot.hidden = false;
      slideshow(slot, list);
      dock(slot, href);
      // The synced album replaces the generic "search Canto" box; its search tip moves under the slideshow.
      const hand = $(".content-body .media-handoff"), tip = hand?.querySelector("p:not(.quiet-note)")?.textContent;
      const note = slot.querySelector(".show-note");
      if (tip && note && !slot.classList.contains("wide")) note.textContent = tip;
      const hid = hand?.querySelector("h2")?.id;
      if (hid) $$("#toc a").find((a) => a.hash === "#" + hid)?.remove();
      hand?.remove();
    });
  }
  // Latest approved assets on the homepage.
  const latest = $("#latestAssets");
  if (latest) loadLatest(latest);
  async function loadLatest(box) {
    const DELIVERABLE = /\.(pptx?|potx|key|docx?|dotx|pdf|zip|ai|eps|svg|indd|idml|xlsx|mp4|mov)$/i;
    const fmtDate = (v) => { try { return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric" }).format(new Date(v)); } catch { return ""; } };
    const fmtSize = (n) => !n ? "" : n > 1048576 ? (n / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1024)) + " KB";
    const strip = box.closest(".latest-strip");
    const status = (msg) => { if (strip) { strip.hidden = true; return; } const p = document.createElement("p"); p.className = "latest-status"; p.textContent = msg; box.replaceChildren(p); };
    const show = (cards) => { box.replaceChildren(...(strip ? cards.slice(0, 3) : cards)); if (strip) strip.hidden = false; };
    // The strip lists pages, newest first: a page that gained three files shows once, as "3 new files".
    const when = (v) => {
      const d = new Date(v), days = Math.floor((Date.now() - d) / 864e5);
      if (isNaN(d)) return "";
      if (days < 1) return "Today";
      if (days < 2) return "Yesterday";
      if (days < 7) return days + " days ago";
      try { return new Intl.DateTimeFormat("en-GB", d.getFullYear() === new Date().getFullYear() ? { day: "numeric", month: "short" } : { day: "numeric", month: "short", year: "numeric" }).format(d); } catch { return ""; }
    };
    const fileName = (t) => t.replace(/\.[a-z0-9]+$/i, "").replace(/_+/g, " ").replace(/\s*\+\s*/g, " + ").replace(/\s+/g, " ").trim();
    const stripItems = (rows, example) => {
      const pages = new Map();
      rows.forEach((r) => { const k = r.pageHref || r.pageTitle || r.title; if (!pages.has(k)) pages.set(k, []); pages.get(k).push(r); });
      return [...pages.values()].slice(0, 3).map((files, i) => {
        const r = files[0], ext = (r.title.match(/\.([a-z0-9]+)$/i)?.[1] || "file").toLowerCase();
        const a = document.createElement("a"); a.className = "strip-item"; a.style.setProperty("--i", i);
        const page = example ? null : safeLink(r.pageHref || r.download);
        if (page) a.href = page + (r.pageHref ? "#downloads" : ""); else a.setAttribute("aria-disabled", "true");
        a.title = files.map((f) => f.title).join("\n");
        const badge = document.createElement("span"); badge.className = "file-badge"; badge.dataset.ext = ext; badge.textContent = ext.toUpperCase().slice(0, 4);
        const text = document.createElement("span"); text.className = "strip-text";
        const name = document.createElement("strong"); name.textContent = r.pageTitle || fileName(r.title);
        const meta = document.createElement("span"); meta.className = "strip-meta";
        // The file name gives way before the date does.
        const what = document.createElement("span"), date = document.createElement("span");
        what.className = "strip-file"; what.textContent = files.length > 1 ? files.length + " new files" : r.pageTitle ? fileName(r.title) : "";
        date.className = "strip-when"; date.textContent = when(r.when);
        if (what.textContent && date.textContent) date.textContent = " · " + date.textContent;
        meta.append(...[what, date].filter((x) => x.textContent));
        text.append(name, meta); a.append(badge, text);
        return a;
      });
    };
    function card(r, example) {
      const a = document.createElement("article"); a.className = "asset-card";
      const ext = (r.title.match(/\.([a-z0-9]+)$/i)?.[1] || "file").toUpperCase();
      const badge = document.createElement("span"); badge.className = "file-badge"; badge.dataset.ext = ext.toLowerCase(); badge.textContent = ext;
      const h = document.createElement("h3"), link = document.createElement("a");
      link.textContent = r.title.replace(/\.[a-z0-9]+$/i, "").replace(/_+/g, " ").replace(/\s+/g, " ").trim();
      const href = example ? null : safeLink(r.download);
      if (href) link.href = href; else link.setAttribute("aria-disabled", "true");
      h.append(link);
      const meta = document.createElement("p"); meta.className = "asset-meta";
      meta.textContent = [r.when && "Added " + fmtDate(r.when), fmtSize(r.size)].filter(Boolean).join(" · ");
      a.append(badge, h, meta);
      if (r.pageTitle) {
        const from = document.createElement("p"), pl = document.createElement("a");
        from.className = "asset-source"; from.append("From ");
        pl.textContent = r.pageTitle; const ph = example ? null : safeLink(r.pageHref);
        if (ph) pl.href = ph;
        from.append(pl); a.append(from);
      }
      if (example) { const t = document.createElement("span"); t.className = "example-tag"; t.textContent = "Example"; a.append(t); }
      return a;
    }
    if (document.body.dataset.mode === "preview") {
      $("#latestLead").textContent = "Examples in this preview";
      const examples = [
        { title: "Presentation-template.potx", when: Date.now() - 2 * 864e5, size: 4.2 * 1048576, pageTitle: "Standard SKAO template" },
        { title: "Letterhead-A4.dotx", when: Date.now() - 6 * 864e5, size: 310 * 1024, pageTitle: "Letterheads" },
        { title: "Poster-A0-portrait.pdf", when: Date.now() - 11 * 864e5, size: 2.8 * 1048576, pageTitle: "Poster templates" },
      ];
      show(strip ? stripItems(examples, true) : examples.map((r) => card(r, true)));
      return;
    }
    const ctx = document.body.dataset.context || "";
    const query = async (cql, limit) => {
      const res = await fetch(ctx + "/rest/api/content/search?" + new URLSearchParams({ cql, limit: String(limit), expand: "container,version" }), { credentials: "same-origin", headers: { Accept: "application/json" } });
      if (!res.ok) throw Error(String(res.status));
      return ((await res.json()).results || []).map((r) => ({
        title: String(r.title || ""),
        when: r.version?.when,
        size: r.extensions?.fileSize,
        download: r._links?.download ? ctx + r._links.download : "",
        pageTitle: r.container?.title ? String(r.container.title) : "",
        pageHref: r.container?._links?.webui ? ctx + r.container._links.webui : "",
      }));
    };
    try {
      const label = cqlLiteral(box.dataset.approvalLabel || "approved");
      let rows = await query(`type=attachment AND space="CRH" AND label="${label}" ORDER BY created DESC`, 6);
      if (!rows.length) {
        // Nothing labelled yet: show recent deliverable files, not page images, and say so.
        rows = (await query('type=attachment AND space="CRH" ORDER BY created DESC', 50)).filter((r) => DELIVERABLE.test(r.title)).slice(0, 6);
        $("#latestHeading").textContent = "Latest files in the Hub";
        $("#latestLead").textContent = "Recent uploads: check approval on the source page";
      }
      if (!rows.length) { status("No new files yet. Browse all resources for everything in the Hub."); return; }
      show(strip ? stripItems(rows, false) : rows.map((r) => card(r, false)));
    } catch (e) {
      status(e.message === "401" || e.message === "403" ? "Sign in to Confluence to see the latest files." : "The latest files could not be loaded. Browse all resources instead.");
    }
  }
  // Header gains a shadow once the navigation is pinned.
  const headerEl = $("header");
  if (headerEl) {
    const pin = () => headerEl.classList.toggle("is-pinned", scrollY > headerEl.querySelector(".brandbar").offsetHeight);
    addEventListener("scroll", pin, { passive: true });
    pin();
  }
  const form = $("#briefForm");
  if (form) form.hidden = false;
  form?.addEventListener("submit", (e) => {
    e.preventDefault();
    const d = new FormData(form),
      lines = ["Creative request draft", ""];
    for (const [key, value] of d)
      lines.push(key + ": " + (String(value).trim() || "To confirm"));
    $("#briefOutput").textContent = lines.join("\n\n");
    $("#draftPanel").hidden = false;
    $("#draftPanel").scrollIntoView({
      block: "nearest",
      behavior: matchMedia("(prefers-reduced-motion: reduce)").matches
        ? "auto"
        : "smooth",
    });
    $("#draftHeading").focus();
  });
  $("#copyBrief")?.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText($("#briefOutput").textContent);
      $("#copyStatus").textContent =
        "Copied. Paste this into your helpdesk request and attach any supporting files there.";
    } catch {
      $("#copyStatus").textContent =
        "Clipboard unavailable. Select and copy the draft text below.";
    }
  });
  const article = $(".content-body"),
    toc = $("#toc");
  if (article && /ASSET\s+TO\s+ADD/i.test(article.textContent)) {
    const notice=document.createElement("aside"); notice.className="source-check";
    const title=document.createElement("h2"), text=document.createElement("p"), route=document.createElement("a");
    title.textContent="Resource not yet ready on this page";
    text.textContent="This page contains asset placeholders. The listed files and version details should not be treated as a released resource. Ask the Comms helpdesk for an available source.";
    route.href="https://jira.skatelescope.org/servicedesk/customer/portal/364";
    route.textContent="Ask for the available resource ↗";
    notice.append(title,text,route); article.prepend(notice);
  }
  if (article && toc && !$("[data-file-feed]") && !article.querySelector(".directory")) {
    const pageTitle = document.querySelector(".page-head h1");
    const first = article.querySelector("h1");
    if (
      first &&
      /^H[1-6]$/.test(first.tagName) &&
      pageTitle &&
      first.textContent.trim() === pageTitle.textContent.trim()
    )
      first.remove();
    const headings = [...article.querySelectorAll("h2")].filter(
      (h) => !h.closest("[hidden], details, .choice-card, .section-next, .file-feed"),
    );
    const rail = toc.closest(".toc-rail"), grid = toc.closest(".page-grid");
    // Only long pages get a contents list: four sections or more.
    if (headings.length > 3 && rail && !grid?.classList.contains("full-width")) {
      rail.hidden = false; grid.classList.add("has-toc");
      headings.forEach((heading, i) => {
        if (!heading.id) { let id = slugify(heading.textContent); while (document.getElementById(id)) id += "-" + i; heading.id = id; }
        const a = document.createElement("a");
        a.href = "#" + heading.id;
        a.textContent = heading.textContent;
        toc.append(a);
      });
    }
    // Mark the section currently in view.
    const tocLinks = [...toc.querySelectorAll("a")];
    const targets = tocLinks.map((a) => document.getElementById(a.hash.slice(1))).filter(Boolean);
    let ticking = false;
    const spy = () => {
      ticking = false;
      const atEnd = scrollY > 0 && innerHeight + scrollY >= document.documentElement.scrollHeight - 4;
      let current = targets.filter((h) => h.getBoundingClientRect().top < innerHeight * 0.35).pop() || targets[0];
      if (atEnd) current = targets[targets.length - 1];
      tocLinks.forEach((a) => a.hash.slice(1) === current?.id ? a.setAttribute("aria-current", "true") : a.removeAttribute("aria-current"));
    };
    if (targets.length) {
      addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(spy); } }, { passive: true });
      spy();
    }
  }
  // Side menus fold away for more room; each viewer's choice is remembered on this device.
  const pageGrid = $(".page-grid:not(.full-width)");
  if (pageGrid) {
    const remember = (k, v) => { try { localStorage.setItem(k, v); } catch {} };
    const recall = (k) => { try { return localStorage.getItem(k); } catch { return null; } };
    const labels = { nav: "the section menu", toc: "On this page" };
    const fold = (button, closed) => {
      const rail = button.dataset.rail;
      pageGrid.classList.toggle(rail + "-closed", closed);
      button.setAttribute("aria-expanded", String(!closed));
      const label = (closed ? "Show " : "Hide ") + labels[rail];
      button.setAttribute("aria-label", label); button.title = label;
    };
    $$(".page-grid .rail-toggle").forEach((button) => {
      const key = "crh-" + button.dataset.rail + "-closed";
      fold(button, recall(key) === "1");
      button.addEventListener("click", () => {
        const closed = !pageGrid.classList.contains(button.dataset.rail + "-closed");
        fold(button, closed); remember(key, closed ? "1" : "0");
      });
    });
  }
  // Section headings can be linked to directly: a small link button copies the address.
  const bodyText = $(".content-body");
  if (bodyText && !bodyText.querySelector(".directory")) {
    bodyText.querySelectorAll("h2").forEach((h) => {
      if (h.closest("[hidden], details, .section-next, .file-feed, .canto-show, .asset-panel, .live-link, .site-photos, .site-card, .kit-item, .attachments-head, .next-step, .downloads-head")) return;
      if (!h.id) { let id = slugify(h.textContent); while (document.getElementById(id)) id += "-2"; h.id = id; }
      const b = document.createElement("button");
      b.type = "button"; b.className = "heading-link"; b.setAttribute("aria-label", "Copy a link to " + h.textContent.trim());
      b.innerHTML = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></svg>';
      b.addEventListener("click", async () => {
        const url = location.href.split("#")[0] + "#" + h.id, status = $("#copyAnnounce");
        try { await navigator.clipboard.writeText(url); b.classList.add("is-copied"); if (status) status.textContent = "Link copied."; }
        catch { history.replaceState(null, "", "#" + h.id); if (status) status.textContent = "Copy the address from the address bar."; }
        clearTimeout(b._t); b._t = setTimeout(() => b.classList.remove("is-copied"), 1800);
      });
      h.append(b);
    });
  }
  // When the page was last changed, under its title.
  const head = $(".page-band .page-head"), thisPage = document.body.dataset.pageId;
  if (head && thisPage && !$("[data-file-feed]") && document.body.dataset.mode !== "preview") (async () => {
    try {
      const ctx = document.body.dataset.context || "";
      const res = await fetch(ctx + "/rest/api/content/" + encodeURIComponent(thisPage) + "?expand=version", { credentials: "same-origin", headers: { Accept: "application/json" } });
      const when = res.ok ? Date.parse((await res.json()).version?.when) : NaN;
      if (!when) return;
      const p = document.createElement("p");
      p.className = "page-updated";
      p.textContent = "Updated " + new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric" }).format(when);
      head.append(p);
    } catch {}
  })();
  const mac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent || "");
  // Copy values such as colour codes.
  $$("[data-copy]").forEach((b) => b.addEventListener("click", async () => {
    const label = b.querySelector("span") || b, before = label.textContent, status = $("#copyAnnounce");
    try {
      await navigator.clipboard.writeText(b.dataset.copy);
      label.textContent = "Copied";
      if (status) status.textContent = (b.dataset.copyLabel || b.dataset.copy) + " copied to clipboard.";
    } catch {
      const code = b.querySelector("code") || b, range = document.createRange();
      range.selectNodeContents(code);
      getSelection().removeAllRanges();
      getSelection().addRange(range);
      label.textContent = mac ? "Press ⌘C" : "Press Ctrl C";
      if (status) status.textContent = "Clipboard unavailable. " + (b.dataset.copyLabel || b.dataset.copy) + " is selected; copy it with your keyboard.";
    }
    clearTimeout(b._t);
    b._t = setTimeout(() => { label.textContent = before; }, 2400);
  }));
  $$("[data-shortcut]").forEach((k) => { k.textContent = mac ? "⌘K" : "Ctrl K"; });
  $$(".navrow .search-trigger").forEach((b) => { b.title = "Search the Hub (" + (mac ? "⌘K" : "Ctrl K") + " or /)"; });
});
