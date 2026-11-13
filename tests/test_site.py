#!/usr/bin/env python3
"""HTML sanity and link checks for the static EmpowerU site.

Checks every .html file for a doctype, required tags, parseability,
local href/src targets that exist on disk, in-page fragment ids,
and that outbound https links return a successful HTTP response.
mailto: and fragment-only links are handled separately. No network
secrets are required.
"""

from __future__ import annotations

import sys
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

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

    def handle_decl(self, decl: str) -> None:
        if decl.lower().startswith("doctype"):
            self.doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.add(tag)
        attr = {k: (v or "") for k, v in attrs}
        if attr.get("id"):
            self.ids.add(attr["id"])
        for key in ("href", "src"):
            if key in attr and attr[key]:
                self.refs.append((key, attr[key]))


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
    except Exception:
        # Fall through to GET on HEAD transport failures too.
        pass
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            if resp.status >= 400:
                raise SystemExit(f"external link {url} returned HTTP {resp.status}")
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"external link {url} returned HTTP {exc.code}") from exc


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

    if errors:
        print("HTML / link check failed:")
        for item in errors:
            print(f"  - {item}")
        return 1

    print(f"OK: {len(pages)} HTML pages passed sanity and link checks")
    if checked_external:
        print(f"OK: {len(checked_external)} unique external https links responded successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
