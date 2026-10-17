const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
const desktop = matchMedia("(min-width: 960px)");
const scrollBehavior = () => (reducedMotion.matches ? "auto" : "smooth");

const initNav = () => {
  const nav = document.querySelector("[data-nav]");
  const sentinel = document.querySelector("[data-nav-sentinel]");
  if (!nav) return;
  if (!sentinel) return nav.classList.add("is-scrolled");
  new IntersectionObserver(([entry]) => nav.classList.toggle("is-scrolled", !entry.isIntersecting)).observe(sentinel);
};

const initReveal = () => {
  const items = $$("[data-reveal]");
  const observer = new IntersectionObserver(
    (entries) =>
      entries
        .filter((entry) => entry.isIntersecting)
        .forEach(({ target }) => {
          target.classList.add("is-visible");
          observer.unobserve(target);
        }),
    { rootMargin: "0px 0px -8% 0px", threshold: 0.1 }
  );
  items.forEach((item) => observer.observe(item));
};

const initShowcase = (root) => {
  const tabs = $$("[role=tab]", root);
  const screens = $$("[role=tabpanel]", root);
  const dots = $$("[data-dots] button", root);
  const stage = root.querySelector("[data-stage]");
  const pause = { hover: false, offscreen: true };
  let active = 0;

  const centerOn = (screen) =>
    stage.scrollTo({ left: screen.offsetLeft - (stage.clientWidth - screen.offsetWidth) / 2, behavior: scrollBehavior() });

  const setActive = (index, { scroll = false } = {}) => {
    active = (index + tabs.length) % tabs.length;
    tabs.forEach((tab, i) => {
      tab.classList.toggle("is-active", i === active);
      tab.setAttribute("aria-selected", String(i === active));
      tab.tabIndex = i === active ? 0 : -1;
    });
    screens.forEach((screen, i) => screen.classList.toggle("is-active", i === active));
    dots.forEach((dot, i) => dot.setAttribute("aria-current", String(i === active)));
    if (scroll && !desktop.matches) centerOn(screens[active]);
  };

  const syncPause = () => root.classList.toggle("is-paused", pause.hover || pause.offscreen);
  const syncAutoplay = () => root.classList.toggle("is-autoplay", desktop.matches && !reducedMotion.matches && !root.dataset.manual);
  const stopAutoplay = () => {
    root.dataset.manual = "true";
    syncAutoplay();
  };

  tabs.forEach((tab, i) => {
    tab.addEventListener("click", () => {
      stopAutoplay();
      setActive(i);
    });
    tab.querySelector(".tab-progress")?.addEventListener("animationend", () => setActive(active + 1));
  });

  root.querySelector("[role=tablist]").addEventListener("keydown", (event) => {
    const step = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[event.key];
    if (!step) return;
    event.preventDefault();
    stopAutoplay();
    setActive(active + step);
    tabs[active].focus();
  });

  dots.forEach((dot, i) => dot.addEventListener("click", () => setActive(i, { scroll: true })));
  screens.forEach((screen, i) =>
    screen.addEventListener("click", () => !desktop.matches && i !== active && setActive(i, { scroll: true }))
  );

  let frame = 0;
  stage.addEventListener(
    "scroll",
    () => {
      if (desktop.matches) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const center = stage.scrollLeft + stage.clientWidth / 2;
        const distances = screens.map((screen) => Math.abs(screen.offsetLeft + screen.offsetWidth / 2 - center));
        const nearest = distances.indexOf(Math.min(...distances));
        if (nearest !== active) setActive(nearest);
      });
    },
    { passive: true }
  );

  root.addEventListener("pointerenter", () => ((pause.hover = true), syncPause()));
  root.addEventListener("pointerleave", () => ((pause.hover = false), syncPause()));
  root.addEventListener("focusin", () => ((pause.hover = true), syncPause()));
  root.addEventListener("focusout", () => ((pause.hover = false), syncPause()));
  new IntersectionObserver(([entry]) => ((pause.offscreen = !entry.isIntersecting), syncPause()), { threshold: 0.35 }).observe(root);

  desktop.addEventListener("change", () => {
    syncAutoplay();
    if (!desktop.matches) requestAnimationFrame(() => centerOn(screens[active]));
  });
  reducedMotion.addEventListener("change", syncAutoplay);

  syncPause();
  syncAutoplay();
};

const initFilm = (root) => {
  const video = root.querySelector("video");
  const play = root.querySelector("[data-film-play]");
  if (!video || !play) return;

  // With JavaScript the poster carries our own play button; the native controls appear once it's pressed.
  video.controls = false;
  const start = () => {
    root.classList.add("is-playing");
    video.controls = true;
    video.play().catch(() => root.classList.remove("is-playing"));
  };
  play.addEventListener("click", start);
  video.addEventListener("click", () => video.paused && !video.controls && start());
  video.addEventListener("ended", () => {
    root.classList.remove("is-playing");
    video.controls = false;
    video.load();
  });
  // Don't keep playing out of sight.
  new IntersectionObserver(([entry]) => !entry.isIntersecting && !video.paused && video.pause(), { threshold: 0.15 }).observe(root);
};

// ---------- Languages ----------
// English lives at the root, Finnish under /fi/ and German under /de/. Every page lists its translations as
// <link rel="alternate" hreflang>. A language picked in the menu (or kept from the hint) is remembered in this
// browser only, so English-only pages (privacy, terms, 404) link back to the right home and blog.
const LANGS = ["en", "fi", "de"];
const HOME = { en: "/", fi: "/fi/", de: "/de/" };
const BLOG = { en: "/blog/", fi: "/fi/blogi/", de: "/de/blog/" };
const LANG_KEY = "fimbl-lang";
const pageLang = () => (LANGS.includes(document.documentElement.lang) ? document.documentElement.lang : "en");
const storedLang = () => {
  try {
    const value = localStorage.getItem(LANG_KEY);
    return LANGS.includes(value) ? value : null;
  } catch {
    return null;
  }
};
const storeLang = (lang) => {
  try {
    localStorage.setItem(LANG_KEY, lang);
  } catch {}
};
const alternates = () =>
  Object.fromEntries($$('link[rel="alternate"][hreflang]').map((link) => [link.hreflang, new URL(link.href).pathname]));

const initLangMenu = () => {
  $$("[data-lang]").forEach((menu) => {
    menu.addEventListener("click", (event) => {
      const link = event.target.closest("a[hreflang]");
      if (link) storeLang(link.hreflang);
    });
    document.addEventListener("click", (event) => menu.open && !menu.contains(event.target) && (menu.open = false));
    menu.addEventListener("keydown", (event) => {
      if (event.key !== "Escape" || !menu.open) return;
      menu.open = false;
      menu.querySelector("summary").focus();
    });
  });
};

// English-only pages: point home, section and blog links at the reader's language.
const initSharedPage = () => {
  if (!document.body.hasAttribute("data-shared")) return;
  const lang = storedLang();
  if (!lang || lang === "en") return;
  $$("a[href]").forEach((link) => {
    const href = link.getAttribute("href");
    if (href === "/" || href.startsWith("/#")) link.setAttribute("href", HOME[lang] + href.slice(1));
    else if (href === "/blog/") link.setAttribute("href", BLOG[lang]);
  });
};

const HINTS = {
  en: { text: "This page is also available in English.", go: "Read in English", close: "Close" },
  fi: { text: "Tämä sivu on saatavilla myös suomeksi.", go: "Lue suomeksi", close: "Sulje" },
  de: { text: "Diese Seite gibt es auch auf Deutsch.", go: "Auf Deutsch lesen", close: "Schließen" },
};

// A gentle suggestion instead of a redirect: search engines and people who chose a language are never moved.
const initLangHint = () => {
  if (storedLang() || document.body.hasAttribute("data-shared")) return;
  const current = pageLang();
  const wanted = (navigator.languages || [navigator.language]).map((tag) => String(tag).slice(0, 2).toLowerCase()).find((tag) => LANGS.includes(tag));
  const target = wanted && wanted !== current ? alternates()[wanted] : null;
  if (!target) return;
  const hint = document.createElement("div");
  hint.className = "lang-hint";
  hint.lang = wanted;
  hint.setAttribute("role", "region");
  hint.setAttribute("aria-label", HINTS[wanted].text);
  hint.innerHTML = `<p></p><a class="btn btn-primary" hreflang="${wanted}"></a><button type="button">×</button>`;
  hint.querySelector("p").textContent = HINTS[wanted].text;
  const go = hint.querySelector("a");
  go.href = target;
  go.textContent = HINTS[wanted].go;
  go.addEventListener("click", () => storeLang(wanted));
  const close = hint.querySelector("button");
  close.setAttribute("aria-label", HINTS[wanted].close);
  close.addEventListener("click", () => {
    storeLang(current);
    hint.remove();
  });
  document.body.append(hint);
};

// ---------- Articles ----------
const initToc = () => {
  const toc = document.querySelector("[data-toc]");
  if (!toc) return;
  const compact = matchMedia("(max-width: 1080px)");
  if (compact.matches) toc.open = false;
  const links = new Map($$("a[href^='#']", toc).map((link) => [decodeURIComponent(link.hash.slice(1)), link]));
  const headings = [...links.keys()].map((id) => document.getElementById(id)).filter(Boolean);
  const visible = new Set();
  const update = () => {
    const current = headings.find((heading) => visible.has(heading)) || null;
    if (!current) return;
    links.forEach((link, id) => link.classList.toggle("is-current", id === current.id));
  };
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => (entry.isIntersecting ? visible.add(entry.target) : visible.delete(entry.target)));
      update();
    },
    { rootMargin: "-80px 0px -60% 0px" }
  );
  headings.forEach((heading) => observer.observe(heading));
  toc.addEventListener("click", (event) => event.target.closest("a") && compact.matches && (toc.open = false));
};

// Wide tables scroll sideways; fade the right edge while columns are still hidden.
const initTables = () => {
  $$(".cmp").forEach((table) => {
    const scroller = table.querySelector(".cmp-scroll");
    const foot = table.querySelector(".cmp-legend");
    if (!scroller) return;
    const update = () => {
      table.style.setProperty("--cmp-foot", `${foot ? foot.offsetHeight : 0}px`);
      table.classList.toggle("can-scroll", scroller.scrollLeft + scroller.clientWidth < scroller.scrollWidth - 2);
    };
    scroller.addEventListener("scroll", update, { passive: true });
    new ResizeObserver(update).observe(scroller);
    update();
  });
};

const initYear = () => $$("[data-year]").forEach((el) => (el.textContent = String(new Date().getFullYear())));

initNav();
initReveal();
$$("[data-showcase]").forEach(initShowcase);
$$("[data-film]").forEach(initFilm);
initYear();
initLangMenu();
initSharedPage();
initLangHint();
initToc();
initTables();
