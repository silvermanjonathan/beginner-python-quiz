"""Colour Python code for the quiz page, in the roles VS Code uses.

highlight(text) returns HTML for the inside of <pre><code>: the text escaped, with
each coloured token wrapped in <span class="tk-ROLE">. Operators, brackets, and
spaces are left bare, so they print in ink. Stripping the spans and unescaping
gives back the original text exactly. Works on Python 3.11 and on 3.12 and later,
which split f-strings into separate tokens.
"""

import html
import io
import re
import tokenize

CONTROL = {
    "if", "elif", "else", "for", "while", "return", "import", "from", "as", "break",
    "continue", "pass", "try", "except", "finally", "raise", "with", "yield", "del",
    "global", "nonlocal", "assert", "async", "await",
}
DECLARE = {"def", "class", "lambda", "and", "or", "not", "in", "is", "True", "False", "None", "self"}
TYPES = {"int", "float", "str", "bool", "list", "dict", "set", "tuple"}
PREFIX = re.compile(r"^([rRbBuUfF]*)('''|\"\"\"|'|\")")
# Python 3.12 and later tokenize f-strings into parts; 3.11 gives one STRING token.
FSTART = getattr(tokenize, "FSTRING_START", -1)
FMIDDLE = getattr(tokenize, "FSTRING_MIDDLE", -1)
FEND = getattr(tokenize, "FSTRING_END", -1)


def span(role, text):
    """Wrap escaped text in a role span; nothing for empty text."""
    if not text:
        return ""
    return f'<span class="tk-{role}">{html.escape(text, quote=False)}</span>'


def top_level_cut(inner):
    """Return where the format spec (: or !) starts, outside brackets and quotes."""
    depth, quote = 0, None
    for i, ch in enumerate(inner):
        if quote:
            quote = None if ch == quote else quote
        elif ch in "'\"":
            quote = ch
        elif ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0 and ch in ":!" and inner[i + 1:i + 2] != "=":
            return i
    return len(inner)


def fstring(tok, known):
    """Colour one f-string token (Python 3.11): f prefix and braces blue, text red, names inside coloured."""
    m = PREFIX.match(tok)
    prefix, quote = m.group(1), m.group(2)
    body = tok[len(prefix) + len(quote):len(tok) - len(quote)]
    out = span("kw", prefix) + '<span class="tk-str">' + html.escape(quote, quote=False)
    i, lit = 0, ""
    while i < len(body):
        two = body[i:i + 2]
        if two in ("{{", "}}"):
            lit += two
            i += 2
            continue
        if body[i] != "{":
            lit += body[i]
            i += 1
            continue
        depth, j = 1, i + 1
        while j < len(body) and depth:
            depth += {"{": 1, "}": -1}.get(body[j], 0)
            j += 1
        inner = body[i + 1:j - 1]
        cut = top_level_cut(inner)
        expr, spec = inner[:cut], inner[cut:]
        out += html.escape(lit, quote=False) + "</span>" + span("kw", "{")
        out += highlight(expr, known) + (span("kw", spec) if spec else "") + span("kw", "}")
        out += '<span class="tk-str">'
        lit, i = "", j
    return out + html.escape(lit + quote, quote=False) + "</span>"


def highlight(text, known=None):
    """Return text as escaped HTML with role spans.

    known carries the module and class names of the whole file into the
    expressions inside an f-string, which are coloured on their own.
    """
    toks = [t for t in tokenize.generate_tokens(io.StringIO(text).readline)
            if t.type != tokenize.ENDMARKER]
    lines = text.splitlines(keepends=True)
    offsets = [0]
    for ln in lines:
        offsets.append(offsets[-1] + len(ln))

    def pos(rc):
        return offsets[rc[0] - 1] + rc[1] if rc[0] - 1 < len(offsets) else len(text)

    sig = [t for t in toks if t.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT,
                                             tokenize.DEDENT, tokenize.COMMENT)]
    classes = {sig[k + 1].string for k, t in enumerate(sig[:-1]) if t.string == "class"}
    modules = set()
    if known:
        classes |= known[0]
        modules |= known[1]
    for k, t in enumerate(sig[:-1]):
        if t.string in ("import", "from") or (t.string == "as" and "import" in
                                               {s.string for s in sig[max(0, k - 6):k]}):
            if sig[k + 1].type == tokenize.NAME:
                modules.add(sig[k + 1].string)

    out, at, in_for = [], 0, False
    fields = []  # one entry per open f-string (Python 3.12 and later split them into tokens)
    order = {id(t): n for n, t in enumerate(sig)}
    for t in toks:
        start, end = pos(t.start), pos(t.end)
        if end < at:
            continue
        start = max(start, at)
        f = fields[-1] if fields else None
        gap = text[at:start]
        in_text = f is not None and not f["open"]
        out.append(span("str", gap) if gap and in_text else html.escape(gap, quote=False))
        s = text[start:end]
        in_spec = f is not None and bool(f["open"]) and f["open"][-1]
        if t.type == FSTART:
            fields.append({"open": [], "brackets": 0})
            quote = PREFIX.match(s).group(2)
            out.append(span("kw", s[:-len(quote)]) + span("str", quote))
        elif t.type == FMIDDLE:
            out.append(span("kw" if in_spec else "str", s))
        elif t.type == FEND:
            fields.pop()
            out.append(span("str", s))
        elif f and t.type == tokenize.OP and s == "{" and (not f["open"] or in_spec):
            f["open"].append(False)  # a replacement field opens; its expression comes next
            out.append(span("kw", s))
        elif f and t.type == tokenize.OP and s == "}" and f["open"] and not f["brackets"]:
            f["open"].pop()
            out.append(span("kw", s))
        elif f and f["open"] and not in_spec and t.type == tokenize.OP and s in (":", "!") \
                and not f["brackets"]:
            f["open"][-1] = True  # the format spec or conversion starts
            out.append(span("kw", s))
        elif in_spec and t.type == tokenize.NAME:
            out.append(span("kw", s))
        elif t.type == tokenize.NAME:
            n = order[id(t)]
            prev = sig[n - 1].string if n else ""
            nxt = sig[n + 1].string if n + 1 < len(sig) else ""
            if s == "for":
                in_for = True
            if s in CONTROL or (s == "in" and in_for):
                role = "ctl"
            elif s in DECLARE:
                role = "kw"
            elif prev == "def":
                role = "fn"
            elif prev == "class" or s in modules or s in classes or (s in TYPES and nxt == "("):
                role = "cls"
            elif nxt == "(":
                role = "fn"
            else:
                role = "var"
            out.append(span(role, s))
        elif t.type == tokenize.OP and s == ":" and in_for:
            in_for = False
            out.append(s)
        elif t.type == tokenize.STRING:
            prefix = PREFIX.match(s).group(1)
            out.append(fstring(s, (classes, modules)) if "f" in prefix.lower() else span("str", s))
        elif t.type == tokenize.NUMBER:
            out.append(span("num", s))
        elif t.type == tokenize.COMMENT:
            out.append(span("com", s))
        else:
            if f and f["open"] and t.type == tokenize.OP and s in "([{":
                f["brackets"] += 1
            elif f and f["open"] and t.type == tokenize.OP and s in ")]}":
                f["brackets"] -= 1
            out.append(html.escape(s, quote=False))
        if t.type == tokenize.NEWLINE:
            in_for = False
        at = max(at, end)
    out.append(html.escape(text[at:], quote=False))
    return "".join(out)


def plain(markup):
    """Strip the spans and unescape: the inverse of highlight."""
    return html.unescape(re.sub(r"</?span[^>]*>", "", markup))
