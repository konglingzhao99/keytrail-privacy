#!/usr/bin/env python3
"""Check language pages, links, the public contact address, and sensitive files."""

import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent
CODES = ["en", "zh-cn", "ja", "ru", "fr", "ko", "de", "hi", "th", "mn"]
LANG = {
    "en": "en",
    "zh-cn": "zh-Hans",
    "ja": "ja",
    "ru": "ru",
    "fr": "fr",
    "ko": "ko",
    "de": "de",
    "hi": "hi",
    "th": "th",
    "mn": "mn",
}
FACTS = ("history.json", "history-recovery.json", "custom-shortcuts.json", "200")
EMAIL = "konglingzhao989@gmail.com"
MAILTO = "mailto:" + EMAIL
ENGLISH_LEAK = "KeyTrail is a native macOS menu bar app."
BANNED = (
    "TODO",
    "FIXME",
    "{{",
    "}}",
    "example.com",
    "lorem ipsum",
    "your-email",
    "data-contact-required",
    "not listed on this page yet",
    "尚未列出公开联系地址",
)
BAD_EXT = {
    ".swift",
    ".m",
    ".entitlements",
    ".p12",
    ".mobileprovision",
    ".cer",
    ".provisionprofile",
    ".pem",
    ".p8",
    ".xcstrings",
    ".pbxproj",
}
SECRET_TEXT = ("BEGIN PRIVATE KEY", "BEGIN CERTIFICATE", "AKIA", "ghp_", "github_pat_")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = ""
        self.hrefs = []
        self.srcs = []
        self.current = []
        self.h2 = 0
        self.scripts = 0
        self.iframes = 0
        self.text = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "html":
            self.lang = data.get("lang", "")
        if tag == "a":
            href = data.get("href", "")
            self.hrefs.append(href)
            if data.get("aria-current") == "page":
                self.current.append(href)
        if tag in {"img", "link", "script"} and data.get("src"):
            self.srcs.append(data["src"])
        if tag == "link" and data.get("href"):
            self.hrefs.append(data["href"])
        if tag == "script":
            self.scripts += 1
        if tag == "iframe":
            self.iframes += 1
        if tag == "h2":
            self.h2 += 1
        if tag in {"script", "style"}:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in {"script", "style"}:
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


def resolve(page: Path, href: str) -> Optional[Path]:
    if href.startswith("#") or href.startswith("mailto:"):
        return None
    path = href.split("#", 1)[0]
    if path == "":
        return page.parent
    return (page.parent / path).resolve()


def main():
    errors = []
    pages = [ROOT / "index.html"] + [ROOT / code / "index.html" for code in CODES]
    for path in pages:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        print("\n".join(errors))
        return 1

    parsed = {}
    for path in pages:
        raw = path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            errors.append(f"{path.relative_to(ROOT)} is not UTF-8: {error}")
            continue
        if "\ufffd" in text:
            errors.append(f"{path.relative_to(ROOT)} contains a replacement character")
        lower = text.lower()
        for token in BANNED:
            if token.lower() in lower:
                errors.append(f"{path.relative_to(ROOT)} contains {token}")
        if "@" in text.replace(EMAIL, ""):
            errors.append(f"{path.relative_to(ROOT)} contains an unexpected email address")
        if "http://" in lower or "https://" in lower:
            errors.append(f"{path.relative_to(ROOT)} contains an external URL")
        if EMAIL not in text:
            errors.append(f"{path.relative_to(ROOT)} is missing the public contact address")
        parser = Page()
        parser.feed(text)
        parsed[path] = (text, parser)

    expected_h2 = None
    bodies = {}
    for path, (text, parser) in parsed.items():
        rel = path.relative_to(ROOT)
        code = "en" if path.parent == ROOT else path.parent.name
        if parser.lang != LANG[code]:
            errors.append(f"{rel} lang is {parser.lang!r}, expected {LANG[code]}")
        if parser.scripts or parser.iframes:
            errors.append(f"{rel} loads a script or iframe")
        if parser.h2 != 10:
            errors.append(f"{rel} has {parser.h2} headings, expected 10")
        expected_h2 = parser.h2
        if len(parser.current) != 1:
            errors.append(f"{rel} has {len(parser.current)} current languages")
        else:
            current = parser.current[0]
            wanted = "en/" if path.parent == ROOT else f"../{code}/"
            if current != wanted:
                errors.append(f"{rel} current link is {current}, expected {wanted}")
        nav = [href for href in parser.hrefs if href.endswith("/") and "assets/" not in href]
        language_links = [href for href in nav if any(href.rstrip("/").endswith(item) for item in CODES)]
        if len(language_links) < len(CODES):
            errors.append(f"{rel} language links: {language_links}")
        if MAILTO not in parser.hrefs:
            errors.append(f"{rel} is missing the mailto link")
        support_href = "support/" if path.parent == ROOT else "../support/"
        if support_href not in parser.hrefs:
            errors.append(f"{rel} is missing the support link")
        for href in parser.hrefs + parser.srcs:
            if href == MAILTO:
                continue
            if href.startswith(("http://", "https://", "mailto:")):
                errors.append(f"{rel} outbound link {href}")
                continue
            target = resolve(path, href)
            if target is None:
                continue
            if target.is_dir():
                if not (target / "index.html").is_file() and target != ROOT:
                    errors.append(f"{rel} link {href} does not resolve")
            elif not target.is_file():
                errors.append(f"{rel} link {href} does not resolve")
        plain = " ".join(parser.text)
        for fact in FACTS:
            if fact not in plain:
                errors.append(f"{rel} is missing {fact}")
        if len(plain) < 1500:
            errors.append(f"{rel} text is too short")
        if code != "en" and ENGLISH_LEAK in plain:
            errors.append(f"{rel} still contains the English introduction")
        bodies[code if path.parent != ROOT else "home"] = plain

    if bodies.get("home") != bodies.get("en"):
        errors.append("home and English pages do not have the same text")
    unique = {bodies[code] for code in CODES}
    if len(unique) != len(CODES):
        errors.append("two language pages have identical text")

    support = ROOT / "support" / "index.html"
    if not support.is_file():
        errors.append("missing support/index.html")
    else:
        support_text = support.read_text(encoding="utf-8")
        if EMAIL not in support_text or MAILTO not in support_text:
            errors.append("support page is missing the public contact address")
        if "<script" in support_text.lower() or "data-contact-required" in support_text:
            errors.append("support page is not a static contact page")
        for code in CODES:
            if f'href="../{code}/"' not in support_text:
                errors.append(f"support page is missing {code}")
        for href in ("../", "../assets/style.css", "../assets/icon.png"):
            target = (support.parent / href).resolve()
            if target.is_dir():
                ok = (target / "index.html").is_file()
            else:
                ok = target.is_file()
            if not ok:
                errors.append(f"support link {href} does not resolve")

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in BAD_EXT or path.name in {"AGENTS.md", "AGENTS_2.md"}:
            errors.append(f"unexpected project file {path.relative_to(ROOT)}")
        if ".cursor" in path.parts:
            errors.append(f"unexpected cursor file {path.relative_to(ROOT)}")
        if path.name == "verify.py":
            continue
        if path.suffix.lower() in {".html", ".css", ".md", ".py"}:
            sample = path.read_text(encoding="utf-8", errors="replace")
            for token in SECRET_TEXT:
                if token in sample:
                    errors.append(f"{path.relative_to(ROOT)} contains {token}")

    if errors:
        print("STRUCTURE FAILED")
        print("\n".join(errors))
        return 1
    print(f"publication ready: {len(pages)} privacy pages, headings {expected_h2}, support page present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
