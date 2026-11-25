"""Check the question bank and the built page. Run after make.py:

    python3 build/check.py

Exits with status 1 if any check fails. Warnings do not fail the build.
"""

import ast
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from highlight import highlight, plain  # noqa: E402
from questions import QUESTIONS, ROUNDS  # noqa: E402

FAILS, WARNS = [], []


def fail(msg):
    FAILS.append(msg)


def warn(msg):
    WARNS.append(msg)


# ------------------------------------------------------------------ code rules
# The quiz keeps to what a first Python course covers: flat if/elif/else, loops with a
# stopping condition you can point at, and nothing from later courses.
BANNED_NODES = {
    ast.Break: "break", ast.Continue: "continue", ast.Try: "try/except",
    ast.ClassDef: "class", ast.Lambda: "lambda", ast.Global: "global",
    ast.Nonlocal: "nonlocal", ast.ListComp: "list comprehension",
    ast.DictComp: "dict comprehension", ast.SetComp: "set comprehension",
    ast.GeneratorExp: "generator expression", ast.FloorDiv: "//",
    ast.Import: "import", ast.ImportFrom: "import", ast.With: "with",
}
# Programs that break a code rule on purpose, because the rule is the question.
RULE_BREAKERS = {"errors-6": "a call before its def is the point of the question"}
MAX_LINE = 41  # longest code line that fits a 390px phone, with line numbers, at 11px


def programs(q):
    """Yield (label, source, may_fail) for every program a question shows."""
    if q["kind"] == "order":
        yield q["id"], "\n".join(q["lines"]), False
    elif q["kind"] == "blank":
        for fill, why in q["fills"]:
            yield f"{q['id']} with {fill!r}", q["code"].replace("___", fill), why is not None
    else:
        yield q["id"], q["code"], q["kind"] in ("error", "line")


def nested_if(tree, src_lines):
    """True if an if sits inside another if's lines (elif does not count)."""
    def inner_ifs(stmts):
        for s in stmts:
            for node in ast.walk(s):
                if isinstance(node, ast.If):
                    return True
        return False

    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        if inner_ifs(node.body):
            return True
        orelse = node.orelse
        if len(orelse) == 1 and isinstance(orelse[0], ast.If) and \
                src_lines[orelse[0].lineno - 1].lstrip().startswith("elif"):
            continue  # an elif, checked on its own when the walk reaches it
        if inner_ifs(orelse):
            return True
    return False


def check_code():
    for q in QUESTIONS:
        for label, src, may_fail in programs(q):
            for n, line in enumerate(src.split("\n"), 1):
                if len(line) > MAX_LINE:
                    warn(f"{label}: line {n} is {len(line)} characters (phone limit {MAX_LINE})")
                if "\t" in line:
                    fail(f"{label}: line {n} has a tab; use spaces")
            try:
                tree = ast.parse(src)
            except SyntaxError:
                if not may_fail:
                    fail(f"{label}: does not parse, and it is not meant to fail")
                continue
            lines = src.split("\n")
            for node in ast.walk(tree):
                for kind, name in BANNED_NODES.items():
                    if isinstance(node, kind):
                        fail(f"{label}: uses {name}, which the quiz leaves out")
                if isinstance(node, ast.While) and isinstance(node.test, ast.Constant):
                    fail(f"{label}: while with a constant condition")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == "open":
                        fail(f"{label}: file input and output is left out")
                    if node.func.id == "print" and len(node.args) > 1:
                        fail(f"{label}: print with several arguments; use an f-string")
            if nested_if(tree, lines):
                fail(f"{label}: an if inside an if; keep gates flat and join with and")
            # every def goes at the top, before any line that does work
            seen_work = False
            for stmt in tree.body:
                if isinstance(stmt, ast.FunctionDef):
                    if seen_work and q["id"] not in RULE_BREAKERS:
                        fail(f"{label}: a def comes after a line that does work")
                else:
                    seen_work = True
            if plain(highlight(src)) != src:
                fail(f"{label}: colouring does not give the code back exactly")


# ------------------------------------------------------------------ prose rules
BANNED_PHRASES = [
    "simply", "obviously", "of course", "easy", "just ", "the whole", "trick",
    "hands back", "hand back", "magic", "!", "basically", "note that",
    "remember", "don't", "can't", "won't", "isn't", "doesn't",
]
DASHES = re.compile("[\\u2012-\\u2015]")


def prose_fields(q):
    yield "ask", q["ask"]
    for h in q["hints"]:
        yield "hint", h
    yield "explain", q["explain"]
    for text, why in q.get("wrong", []):
        yield "why", why
        if text.startswith("~"):
            yield "option", text[1:]
    for fill, why in q.get("fills", []):
        if why:
            yield "why", why
    for text, why in q.get("common", []):
        yield "why", why


def check_prose():
    for r in ROUNDS:
        for field in ("title", "about"):
            if DASHES.search(r[field]):
                fail(f"round {r['id']}: dash in {field}")
    for q in QUESTIONS:
        if not q["hints"]:
            fail(f"{q['id']}: no hint")
        for field, text in prose_fields(q):
            if not text.strip():
                fail(f"{q['id']}: empty {field}")
            if DASHES.search(text):
                fail(f"{q['id']}: dash in {field}: {text[:60]}")
            low = " " + re.sub(r"`[^`]*`", "", text).lower() + " "
            for phrase in BANNED_PHRASES:
                if phrase in low:
                    fail(f"{q['id']}: {field} uses {phrase.strip()!r}: {text[:70]}")
            if text.count("`") % 2:
                fail(f"{q['id']}: unmatched backtick in {field}")
            if text.count("**") % 2:
                fail(f"{q['id']}: unmatched ** in {field}")
        if q["kind"] in ("output", "last", "error", "line"):
            if len(q["wrong"]) != 3:
                fail(f"{q['id']}: needs exactly 3 wrong options, has {len(q['wrong'])}")
            texts = [t for t, _ in q["wrong"]]
            if len(set(texts)) != len(texts):
                fail(f"{q['id']}: two wrong options are the same")
        if q["kind"] == "blank" and len(q["fills"]) != 4:
            fail(f"{q['id']}: needs 4 fills")


# ------------------------------------------------------------------ the page
VOID = {"meta", "link", "br", "img", "input", "hr", "source", "wbr"}


class Balance(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"</{tag}> does not close <{self.stack[-1] if self.stack else '?'}>")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()


def balanced(fragment):
    p = Balance()
    p.feed(fragment)
    p.close()
    return p.errors + ([f"unclosed {p.stack}"] if p.stack else [])


# Words that must never appear in this public repo (the teacher's workplace and its
# address), stored as the first 16 hex digits of their SHA-256 so this file does not
# name them either. Every run of 1 to 3 words in every file is hashed and compared.
PRIVATE = {"ca40b2eea6cc8af9", "42b1e4abb0dd25d5", "f47b4879ae85b3b0", "5be8d6f4f1fcac3f",
           "d0325f51b6719cbd", "55976da4abfb758a", "89259723ef047a55"}


def names_private(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    for n in (1, 2, 3):
        for i in range(len(words) - n + 1):
            h = hashlib.sha256(" ".join(words[i:i + n]).encode()).hexdigest()[:16]
            if h in PRIVATE:
                return True
    return False
STORAGE = re.compile(r"localStorage|sessionStorage|indexedDB|document\.cookie")


def repo_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in files:
            if f.endswith((".py", ".js", ".html", ".md", ".txt", ".json", ".yml")):
                yield os.path.join(base, f)


def check_page():
    path = os.path.join(ROOT, "index.html")
    page = open(path, encoding="utf-8").read()

    for f in repo_files():
        text = open(f, encoding="utf-8").read()
        rel = os.path.relpath(f, ROOT)
        if DASHES.search(text):
            fail(f"{rel}: has an em or en dash")
        if names_private(text):
            fail(f"{rel}: names the workplace; keep it out of the public repo")
    if STORAGE.search(page):
        fail("index.html: uses browser storage")
    for url in re.findall(r'(?:src|href)="(https?://[^"]+)"', page):
        if not url.startswith(("https://fonts.googleapis.com", "https://fonts.gstatic.com",
                               "https://github.com/silvermanjonathan/")):
            fail(f"index.html: loads or links something outside the allowed list: {url}")
    if "<title>" not in page or "<h1>" not in page:
        fail("index.html: needs a title and an h1")

    shell = re.sub(r'<script type="application/json" id="quiz-data">.*?</script>', "", page, flags=re.S)
    for err in balanced(re.sub(r"<script>.*?</script>", "", shell, flags=re.S)):
        fail(f"index.html: {err}")

    m = re.search(r'<script type="application/json" id="quiz-data">(.*?)</script>', page, re.S)
    data = json.loads(m.group(1))
    qs = data["questions"]
    if len(qs) != len(QUESTIONS):
        fail(f"index.html has {len(qs)} questions, the bank has {len(QUESTIONS)}; run make.py")
    by_id = {q["id"]: q for q in QUESTIONS}
    for item in qs:
        src = by_id.get(item["id"])
        if not src:
            fail(f"index.html: {item['id']} is not in the bank; run make.py")
            continue
        fragments = [item["ask"], item["explain"]] + item["hints"]
        if "code" in item:
            fragments.append(item["code"])
        if "finished" in item:
            fragments.append(item["finished"])
        if item.get("opts"):
            oks = [o for o in item["opts"] if o["ok"]]
            if len(oks) != 1:
                fail(f"{item['id']}: {len(oks)} right options on the page")
            for o in item["opts"]:
                fragments += [o["h"], o["why"]]
                if not o["ok"] and not o["why"]:
                    fail(f"{item['id']}: wrong option {o['t']!r} has no reason")
        if item["kind"] == "order":
            own = ",".join(str(i) for i in range(len(item["lines"])))
            if own not in item["okKeys"]:
                fail(f"{item['id']}: the written order is not marked right")
            import math
            if len(item["perms"]) != math.factorial(len(item["lines"])):
                fail(f"{item['id']}: not every order was run")
            fragments += item["lines"]
        for frag in fragments:
            for err in balanced(frag):
                fail(f"{item['id']}: {err} in {frag[:60]}")
            if "<" in re.sub(r"</?(span|code|b)[^>]*>", "", frag):
                fail(f"{item['id']}: raw < in {frag[:60]}")
        if "code" in item and item["kind"] != "blank":
            if plain(item["code"]) != src["code"]:
                fail(f"{item['id']}: code on the page differs from the bank")

    # the script must at least parse
    node = shutil.which("node")
    if node:
        js = re.search(r"<script>\n(.*?)\n</script>", page, re.S).group(1)
        tmp = os.path.join(HERE, "_check_tmp.js")
        with open(tmp, "w") as fh:
            fh.write(js)
        r = subprocess.run([node, "--check", tmp], capture_output=True, text=True)
        os.remove(tmp)
        if r.returncode:
            fail("index.html: the script does not parse:\n" + r.stderr)
    else:
        warn("node not found; the script was not syntax checked")


def main():
    check_code()
    check_prose()
    check_page()
    for w in WARNS:
        print("warn:", w)
    for f in FAILS:
        print("FAIL:", f)
    if FAILS:
        print(f"{len(FAILS)} check(s) failed")
        sys.exit(1)
    print(f"all checks passed: {len(QUESTIONS)} questions, {len(WARNS)} warning(s)")


if __name__ == "__main__":
    main()
