"""Review for Advanced Python Fall 2026. Writes advanced_python_fall2026_review.html.

A short review in two parts. Each part is a 10 minute opener for the start of a
class session, so the review never takes a whole session. The questions are weighted
by the assessment result in WEIGHTS below: the topics with the most wrong answers get
the most questions, and dictionaries, the weakest topic, come back in part 2.

Every program here is run with real Python when the page is built. The output boxes
are what the run printed. In an explanation, [[text]] marks a quoted output line (or
an error's name): the build stops unless that text is a real line of a run on that
question. Each question can also list facts, small Python expressions that back a
number the prose states, and the build stops if one is False.

    python3 build/review.py

Edit the questions here, never in the .html.
"""

import ast
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from check import BANNED_NODES, BANNED_PHRASES, DASHES, balanced, nested_if  # noqa: E402
from highlight import highlight, plain  # noqa: E402
from make import FONTS, PYTHON, Fail, error_name, run  # noqa: E402

OUT_NAME = "advanced_python_fall2026_review.html"
TITLE = "Review for Advanced Python Fall 2026"
MAX_LINE = 41  # longest code line that fits a 390px phone


def c(text):
    return text[1:] if text.startswith("\n") else text


# ------------------------------------------------------------------ the result
# The assessment result this review was built from, one row per quiz round:
# (round id, title, right, asked, sure but wrong, what the wrong answers were about).
WEIGHTS = [
    ("dicts", "Dictionaries", 1, 4, 3,
     "changing and adding a pair, a key that does not match, what `in` checks"),
    ("remainders", "Remainders", 2, 4, 2,
     "what `%` gives, and using it to go round a list again"),
    ("functions", "Functions", 3, 5, 2,
     "`print` or `return`, and the order of the values in a call"),
    ("strings", "Strings", 3, 5, 1,
     "index numbers and slices, and storing what `strip` or `replace` makes"),
    ("types", "Input and types", 3, 5, 2,
     "`input` gives text, so `+` joins"),
    ("gates", "Comparisons and if", 3, 4, 1,
     "the first condition that is True wins"),
    ("loops", "for loops and range", 3, 4, 1,
     "adding up a total in a loop"),
    ("names", "Printing and names", 3, 4, 1,
     "capital and small letters make different names"),
    ("andor", "and, or, and while", 4, 5, 1,
     "the order of the lines in a `while` loop"),
    ("lists", "Lists", 4, 5, 1,
     "an index number past the end of a list"),
    ("errors", "Reading errors", 5, 6, 1,
     "calling a function above its `def`"),
]

# ------------------------------------------------------------------ the questions
# topic    shown above the question
# patches  the round ids in WEIGHTS this question works on
# ask      the prediction question
# code     the program; stdin is what is typed when it asks
# explain  paragraphs shown with the real output
# then     optional second program: lead (text before it), code, after (text under it)
# facts    Python expressions that must be True
# allow    code rules this program breaks on purpose

PARTS = [
{"id": "part1", "name": "Part 1", "focus": "Dictionaries, remainders and strings",
 "questions": [

 {"topic": "Dictionaries", "patches": ["dicts"],
  "ask": "A dictionary holds pairs: a **key** and the **value** stored under it. "
         "What two lines does this program print?",
  "code": c('''
prices = {"pen": 2, "cup": 5}
prices["cup"] = 6
prices["hat"] = 9
print(prices["cup"])
print(len(prices))
'''),
  "explain": [
      "Line 2 uses the key `\"cup\"`, which is already in the dictionary, so the value "
      "stored under it changes from 5 to 6. Line 4 prints [[6]].",
      "Line 3 uses the key `\"hat\"`, which is not in the dictionary yet, so Python adds "
      "a new pair. `len` counts the pairs. There were 2 and line 3 added one more, so "
      "line 5 prints [[3]].",
      "**`prices[key] = value` changes the value when the key is already there, and "
      "adds a new pair when it is not.**",
  ]},

 {"topic": "Dictionaries", "patches": ["dicts", "names"],
  "ask": "Does this program stop with an error? If it does, say the error's name.",
  "code": c('''
prices = {"pen": 2, "cup": 5}
print(prices["Cup"])
'''),
  "explain": [
      "The dictionary has the key `\"cup\"` with a small c. Line 2 asks for `\"Cup\"` "
      "with a capital C. Python treats capital and small letters as different, so "
      "there is no such key and the program stops with a [[KeyError]].",
      "The last line of the error message shows the key Python could not find: "
      "[[KeyError: 'Cup']]",
      "**A key has to match exactly, capital letters included.** Variable names work "
      "the same way: `score` and `Score` are two different names.",
  ]},

 {"topic": "Dictionaries", "patches": ["dicts"],
  "ask": "`in` asks a yes or no question about a dictionary. What two lines does this "
         "program print?",
  "code": c('''
prices = {"pen": 2, "cup": 5}
print(2 in prices)
print("pen" in prices)
'''),
  "explain": [
      "With a dictionary, `in` looks at the keys only. The keys are `\"pen\"` and "
      "`\"cup\"`. The number 2 is a value, not a key, so line 2 prints [[False]].",
      "`\"pen\"` is a key, so line 3 prints [[True]].",
      "**`in` checks the keys of a dictionary, not the values.**",
  ]},

 {"topic": "Remainders", "patches": ["remainders"],
  "ask": "`%` gives the **remainder**: what is left over after dividing. What three "
         "lines does this program print?",
  "code": c('''
print(14 % 4)
print(12 % 4)
print(3 % 7)
'''),
  "explain": [
      "Three 4s fit into 14 and make 12, with 2 left over, so line 1 prints [[2]].",
      "Three 4s fit into 12 with nothing left over, so line 2 prints [[0]].",
      "No 7 fits into 3, so all of the 3 is left over and line 3 prints [[3]].",
      "**When the first number is smaller than the second, the remainder is the first "
      "number.**",
  ],
  "facts": ["3 * 4 == 12", "14 - 12 == 2"]},

 {"topic": "Remainders and lists", "patches": ["remainders", "lists"],
  "ask": "The list has two names, at index 0 and index 1. The loop makes five passes. "
         "What does the program print?",
  "code": c('''
team = ["Ada", "Mo"]
for turn in range(5):
    print(team[turn % 2])
'''),
  "explain": [
      "`turn` counts 0, 1, 2, 3, 4. `turn % 2` changes those numbers into 0, 1, 0, 1, 0. "
      "The index number never goes past 1, so the two names take turns.",
  ],
  "then": {
      "lead": "Without `% 2`, the third pass asks for `team[2]`:",
      "code": c('''
team = ["Ada", "Mo"]
for turn in range(5):
    print(team[turn])
'''),
      "after": [
          "The error's name is [[IndexError]]. A list with 2 items has index 0 and "
          "index 1, and no index 2.",
          "**The last index number of a list is one less than its length.**",
      ]},
  "facts": ["[turn % 2 for turn in range(5)] == [0, 1, 0, 1, 0]",
            "list(range(5)) == [0, 1, 2, 3, 4]"]},

 {"topic": "Strings", "patches": ["strings", "loops"],
  "ask": "Each letter of a string has an index number, starting at 0. What two lines "
         "does this program print?",
  "code": c('''
word = "planet"
print(word[0])
print(word[2:5])
'''),
  "explain": [
      "Index 0 is the first letter, so line 2 prints [[p]].",
      "`word[2:5]` is a **slice**. It starts at index 2 and stops before index 5. That "
      "is index 2, 3 and 4: the letters a, n and e. Line 3 prints [[ane]]. The letter "
      "at index 5, t, is left out.",
      "**A slice includes its first index number and stops before its second.** "
      "`range(2, 5)` counts the same way: 2, 3, 4.",
  ],
  "facts": ["'planet'[5] == 't'", "list(range(2, 5)) == [2, 3, 4]",
            "['planet'[i] for i in (2, 3, 4)] == ['a', 'n', 'e']"]},

 {"topic": "Strings", "patches": ["strings"],
  "ask": "Line 2 replaces a letter. What does line 3 print?",
  "code": c('''
word = "cool"
word.replace("c", "p")
print(word)
'''),
  "explain": [
      "`replace` makes a new string, `\"pool\"`, and leaves `word` as it was. Line 2 "
      "does not store the new string under any name, so it is lost. Line 3 prints "
      "[[cool]].",
  ],
  "then": {
      "lead": "To keep the new string, store it under the name:",
      "code": c('''
word = "cool"
word = word.replace("c", "p")
print(word)
'''),
      "after": [
          "Now line 3 prints [[pool]].",
          "**`replace` and `strip` make a new string. Store it, or it is lost.**",
      ]},
  "facts": ["'cool'.replace('c', 'p') == 'pool'"]},
 ]},

{"id": "part2", "name": "Part 2", "focus": "Dictionaries again, functions, input, if and loops",
 "questions": [

 {"topic": "Dictionaries", "patches": ["dicts"],
  "ask": "`tally` starts as an empty dictionary. The loop looks at one vote on each "
         "pass. What two lines does the program print?",
  "code": c('''
votes = ["cat", "dog", "cat", "cat"]
tally = {}
for v in votes:
    if v in tally:
        tally[v] = tally[v] + 1
    else:
        tally[v] = 1
print(tally["cat"])
print(len(tally))
'''),
  "explain": [
      "On the first pass `\"cat\"` is not a key yet, so line 7 adds it with the value 1. "
      "On the second pass line 7 adds `\"dog\"` the same way. On the third and fourth "
      "passes `\"cat\"` is already a key, so line 5 adds 1 to its value: 2, then 3. "
      "Line 8 prints [[3]].",
      "The dictionary ends with two keys, `\"cat\"` and `\"dog\"`, so line 9 prints "
      "[[2]]. Four votes went in, but each key is stored once and `len` counts the keys.",
  ],
  "facts": ["['cat', 'dog', 'cat', 'cat'].count('cat') == 3",
            "len(set(['cat', 'dog', 'cat', 'cat'])) == 2"]},

 {"topic": "Functions", "patches": ["functions"],
  "ask": "The function prints, but it has no `return` line. What two lines does the "
         "program print?",
  "code": c('''
def add_one(n):
    print(n + 1)

result = add_one(4)
print(result)
'''),
  "explain": [
      "Line 4 calls the function, and line 2 prints [[5]].",
      "The function has no `return` line, so the call gives the value `None`. That is "
      "what line 4 stores in `result`, and line 5 prints [[None]].",
  ],
  "then": {
      "lead": "With `return` in place of `print`, the call gives the value 5 to line 4:",
      "code": c('''
def add_one(n):
    return n + 1

result = add_one(4)
print(result)
'''),
      "after": [
          "**`print` shows a value on the screen. `return` gives a value to the line "
          "that called the function, so that line can store it or use it.**",
      ]}},

 {"topic": "Functions", "patches": ["functions"],
  "ask": "Look at the order of the two values in the call on line 4. What does the "
         "program print?",
  "code": c('''
def ticket(name, seat):
    return f"{name} sits in {seat}"

print(ticket(12, "Mo"))
'''),
  "explain": [
      "Python matches the values in the call to the parameters by position. The first "
      "value, 12, goes to `name`. The second value, `\"Mo\"`, goes to `seat`. The "
      "program prints [[12 sits in Mo]].",
      "Python gives no error message here, because every line is allowed. The mistake "
      "shows only in the output.",
      "**The first value in a call goes to the first parameter, the second value to the "
      "second parameter.**",
  ]},

 {"topic": "Functions", "patches": ["functions", "errors"],
  "ask": "Does this program stop with an error? If it does, say the error's name.",
  "code": c('''
print(square(3))

def square(n):
    return n * n
'''),
  "allow": ["def after work"],
  "explain": [
      "Python runs a file from the top. Line 1 calls `square` before Python has reached "
      "the `def` on line 3, so the name `square` has no value yet. The program stops "
      "with a [[NameError]].",
      "**Every `def` goes at the top of the file, before any line that does work.**",
  ]},

 {"topic": "Input and types", "patches": ["types"],
  "ask": "The person types 4 and presses Enter. What does line 2 print?",
  "stdin": "4",
  "code": c('''
laps = input("Laps: ")
print(laps + laps)
'''),
  "explain": [
      "`input` gives text, even when the person types digits. `laps` holds the text "
      "`\"4\"`. With two pieces of text, `+` joins them end to end, so line 2 prints "
      "[[44]].",
  ],
  "then": {
      "lead": "To add, change the type to a whole number with `int`:",
      "stdin": "4",
      "code": c('''
laps = input("Laps: ")
laps = int(laps)
print(laps + laps)
'''),
      "after": [
          "Now `+` adds two numbers, and line 3 prints [[8]].",
          "**`input` gives text. Change the type with `int` before doing arithmetic.**",
      ]}},

 {"topic": "Comparisons and if", "patches": ["gates"],
  "ask": "35 is more than 20 and more than 30. What does the program print?",
  "code": c('''
temp = 35
if temp > 20:
    print("warm")
elif temp > 30:
    print("hot")
else:
    print("cold")
'''),
  "explain": [
      "Python checks the conditions from the top and runs the lines under the first one "
      "that is True. `temp > 20` is True, so line 3 prints [[warm]]. Python then skips "
      "the `elif` and the `else` without checking them.",
  ],
  "then": {
      "lead": "To print hot for 35, put the `temp > 30` check first:",
      "code": c('''
temp = 35
if temp > 30:
    print("hot")
elif temp > 20:
    print("warm")
else:
    print("cold")
'''),
      "after": [
          "Now the first condition that is True is `temp > 30`, and line 3 prints [[hot]].",
          "**In an `if`, `elif`, `else` chain, only the first condition that is True "
          "runs its lines.**",
      ]}},

 {"topic": "Loops and totals", "patches": ["loops", "andor"],
  "ask": "Say the value of `total` after each pass of the loop. Then say what line 6 "
         "prints.",
  "code": c('''
count = 1
total = 0
while count <= 4:
    total = total + count
    count = count + 1
print(total)
'''),
  "explain": [
      "**The value of `total` after each pass.** `total` starts at 0, and line 4 adds "
      "`count` to it on each pass: 1, then 3, then 6, then 10.",
      "**What line 6 prints.** Line 5 makes `count` one bigger on each pass. When "
      "`count` reaches 5, `count <= 4` is False and the loop stops. Line 6 prints [[10]].",
      "Without line 5, `count` would stay at 1, the condition would stay True, and the "
      "loop would never stop.",
  ],
  "facts": ["[sum(range(1, k + 1)) for k in (1, 2, 3, 4)] == [1, 3, 6, 10]"]},
 ]},
]


# ------------------------------------------------------------------ text and code

def fmt(text):
    """Escape, then `code` -> <code>, **term** -> <b>, [[line]] -> <code class="said">."""
    t = html.escape(text, quote=False)
    t = re.sub(r"\[\[(.+?)\]\]", r'<code class="said">\1</code>', t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t


def code_block(src):
    """Coloured code, one span per line, each four-space step inside an indent guide."""
    lines = []
    for raw in highlight(src.rstrip("\n")).split("\n"):
        m = re.match(r"^((?: {4})+)", raw)
        steps = len(m.group(1)) // 4 if m else 0
        guides = '<span class="ig">    </span>' * steps
        lines.append(f'<span class="cl">{guides}{raw[steps * 4:]}</span>')
    block = "\n".join(lines)
    if plain(block) != src.rstrip("\n"):
        raise Fail("colouring does not give the code back exactly:\n" + src)
    return f'<pre class="py"><code>{block}</code></pre>'


def check_program(label, src, may_fail, allow=()):
    for n, line in enumerate(src.split("\n"), 1):
        if len(line) > MAX_LINE:
            raise Fail(f"{label}: line {n} is {len(line)} characters (limit {MAX_LINE})")
        if "\t" in line:
            raise Fail(f"{label}: line {n} has a tab")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        for kind, name in BANNED_NODES.items():
            if isinstance(node, kind):
                raise Fail(f"{label}: uses {name}")
        if isinstance(node, ast.While) and isinstance(node.test, ast.Constant):
            raise Fail(f"{label}: while with a constant condition")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and \
                node.func.id == "print" and len(node.args) > 1:
            raise Fail(f"{label}: print with several arguments; use an f-string")
    if nested_if(tree, src.split("\n")):
        raise Fail(f"{label}: an if inside an if")
    seen_work = False
    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef):
            if seen_work and "def after work" not in allow:
                raise Fail(f"{label}: a def comes after a line that does work")
        else:
            seen_work = True


def check_prose(label, texts):
    for text in texts:
        if DASHES.search(text):
            raise Fail(f"{label}: has an em or en dash")
        bare = re.sub(r"`[^`]*`|\[\[.+?\]\]", "", text).lower()
        for phrase in BANNED_PHRASES:
            if phrase in bare:
                raise Fail(f"{label}: uses {phrase!r} in: {text[:70]}")


def said(texts):
    return [m for t in texts for m in re.findall(r"\[\[(.+?)\]\]", t)]


def build_question(part, n, q):
    """Run the question's programs and return (html, record for the report)."""
    label = f"{part['id']} question {n}"
    qid = f"{part['id']}-q{n}"
    allow = q.get("allow", ())
    check_program(label, q["code"], False, allow)
    r = run(q["code"], q.get("stdin"))
    if r["timed_out"]:
        raise Fail(f"{label}: the program never stops")
    real = set(r["term"].splitlines())
    names = {error_name(r)} if error_name(r) else set()
    texts = [q["ask"]] + q["explain"]

    then_html = ""
    then = q.get("then")
    if then:
        check_program(label + " (second program)", then["code"], False, allow)
        r2 = run(then["code"], then.get("stdin"))
        if r2["timed_out"]:
            raise Fail(f"{label}: the second program never stops")
        real |= set(r2["term"].splitlines())
        if error_name(r2):
            names.add(error_name(r2))
        texts += [then["lead"]] + then["after"]
        then_html = (f'<p>{fmt(then["lead"])}</p>{code_block(then["code"])}'
                     f'<p class="label green">What actually happens</p>'
                     f'<pre class="out">{html.escape(r2["term"], quote=False)}</pre>'
                     + "".join(f"<p>{fmt(t)}</p>" for t in then["after"]))

    check_prose(label, texts)
    for quote in said(texts):
        if quote not in real and quote not in names:
            raise Fail(f"{label}: [[{quote}]] is not a line of the real output:\n{r['term']}")
    for fact in q.get("facts", []):
        if eval(fact, {}) is not True:  # facts are written in this file
            raise Fail(f"{label}: fact is not True: {fact}")
    if not said(texts):
        raise Fail(f"{label}: the explanation quotes no output line")

    out = html.escape(r["term"], quote=False) or '<span class="empty">(prints nothing)</span>'
    body = (f'<section class="q" id="{qid}">'
            f'<p class="label">Question {n} · {html.escape(q["topic"])}</p>'
            f'<div class="predict"><p>{fmt(q["ask"])}</p></div>'
            f'{code_block(q["code"])}'
            f'<p><button type="button" class="btn" aria-expanded="false" '
            f'aria-controls="{qid}-a">Say your answer first, then check here</button></p>'
            f'<div class="answer" id="{qid}-a" hidden>'
            f'<p class="label green">What actually happens</p>'
            f'<pre class="out">{out}</pre>'
            + "".join(f"<p>{fmt(t)}</p>" for t in q["explain"]) + then_html +
            '</div></section>')
    for err in balanced(body):
        raise Fail(f"{label}: {err}")
    return body, {"label": label, "topic": q["topic"], "term": r["term"]}


# ------------------------------------------------------------------ teacher panel

def teacher_panel():
    count = {w[0]: 0 for w in WEIGHTS}
    where = {w[0]: [] for w in WEIGHTS}
    for part in PARTS:
        for n, q in enumerate(part["questions"], 1):
            for rid in q["patches"]:
                if rid not in count:
                    raise Fail(f"{part['id']} question {n}: unknown round {rid}")
                count[rid] += 1
                where[rid].append(f"{part['name']} Q{n}")
    for w in WEIGHTS:
        if not count[w[0]]:
            raise Fail(f"no review question works on {w[1]}")
    rows = "".join(
        f"<tr><td>{html.escape(title)}</td><td>{right} of {asked}</td><td>{sw}</td>"
        f"<td>{fmt(about)}</td><td>{', '.join(where[rid])}</td></tr>"
        for rid, title, right, asked, sw, about in WEIGHTS)
    wrong = sum(w[3] - w[2] for w in WEIGHTS)
    asked = sum(w[3] for w in WEIGHTS)
    weakest = ",".join(w[0] for w in WEIGHTS[:4])
    n1, n2 = (len(p["questions"]) for p in PARTS)
    return f"""<details class="teacher"><summary>Teacher panel</summary>
<h3>How to run it</h3>
<ul>
<li>Use one part as the opener of each of two class sessions. Each part is planned for 10 minutes: {n1} questions in part 1 and {n2} in part 2.</li>
<li>For each question, students read the program and say their prediction to a neighbour. Then press the button. Nothing a program prints shows before the press.</li>
<li>The questions in each part run from the weakest topic down. If time runs out, stop where you are. Part 1 questions 1 to 5 and part 2 questions 1 to 4 are the ones to finish.</li>
<li>The address <code>?part=2</code> opens the page on part 2.</li>
</ul>
<h3>Why these questions</h3>
<p>The review was built from an assessment result with {wrong} wrong answers out of {asked}. Most of the wrong answers were given with Sure pressed, which points to a wrong idea about Python, not a guess. So every question here asks for a prediction first and then shows the real output. The programs are new, so a remembered answer from the assessment does not help.</p>
<div class="scroll"><table>
<thead><tr><th>Topic</th><th>Right</th><th>Sure but wrong</th><th>The wrong answers were about</th><th>Reviewed in</th></tr></thead>
<tbody>{rows}</tbody>
</table></div>
<p>Dictionaries had the lowest score, so they get three questions in part 1 and come back as the first question of part 2.</p>
<h3>More practice</h3>
<p>The quiz can run the four weakest rounds again, on the projector with no score: <a href="index.html?rounds={weakest}&amp;mode=class">dictionaries, remainders, functions and strings in class mode</a>.</p>
</details>"""


# ------------------------------------------------------------------ the page
CSS = r"""
:root{
  --paper:#F4F0E6; --card:#FFFDF7; --ink:#17181B; --ink-soft:#4A4D53; --rule:#D3CBB8;
  --teal:#0E4D52; --teal-deep:#0A3A3E; --teal-tint:#E3EDEE; --clay:#9C2B22;
  --ochre:#8A5A00; --ochre-line:#D99B12; --ochre-tint:#FBF2DC;
  --green:#1D5B39; --green-tint:#E8F1E9; --green-ink:#122B1C; --code-bg:#EDE7D9;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0; background:var(--paper); color:var(--ink);
  font-family:'DM Sans',system-ui,sans-serif; font-size:18px; font-weight:500; line-height:1.65}
header.top{background:var(--teal); color:#FFFDF7; border-bottom:6px solid var(--ochre-line);
  padding:30px 22px 26px}
.wrap{max-width:1080px; margin:0 auto}
.eyebrow{font-family:'JetBrains Mono',monospace; font-size:13px; letter-spacing:.14em;
  text-transform:uppercase; color:#F2D89B; margin:0 0 10px; font-weight:700}
h1{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:800;
  font-size:clamp(29px,4.8vw,44px); line-height:1.1; margin:0 0 10px; color:#FFFDF7}
h2{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:700; font-size:25px;
  line-height:1.25; margin:0 0 14px; color:var(--teal-deep)}
h3{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:700; font-size:20px;
  margin:18px 0 10px; color:var(--teal-deep)}
.sub{color:#EAE3D2; margin:0 0 14px; font-size:19px; font-weight:400}
.pills{display:flex; flex-wrap:wrap; gap:8px; margin:0; padding:0; list-style:none}
.pills li{font-family:'JetBrains Mono',monospace; font-size:13.5px; font-weight:700;
  border:2px solid #F2D89B; color:#FFFDF7; border-radius:999px; padding:3px 12px; margin:0}
main{padding:28px 22px 12px}
section,details.teacher{background:var(--card); border:2px solid var(--rule); border-radius:6px;
  padding:22px 24px; margin:0 0 20px}
section.how{border-left:8px solid var(--green)}
section.q{border-left:8px solid var(--ochre-line)}
details.teacher{border-left:8px solid var(--clay)}
details.teacher summary{font-family:'Bricolage Grotesque','DM Sans',sans-serif; font-weight:700;
  font-size:22px; color:var(--clay); cursor:pointer}
.label{font-family:'JetBrains Mono',monospace; font-size:13px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--ochre); margin:0 0 8px; font-weight:700}
.label.green{color:var(--green)}
p,li{max-width:72ch}
p{margin:0 0 14px}
ol,ul{margin:0 0 14px; padding-left:26px} li{margin:0 0 8px}
code,pre{font-variant-ligatures:none; font-feature-settings:"liga" 0,"calt" 0,"dlig" 0}
code{font-family:'JetBrains Mono',monospace; font-size:.9em; font-weight:700;
  background:var(--code-bg); color:#1E2A2B; padding:2px 6px; border-radius:3px}
.predict{border:2px dashed var(--ochre); background:var(--ochre-tint); border-radius:5px;
  padding:14px 16px 2px; margin:0 0 16px}
pre{font-family:'JetBrains Mono',monospace; margin:0 0 16px; overflow-x:auto; border-radius:4px}
/* Code: white ground, 19px, the colours VS Code gives Python, each at 7:1 or better. */
pre.py{background:#FFFFFF; color:#1F1F1F; border:2px solid var(--rule); padding:14px 16px;
  font-size:19px; line-height:1.6; font-weight:500; counter-reset:ln}
pre.py code{font:inherit; background:none; color:inherit; padding:0; border-radius:0}
pre.py .cl::before{counter-increment:ln; content:counter(ln); display:inline-block; width:2ch;
  margin-right:1.4ch; text-align:right; color:#595959; -webkit-user-select:none; user-select:none}
.tk-ctl{color:#8A00B0} .tk-kw{color:#0000FF} .tk-str{color:#A31515} .tk-num{color:#035F3E}
.tk-com{color:#006400} .tk-fn{color:#6A4E14} .tk-cls{color:#135C70} .tk-var{color:#001080}
/* Indent guides: one thick bar for each four-space step, so they show on a projector. */
.ig{display:inline-block; width:4ch; height:1.6em; vertical-align:top; white-space:pre;
  border-left:6px solid #595959}
pre.out{background:var(--green-tint); border:2px solid #A9C6B2; border-left:6px solid var(--green);
  color:var(--green-ink); padding:14px 16px; font-size:18px; line-height:1.55; font-weight:500}
.empty{font-family:'DM Sans',sans-serif; font-style:italic; color:var(--ink-soft)}
a{color:var(--teal)}
button{font-family:'DM Sans',sans-serif}
.btn{display:inline-block; font-size:17px; font-weight:700; background:var(--teal);
  color:#FFFDF7; border:2px solid var(--teal); border-radius:4px; padding:11px 20px;
  cursor:pointer; line-height:1.3}
.btn:hover{background:var(--teal-deep)}
.tabs{display:flex; flex-wrap:wrap; gap:10px; margin:0 0 20px}
.tab{font-size:18px; font-weight:700; background:var(--card); color:var(--teal);
  border:2px solid var(--teal); border-radius:4px; padding:10px 18px; cursor:pointer; line-height:1.3}
.tab[aria-selected="true"]{background:var(--teal); color:#FFFDF7}
.tab span{display:block; font-size:15px; font-weight:500}
:focus-visible{outline:3px solid var(--ochre-line); outline-offset:2px}
.answer{border-top:2px solid var(--rule); padding-top:16px; margin-top:4px}
.answer p:last-child{margin-bottom:0}
.scroll{overflow-x:auto; margin:0 0 14px}
table{border-collapse:collapse; width:100%; font-size:16px}
th,td{border:2px solid var(--rule); padding:7px 10px; text-align:left; vertical-align:top}
th{background:#EFE9DA}
footer{max-width:1080px; margin:0 auto; padding:8px 22px 40px; color:var(--ink-soft); font-size:16px}
@media(max-width:760px){
  section,details.teacher{padding:16px 14px}
  pre.py{font-size:15px; padding:10px 10px}
  pre.out{font-size:15px}
}
@media print{
  body{background:#fff; font-size:11pt}
  header.top{background:#fff; border-bottom:3px solid #000; padding:0 0 8px}
  h1,.eyebrow,.sub{color:#000} .pills li{color:#000; border-color:#000}
  .tabs,.btn,details.teacher{display:none}
  .part,.answer{display:block}
  section{break-inside:avoid}
  pre.py{font-size:15.5px}
}
"""

JS = r"""
(function () {
  var tabs = Array.prototype.slice.call(document.querySelectorAll(".tab"));
  function show(id) {
    tabs.forEach(function (t) {
      var on = t.getAttribute("aria-controls") === id;
      t.setAttribute("aria-selected", on ? "true" : "false");
      document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
    });
  }
  tabs.forEach(function (t) {
    t.addEventListener("click", function () { show(t.getAttribute("aria-controls")); window.scrollTo(0, 0); });
  });
  var want = new URLSearchParams(location.search).get("part");
  show(want === "2" ? "part2" : "part1");
  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("button[aria-controls][aria-expanded]");
    if (!b) return;
    var box = document.getElementById(b.getAttribute("aria-controls"));
    var open = b.getAttribute("aria-expanded") === "true";
    b.setAttribute("aria-expanded", open ? "false" : "true");
    box.hidden = open;
    b.textContent = open ? "Say your answer first, then check here" : "Hide the answer";
  });
})();
"""


def render():
    """Build the whole page as a string and return (page, records)."""
    records, parts_html, tabs = [], [], []
    for i, part in enumerate(PARTS):
        qs = []
        for n, q in enumerate(part["questions"], 1):
            body, rec = build_question(part, n, q)
            qs.append(body)
            records.append(rec)
        tabs.append(f'<button type="button" class="tab" role="tab" aria-controls="{part["id"]}" '
                    f'aria-selected="{"true" if i == 0 else "false"}">{part["name"]}'
                    f'<span>{html.escape(part["focus"])}</span></button>')
        parts_html.append(
            f'<div class="part" id="{part["id"]}" role="tabpanel"{"" if i == 0 else " hidden"}>'
            f'<h2>{part["name"]} · 10 minutes</h2>' + "".join(qs) + '</div>')
    total = sum(len(p["questions"]) for p in PARTS)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<meta name="description" content="A short Python review in two 10 minute parts. Predict what each program prints, then see what Python really prints.">
{FONTS}
<style>{CSS}</style>
</head>
<body>
<header class="top"><div class="wrap">
<p class="eyebrow">Advanced Python · Fall 2026 · Review</p>
<h1>{TITLE}</h1>
<p class="sub">Read each program and say what it will print. Then check.</p>
<ul class="pills"><li>2 parts</li><li>10 minutes each</li><li>{total} questions</li><li>No new syntax</li></ul>
</div></header>
<main class="wrap">
<section class="how">
<p class="label green">How this works</p>
<ol>
<li>Read the program. Go one line at a time, top to bottom.</li>
<li>Say what it will print to the person next to you.</li>
<li>Press the button to see what Python really printed, and why.</li>
</ol>
</section>
<div class="tabs" role="tablist" aria-label="Parts of the review">{"".join(tabs)}</div>
{"".join(parts_html)}
{teacher_panel()}
</main>
<footer>
<p>Every program on this page was run with {PYTHON} when the page was built, and every output box shows what it really printed. Newer versions of Python word a few error messages differently, but the error names are the same.</p>
<p><a href="index.html">Beginner Python Quiz</a></p>
</footer>
<script>
{JS}
</script>
</body>
</html>
"""
    for err in balanced(re.sub(r"<script>.*?</script>", "", page, flags=re.S)):
        raise Fail(f"{OUT_NAME}: {err}")
    ids = re.findall(r'\sid="([^"]+)"', page)
    if len(ids) != len(set(ids)):
        raise Fail(f"{OUT_NAME}: an id repeats")
    for target in re.findall(r'aria-controls="([^"]+)"', page):
        if target not in ids:
            raise Fail(f"{OUT_NAME}: a button points at {target}, which is not on the page")
    return page, records


def main():
    page, records = render()
    for rec in records:
        print(f"  ok  {rec['label']:<18} {rec['topic']}")
    with open(os.path.join(ROOT, OUT_NAME), "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"wrote {OUT_NAME}: {len(records)} questions in {len(PARTS)} parts ({PYTHON})")


if __name__ == "__main__":
    try:
        main()
    except Fail as e:
        print("FAIL:", e)
        sys.exit(1)
