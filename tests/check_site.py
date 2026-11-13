"""Content and hygiene checks for the static portfolio site.

Run from the repo root:  python tests/check_site.py
Prints OK and exits 0 when everything passes; otherwise prints one
"FAIL <file>: <reason>" line per problem and exits 1.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["index.html", "academic_projects.html", "personal_projects.html"]
BANNED_TEXT = ["+65", "lorem", "add your project", "project 2",
               "project 3", "your name",
               # claims the sources don't support
               "every week", "bicycle retailer", "every push",
               # Japfa rules: no legal claim, no location tied to the project
               "patent pending", "present · singapore", "japfa in singapore"]
# Private words (names of unannounced projects etc.) live in an untracked file so the
# public repo never contains them. One word or phrase per line, case-insensitive.
PRIVATE_WORDS_FILE = ROOT / "tests" / "banned_local.txt"
TEXT_EXT = {".html", ".css", ".js", ".md", ".py", ".txt", ".json", ".yml", ".yaml", ""}
BANNED_STYLES = ["backdrop-filter", "background-clip: text", ".glow", "orbit"]
HOME_IDS = ["experience", "projects", "skills", "education", "contact"]
HOME_TEXT = ["Associate AI Developer", "Apr 2026", "Project details coming soon", "In progress",
             'href="#education"']
MAX_IMAGE_BYTES = 300 * 1024
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
EXTERNAL = ("http://", "https://", "//", "mailto:", "tel:", "data:")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.refs: list[str] = []  # href / src values

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name == "id" and value:
                self.ids.add(value)
            if name in ("href", "src") and value is not None:
                self.refs.append(value)


def parse(page: str) -> PageParser:
    p = PageParser()
    p.feed((ROOT / page).read_text(encoding="utf-8"))
    return p


def check_pages_exist() -> list[str]:
    return [f"FAIL {p}: page missing" for p in PAGES if not (ROOT / p).exists()]


def check_banned_text(page: str) -> list[str]:
    text = (ROOT / page).read_text(encoding="utf-8").lower()
    fails = [f"FAIL {page}: contains banned text {b!r}" for b in BANNED_TEXT if b in text]
    fails += [f"FAIL {page}: contains private text (word #{i + 1})"
              for i, w in enumerate(private_words()) if w in text]
    return fails


def check_dead_links(page: str) -> list[str]:
    refs = parse(page).refs
    return [f"FAIL {page}: dead link href={r!r}" for r in refs if r.strip() in ("", "#")]


def check_local_links(page: str) -> list[str]:
    fails = []
    own = parse(page)
    for ref in own.refs:
        r = ref.strip()
        if not r or r == "#" or r.startswith(EXTERNAL):
            continue
        path, _, frag = r.partition("#")
        if path:
            target = ROOT / path
            if not target.exists():
                fails.append(f"FAIL {page}: broken local link {r!r}")
                continue
            ids = parse(path).ids if frag and path.endswith(".html") else set()
        else:
            ids = own.ids
        if frag and frag not in ids:
            fails.append(f"FAIL {page}: missing anchor {r!r}")
    return fails


def check_no_hidden_content() -> list[str]:
    fails = []
    pattern = re.compile(r"opacity\s*[:=]\s*['\"]?0(?![.\d])")
    for name in ("script.js", "styles.css"):
        f = ROOT / name
        if f.exists() and pattern.search(f.read_text(encoding="utf-8")):
            fails.append(f"FAIL {name}: sets content to opacity 0")
    return fails


def check_banned_styles() -> list[str]:
    f = ROOT / "styles.css"
    if not f.exists():
        return ["FAIL styles.css: missing"]
    css = f.read_text(encoding="utf-8")
    return [f"FAIL styles.css: uses banned style {b!r}" for b in BANNED_STYLES if b in css]


def check_image_sizes() -> list[str]:
    files: set[Path] = set()
    img_dir = ROOT / "images"
    if img_dir.exists():
        files |= {p for p in img_dir.rglob("*") if p.suffix.lower() in IMAGE_EXT}
    for page in PAGES:
        if not (ROOT / page).exists():
            continue
        for r in parse(page).refs:
            path = r.split("#")[0]
            if path and not path.startswith(EXTERNAL) and Path(path).suffix.lower() in IMAGE_EXT:
                if (ROOT / path).exists():
                    files.add(ROOT / path)
    return [f"FAIL {p.relative_to(ROOT).as_posix()}: image is {p.stat().st_size // 1024} KB (max 300 KB)"
            for p in sorted(files) if p.stat().st_size > MAX_IMAGE_BYTES]


def check_home_sections() -> list[str]:
    page = "index.html"
    if not (ROOT / page).exists():
        return []
    ids = parse(page).ids
    text = (ROOT / page).read_text(encoding="utf-8")
    fails = [f"FAIL {page}: missing section id {i!r}" for i in HOME_IDS if i not in ids]
    fails += [f"FAIL {page}: missing text {t!r}" for t in HOME_TEXT if t not in text]
    return fails


def private_words() -> list[str]:
    if not PRIVATE_WORDS_FILE.exists():
        return []
    lines = PRIVATE_WORDS_FILE.read_text(encoding="utf-8").splitlines()
    return [w.strip().lower() for w in lines if w.strip() and not w.startswith("#")]


def check_private_words_file() -> list[str]:
    if not private_words():
        return [f"FAIL {PRIVATE_WORDS_FILE.relative_to(ROOT).as_posix()}: missing or empty (untracked list of private words)"]
    return []


def check_repo_text() -> list[str]:
    """Every file that would be pushed must be free of private words and secrets."""
    import subprocess
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    words = private_words()
    fails = []
    for name in out.splitlines():
        f = ROOT / name
        if not f.is_file() or f.suffix.lower() not in TEXT_EXT or f == PRIVATE_WORDS_FILE:
            continue
        text = f.read_text(encoding="utf-8", errors="ignore").lower()
        fails += [f"FAIL {name}: contains private text (word #{i + 1})" for i, w in enumerate(words) if w in text]
    return fails


class MetaParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and a.get("property"):
            self.meta[a["property"]] = a.get("content") or ""


def check_og_tags() -> list[str]:
    page = "index.html"
    if not (ROOT / page).exists():
        return []
    m = MetaParser()
    m.feed((ROOT / page).read_text(encoding="utf-8"))
    fails = []
    if not m.meta.get("og:image", "").startswith("https://"):
        fails.append(f"FAIL {page}: og:image must be an absolute https URL for LinkedIn previews")
    if not m.meta.get("og:url", "").startswith("https://"):
        fails.append(f"FAIL {page}: missing absolute og:url")
    return fails


def check_tag_label_hidden() -> list[str]:
    """The headline's annotation label must not be read aloud as part of the h1."""
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    block = re.search(r"\.tag::after\s*\{([^}]*)\}", css)
    if block and not re.search(r'content:\s*attr\(data-label\)\s*/\s*""', block.group(1)):
        return ['FAIL styles.css: .tag::after label needs empty alt text (content: attr(data-label) / "")']
    return []


def check_always_light() -> list[str]:
    css = (ROOT / "styles.css").read_text(encoding="utf-8")
    if "prefers-color-scheme: dark" in css or "color-scheme: light" not in css:
        return ["FAIL styles.css: site must always render the light theme"]
    return []


def check_favicon(page: str) -> list[str]:
    html = (ROOT / page).read_text(encoding="utf-8")
    if not re.search(r'<link rel="icon"[^>]*href="[^"]+"', html):
        return [f"FAIL {page}: missing favicon link"]
    return []


def run() -> list[str]:
    fails = check_pages_exist()
    for page in PAGES:
        if (ROOT / page).exists():
            fails += check_banned_text(page) + check_dead_links(page) + check_local_links(page)
            fails += check_favicon(page)
    fails += check_no_hidden_content() + check_banned_styles() + check_image_sizes()
    fails += check_home_sections() + check_og_tags() + check_tag_label_hidden()
    fails += check_private_words_file() + check_repo_text() + check_always_light()
    return fails


if __name__ == "__main__":
    failures = run()
    if failures:
        print("\n".join(failures))
        sys.exit(1)
    print("OK")
