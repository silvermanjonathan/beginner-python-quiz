"""Build index.html from build/questions.py.

Every program is run with real Python. The right answer to each question comes from
what the run printed. The build stops if:
  - a wrong option is what Python really prints,
  - a blank has no fill, or more than one fill, that prints the target,
  - an order question's own order does not print the target, or the number of
    orders that do is not the number the question says,
  - a program that should run stops with an error, or one that should stop does not.

Run from the repo root or from build/:
    python3 build/make.py
Then run the checks:
    python3 build/check.py
"""

import html
import itertools
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from highlight import highlight  # noqa: E402
from questions import FILE_NAME, QUESTIONS, ROUNDS  # noqa: E402

REPO_URL = "https://github.com/silvermanjonathan/beginner-python-quiz"
PYTHON = "Python " + platform.python_version()
LIMIT = 4000  # characters of output kept from a run

# Installed as sitecustomize so the typed answer appears after the input() prompt,
# the way a real terminal shows it. Piped input does not echo on its own.
ECHO_INPUT = '''
import builtins
import sys as _sys
def _echo_input(prompt=""):
    line = _sys.stdin.readline()
    if line == "":
        raise EOFError("EOF when reading a line")
    answer = line.rstrip("\\n")
    print(str(prompt) + answer)
    return answer
builtins.input = _echo_input
'''


class Fail(Exception):
    pass


# ------------------------------------------------------------------ running programs

def run(code, stdin=None, timeout=4):
    """Run one program as FILE_NAME. Returns a dict: out, err, rc, timed_out, term."""
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, FILE_NAME), "w") as fh:
            fh.write(code if code.endswith("\n") else code + "\n")
        with open(os.path.join(d, "sitecustomize.py"), "w") as fh:
            fh.write(ECHO_INPUT)
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        env.update(PYTHONPATH=d, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        out_path, err_path = os.path.join(d, "o.txt"), os.path.join(d, "e.txt")
        with open(out_path, "w") as o, open(err_path, "w") as e:
            proc = subprocess.Popen([sys.executable, FILE_NAME], cwd=d, env=env,
                                    stdin=subprocess.PIPE, stdout=o, stderr=e, text=True)
            try:
                proc.communicate(input=(stdin + "\n") if stdin is not None else "",
                                 timeout=timeout)
                timed_out = False
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                timed_out = True
        with open(out_path, errors="replace") as fh:
            out = fh.read(LIMIT)
        with open(err_path, errors="replace") as fh:
            err = fh.read(LIMIT)
        err = err.replace(os.path.realpath(d) + os.sep, "").replace(d + os.sep, "")
    out = out.rstrip("\n")
    err = "\n".join(ln.rstrip() for ln in err.rstrip().splitlines())
    if timed_out:
        lines = out.splitlines()[:6]
        term = "\n".join(lines + ["...", "(it never stops: the loop repeats forever)"])
    else:
        term = "\n".join(part for part in (out, err) if part)
    return {"out": out, "err": err, "rc": proc.returncode, "timed_out": timed_out,
            "term": term}


def error_name(r):
    last = r["err"].splitlines()[-1] if r["err"] else ""
    m = re.match(r"^([A-Za-z]+Error)\b", last)
    return m.group(1) if m else None


def error_line(r):
    found = re.findall(r'File "[^"]*' + re.escape(FILE_NAME) + r'", line (\d+)', r["err"])
    return int(found[-1]) if found else None


def must_run_clean(q, r):
    if r["rc"] != 0 or r["timed_out"] or r["err"]:
        raise Fail(f"{q['id']}: program should run without an error but printed:\n{r['term']}")


def must_error(q, r):
    if r["rc"] == 0 or not error_name(r):
        raise Fail(f"{q['id']}: program should stop with an error but printed:\n{r['term']}")


# ------------------------------------------------------------------ text

def fmt(text):
    """Escape, then `code` -> <code>, **term** -> <b>."""
    t = html.escape(text, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t


def esc(text):
    return html.escape(text, quote=False)


def mark_blank(code_html):
    return code_html.replace('<span class="tk-var">___</span>',
                             '<span class="blank" aria-label="blank">___</span>')


def mark_line(code_html, line_no):
    lines = code_html.split("\n")
    lines[line_no] = f'<span class="filled">{lines[line_no]}</span>'
    return "\n".join(lines)


ERROR_NAME = re.compile(r"^[A-Z][A-Za-z]+Error$")


def option(text, ok, why, style=None, out=None):
    prose = text.startswith("~")
    plain = text[1:] if prose else text
    if style is None:
        style = "text" if prose else "out"
    if style == "err":
        style = "err" if ERROR_NAME.match(plain) else "text"
    if style == "code":
        h = mark_blank(highlight(plain))
    elif style in ("out", "err"):
        h = esc(plain)
    else:
        h = fmt(plain)
    return {"t": plain, "h": h, "s": style, "ok": ok, "why": fmt(why) if why else "",
            "out": out}


# ------------------------------------------------------------------ one question

def build(q):
    kind = q["kind"]
    stdin = q.get("stdin")
    shown = q["target"].split("\n")[0] if kind == "order" else q["code"].split("\n")[0]
    item = {"id": q["id"], "round": q["round"], "kind": kind, "ask": fmt(q["ask"]),
            "peek": ("prints " if kind == "order" else "") + shown,
            "hints": [fmt(h) for h in q["hints"]], "explain": fmt(q["explain"]),
            "stdin": stdin}
    key = {"id": q["id"], "kind": kind, "ask": q["ask"]}

    if kind in ("output", "last", "error", "line", "type"):
        code = q["code"]
        r = run(code, stdin)
        item["code"] = highlight(code)
        item["copy"] = code
        item["real"] = r["term"]
        key.update(code=code, real=r["term"])

    if kind in ("output", "last"):
        must_run_clean(q, r)
        answer = r["out"] if kind == "output" else r["out"].splitlines()[-1]
        opts = [option(answer, True, None)]
        for text, why in q["wrong"]:
            if text.lstrip("~") == answer:
                raise Fail(f"{q['id']}: wrong option {text!r} is what Python prints")
            opts.append(option(text, False, why))
        item["opts"] = opts
        key["answer"] = answer

    elif kind == "error":
        must_error(q, r)
        answer = error_name(r)
        opts = [option(answer, True, None, "err")]
        for text, why in q["wrong"]:
            if text == answer:
                raise Fail(f"{q['id']}: wrong option {text!r} is the real error")
            opts.append(option(text, False, why, "err"))
        item["opts"] = opts
        key["answer"] = answer

    elif kind == "line":
        must_error(q, r)
        answer = f"Line {error_line(r)}"
        opts = [option(answer, True, None, "text")]
        for text, why in q["wrong"]:
            if text == answer:
                raise Fail(f"{q['id']}: wrong option {text!r} is the real line")
            opts.append(option(text, False, why, "text"))
        opts.sort(key=lambda o: int(o["t"].split()[1]))
        item["opts"] = opts
        item["fixed"] = True  # keep the line numbers in order on the page
        key["answer"] = answer

    elif kind == "type":
        must_run_clean(q, r)
        answer = r["out"].splitlines()[-1] if q.get("take") == "last" else r["out"]
        if "\n" in answer:
            raise Fail(f"{q['id']}: a typed answer must be one line")
        item["answer"] = answer
        item["common"] = []
        for text, why in q["common"]:
            if text == answer:
                raise Fail(f"{q['id']}: common wrong answer {text!r} is the real answer")
            item["common"].append({"t": text, "why": fmt(why)})
        key["answer"] = answer

    elif kind == "blank":
        code = q["code"]
        if code.count("___") != 1:
            raise Fail(f"{q['id']}: a blank question needs exactly one ___")
        blank_line = code.split("\n").index(next(ln for ln in code.split("\n") if "___" in ln))
        target = q["target"]
        opts, winners = [], []
        for fill, why in q["fills"]:
            r = run(code.replace("___", fill), stdin)
            ok = r["rc"] == 0 and not r["err"] and not r["timed_out"] and r["out"] == target
            if ok:
                winners.append(fill)
            if ok != (why is None):
                raise Fail(f"{q['id']}: fill {fill!r} was expected to be "
                           f"{'right' if why is None else 'wrong'} but printed:\n{r['term']}")
            opts.append(option(fill, ok, why, "code", r["term"]))
            if ok:
                finished = code.replace("___", fill)
                item["real"] = r["term"]
                item["finished"] = mark_line(highlight(finished), blank_line)
                item["copy"] = finished
        if len(winners) != 1:
            raise Fail(f"{q['id']}: {len(winners)} fills print the target, need exactly 1")
        item["code"] = mark_blank(highlight(code))
        item["target"] = target
        item["opts"] = opts
        key.update(code=code, answer=winners[0], real=item["real"],
                   wrong={o["t"]: o["out"] for o in opts if not o["ok"]})

    elif kind == "order":
        lines = q["lines"]
        target = q["target"]
        n = len(lines)
        perms = list(itertools.permutations(range(n)))
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(
                lambda p: run("\n".join(lines[i] for i in p), stdin), perms))
        outs, out_index, perm_map, ok_keys = [], {}, {}, []
        for p, r in zip(perms, results):
            k = ",".join(map(str, p))
            if r["term"] not in out_index:
                out_index[r["term"]] = len(outs)
                outs.append(r["term"])
            perm_map[k] = out_index[r["term"]]
            if r["rc"] == 0 and not r["err"] and not r["timed_out"] and r["out"] == target:
                ok_keys.append(k)
        own = ",".join(map(str, range(n)))
        if own not in ok_keys:
            raise Fail(f"{q['id']}: the lines in their written order do not print the target")
        if len(ok_keys) != q["ways"]:
            raise Fail(f"{q['id']}: {len(ok_keys)} orders print the target, "
                       f"the question says {q['ways']}")
        program = "\n".join(lines)
        item["lines"] = highlight(program).split("\n")
        item["plain"] = lines
        item["target"] = target
        item["perms"] = perm_map
        item["outs"] = outs
        item["okKeys"] = ok_keys
        item["finished"] = highlight(program)
        item["copy"] = program
        item["real"] = outs[perm_map[own]]
        key.update(code=program, answer="(the order above)", real=item["real"],
                   ways=len(ok_keys))

    else:
        raise Fail(f"{q['id']}: unknown kind {kind}")

    return item, key


# ------------------------------------------------------------------ page

CSS = r"""
/* Lecture Light: built for a projector in a room with the lights on.
   Light ground, near-black text, few accents, no hairlines. */
:root{
  --paper:#F4F0E6; --card:#FFFDF7; --ink:#17181B; --ink-soft:#4A4D53; --rule:#D3CBB8;
  --teal:#0E4D52; --teal-deep:#0A3A3E; --teal-tint:#E3EDEE; --clay:#9C2B22; --clay-tint:#F7E4E1;
  --ochre:#8A5A00; --ochre-line:#D99B12; --ochre-tint:#FBF2DC;
  --green:#1D5B39; --green-tint:#E8F1E9; --green-ink:#122B1C; --code-bg:#EDE7D9;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0; background:var(--paper); color:var(--ink);
  font-family:'DM Sans',system-ui,sans-serif; font-size:18px; font-weight:500; line-height:1.65}
header.top{background:var(--teal); color:#FFFDF7; border-bottom:6px solid var(--ochre-line);
  padding:30px 22px 26px}
.wrap{max-width:900px; margin:0 auto}
.eyebrow{font-family:'JetBrains Mono',monospace; font-size:13px; letter-spacing:.14em;
  text-transform:uppercase; color:#F2D89B; margin:0 0 10px; font-weight:700}
h1{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:800;
  font-size:clamp(29px,4.8vw,44px); line-height:1.1; margin:0 0 10px}
h2{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:700; font-size:25px;
  line-height:1.25; margin:0 0 14px; color:var(--teal-deep)}
h3{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:700; font-size:20px;
  margin:18px 0 10px; color:var(--teal-deep)}
header.top h1{color:#FFFDF7}
.sub{color:#EAE3D2; margin:0; font-size:19px; font-weight:400}
main{padding:28px 22px 12px}
section{background:var(--card); border:2px solid var(--rule); border-radius:6px;
  padding:22px 24px; margin:0 0 20px}
section.intro{border-left:8px solid var(--green)}
section.pick{border-left:8px solid var(--teal)}
section.q{border-left:8px solid var(--ochre-line)}
section.res{border-left:8px solid var(--teal)}
.label,.chunk-no{font-family:'JetBrains Mono',monospace; font-size:13px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ochre); margin:0 0 8px; font-weight:700}
.label.green{color:var(--green)} .label.clay{color:var(--clay)} .label.teal{color:var(--teal)}
p{margin:0 0 14px}
ol,ul{margin:0 0 14px; padding-left:26px} li{margin:0 0 8px}
code,pre,.tile,.typed{font-variant-ligatures:none; font-feature-settings:"liga" 0,"calt" 0,"dlig" 0}
code{font-family:'JetBrains Mono',monospace; font-size:.9em; font-weight:700;
  background:var(--code-bg); color:#1E2A2B; padding:2px 6px; border-radius:3px}
pre{font-family:'JetBrains Mono',monospace; font-size:15.5px; line-height:1.6;
  background:var(--code-bg); color:var(--ink); border:2px solid var(--rule);
  border-left:6px solid #B9AF96; border-radius:4px; padding:14px 16px; overflow-x:auto;
  margin:0 0 16px; font-weight:500}
pre.out{background:var(--green-tint); border-color:#A9C6B2; border-left:6px solid var(--green);
  color:var(--green-ink)}
pre.target{background:#FFFDF7; border-color:var(--ochre-line); border-left:6px solid var(--ochre-line)}
.empty{font-family:'DM Sans',sans-serif; font-style:italic; color:var(--ink-soft)}
/* Code colours by role, from VS Code's Light+ theme, darkened where needed to clear 4.5:1. */
.tk-ctl{color:#9A00C2} .tk-kw{color:#0000FF} .tk-str{color:#A31515} .tk-num{color:#06704A}
.tk-com{color:#3B6E2A} .tk-fn{color:#795E26} .tk-cls{color:#1D6A80} .tk-var{color:#001080}
.blank{background:var(--ochre-tint); color:var(--ochre); border-bottom:3px solid var(--ochre-line);
  font-weight:700; padding:0 2px}
.filled{background:#FBF2DC; box-shadow:0 0 0 2px #FBF2DC}
a{color:var(--teal)}
kbd{font-family:'JetBrains Mono',monospace; font-size:.9em; font-weight:700; background:#fff;
  border:2px solid var(--rule); border-bottom-width:3px; border-radius:4px; padding:0 7px}
button{font-family:'DM Sans',sans-serif}
.btn{display:inline-block; font-size:17px; font-weight:700; background:var(--teal);
  color:#FFFDF7; border:2px solid var(--teal); border-radius:4px; padding:11px 20px;
  cursor:pointer; text-decoration:none; line-height:1.3}
.btn:hover{background:var(--teal-deep)}
.btn.quiet{background:var(--card); color:var(--teal)}
.btn.quiet:hover{background:#EFE9DA}
.btn.big{font-size:19px; padding:14px 26px}
.btn:disabled{opacity:.45; cursor:not-allowed}
.btn.hint{background:var(--card); color:var(--ochre); border-color:var(--ochre-line)}
.btn.hint:hover{background:var(--ochre-tint)}
.row{display:flex; flex-wrap:wrap; gap:12px; align-items:center; margin:0 0 14px}
:focus-visible{outline:3px solid var(--ochre-line); outline-offset:2px}

/* start screen */
.rounds{display:grid; gap:10px; grid-template-columns:minmax(0,1fr); margin:0 0 6px}
@media(min-width:760px){.rounds{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
.round{display:flex; gap:12px; align-items:flex-start; border:2px solid var(--rule);
  border-radius:5px; padding:12px 14px; background:#FFFDF7; cursor:pointer}
.round:has(input:checked){border-color:var(--teal); background:var(--teal-tint)}
.round input{width:22px; height:22px; margin:3px 0 0; accent-color:var(--teal); flex:none}
.round .n{font-family:'JetBrains Mono',monospace; font-weight:700; color:var(--teal);
  min-width:26px}
.round b{display:block; font-size:18px; line-height:1.3}
.round .about{display:block; font-size:15.5px; color:var(--ink-soft); line-height:1.45}
.round .count{display:block; font-family:'JetBrains Mono',monospace; font-size:13px;
  color:var(--ochre); font-weight:700; margin-top:4px}
.modes{display:grid; gap:10px; margin:0 0 14px}
.mode{display:flex; gap:12px; align-items:flex-start; border:2px solid var(--rule);
  border-radius:5px; padding:12px 14px; cursor:pointer; background:#FFFDF7}
.mode:has(input:checked){border-color:var(--teal); background:var(--teal-tint)}
.mode input{width:20px; height:20px; margin:4px 0 0; accent-color:var(--teal); flex:none}
.mode span{display:block; font-size:16px; color:var(--ink-soft)}
.check{display:flex; gap:10px; align-items:center; cursor:pointer}
.check input{width:20px; height:20px; accent-color:var(--teal)}
.note{font-size:16px; color:var(--ink-soft)}

/* question */
.qmeta{display:flex; flex-wrap:wrap; justify-content:space-between; align-items:center;
  gap:8px 16px; margin:0 0 10px}
.qmeta .where{font-family:'JetBrains Mono',monospace; font-size:13.5px; font-weight:700;
  color:var(--teal); letter-spacing:.06em; text-transform:uppercase}
.progress{height:14px; background:#E6DFCD; border:2px solid var(--rule); border-radius:999px;
  overflow:hidden; margin:0 0 20px}
.progress i{display:block; height:100%; background:var(--teal)}
.ask{font-size:24px; outline:none}
.codehead{display:flex; justify-content:space-between; align-items:center; gap:10px;
  margin:0 0 6px}
.codehead .fname{font-family:'JetBrains Mono',monospace; font-size:13px; font-weight:700;
  color:var(--ink-soft)}
.small{font-size:14.5px; font-weight:700; background:var(--card); color:var(--teal);
  border:2px solid var(--rule); border-radius:4px; padding:5px 11px; cursor:pointer}
.small:hover{background:#EFE9DA}
.stdin{background:var(--ochre-tint); border:2px dashed var(--ochre); border-radius:5px;
  padding:10px 14px; margin:0 0 16px}
.opts{display:grid; gap:12px; margin:0 0 18px}
.opt{display:flex; gap:14px; align-items:flex-start; width:100%; text-align:left;
  background:#FFFDF7; border:2px solid var(--rule); border-radius:6px; padding:12px 14px;
  font:inherit; color:var(--ink); cursor:pointer; min-width:0}
.opt:hover:not([disabled]){border-color:var(--teal)}
.opt[aria-checked="true"]{border-color:var(--teal); background:var(--teal-tint);
  box-shadow:inset 0 0 0 1px var(--teal)}
.opt[disabled]{cursor:default}
.opt .letter{flex:none; width:36px; height:36px; border-radius:50%; border:2px solid var(--teal);
  display:flex; align-items:center; justify-content:center;
  font-family:'JetBrains Mono',monospace; font-weight:700; color:var(--teal); background:#fff}
.opt[aria-checked="true"] .letter{background:var(--teal); color:#fff}
.opt .body{flex:1; min-width:0; padding-top:4px}
.opt .body pre{margin:0; padding:0; background:none; border:0; font-size:16px; line-height:1.5;
  white-space:pre; overflow-x:auto}
.opt .body .err{font-family:'JetBrains Mono',monospace; font-weight:700}
.opt .tag{flex:none; font-family:'JetBrains Mono',monospace; font-size:12.5px; font-weight:700;
  letter-spacing:.08em; text-transform:uppercase; padding-top:8px}
.opt.right{border-color:var(--green); background:var(--green-tint); box-shadow:none}
.opt.right .tag{color:var(--green)}
.opt.right .letter{border-color:var(--green); color:var(--green); background:#fff}
.opt.wrong{border-color:var(--clay); background:var(--clay-tint); box-shadow:none}
.opt.wrong .tag{color:var(--clay)}
.opt.wrong .letter{border-color:var(--clay); color:#fff; background:var(--clay)}
.opt.dim{opacity:.7}
.hints{margin:0 0 12px}
.hintbox{border-top:2px solid var(--ochre-line); padding-top:10px; margin:0 0 12px}
.sure p{font-weight:700; margin:0 0 8px}
.typed{font-family:'JetBrains Mono',monospace; font-size:18px; padding:10px 12px;
  border:2px solid var(--ink-soft); border-radius:4px; width:100%; max-width:460px;
  background:#fff; color:var(--ink); margin:0 0 16px}
.fb{margin-top:20px; padding-top:18px; border-top:2px solid var(--rule)}
.verdict{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:800; font-size:26px;
  padding:10px 16px; border-radius:5px; margin:0 0 16px; outline:none}
.verdict.good{background:var(--green-tint); color:var(--green); border-left:8px solid var(--green)}
.verdict.bad{background:var(--clay-tint); color:var(--clay); border-left:8px solid var(--clay)}
.verdict.plain{background:var(--teal-tint); color:var(--teal-deep); border-left:8px solid var(--teal)}
.why{border-left:4px solid var(--clay); padding-left:14px; margin:0 0 16px}
.why.good{border-left-color:var(--green)}
.why p:last-child,.why pre:last-child{margin-bottom:0}
.keys{font-family:'JetBrains Mono',monospace; font-size:13px; color:var(--ink-soft); margin:0 0 20px}
@media(max-width:700px){.keys{display:none}}

/* put the lines in order */
.parsons{display:grid; gap:16px; grid-template-columns:minmax(0,1fr); margin:0 0 16px}
@media(min-width:820px){.parsons{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}
.parsons > div{min-width:0}
.well{border:2px dashed var(--rule); border-radius:6px; padding:10px; min-height:70px; background:#FBF9F3}
.well.prog{border-color:var(--teal); background:#FFFDF7}
.well ol{list-style:none; margin:0; padding:0}
.well li{margin:0 0 8px; display:flex; gap:8px; align-items:stretch}
.well li:last-child{margin-bottom:0}
.ln{flex:none; width:28px; font-family:'JetBrains Mono',monospace; font-size:13px; color:var(--ink-soft);
  font-weight:700; padding-top:10px; text-align:right}
.tile{flex:1; min-width:0; display:block; text-align:left; font-family:'JetBrains Mono',monospace;
  font-size:15.5px; line-height:1.5; white-space:pre; overflow-x:auto; background:var(--code-bg);
  border:2px solid var(--rule); border-radius:4px; padding:8px 12px; cursor:pointer; color:var(--ink)}
.tile:hover:not([disabled]){border-color:var(--teal)}
.tile[disabled]{cursor:default}
.well .placeholder{color:var(--ink-soft); font-size:15.5px; margin:8px 6px}

/* results */
.score{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:800;
  font-size:clamp(34px,6vw,52px); line-height:1.1; color:var(--teal-deep); margin:0 0 8px}
.conf{display:grid; gap:12px; grid-template-columns:1fr; margin:6px 0 0}
@media(min-width:700px){.conf{grid-template-columns:1fr 1fr}}
.cbox{border:2px solid var(--rule); border-radius:5px; padding:14px 16px; background:#FFFDF7}
.cbox .num{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:800; font-size:32px;
  line-height:1}
.cbox b{display:block; margin:4px 0 4px}
.cbox span{display:block; font-size:15.5px; color:var(--ink-soft); line-height:1.45}
.cbox.sw{border-top:6px solid var(--clay)} .cbox.sw .num{color:var(--clay)}
.cbox.nw{border-top:6px solid var(--ochre-line)} .cbox.nw .num{color:var(--ochre)}
.cbox.nr{border-top:6px solid var(--teal)} .cbox.nr .num{color:var(--teal)}
.cbox.sr{border-top:6px solid var(--green)} .cbox.sr .num{color:var(--green)}
.bars{display:grid; gap:10px}
.bar{display:grid; grid-template-columns:minmax(0,1fr) auto; gap:4px 12px; align-items:center}
.bar .t{font-weight:700}
.bar .v{font-family:'JetBrains Mono',monospace; font-weight:700; color:var(--teal)}
.bar .track{grid-column:1 / -1; height:14px; background:#E6DFCD; border:2px solid var(--rule);
  border-radius:999px; overflow:hidden}
.bar .track i{display:block; height:100%; background:var(--green)}
details.rev{border:2px solid var(--rule); border-radius:5px; background:#FFFDF7; margin:0 0 10px}
details.rev summary{cursor:pointer; padding:12px 14px; font-weight:700}
details.rev[open] summary{border-bottom:2px solid var(--rule)}
details.rev .in{padding:14px}
.meta{font-family:'JetBrains Mono',monospace; font-size:12.5px; color:var(--ochre);
  letter-spacing:.06em; text-transform:uppercase; margin-right:8px}
.peek{display:block; font-family:'JetBrains Mono',monospace; font-size:14px; font-weight:500;
  color:var(--ink-soft); margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}

footer{background:#EAE4D5; border-top:4px solid var(--teal); padding:22px 22px 36px;
  font-size:15px; color:var(--ink-soft)}
footer p{max-width:900px; margin:0 auto 8px}

/* class mode: for a projector */
body.classmode{font-size:21px}
body.classmode .ask{font-size:31px}
body.classmode pre{font-size:20px}
body.classmode .opt .body pre{font-size:20px}
body.classmode .tile{font-size:19px}
body.classmode .opt .letter{width:44px; height:44px; font-size:20px}
body.classmode .wrap{max-width:1100px}

@media(max-width:600px){
  header.top{padding:24px 16px 22px}
  main{padding:20px 16px 8px}
  section{padding:18px 14px}
  footer{padding:20px 16px 30px}
  .ask{font-size:21px}
  pre{font-size:14px; padding:10px 10px; border-left-width:5px}
  .tile{font-size:14px; padding:8px 10px}
  .well{padding:8px}
  .ln{width:20px}
  .opt{padding:10px 10px; gap:10px}
  .opt .tag{display:none}
  .opt.right .body::after{content:"Right answer"; display:block; font-family:'JetBrains Mono',monospace;
    font-size:12px; font-weight:700; color:var(--green); letter-spacing:.08em; text-transform:uppercase; margin-top:4px}
  .opt.wrong .body::after{content:"Your answer"; display:block; font-family:'JetBrains Mono',monospace;
    font-size:12px; font-weight:700; color:var(--clay); letter-spacing:.08em; text-transform:uppercase; margin-top:4px}
  .btn{padding:11px 16px}
}
@media print{
  body{background:#fff}
  header.top{background:#fff; color:#111; border-bottom:3px solid #111}
  header.top h1,.sub,.eyebrow{color:#111}
  section{background:#fff; break-inside:avoid}
  .row,.keys,footer{display:none}
}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?'
         'family=Bricolage+Grotesque:opsz,wght@12..96,400..800&'
         'family=DM+Sans:wght@400;500;700&'
         'family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">')

JS_PATH = os.path.join(HERE, "quiz.js")


def page(data):
    total = len(data["questions"])
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    with open(JS_PATH) as fh:
        js = fh.read()
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Beginner Python Quiz</title>
<meta name="description" content="A {total}-question quiz for Python beginners. Read a short program, predict what it does, then see what Python really prints.">
{FONTS}
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="wrap">
<p class="eyebrow">Python for beginners · Quiz</p>
<h1>Beginner Python Quiz</h1>
<p class="sub">{total} questions in {len(data["rounds"])} rounds. Each one shows a short program and asks what it will do.</p>
</div></header>
<main class="wrap" id="app">
<noscript><section><p>This quiz needs JavaScript turned on in your browser.</p></section></noscript>
</main>
<footer>
<p>Every program on this page was run with {PYTHON} when the page was built, and every right answer comes from what it really printed. Newer versions of Python word a few error messages differently, but the error names are the same.</p>
<p>The questions are in <a href="{REPO_URL}/blob/main/build/questions.py">build/questions.py</a>. Source: <a href="{REPO_URL}">{REPO_URL.replace("https://", "")}</a></p>
</footer>
<script type="application/json" id="quiz-data">{blob}</script>
<script>
{js}
</script>
</body>
</html>
"""


def answer_key(keys):
    out = ["# Answer key", "",
           "Generated by `build/make.py`. Every answer below comes from running the program "
           f"with {PYTHON}. Do not edit by hand.", ""]
    by_round = {r["id"]: r for r in ROUNDS}
    current = None
    for k, q in zip(keys, QUESTIONS):
        if q["round"] != current:
            current = q["round"]
            n = [r["id"] for r in ROUNDS].index(current) + 1
            out += [f"## Round {n}: {by_round[current]['title']}", ""]
        out += [f"### {k['id']} ({k['kind']})", "", k["ask"], "", "```python", k["code"].rstrip(),
                "```", ""]
        if q.get("stdin"):
            out += [f"Typed when asked: `{q['stdin']}`", ""]
        if k["kind"] == "blank":
            out += [f"Answer: `{k['answer']}`", "", "What each wrong fill really prints:", ""]
            for fill, term in k["wrong"].items():
                out += [f"- `{fill}`:", "", "  ```", *["  " + ln for ln in term.splitlines()],
                        "  ```", ""]
        elif k["kind"] == "order":
            out += [f"Answer: the order above ({k['ways']} order(s) print the target).", ""]
        else:
            out += [f"Answer: `{k['answer']}`", ""]
        out += ["Real output:", "", "```", k["real"] or "(prints nothing)", "```", ""]
    return "\n".join(out)


def main():
    ids = [q["id"] for q in QUESTIONS]
    if len(ids) != len(set(ids)):
        raise Fail("question ids repeat")
    round_ids = [r["id"] for r in ROUNDS]
    items, keys = [], []
    for q in QUESTIONS:
        if q["round"] not in round_ids:
            raise Fail(f"{q['id']}: unknown round {q['round']}")
        item, key = build(q)
        items.append(item)
        keys.append(key)
        print(f"  ok  {q['id']:<14} {q['kind']}")
    rounds = [{"id": r["id"], "title": r["title"], "about": r["about"],
               "count": sum(1 for q in QUESTIONS if q["round"] == r["id"])} for r in ROUNDS]
    data = {"rounds": rounds, "questions": items, "file": FILE_NAME, "python": PYTHON}
    with open(os.path.join(ROOT, "index.html"), "w") as fh:
        fh.write(page(data))
    with open(os.path.join(HERE, "answer_key.md"), "w") as fh:
        fh.write(answer_key(keys))
    print(f"wrote index.html: {len(items)} questions in {len(rounds)} rounds ({PYTHON})")


if __name__ == "__main__":
    try:
        main()
    except Fail as exc:
        print("BUILD FAILED:", exc)
        sys.exit(1)
