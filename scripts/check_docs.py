"""Check the two tutorial sources without third-party Python dependencies."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urldefrag, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DOCS = ("Readme.adoc", "gitprimer.md")
# This settings page requires a signed-in user; do not send credentials from CI.
EXCLUDED_EXTERNAL = {"https://github.com/settings/emails"}
errors = []
urls = set()


def fail(message):
    errors.append(message)


def prose(text, suffix):
    """Skip fenced code and AsciiDoc literal/source blocks when finding links."""
    result = []
    inside = False
    delimiter = "----" if suffix == ".adoc" else "~~~unused"
    for line in text.splitlines():
        if suffix == ".md" and line.startswith("```"):
            inside = not inside
            continue
        if suffix == ".adoc" and line == delimiter:
            inside = not inside
            continue
        if not inside:
            result.append(line)
    if inside:
        fail("Unclosed source/code block")
    return "\n".join(result)


def anchors(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".adoc":
        return set(re.findall(r"^\[\[([^\],]+)\]\]$", text, re.M))
    # GitHub-style IDs for the simple headings used in this repository.
    found = set()
    for heading in re.findall(r"^#{1,6} (.+)$", text, re.M):
        heading = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        found.add(heading)
    return found


def check_target(source, target):
    if urlsplit(target).scheme in {"http", "https"}:
        urls.add(urldefrag(target)[0])
        return
    filename, fragment = urldefrag(target)
    candidate = (source.parent / unquote(filename)).resolve() if filename else source
    if not candidate.is_relative_to(ROOT):
        fail(f"{source.name}: target leaves repository: {target}")
    elif not candidate.is_file():
        fail(f"{source.name}: missing file: {target}")
    elif fragment and unquote(fragment) not in anchors(candidate):
        fail(f"{source.name}: missing section anchor: {target}")


for filename in DOCS:
    path = ROOT / filename
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n"):
        fail(f"{filename}: missing final newline")
    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            fail(f"{filename}:{number}: trailing whitespace")
        if "\t" in line:
            fail(f"{filename}:{number}: use spaces instead of tabs")
    clean = prose(text, path.suffix)
    if path.suffix == ".md":
        targets = re.findall(r"!?\[[^\]]*\]\(([^)\s]+)\)", clean)
        for line in clean.splitlines():
            if line.startswith("|") and not line.endswith("|"):
                fail(f"{filename}: table row must end with |")
    else:
        if text.splitlines().count("|===") % 2:
            fail(f"{filename}: unclosed AsciiDoc table")
        targets = re.findall(r"(?:link:)?((?:https?://|[A-Za-z0-9_./-]+)[^\s\[]*)\[[^\]]*\]", clean)
        for target, alt in re.findall(r"image::([^\[]+)\[([^\]]*)\]", clean):
            check_target(path, target)
            if not alt.strip():
                fail(f"{filename}: image has no alternative text: {target}")
        for target in re.findall(r"<<([^,>]+)(?:,[^>]+)?>>", clean):
            check_target(path, "#" + target)
    for target in targets:
        if not target.startswith("image::"):
            check_target(path, target)


def check_http(url):
    if url in EXCLUDED_EXTERNAL:
        return "SKIP authenticated settings page: " + url, False
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": "GitHub-primer-doc-check/1.0"})
            with urlopen(request, timeout=25) as response:
                response.read(1)
            return "OK " + url, False
        except HTTPError as exc:
            if exc.code in {401, 403, 429} or exc.code >= 500:
                if attempt < 2:
                    time.sleep(attempt + 1)
                    continue
                return f"WARNING HTTP {exc.code}; not classified as broken: {url}", False
            return f"ERROR HTTP {exc.code}: {url}", True
        except (URLError, TimeoutError, OSError) as exc:
            if attempt < 2:
                time.sleep(attempt + 1)
                continue
            return f"WARNING network failure; retry later: {url} ({exc})", False


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--external", action="store_true", help="also check public HTTP links")
args = parser.parse_args()
if args.external:
    with ThreadPoolExecutor(max_workers=4) as pool:
        for message, broken in pool.map(check_http, sorted(urls)):
            print(message)
            if broken:
                fail(message)
for error in errors:
    print("ERROR:", error, file=sys.stderr)
if errors:
    sys.exit(1)
print(f"Checked {len(DOCS)} documents, local links, section anchors, image paths/alt text and basic source formatting.")

