"use strict";
document.documentElement.classList.add("js");
document.addEventListener("DOMContentLoaded", () => {
  const $ = (s) => document.querySelector(s),
    $$ = (s) => [...document.querySelectorAll(s)];
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
      motion.querySelector("span").textContent = paused ? "▷" : "Ⅱ";
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
  const terms = (q) => q.toLowerCase().split(/[^\p{L}\p{N}-]+/u).filter((t) => t.length > 1);
  const escapeRe = (t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  function rank(rows, q) {
    const words = terms(q), phrase = q.toLowerCase().trim();
    if (!words.length) return [];
    return rows
      .map((r) => {
        const title = (r.title || "").toLowerCase(), excerpt = (r.excerpt || "").toLowerCase(), body = (r.keywords || "").toLowerCase();
        let score = title === phrase ? 40 : title.includes(phrase) ? 15 : 0;
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
  function renderRows(rows) {
    results.replaceChildren();
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
      results.replaceChildren();
      message.textContent = "";
      return;
    }
    message.textContent = "Searching…";
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
        const labels={"381891696":"Templates and assets","381891810":"Share material","381891794":"Prepare a presentation","381891661":"Request creative help"};
        const local = rank(localRoutes().map((r) => ({ ...r, title: labels[r.id] || r.title })), q);
        if (local.length) { results.replaceChildren(); renderRows(local); }
        const ctx = document.body.dataset.context || "";
        const alts = [q, ...terms(q).flatMap(expand)].filter((v, i, all) => all.indexOf(v) === i).slice(0, 8);
        const cql =
          'type=page AND space="CRH" AND (' +
          alts.map((t) => 'title~"' + cqlLiteral(t) + '" OR text~"' + cqlLiteral(t) + '"').join(" OR ") +
          ")";
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
        const seen = new Set(local.map((r) => r.href));
        rows = [...local, ...remote.filter((r) => !seen.has(r.href))];
      }
      if (id !== serial || !dialog.open) return;
      const count = renderRows(rows);
      rendered = count ? q : "";
      message.textContent = count
        ? `${count} result${count === 1 ? "" : "s"}.` + (matchMedia("(pointer: fine)").matches ? " Use ↑ ↓ to move, Enter to open." : "")
        : "No matching pages. Try another word, browse templates and assets, or ask the team.";
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
  // Resource catalogue: text filter plus type chips.
  const filter = $("#resourceFilter"),
    chips = $$("[data-type-filter]");
  let type = "all";
  function filterResources() {
    const words = terms(filter?.value || "");
    let n = 0;
    $$("[data-resource]").forEach((card) => {
      const hay = card.textContent.toLowerCase();
      const match = (type === "all" || card.dataset.type === type) &&
        words.every((w) => expand(w).some((alt) => hay.includes(alt)));
      card.hidden = !match;
      if (match) n++;
    });
    const status = $("#filterStatus");
    if (status) status.textContent = n ? `Showing ${n} resource${n === 1 ? "" : "s"}.` : "";
    const empty = $("#catalogueEmpty");
    if (empty) empty.hidden = n > 0;
  }
  filter?.addEventListener("input", filterResources);
  chips.forEach((chip) => chip.addEventListener("click", () => {
    type = chip.dataset.typeFilter;
    chips.forEach((c) => c.setAttribute("aria-pressed", String(c === chip)));
    filterResources();
  }));
  $("#clearFilters")?.addEventListener("click", () => {
    filter.value = ""; type = "all";
    chips.forEach((c) => c.setAttribute("aria-pressed", String(c.dataset.typeFilter === "all")));
    filterResources(); filter.focus();
  });
  // Homepage search box hands over to the full search dialog as you type.
  const hero = $("#heroSearch");
  hero?.addEventListener("input", () => {
    if (!hero.value) return;
    openSearch({ currentTarget: hero });
    input.value = hero.value;
    hero.value = "";
    input.dispatchEvent(new Event("input"));
  });
  // Checklists: ticks stay in this browser only.
  $$("[data-checklist]").forEach((bar) => {
    const key = "crh-check:" + bar.dataset.checklist;
    const boxes = $$(".check-list input[type=checkbox]");
    const progress = bar.querySelector(".checklist-progress"), meter = bar.querySelector(".checklist-meter i");
    let saved = [];
    try { saved = JSON.parse(localStorage.getItem(key) || "[]"); } catch {}
    boxes.forEach((b, i) => { b.checked = saved.includes(i); });
    const update = () => {
      const done = boxes.filter((b) => b.checked).length;
      progress.textContent = `${done} of ${boxes.length} done`;
      if (meter) meter.style.width = (boxes.length ? (100 * done) / boxes.length : 0) + "%";
      bar.classList.toggle("is-complete", done === boxes.length);
      try { localStorage.setItem(key, JSON.stringify(boxes.map((b, i) => (b.checked ? i : -1)).filter((i) => i >= 0))); } catch {}
    };
    boxes.forEach((b) => b.addEventListener("change", update));
    bar.querySelector("[data-checklist-reset]")?.addEventListener("click", () => { boxes.forEach((b) => { b.checked = false; }); update(); });
    update();
  });
  $$("[data-print]").forEach((b) => b.addEventListener("click", () => print()));
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
  // Latest approved assets on the homepage.
  const latest = $("#latestAssets");
  if (latest) loadLatest(latest);
  async function loadLatest(box) {
    const DELIVERABLE = /\.(pptx?|potx|key|docx?|dotx|pdf|zip|ai|eps|svg|indd|idml|xlsx|mp4|mov)$/i;
    const fmtDate = (v) => { try { return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric" }).format(new Date(v)); } catch { return ""; } };
    const fmtSize = (n) => !n ? "" : n > 1048576 ? (n / 1048576).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1024)) + " KB";
    const status = (msg) => { const p = document.createElement("p"); p.className = "latest-status"; p.textContent = msg; box.replaceChildren(p); };
    function card(r, example) {
      const a = document.createElement("article"); a.className = "asset-card";
      const ext = (r.title.match(/\.([a-z0-9]+)$/i)?.[1] || "file").toUpperCase();
      const badge = document.createElement("span"); badge.className = "file-badge"; badge.dataset.ext = ext.toLowerCase(); badge.textContent = ext;
      const h = document.createElement("h3"), link = document.createElement("a");
      link.textContent = r.title.replace(/\.[a-z0-9]+$/i, "").replace(/[_-]+/g, " ");
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
      $("#latestLead").textContent = "Preview only: in Confluence this shows the newest files labelled “" + box.dataset.approvalLabel + "” in the Creative Hub space.";
      box.replaceChildren(...[
        { title: "Presentation-template.potx", when: Date.now() - 2 * 864e5, size: 4.2 * 1048576, pageTitle: "Standard SKAO template" },
        { title: "Letterhead-A4.dotx", when: Date.now() - 6 * 864e5, size: 310 * 1024, pageTitle: "Letterheads" },
        { title: "Poster-A0-portrait.pdf", when: Date.now() - 11 * 864e5, size: 2.8 * 1048576, pageTitle: "Poster templates" },
      ].map((r) => card(r, true)));
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
        $("#latestLead").textContent = "Recently uploaded files. Check the source page for approval and usage notes before reuse.";
      }
      if (!rows.length) { status("No new files yet. Browse templates and assets for everything in the Hub."); return; }
      box.replaceChildren(...rows.map((r) => card(r, false)));
    } catch (e) {
      status(e.message === "401" || e.message === "403" ? "Sign in to Confluence to see the latest files." : "The latest files could not be loaded. Browse templates and assets instead.");
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
    text.textContent="This page contains asset placeholders. The listed files and version details should not be treated as a released resource. Ask the creative helpdesk for an available source.";
    route.href="https://jira.skatelescope.org/servicedesk/customer/portal/364";
    route.textContent="Ask for the available resource ↗";
    notice.append(title,text,route); article.prepend(notice);
  }
  if (article && toc && !filter && !article.querySelector(".directory")) {
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
      (h) => !h.closest("[hidden], details, .choice-card, .section-next, .catalogue"),
    );
    if (headings.length > 2) {
      const h = document.createElement("strong");
      h.textContent = "On this page";
      toc.append(h);
      headings.forEach((heading, i) => {
        if (!heading.id) heading.id = "section-" + i;
        const a = document.createElement("a");
        a.href = "#" + heading.id;
        a.textContent = heading.textContent;
        toc.append(a);
      });
    } else toc.hidden = true;
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
  const mac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent || "");
  // Copy values such as colour codes.
  $$("[data-copy]").forEach((b) => b.addEventListener("click", async () => {
    const label = b.querySelector("span") || b, before = label.textContent, status = $("#copyAnnounce");
    try {
      await navigator.clipboard.writeText(b.dataset.copy);
      label.textContent = "Copied";
      if (status) status.textContent = b.dataset.copy + " copied to clipboard.";
    } catch {
      const code = b.querySelector("code") || b, range = document.createRange();
      range.selectNodeContents(code);
      getSelection().removeAllRanges();
      getSelection().addRange(range);
      label.textContent = mac ? "Press ⌘C" : "Press Ctrl C";
      if (status) status.textContent = "Clipboard unavailable. " + b.dataset.copy + " is selected; copy it with your keyboard.";
    }
    clearTimeout(b._t);
    b._t = setTimeout(() => { label.textContent = before; }, 2400);
  }));
  $$("[data-shortcut]").forEach((k) => { k.textContent = mac ? "⌘K" : "Ctrl K"; });
});
