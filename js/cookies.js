(() => {
  const KEY = "trickless.consent.v1";
  const defaults = {
    necessary: true,
    preferences: false,
    analytics: false,
    marketing: false,
    embeds: false,
  };

  const read = () => {
    try {
      const raw = localStorage.getItem(KEY);
      return raw ? { ...defaults, ...JSON.parse(raw), necessary: true } : null;
    } catch {
      return null;
    }
  };

  const write = (value) => {
    localStorage.setItem(KEY, JSON.stringify({ ...defaults, ...value, necessary: true, updatedAt: new Date().toISOString() }));
    document.dispatchEvent(new CustomEvent("trickless:consent", { detail: get() }));
  };

  const get = () => read() || { ...defaults };

  const bar = document.querySelector("[data-consent-bar]");
  const panel = document.querySelector("[data-consent-panel]");
  const form = document.querySelector("[data-consent-form]");

  const setOpen = (node, open) => {
    if (!node) return;
    node.classList.toggle("open", open);
    node.hidden = !open;
  };

  const syncForm = () => {
    if (!form) return;
    const current = get();
    form.querySelectorAll("[data-consent]").forEach((input) => {
      input.checked = Boolean(current[input.dataset.consent]);
      if (input.dataset.consent === "necessary") input.checked = true;
    });
  };

  const apply = () => {
    const current = get();
    document.documentElement.dataset.consent = current.embeds ? "embeds" : "restricted";
    document.querySelectorAll("[data-needs-consent]").forEach((node) => {
      const need = node.dataset.needsConsent;
      const allowed = Boolean(current[need]);
      node.hidden = !allowed;
      const fallback = node.nextElementSibling;
      if (fallback && fallback.matches("[data-consent-fallback]")) fallback.hidden = allowed;
    });
  };

  const saved = read();
  if (!saved) setOpen(bar, true);
  syncForm();
  apply();

  document.querySelector("[data-consent-accept]")?.addEventListener("click", () => {
    write({ necessary: true, preferences: true, analytics: true, marketing: true, embeds: true });
    setOpen(bar, false);
    setOpen(panel, false);
    apply();
  });

  document.querySelector("[data-consent-reject]")?.addEventListener("click", () => {
    write({ ...defaults });
    setOpen(bar, false);
    setOpen(panel, false);
    apply();
  });

  document.querySelectorAll("[data-consent-open]").forEach((button) => {
    button.addEventListener("click", () => {
      syncForm();
      setOpen(panel, true);
      setOpen(bar, false);
      panel?.querySelector("h2, h3")?.focus?.();
    });
  });

  document.querySelector("[data-consent-close]")?.addEventListener("click", () => {
    setOpen(panel, false);
    if (!read()) setOpen(bar, true);
  });

  form?.addEventListener("submit", (event) => {
    event.preventDefault();
    const next = { ...defaults };
    form.querySelectorAll("[data-consent]").forEach((input) => {
      next[input.dataset.consent] = input.checked;
    });
    write(next);
    setOpen(panel, false);
    setOpen(bar, false);
    apply();
  });

  window.TrickLessConsent = { get, apply };
})();
