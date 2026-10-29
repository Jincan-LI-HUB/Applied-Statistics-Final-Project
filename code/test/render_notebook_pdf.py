from pathlib import Path

from playwright.sync_api import sync_playwright


def find_project_root() -> Path:
    start = Path(__file__).resolve()
    for p in [start.parent] + list(start.parents):
        if (p / "report.tex").exists() and (p / "code" / "formal").exists():
            return p
    raise FileNotFoundError("Could not locate final_project_v3 root.")


ROOT = find_project_root()
HTML = ROOT / "code" / "formal" / "project_notebook.executed.html"
PDF = ROOT / "project_notebook.pdf"

if not HTML.exists():
    raise FileNotFoundError(f"Executed notebook HTML not found: {HTML}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1240, "height": 1754})
    page.goto(HTML.as_uri(), wait_until="networkidle")
    page.pdf(
        path=str(PDF),
        format="A4",
        print_background=True,
        margin={"top": "12mm", "right": "10mm", "bottom": "12mm", "left": "10mm"},
    )
    browser.close()

print(PDF)
print(PDF.stat().st_size)
