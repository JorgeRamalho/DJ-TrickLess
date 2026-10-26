(() => {
  const navToggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector("[data-nav]");
  if (navToggle && nav) {
    const setOpen = (open) => {
      nav.classList.toggle("open", open);
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    };
    navToggle.addEventListener("click", () => setOpen(!nav.classList.contains("open")));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && nav.classList.contains("open")) {
        setOpen(false);
        navToggle.focus();
      }
    });
  }

  document.querySelectorAll("[data-year]").forEach((node) => {
    node.textContent = String(new Date().getFullYear());
  });

  const filters = document.querySelector("[data-filters]");
  if (filters) {
    const cards = [...document.querySelectorAll("[data-kind]")];
    filters.addEventListener("click", (event) => {
      const button = event.target.closest("button");
      if (!button) return;
      filters.querySelectorAll("button").forEach((item) => item.setAttribute("aria-pressed", "false"));
      button.setAttribute("aria-pressed", "true");
      const kind = button.dataset.filter;
      cards.forEach((card) => {
        card.classList.toggle("hidden", kind !== "todos" && card.dataset.kind !== kind);
      });
    });
  }

  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const target = document.querySelector(button.dataset.copy);
      const text = target ? target.innerText.trim() : button.dataset.text || "";
      try {
        await navigator.clipboard.writeText(text);
        const original = button.textContent;
        button.textContent = "Copiado";
        setTimeout(() => {
          button.textContent = original;
        }, 1400);
      } catch {
        button.textContent = "Selecione e copie";
      }
    });
  });

  const form = document.querySelector("[data-booking]");
  if (form) {
    const status = form.querySelector("[data-form-status]");
    const DRAFT = "trickless.booking.draft";
    try {
      const allowed = window.TrickLessConsent?.get()?.preferences;
      const draft = allowed ? JSON.parse(localStorage.getItem(DRAFT) || "null") : null;
      if (!allowed) localStorage.removeItem(DRAFT);
      if (draft) {
        Object.entries(draft).forEach(([name, value]) => {
          const field = form.elements.namedItem(name);
          if (field && "value" in field) field.value = value;
        });
      }
    } catch {
      /* ignore broken draft */
    }

    form.addEventListener("input", () => {
      const allowed = window.TrickLessConsent?.get()?.preferences;
      if (!allowed) {
        localStorage.removeItem(DRAFT);
        return;
      }
      const data = Object.fromEntries(new FormData(form).entries());
      localStorage.setItem(DRAFT, JSON.stringify(data));
    });

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(form).entries());
      const required = ["nome", "email", "evento", "data", "cidade"];
      const missing = required.filter((key) => !String(data[key] || "").trim());
      if (missing.length) {
        if (status) {
          status.textContent = "Preencha nome, e-mail, evento, data e cidade.";
          status.style.color = "var(--danger)";
        }
        return;
      }
      const body = [
        `Booking TrickLess`,
        `Nome: ${data.nome}`,
        `E-mail: ${data.email}`,
        `WhatsApp: ${data.whatsapp || "-"}`,
        `Evento: ${data.evento}`,
        `Data: ${data.data}`,
        `Cidade: ${data.cidade}`,
        `Casa: ${data.casa || "-"}`,
        `Formato: ${data.formato || "-"}`,
        `Mensagem: ${data.mensagem || "-"}`,
      ].join("\n");
      const mailto = `mailto:tricklessdj@gmail.com?subject=${encodeURIComponent("Booking TrickLess — " + data.evento)}&body=${encodeURIComponent(body)}`;
      window.location.href = mailto;
      localStorage.removeItem(DRAFT);
      if (status) {
        status.textContent = "Abrimos seu e-mail com o briefing. Se nada abrir, escreva para tricklessdj@gmail.com.";
        status.style.color = "var(--ok)";
      }
    });
  }

  const canvas = document.querySelector("[data-hero-canvas]");
  if (canvas && canvas.getContext && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const context = canvas.getContext("2d");
    const particles = Array.from({ length: 42 }, () => ({
      x: Math.random(),
      y: Math.random(),
      r: Math.random() * 1.8 + 0.4,
      s: Math.random() * 0.25 + 0.05,
    }));
    const draw = () => {
      const ratio = Math.min(window.devicePixelRatio || 1, 2);
      const width = Math.floor(canvas.clientWidth * ratio);
      const height = Math.floor(canvas.clientHeight * ratio);
      if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
      }
      context.clearRect(0, 0, width, height);
      particles.forEach((dot) => {
        dot.y -= dot.s / 120;
        if (dot.y < 0) dot.y = 1;
        context.fillStyle = "rgba(230,195,74,0.28)";
        context.beginPath();
        context.arc(dot.x * width, dot.y * height, dot.r * ratio, 0, Math.PI * 2);
        context.fill();
      });
      requestAnimationFrame(draw);
    };
    draw();
  }

  document.querySelectorAll("[data-clock]").forEach((node) => {
    const tick = () => {
      const now = new Date();
      node.textContent = now.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
    };
    tick();
    setInterval(tick, 1000);
  });

  const lightbox = document.querySelector("[data-lightbox]");
  if (lightbox) {
    const image = lightbox.querySelector("img");
    const caption = lightbox.querySelector("[data-lightbox-caption]");
    const closeButton = lightbox.querySelector("[data-lightbox-close]");
    const close = () => {
      lightbox.classList.remove("open");
      document.body.style.removeProperty("overflow");
      if (closeButton) closeButton.blur();
    };
    const open = (href, alt, text) => {
      if (!image || !href) return;
      image.src = href;
      image.alt = alt || text || "";
      if (caption) caption.textContent = text || "";
      lightbox.classList.add("open");
      document.body.style.overflow = "hidden";
      if (closeButton) closeButton.focus();
    };
    document.querySelectorAll("[data-lightbox-src]").forEach((link) => {
      link.addEventListener("click", (event) => {
        event.preventDefault();
        const href = link.getAttribute("href") || link.dataset.lightboxSrc;
        const img = link.querySelector("img");
        open(href, img ? img.alt : "", link.dataset.caption || "");
      });
    });
    lightbox.addEventListener("click", (event) => {
      if (event.target === lightbox || event.target.closest("[data-lightbox-close]")) close();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && lightbox.classList.contains("open")) close();
    });
  }
})();
