from playwright.sync_api import sync_playwright
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "instagram"
OUT.mkdir(parents=True, exist_ok=True)


def harvest(page, handle):
    url = f"https://www.instagram.com/{handle}/"
    page.goto(url, wait_until="domcontentloaded", timeout=45000)
    page.wait_for_timeout(4000)
    for label in ("Allow all cookies", "Permitir todos", "Allow", "Permitir", "Not now", "Agora não"):
        try:
            page.get_by_role("button", name=label).first.click(timeout=1200)
        except Exception:
            pass
    page.wait_for_timeout(2000)
    shot = OUT / f"profile-{handle}.png"
    page.screenshot(path=str(shot), full_page=False)
    imgs = page.eval_on_selector_all(
        "img",
        "els => els.map(e => ({alt: e.alt, src: e.currentSrc || e.src, w: e.naturalWidth, h: e.naturalHeight}))",
    )
    meta = page.eval_on_selector_all(
        "meta",
        "els => els.map(e => ({name: e.getAttribute('name') || e.getAttribute('property'), content: e.getAttribute('content')}))",
    )
    return {
        "url": url,
        "title": page.title(),
        "text": page.inner_text("body")[:4500],
        "imgs": imgs[:50],
        "meta": [item for item in meta if item.get("content")][:40],
        "shot": str(shot),
    }


def main():
    report = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 1800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="pt-BR",
        )
        page = context.new_page()
        for handle in ("tricklessmusic", "diplomatamusicoficial"):
            try:
                report[handle] = harvest(page, handle)
            except Exception as error:
                report[handle] = {"error": str(error)}
        browser.close()
    path = OUT / "harvest-2026-10-26.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {path}")
    for handle, data in report.items():
        print(handle, data.get("title") or data.get("error"))
        print("imgs", len(data.get("imgs") or []))
        print((data.get("text") or "")[:800])
        print("---")


if __name__ == "__main__":
    main()
