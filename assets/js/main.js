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

const initYear = () => $$("[data-year]").forEach((el) => (el.textContent = String(new Date().getFullYear())));

initNav();
initReveal();
$$("[data-showcase]").forEach(initShowcase);
initYear();
