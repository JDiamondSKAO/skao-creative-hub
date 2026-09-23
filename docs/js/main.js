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
  [...navItems, ...$$(".sidebar > a")].forEach(a => {
    if (new URL(a.href).pathname.replace(/\/$/, "") === currentPath) a.setAttribute("aria-current", "page");
  });
  if ($(".start-hero")) navItems[0]?.setAttribute("aria-current", "page");
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
    input.focus();
  }
  $$("[data-search]").forEach((b) => b.addEventListener("click", openSearch));
  $$("[data-hub-search]").forEach((form) => form.addEventListener("submit", (e) => {
    e.preventDefault(); openSearch({currentTarget: form.querySelector("input")});
    input.value = form.querySelector("input").value; search();
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
  async function search() {
    controller?.abort();
    const id = ++serial;
    results.replaceChildren();
    const q = input.value.trim();
    if (q.length < 2) {
      message.textContent = "Type at least two characters.";
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
        rows = index.filter((r) =>
          (r.title + " " + r.excerpt + " " + r.keywords)
            .toLowerCase()
            .includes(q.toLowerCase()),
        );
      } else {
        const ctx = document.body.dataset.context || "";
        const cql =
          'type=page AND space="CRH" AND (title~"' +
          cqlLiteral(q) +
          '" OR text~"' +
          cqlLiteral(q) +
          '")';
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
        const labels={"381891696":"Templates and assets","381891810":"Share material","381891794":"Prepare a presentation","381891661":"Request creative help"};
        rows = (data.results || []).map((r) => ({
          title: labels[String(r.id)] || r.title,
          excerpt: (r.ancestors || []).map((a) => a.title).join(" / "),
          href: routes.get(String(r.id))?.href || ctx + (r._links?.webui || "/pages/viewpage.action?pageId=" + encodeURIComponent(r.id)),
        }));
      }
      if (id !== serial || !dialog.open) return;
      let count = 0;
      rows.forEach((r) => {
        const href = safeLink(r.href);
        if (!href) return;
        const a = document.createElement("a"),
          label = document.createElement("strong"),
          desc = document.createElement("small");
        a.href = href;
        label.textContent = r.title;
        desc.textContent = r.excerpt;
        a.append(label, desc);
        results.append(a);
        count++;
      });
      message.textContent = count
        ? `${count} result${count === 1 ? "" : "s"}.`
        : "No matching resources. Try “presentation”, “logo” or “request”.";
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
  input?.addEventListener("input", () => {
    clearTimeout(timer);
    controller?.abort();
    serial++;
    timer = setTimeout(search, 220);
  });
  $("#searchForm")?.addEventListener("submit", (e) => {
    e.preventDefault();
    clearTimeout(timer);
    search();
  });
  const filter = $("#resourceFilter"),
    type = $("#resourceType");
  function filterResources() {
    let n = 0;
    $$("[data-resource]").forEach((card) => {
      const match =
        card.textContent.toLowerCase().includes(filter.value.toLowerCase()) &&
        (type.value === "all" || card.dataset.type === type.value);
      card.hidden = !match;
      if (match) n++;
    });
    $("#filterStatus").textContent = n
      ? `${n} categor${n === 1 ? "y" : "ies"} shown.`
      : "No matching resources. Clear the filter or try another format.";
  }
  filter?.addEventListener("input", filterResources);
  type?.addEventListener("change", filterResources);
  $("#clearFilters")?.addEventListener("click", () => {
    filter.value = ""; type.value = "all"; filterResources(); filter.focus();
  });
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
  if (article && toc && !filter) {
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
      (h) => !h.closest("[hidden], details, .choice-card"),
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
  }
});
