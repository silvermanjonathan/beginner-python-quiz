# Beginner Python Quiz

A quiz for people learning their first Python. Each question shows a short program and
asks what it will do. After each answer the quiz shows why that answer is right or
wrong, and what Python really printed.

**Take the quiz:** https://silvermanjonathan.github.io/beginner-python-quiz/

## What is in it

51 questions in 11 rounds:

| # | Round | Questions | Covers |
|---|---|---|---|
| 1 | Printing and names | 4 | print, quote marks, and names that hold values |
| 2 | Input and types | 5 | input, text and numbers, type(), int(), f-strings |
| 3 | Comparisons and if | 4 | True and False, ==, if, elif, else |
| 4 | and, or, and while | 5 | two conditions at once, and loops that stop |
| 5 | for loops and range | 4 | range, the loop variable, adding up a total |
| 6 | Lists | 5 | index numbers, len, max, sum, counters, best so far |
| 7 | Functions | 5 | def, parameters, return and print |
| 8 | Strings | 5 | index numbers, slices, strip, replace, in |
| 9 | Remainders | 4 | %, wrapping around, even and odd |
| 10 | Dictionaries | 4 | keys and values, KeyError, counting with a dictionary |
| 11 | Reading errors | 6 | error names, which line, bugs with no error message |

Seven kinds of question, so it is not all multiple choice:

- **What does it print?** Pick the whole output.
- **What does the last line show?** For programs that ask for input first.
- **Does it run?** Pick the error name, or "No error".
- **Which line?** Pick the line the error message names.
- **Fill the blank.** Pick the piece of code that makes the program print the target.
  Every wrong piece shows what the program would really print with it.
- **Put the lines in order.** Tap the lines into order. Every possible order was run
  when the page was built, so a wrong order shows exactly what it would print, and
  any order that works counts as right.
- **Type the answer.** Type exactly what the program prints.

## How it works

**On your own.** Pick an answer, then press **Sure** or **Not sure** to check it. Every
wrong answer has its own reason. At the end comes a strengths and weaknesses picture:

- **Strongest topics and Work on next.** Rounds with 4 in 5 right or better are strong;
  rounds under half right are the ones to work on, each with a **Practise this round**
  button. A round needs at least 3 answers before it is rated, so a quick quiz says it is
  too few to tell.
- **Topic by topic.** One square for each question: a tick or a cross for right or wrong,
  filled for Sure and outlined for Not sure, so it reads without colour. Each round is
  rated Strong, Nearly there, or Work on this.
- **Sure but wrong.** The questions a student felt sure about and got wrong, and where
  they were. Those show the ideas about Python to fix first.
- **Skills.** Right answers by kind of question: predicting output, reading errors,
  choosing the missing code, putting lines in order.
- **How sure you were.** How often the student was right when they pressed Sure, and when
  they pressed Not sure.

A student can type their name onto the picture and press **Print this picture** to print
it on one page (or save it as a PDF) to hand in. Below the picture, the questions are
sorted into sure and wrong, not sure and wrong, and not sure but right, and one button
runs just those questions again.

**With a class on a projector.** Bigger text and no score. The class picks an answer,
then the teacher presses **Show the answer**, which shows the right one and the reason
for every wrong one. On a put-the-lines-in-order question, **Check this order** shows
what any order prints without giving the answer away.

**Keys.** A to D pick an answer, S checks as sure, N checks as not sure, H shows a hint,
R shows the answer in class mode, Enter goes to the next question.

**Links for a class.** Add these to the address to set up the start screen:

- `?rounds=gates,andor` picks rounds by id: `names`, `types`, `gates`, `andor`, `loops`,
  `lists`, `functions`, `strings`, `remainders`, `dicts`, `errors`
- `?mode=class` starts in class mode
- `?shuffle=1` mixes up the order of the questions

For example:
`https://silvermanjonathan.github.io/beginner-python-quiz/?rounds=loops,lists&mode=class`

Nothing is saved in the browser. Closing or reloading the page starts fresh.

## How the answers are checked

`index.html` is generated. Edit `build/questions.py`, never the HTML.

`build/make.py` runs every program in the quiz with real Python and takes each right
answer from what the program really printed. No right answer is typed by hand. The
build stops if:

- a wrong option turns out to be what Python prints,
- a fill-the-blank question has no fill, or more than one, that prints the target,
- a put-in-order question's own order does not print the target, or the number of
  orders that do is not the number the question says,
- a program meant to run stops with an error, or one meant to stop does not.

It also writes `build/answer_key.md`: every question, its answer, and its real output.

`build/check.py` then checks the question bank and the page:

- every program keeps to the code rules below,
- every wrong option has a reason, every question has a hint,
- no em or en dashes, and none of a list of filler words,
- the page's answers match the bank, every order was run, the HTML is balanced,
  the script parses, and nothing uses browser storage.

```
python3 build/make.py
python3 build/check.py
```

Both must pass before the page is published.

## Code rules the questions keep to

The programs use only what a first Python course covers:

- flat `if`, `elif`, `else`: no `if` inside another `if` (join two conditions with `and`)
- every `while` has a stopping condition you can point at: no `while True`, `break`,
  or `continue`
- f-strings for any print that mixes words and values
- every `def` at the top of the file, before any line that does work (one question
  breaks this on purpose, because the rule is the question)
- nothing from later courses: no `try`, `class`, `lambda`, `global`, comprehensions,
  `//`, imports, or files

## Adding a question

Add a dict to `QUESTIONS` in `build/questions.py`. The top of that file explains each
kind. The short version:

```python
{"id": "loops-5", "round": "loops", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
for i in range(2):
    print("hi")
'''),
 "wrong": [
    ["hi", "The print line is indented, so it runs on every pass."],
    ["hi\nhi\nhi", "`range(2)` gives two numbers, 0 and 1."],
    ["0\n1", "The print line prints the text in quote marks, not `i`."],
 ],
 "hints": ["How many numbers does range(2) give?"],
 "explain": "`range(2)` gives 0 and 1, so the loop makes two passes and prints hi each time."},
```

Write the wrong answers and their reasons. Do not write the right answer: `make.py`
gets it by running the code. In the text, `backticks` show as code and `**two stars**`
show in bold.

## Files

| File | What it is |
|---|---|
| `index.html` | The quiz. One self-contained page; the only outside files are the fonts. |
| `build/questions.py` | Every question, wrong answer, reason, hint, and explanation. |
| `build/make.py` | Runs every program and writes `index.html` and the answer key. |
| `build/quiz.js` | The quiz's script. `make.py` puts it inside `index.html`. |
| `build/highlight.py` | Colours code the way VS Code's Light+ theme does. |
| `build/check.py` | Checks the bank and the page. |
| `build/answer_key.md` | Generated. Every answer with its real output. |

The look is the Lecture Light style: a light theme made to be read on a projector in a
room with the lights on, with code coloured by role the way VS Code colours it.
