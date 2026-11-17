#!/usr/bin/env python3
"""HTML sanity and link checks for the static EmpowerU site.

Checks every .html file for a doctype, required tags, parseability,
local href/src targets that exist on disk, in-page fragment ids,
the primary navigation (including Blog), the blog index listing every
tutorial, and that outbound https links return a successful HTTP response.
mailto: and fragment-only links are handled separately. No network
secrets are required.
"""

from __future__ import annotations

import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urlparse

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TAGS = {"html", "head", "title", "body"}
SKIP_SCHEMES = {"mailto", "tel", "javascript", "data"}
USER_AGENT = "eu-security-site-ci/1.0 (HTML and link check)"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: set[str] = set()
        self.ids: set[str] = set()
        self.refs: list[tuple[str, str]] = []
        self.doctype = False
        self.nav_links: list[str] = []
        self.h1 = 0
        self.times: list[str] = []
        self._nav_depth = 0

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype"):
            self.doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        attr = {k: (v or "") for k, v in attrs}
        if tag == "nav" and "primary" in attr.get("class", "").split():
            self._nav_depth = 1
        elif tag == "nav" and self._nav_depth:
            self._nav_depth += 1
        if tag == "a" and self._nav_depth and attr.get("href"):
            self.nav_links.append(attr["href"])
        if tag == "h1":
            self.h1 += 1
        if tag == "time" and attr.get("datetime"):
            self.times.append(attr["datetime"])
        if attr.get("id"):
            self.ids.add(attr["id"])
        for key in ("href", "src"):
            if key in attr and attr[key]:
                self.refs.append((key, attr[key]))


    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self._nav_depth:
            self._nav_depth -= 1


# Primary navigation every page (except 404.html) must carry, as site-root paths.
NAV_TARGETS = {
    "index.html",
    "docs/quick-start.html",
    "docs/wazuh-pack.html",
    "docs/installer.html",
    "blog/index.html",
    "docs/security.html",
}
# Tutorials that must exist and be listed on the blog index.
BLOG_POSTS = {
    "getting-started-community-edition.html",
    "wazuh-docker-lab.html",
    "simulating-detections.html",
    "sigma-rules.html",
    "hardening-audit.html",
}


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def site_path(page: Path, href: str) -> str:
    target = (page.parent / urldefrag(href)[0]).resolve()
    try:
        return target.relative_to(ROOT).as_posix()
    except ValueError:
        return href


def check_nav_and_blog(pages: list[Path]) -> list[str]:
    """Primary nav (with Blog) on every page; blog index lists every tutorial."""
    errors: list[str] = []
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        if rel == "404.html":
            continue
        got = {site_path(page, h) for h in parse(page).nav_links}
        missing = NAV_TARGETS - got
        if missing:
            errors.append(f"{rel}: primary nav missing {', '.join(sorted(missing))}")

    blog = ROOT / "blog"
    index = blog / "index.html"
    if not index.exists():
        return errors + ["blog/index.html does not exist"]
    posts = {p.name for p in blog.glob("*.html") if p.name != "index.html"}
    for name in sorted(BLOG_POSTS - posts):
        errors.append(f"blog/{name}: expected tutorial is missing")
    listed = {site_path(index, h) for _, h in parse(index).refs}
    for name in sorted(posts):
        if f"blog/{name}" not in listed:
            errors.append(f"blog/index.html does not link to blog/{name}")
        post = parse(blog / name)
        if post.h1 != 1:
            errors.append(f"blog/{name}: expected exactly one <h1>, found {post.h1}")
        if not post.times:
            errors.append(f"blog/{name}: missing <time datetime=...>")
        if "blog/index.html" not in {site_path(blog / name, h) for _, h in post.refs}:
            errors.append(f"blog/{name}: no link back to the blog index")
    home_links = {site_path(ROOT / "index.html", h) for _, h in parse(ROOT / "index.html").refs}
    if "blog/index.html" not in home_links:
        errors.append("index.html: no link to blog/index.html")
    return errors


def discover_html() -> list[Path]:
    files = sorted(
        p
        for p in ROOT.rglob("*.html")
        if ".git" not in p.parts and "tests" not in p.parts
    )
    if not files:
        raise SystemExit("no HTML files found")
    return files


def resolve_local(page: Path, url: str) -> Path:
    # Paths are relative to the page, as a static file server would treat them.
    target = (page.parent / url).resolve()
    return target


def check_external(url: str) -> None:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status >= 400:
                raise SystemExit(f"external link {url} returned HTTP {resp.status}")
            return
    except urllib.error.HTTPError as exc:
        if exc.code in {405, 403, 400}:
            # Some hosts reject HEAD; retry with GET.
            pass
        else:
            raise SystemExit(f"external link {url} returned HTTP {exc.code}") from exc
    except OSError:
        # Fall through to GET on HEAD transport failures too (URLError,
        # timeouts, resets). Anything else is a bug and should surface.
        pass
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status >= 400:
                raise SystemExit(f"external link {url} returned HTTP {resp.status}")
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"external link {url} returned HTTP {exc.code}") from exc
    except OSError as exc:
        # Report as a link error (with the URL) instead of crashing the whole
        # run with a bare traceback that drops every other finding.
        raise SystemExit(f"external link {url} unreachable: {type(exc).__name__}") from exc


def main() -> int:
    errors: list[str] = []
    pages = discover_html()
    checked_external: set[str] = set()

    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        text = page.read_text(encoding="utf-8")
        if not text.strip():
            errors.append(f"{rel}: file is empty")
            continue
        lower = text.lstrip().lower()
        if not lower.startswith("<!doctype html"):
            errors.append(f"{rel}: missing <!DOCTYPE html>")
        parser = PageParser()
        try:
            parser.feed(text)
            parser.close()
        except Exception as exc:  # noqa: BLE001 — report parse failures as test errors
            errors.append(f"{rel}: failed to parse HTML: {exc}")
            continue
        missing = REQUIRED_TAGS - parser.tags
        if missing:
            errors.append(f"{rel}: missing required tags: {', '.join(sorted(missing))}")

        for attr, raw in parser.refs:
            parsed = urlparse(raw)
            if parsed.scheme in SKIP_SCHEMES:
                continue
            if parsed.scheme in {"http", "https"}:
                if raw not in checked_external:
                    try:
                        check_external(raw)
                    except SystemExit as exc:
                        errors.append(f"{rel}: {exc}")
                    checked_external.add(raw)
                continue
            if parsed.scheme and parsed.scheme not in {"", "file"}:
                errors.append(f"{rel}: unsupported {attr} scheme in {raw!r}")
                continue

            path_part, fragment = urldefrag(raw)
            if path_part:
                target = resolve_local(page, path_part)
                try:
                    target.relative_to(ROOT)
                except ValueError:
                    errors.append(f"{rel}: {attr} {raw!r} escapes the site root")
                    continue
                if not target.exists():
                    errors.append(f"{rel}: {attr} {raw!r} does not exist")
                    continue
                if fragment and target.suffix.lower() == ".html":
                    dest_text = target.read_text(encoding="utf-8")
                    dest = PageParser()
                    dest.feed(dest_text)
                    dest.close()
                    if fragment not in dest.ids:
                        errors.append(
                            f"{rel}: fragment #{fragment} from {attr} {raw!r} not found in {target.relative_to(ROOT)}"
                        )
            elif fragment:
                if fragment not in parser.ids:
                    errors.append(f"{rel}: in-page fragment #{fragment} not found")

    errors.extend(check_nav_and_blog(pages))

    if errors:
        print("HTML / link check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    print(f"OK: {len(pages)} HTML pages passed sanity and link checks")
    print(f"OK: primary nav (with Blog) on every page; {len(BLOG_POSTS)} tutorials listed on blog/index.html")
    if checked_external:
        print(f"OK: {len(checked_external)} unique external https links responded successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
