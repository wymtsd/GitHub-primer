"""Validate repository Markdown and render HTML for inspection."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import os
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urldefrag, urlsplit
from urllib.request import Request, urlopen
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_EXTERNAL = {"https://github.com/settings/emails"}
IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "work", "__pycache__"}
PARSER = MarkdownIt("commonmark", {"html": True}).enable("table")


class RenderedLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors = set()
        self.links = []
        self.missing_alt = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.anchors.add(attrs["id"])
        if tag == "a":
            if attrs.get("name"):
                self.anchors.add(attrs["name"])
            if attrs.get("href"):
                self.links.append(attrs["href"])
        if tag == "img":
            if not attrs.get("alt", "").strip():
                self.missing_alt = True
            if attrs.get("src"):
                self.links.append(attrs["src"])


def table_cells(line):
    line = re.sub(r"(`+).*?\1", "", line.strip())
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith(r"\|"):
        line = line[:-1]
    return re.split(r"(?<!\\)\|", line)


def render_document(text):
    errors = []
    tokens = PARSER.parse(text)
    counts = {}
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            inline = tokens[index + 1]
            title = "".join(t.content for t in inline.children or [] if t.type in {"text", "code_inline"})
            slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
            number = counts.get(slug, 0)
            counts[slug] = number + 1
            token.attrSet("id", slug if number == 0 else f"{slug}-{number}")
    protected = set()
    lines = text.splitlines()
    for token in tokens:
        if token.type in {"fence", "code_block"} and token.map:
            protected.update(range(*token.map))
        if token.type == "fence" and token.map:
            last = lines[token.map[1] - 1].strip()
            if not re.fullmatch(re.escape(token.markup[0]) + "{" + str(len(token.markup)) + ",}", last):
                errors.append("Unclosed Markdown code block")
    expected = None
    for i, line in enumerate(lines):
        if line.rstrip() != line:
            errors.append(f"line {i + 1}: trailing whitespace")
        if "\t" in line:
            errors.append(f"line {i + 1}: use spaces instead of tabs")
        if i in protected or not line.lstrip().startswith("|"):
            expected = None
            continue
        if not line.rstrip().endswith("|"):
            errors.append(f"line {i + 1}: table row must end with |")
        width = len(table_cells(line))
        if expected is None:
            expected = width
        elif width != expected:
            errors.append(f"line {i + 1}: table has {width} columns; expected {expected}")
    if not text.endswith("\n"):
        errors.append("Missing final newline")
    html = PARSER.renderer.render(tokens, PARSER.options, {})
    parsed = RenderedLinks()
    parsed.feed(html)
    if parsed.missing_alt:
        errors.append("Image has no alternative text")
    return html, parsed, errors


def validate(root, render_dir=None):
    docs = sorted(p for p in root.rglob("*.md") if not any(part in IGNORED_DIRS for part in p.relative_to(root).parts))
    errors, urls, rendered = [], set(), {}
    if not docs:
        return ["No Markdown documents found"], set(), 0
    for path in docs:
        html, parsed, problems = render_document(path.read_text(encoding="utf-8"))
        rendered[path.resolve()] = parsed
        errors.extend(f"{path.relative_to(root)}: {message}" for message in problems)
        if render_dir:
            output = render_dir / path.relative_to(root).with_suffix(".html")
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text("<!doctype html><meta charset='utf-8'><title>" + escape(path.name) + "</title>\n" + html, encoding="utf-8")
    for path, parsed in rendered.items():
        for target in parsed.links:
            scheme = urlsplit(target).scheme
            if scheme in {"http", "https"}:
                urls.add(urldefrag(target)[0])
                continue
            if scheme in {"mailto", "tel"}:
                continue
            if scheme:
                errors.append(f"{path.name}: unsupported link scheme: {target}")
                continue
            filename, fragment = urldefrag(target)
            candidate = (path.parent / unquote(filename)).resolve() if filename else path
            if not candidate.is_relative_to(root.resolve()):
                errors.append(f"{path.name}: link leaves repository: {target}")
            elif not candidate.is_file():
                errors.append(f"{path.name}: missing file: {target}")
            elif fragment:
                if candidate not in rendered or unquote(fragment) not in rendered[candidate].anchors:
                    errors.append(f"{path.name}: missing section anchor: {target}")
    return errors, urls, len(docs)


def check_http(url):
    if url in EXCLUDED_EXTERNAL:
        return "excluded", "Authenticated settings page: " + url
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent": "GitHub-primer-doc-check/1.0"}), timeout=25) as response:
                response.read(1)
            return "verified", url
        except HTTPError as exc:
            temporary = exc.code in {401, 403, 429} or exc.code >= 500
            if temporary and attempt < 2:
                time.sleep(attempt + 1)
                continue
            return ("unverified" if temporary else "broken"), f"HTTP {exc.code}: {url}"
        except (URLError, TimeoutError, OSError) as exc:
            if attempt < 2:
                time.sleep(attempt + 1)
                continue
            return "unverified", f"Network failure: {url} ({exc})"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--external", action="store_true")
    parser.add_argument("--render-dir", type=Path)
    args = parser.parse_args()
    errors, urls, count = validate(ROOT, args.render_dir)
    results = []
    if args.external:
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(check_http, sorted(urls)))
        for state, message in results:
            print(f"{state.upper()}: {message}")
            if state == "broken":
                errors.append(message)
    summary = [f"## Documentation checks\n\nRendered and checked {count} Markdown documents.\n"]
    for state in ("verified", "unverified", "excluded", "broken"):
        messages = [message for result, message in results if result == state]
        summary.append(f"\n### {state.title()} external links: {len(messages)}\n")
        summary.extend(f"- {message}\n" for message in messages)
    if not args.external:
        summary.append("\nExternal links were not checked.\n")
    summary.append(f"\nDocument/link errors: {len(errors)}\n")
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as stream:
            stream.writelines(summary)
    for message in errors:
        print("ERROR:", message, file=sys.stderr)
    if errors:
        return 1
    unverified = sum(state == "unverified" for state, _ in results)
    print(f"PASS: {count} Markdown documents rendered and checked; {unverified} external links remain unverified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
