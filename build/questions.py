"""The question bank. Edit questions here, never in index.html.

Every program in this file is run by make.py with real Python. The right answer to
every question is taken from what that run printed, never typed here. What is typed
here is the wrong answers, the reason each one is wrong, the hints, and the
explanation. make.py stops if a wrong answer turns out to be what Python prints.

Text markup, used in ask, why, hints and explain:
    `code`    shows as code
    **term**  shows in bold (use it the first time a term is defined)

Kinds of question:
    output  What does this program print? Options are whole outputs.
    last    Options are the last line printed (used when input() puts a prompt line first).
    error   The program stops with an error. Options are error names.
    line    The program stops with an error. Options are line numbers.
    blank   Which fill for ___ makes the program print the target? Each fill is run.
    order   Put the lines in order. Every order is run; any order that prints the target counts.
    type    Type the answer. take="last" means the last printed line.

A wrong option that starts with ~ is shown as a sentence, not as program output.

Code boxes on the page show line numbers, counting blank lines, so a reason may name
a line by its number.
"""

FILE_NAME = "Ada_quiz.py"

ERROR_ASK = "Does this program stop with an error? If it does, what is the error's name?"


def c(text):
    """Strip the first newline of a triple-quoted program."""
    return text[1:] if text.startswith("\n") else text


ROUNDS = [
    {"id": "names", "title": "Printing and names",
     "about": "print, quote marks, and names that hold values"},
    {"id": "types", "title": "Input and types",
     "about": "input, text and numbers, type(), int(), f-strings"},
    {"id": "gates", "title": "Comparisons and if",
     "about": "True and False, ==, if, elif, else"},
    {"id": "andor", "title": "and, or, and while",
     "about": "two conditions at once, and loops that stop"},
    {"id": "loops", "title": "for loops and range",
     "about": "range, the loop variable, adding up a total"},
    {"id": "lists", "title": "Lists",
     "about": "index numbers, len, max, sum, counters, best so far"},
    {"id": "functions", "title": "Functions",
     "about": "def, parameters, return and print"},
    {"id": "strings", "title": "Strings",
     "about": "index numbers, slices, strip, replace, in"},
    {"id": "remainders", "title": "Remainders",
     "about": "%, wrapping around, even and odd"},
    {"id": "dicts", "title": "Dictionaries",
     "about": "keys and values, KeyError, counting with a dictionary"},
    {"id": "errors", "title": "Reading errors",
     "about": "error names, which line, bugs with no error message"},
]


QUESTIONS = [

# ---------------------------------------------------------------- printing and names
{"id": "names-1", "round": "names", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
pet = "Rex"
print("pet")
print(pet)
'''),
 "wrong": [
    ["Rex\nRex",
     "The first print has quote marks around pet. Quote marks make text, so Python "
     "prints the three letters p, e, t. It does not look up the name."],
    ["pet\npet",
     "The second print has no quote marks, so Python looks up the name `pet` and "
     "prints the value stored under it: Rex."],
    ["Rex\npet",
     "Python runs the lines from top to bottom. The print with quote marks comes first."],
 ],
 "hints": ["Quote marks make text. A word with no quote marks is a name, and Python "
           "looks up its value."],
 "explain": "Line 2 prints the text inside the quote marks: pet. Line 3 has no quote "
            "marks, so Python looks up the name `pet` and prints its value: Rex. A name "
            "that holds a value, like `pet`, is called a **variable**."},

{"id": "names-2", "round": "names", "kind": "output",
 "ask": "Line 2 and line 3 are the same. What does the program print?",
 "code": c('''
score = 10
score = score + 5
score = score + 5
print(score)
'''),
 "wrong": [
    ["15", "Line 3 runs too. It adds 5 to the 15 that line 2 stored."],
    ["10", "Each line with `=` stores a new value under `score`. The 10 is replaced on "
           "line 2, and replaced again on line 3."],
    ["score + 5", "There are no quote marks, so Python works out `score + 5` as "
                  "arithmetic. It does not print the words."],
 ],
 "hints": ["Go one line at a time and write down the value of score after each line."],
 "explain": "Python works out the right side of `=` first, then stores the answer under "
            "the name on the left. Line 2 gives 10 + 5 = 15. Line 3 gives 15 + 5 = 20."},

{"id": "names-3", "round": "names", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
a = 3
b = a
a = 7
print(b)
'''),
 "wrong": [
    ["7", "`b = a` stores the value `a` has at that moment, which is 3. Giving `a` a new "
          "value on line 3 does not change `b`."],
    ["a", "Line 2 has no quote marks, so `b` gets the value of `a`, which is 3, not the "
          "letter a."],
    ["10", "Nothing here adds. Line 3 replaces the value of `a` with 7. It does not add 7 to it."],
 ],
 "hints": ["Keep a list of each name and its value. Line 2 sets b to whatever a is at "
           "that moment."],
 "explain": "Line 2 stores the value of `a`, which is 3, under the name `b`. Line 3 gives "
            "`a` a new value, 7, but `b` still holds 3."},

{"id": "names-4", "round": "names", "kind": "error",
 "ask": ERROR_ASK,
 "code": c('''
name = "Mo"
print(Name)
'''),
 "wrong": [
    ["No error. It prints Mo",
     "Python treats a capital N and a small n as different letters. `name` and `Name` "
     "are two different names, and only `name` was given a value."],
    ["No error. It prints Name",
     "`Name` has no quote marks, so Python looks for a value stored under `Name`. "
     "Nothing was stored under it, so Python stops with an error."],
    ["SyntaxError",
     "A SyntaxError means Python cannot read a line at all, like a missing bracket. "
     "Both lines here are written correctly. The problem is a name Python does not know."],
 ],
 "hints": ["Look closely at the first letter of the name on each line."],
 "explain": "The last line of the error starts with NameError and names the word `Name`. "
            "Python treats capital and small letters as different, so `Name` is a new "
            "name that was never given a value."},

# ---------------------------------------------------------------- input and types
{"id": "types-1", "round": "types", "kind": "last", "stdin": "3",
 "ask": "What does the print line show?",
 "code": c('''
age = input("Robot age: ")
print(age + age)
'''),
 "wrong": [
    ["6", "`input` always gives text. `age` holds the text `\"3\"`, and `+` joins two "
          "pieces of text end to end."],
    ["~It stops with an error",
     "Text plus text is allowed: `+` joins them. The error comes from text plus a "
     "number, and there is no number here."],
    ["3 3", "`+` joins text with nothing in between. It does not add a space."],
 ],
 "hints": ["What type of value does input give you: text or a number?"],
 "explain": "`input` always gives text, even when the person types digits. So `age` holds "
            "the text `\"3\"`. With two pieces of text, `+` joins them end to end: "
            "`\"3\" + \"3\"` is `\"33\"`."},

{"id": "types-2", "round": "types", "kind": "error", "stdin": "3",
 "ask": ERROR_ASK,
 "code": c('''
age = input("Robot age: ")
print(age + 1)
'''),
 "wrong": [
    ["No error. It prints 4",
     "`age` holds the text `\"3\"`, not the number 3. Python will not add a number to text."],
    ["NameError",
     "Every name here has a value: `age` was given one on line 1. The problem is the "
     "type of value `age` holds."],
    ["SyntaxError",
     "Both lines are written correctly, so Python starts running. The error happens on "
     "line 2, when Python tries text plus a number."],
 ],
 "hints": ["The 3 the person typed comes back from input as text."],
 "explain": "`age` holds the text `\"3\"`. Text plus a number is not allowed, so Python "
            "stops on line 2 with a TypeError. The last line of the error says "
            "`can only concatenate str (not \"int\") to str`. Concatenate means join, str "
            "means text, and int means a whole number: Python joins text only to more text."},

{"id": "types-3", "round": "types", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
print(type("7"))
print(type(7))
'''),
 "wrong": [
    ["<class 'int'>\n<class 'int'>",
     "Quote marks make text, even around digits. `\"7\"` is a str, Python's word for text."],
    ["<class 'str'>\n<class 'str'>",
     "7 with no quote marks is a whole number. Python's name for that type is int."],
    ["7\n7", "`print(type(7))` prints the type of 7, not 7 itself."],
 ],
 "hints": ["One 7 has quote marks and one does not."],
 "explain": "A value's **type** is the kind of value it is. `type()` tells you the type. "
            "`\"7\"` has quote marks, so its type is str (text). `7` has none, so its type "
            "is int (a whole number)."},

{"id": "types-4", "round": "types", "kind": "blank", "stdin": "4",
 "ask": "Which fills the blank so the program prints exactly what is shown below it?",
 "code": c('''
coins = input("Coins: ")
coins = ___
print(coins + 1)
'''),
 "target": "Coins: 4\n5",
 "fills": [
    ["int(coins)", None],
    ["coins", "This stores the same text back. `coins` still holds `\"4\"`, so `coins + 1` "
              "is text plus a number."],
    ["str(coins)", "`str()` changes a value to text. `coins` is already text, so nothing "
                   "changes and `coins + 1` still fails."],
    ['"coins"', "With quote marks, this stores the word coins, not the value. `coins + 1` "
                "is then text plus a number."],
 ],
 "hints": ["The first line always gives text. Which fill changes the type to a whole number?"],
 "explain": "`int()` changes the type from text to a whole number: `int(\"4\")` gives 4. The "
            "answer is stored back under `coins`, so line 3 works out 4 + 1."},

{"id": "types-5", "round": "types", "kind": "type",
 "ask": "Type exactly what this program prints.",
 "code": c('''
name = "Ada"
laps = 3
print(f"{name} ran {laps} laps")
'''),
 "common": [
    ["{name} ran {laps} laps",
     "The `f` in front of the opening quote tells Python to put in the value of each name "
     "in curly brackets."],
    ["name ran laps laps",
     "The curly brackets tell Python to put in the value of the name, not the name itself."],
 ],
 "hints": ["Look at the letter in front of the opening quote mark. What does it tell "
           "Python to do with each name in curly brackets?"],
 "explain": "The `f` in front of the quote makes an **f-string**. Python puts the value of "
            "each name in curly brackets into the text: `{name}` becomes Ada and `{laps}` "
            "becomes 3."},

# ---------------------------------------------------------------- comparisons and if
{"id": "gates-1", "round": "gates", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
print(5 > 3)
print(5 == 3)
print(5 != 3)
'''),
 "wrong": [
    ["True\nFalse\nFalse", "`!=` means not equal. 5 is not equal to 3, so `5 != 3` is True."],
    ["Yes\nNo\nYes", "A comparison gives one of Python's two yes-or-no values: True or False."],
    ["5 > 3\n5 == 3\n5 != 3", "There are no quote marks, so Python works out each "
                              "comparison and prints the result."],
 ],
 "hints": ["`==` asks whether two values are equal. `!=` asks whether they are not equal."],
 "explain": "Each comparison gives True or False. 5 is greater than 3: True. 5 is not "
            "equal to 3, so `5 == 3` is False and `5 != 3` is True."},

{"id": "gates-2", "round": "gates", "kind": "output",
 "ask": "85 is more than 50 and more than 80. What does the program print?",
 "code": c('''
score = 85
if score > 50:
    print("pass")
elif score > 80:
    print("great")
else:
    print("try again")
'''),
 "wrong": [
    ["great", "`85 > 80` is True, but Python never gets to it. Python checks from the top "
              "and runs the lines under the first condition that is True: `score > 50`."],
    ["pass\ngreat", "With an `else` at the end, `if`, `elif` and `else` together run "
                    "exactly one set of lines. Once a condition is True, Python skips the rest."],
    ["try again", "The lines under `else` run only when every condition above is False. "
                  "Here the first condition is True."],
 ],
 "hints": ["Each comparison after `if` or `elif` is a condition: it is True or False. "
           "Python checks the conditions in order, from the top. How many of the three "
           "print lines can run?"],
 "explain": "The comparison after `if` or `elif` is a **condition**: it is True or False. "
            "Python checks the conditions from the top down. `score > 50` is True, so it "
            "prints pass and skips the `elif` and the `else`. To print great for 85, the "
            "`score > 80` check would have to come first."},

{"id": "gates-3", "round": "gates", "kind": "error",
 "ask": ERROR_ASK,
 "code": c('''
lives = 3
if lives = 0:
    print("game over")
'''),
 "wrong": [
    ["No error. It prints nothing",
     "One equals sign stores a value. An `if` needs a condition that is True or False, "
     "like `lives == 0`, with two equals signs. Python cannot read line 2 as it is."],
    ["NameError", "`lives` has a value from line 1. The problem is the punctuation on "
                  "line 2, not a name."],
    ["TypeError", "Python never gets as far as comparing values. It cannot read line 2, so "
                  "no line runs at all."],
 ],
 "hints": ["Count the equals signs on line 2. What does one equals sign do?"],
 "explain": "One equals sign stores a value. Two equals signs compare two values: "
            "`lives == 0` is True or False. An `if` needs a condition that is True or "
            "False, so Python cannot read line 2. It stops with a SyntaxError before "
            "running any line."},

{"id": "gates-4", "round": "gates", "kind": "blank",
 "ask": "A ride's rule: you must be at least 120 cm tall. Which fills the blank so a "
        "rider who is exactly 120 cm gets on?",
 "code": c('''
height = 120
if height ___ 120:
    print("you can ride")
else:
    print("too short")
'''),
 "target": "you can ride",
 "fills": [
    [">", "`120 > 120` is False, because 120 is not more than itself. The rider who is "
          "exactly 120 is turned away."],
    [">=", None],
    ["<", "`<` means less than. `120 < 120` is False, so this prints too short. It would "
          "also let shorter riders on."],
    ["=>", "Greater than or equal to is written `>=`, with the `>` first. Python cannot "
           "read `=>`, so it stops with a SyntaxError."],
 ],
 "hints": ["At least 120 includes 120 itself."],
 "explain": "`>=` means greater than or equal to. `120 >= 120` is True, so the rider gets "
            "on."},

# ---------------------------------------------------------------- and, or, while
{"id": "andor-1", "round": "andor", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
age = 10
height = 130
print(age >= 8 and height >= 140)
print(age >= 8 or height >= 140)
'''),
 "wrong": [
    ["True\nTrue", "`and` needs both sides to be True. `height >= 140` is False, so the "
                   "first line is False."],
    ["False\nFalse", "`or` needs at least one side to be True. `age >= 8` is True, so the "
                     "second line is True."],
    ["True\nFalse", "This has `and` and `or` the wrong way round. `and` needs both sides "
                    "True; `or` needs at least one."],
 ],
 "hints": ["Work out `age >= 8` and `height >= 140` first. Each one is True or False."],
 "explain": "`age >= 8` is True and `height >= 140` is False. With **and**, both sides must "
            "be True, so the first line is False. With **or**, one True side is enough, so "
            "the second line is True."},

{"id": "andor-2", "round": "andor", "kind": "output",
 "ask": "The door needs the key and at least 3 coins. What does the program print?",
 "code": c('''
has_key = True
coins = 2
if has_key and coins >= 3:
    print("door opens")
else:
    print("door stays shut")
'''),
 "wrong": [
    ["door opens", "`has_key` is True, but `coins >= 3` is `2 >= 3`, which is False. `and` "
                   "needs both sides True."],
    ["door opens\ndoor stays shut", "Python runs the lines under the `if` or the lines "
                                    "under the `else`, never both."],
    ["~It stops with an error",
     "True is already a yes-or-no value, so `has_key` can stand on its own in a condition."],
 ],
 "hints": ["Is `coins >= 3` True or False when coins is 2?"],
 "explain": "`has_key` is True. `coins >= 3` is `2 >= 3`, which is False. With `and`, one "
            "False side makes the condition False, so the lines under `else` run."},

{"id": "andor-3", "round": "andor", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
fuel = 3
while fuel > 0:
    print(fuel)
    fuel = fuel - 1
print("empty")
'''),
 "wrong": [
    ["3\n2\n1\n0\nempty", "When fuel reaches 0, the condition `0 > 0` is False, so the "
                          "loop stops before it prints 0."],
    ["2\n1\n0\nempty", "`print(fuel)` comes before `fuel = fuel - 1`, so the first pass "
                       "prints 3."],
    ["3\nempty", "`while` repeats its lines as long as its condition is True. It checks the "
                 "condition again before every pass."],
 ],
 "hints": ["One time through the indented lines is one pass. The condition is checked "
           "before every pass."],
 "explain": "The loop checks `fuel > 0` before every **pass** (one time through its "
            "indented lines). It prints 3, 2 and 1, lowering fuel by 1 each time. When fuel "
            "is 0, `0 > 0` is False, so the loop stops. `fuel > 0` is the loop's "
            "**stopping condition**: the loop keeps going while it is True and stops the "
            "first time it is False. The last line then prints empty."},

{"id": "andor-4", "round": "andor", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
steps = 0
while steps < 10:
    steps = steps + 3
print(steps)
'''),
 "wrong": [
    ["9", "When steps is 9, the condition `9 < 10` is still True, so the loop runs once "
          "more and adds 3."],
    ["10", "steps goes up by 3 each pass: 0, 3, 6, 9, 12. It is never exactly 10."],
    ["3\n6\n9\n12", "`print(steps)` is not indented, so it is not part of the loop. It "
                    "runs once, after the loop stops."],
 ],
 "hints": ["Write down steps after each pass: 3, 6, ... Check `steps < 10` each time."],
 "explain": "steps goes 0, 3, 6, 9, 12. The loop checks `steps < 10` before each pass. "
            "`9 < 10` is True, so it adds 3 once more. `12 < 10` is False, so the loop "
            "stops and the program prints 12."},

{"id": "andor-5", "round": "andor", "kind": "order",
 "ask": "Put the lines in order so the program prints the countdown shown.",
 "lines": [
    'count = 3',
    'while count > 0:',
    '    print(count)',
    '    count = count - 1',
    'print("lift off")',
 ],
 "target": "3\n2\n1\nlift off",
 "ways": 1,
 "hints": ["The while line checks count, so count needs a value before it.",
           "The countdown shows 3 first. Which indented line has to come first?"],
 "explain": "`count = 3` comes first, because the `while` line uses `count`. The two "
            "indented lines are the loop's body: print, then take away 1, so 3 is printed "
            "before it goes down. `print(\"lift off\")` is not indented, so it runs once, "
            "after the loop stops."},

# ---------------------------------------------------------------- for loops and range
{"id": "loops-1", "round": "loops", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
for i in range(3):
    print(i)
'''),
 "wrong": [
    ["1\n2\n3", "`range(3)` starts at 0, not 1."],
    ["0\n1\n2\n3", "`range(3)` stops before 3. It gives three numbers: 0, 1 and 2."],
    ["3", "The print line is indented, so it runs once for every number `range` gives."],
 ],
 "hints": ["`range(3)` gives three numbers. What is the first one?"],
 "explain": "`range(3)` gives the numbers 0, 1 and 2: three numbers, starting at 0 and "
            "stopping before 3. `i` is the **loop variable**: the name after `for`, which "
            "holds the next number from `range` on each pass. The print line runs once "
            "for each."},

{"id": "loops-2", "round": "loops", "kind": "type", "take": "last",
 "ask": "What is the last number this program prints? Type it.",
 "code": c('''
for n in range(1, 5):
    print(n)
'''),
 "common": [
    ["5", "`range(1, 5)` starts at 1 and stops before 5."],
    ["1", "The question asks for the last number printed. `n` takes several values, one "
          "each pass."],
 ],
 "hints": ["With two numbers, range starts at the first and stops before the second."],
 "explain": "`range(1, 5)` gives 1, 2, 3 and 4. It starts at the first number and stops "
            "before the second, so the last number printed is 4."},

{"id": "loops-3", "round": "loops", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
total = 0
for n in range(1, 4):
    total = total + n
print(total)
'''),
 "wrong": [
    ["10", "`range(1, 4)` gives 1, 2 and 3. It stops before 4, so 4 is not added."],
    ["3", "3 is the last value of `n`. `total` keeps everything added so far."],
    ["1\n3\n6", "`print(total)` is not indented, so it runs once, after the loop is "
                "finished."],
 ],
 "hints": ["Write down total after each pass. It starts at 0."],
 "explain": "`total` starts at 0. Each pass adds the loop variable `n`: 0 + 1 = 1, then "
            "1 + 2 = 3, then 3 + 3 = 6. A variable that keeps a running total like this is "
            "called an **accumulator**."},

{"id": "loops-4", "round": "loops", "kind": "order",
 "ask": "Put the lines in order so the program prints the total of 1, 2, 3, 4 and 5.",
 "lines": [
    'total = 0',
    'for n in range(1, 6):',
    '    total = total + n',
    'print(total)',
 ],
 "target": "15",
 "ways": 1,
 "hints": ["The line inside the loop uses total, so total needs a value first."],
 "explain": "`total = 0` goes first, because the loop adds to it. The indented line goes "
            "straight under the `for` line, so it runs on every pass. `print(total)` is not "
            "indented, so it goes last and runs once, after the loop."},

# ---------------------------------------------------------------- lists
{"id": "lists-1", "round": "lists", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
colours = ["red", "green", "blue"]
print(colours[1])
'''),
 "wrong": [
    ["red", "Index numbers start at 0. `colours[0]` is red, so `colours[1]` is the next one."],
    ["blue", "Count from 0: red is at index 0, green at 1, blue at 2."],
    ["~It stops with an IndexError", "Index 1 is inside the list. The list has index "
                                     "numbers 0, 1 and 2."],
 ],
 "hints": ["The first item in a list is at index 0."],
 "explain": "A **list** holds many values in order. Each item has an **index**, its "
            "position number, and the first index is 0. So red is at index 0, green at 1 "
            "and blue at 2."},

{"id": "lists-2", "round": "lists", "kind": "error",
 "ask": ERROR_ASK,
 "code": c('''
colours = ["red", "green", "blue"]
print(colours[3])
'''),
 "wrong": [
    ["No error. It prints blue", "blue is at index 2. The list has 3 items, at index 0, 1 "
                                 "and 2, so there is no index 3."],
    ["NameError", "`colours` was given a value on line 1, so Python knows the name. The "
                  "problem is the index."],
    ["TypeError", "A TypeError is about the wrong type of value. 3 is the right type for "
                  "an index, but no item is there."],
 ],
 "hints": ["The list has 3 items. Write down the index of each one."],
 "explain": "The list has 3 items, at index 0, 1 and 2. Asking for index 3 goes past the "
            "end, so Python stops with an IndexError."},

{"id": "lists-3", "round": "lists", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
scores = [4, 9, 2, 7]
print(len(scores))
print(max(scores))
print(sum(scores))
'''),
 "wrong": [
    ["3\n9\n22", "`len` counts the items, and there are 4. The last index is 3, but the "
                 "count is 4."],
    ["4\n7\n22", "`max` gives the biggest value in the list, not the last one."],
    ["4\n1\n22", "`max` gives the biggest value itself, 9, not its index number. 9 is at "
                 "index 1."],
 ],
 "hints": ["`len` counts, `max` finds the biggest, `sum` adds them all."],
 "explain": "`len` counts the items: 4. `max` gives the biggest value: 9. `sum` adds them "
            "all: 4 + 9 + 2 + 7 = 22."},

{"id": "lists-4", "round": "lists", "kind": "blank",
 "ask": "Which fills the blank so the program counts how many scores are 10 or more?",
 "code": c('''
scores = [12, 7, 10, 3, 15]
count = 0
for s in scores:
    if s >= 10:
        ___
print(count)
'''),
 "target": "3",
 "fills": [
    ["count = count + 1", None],
    ["count = s", "This stores the score itself, not a count. After the loop, `count` holds "
                  "the last score where `s >= 10` is True."],
    ["count = count + s", "This adds up the scores that are 10 or more, 12 + 10 + 15 = 37, "
                          "instead of counting them."],
    ["count + 1", "This works out `count + 1` but never stores it, so `count` stays 0."],
 ],
 "hints": ["The program should add 1 to count for each score where `s >= 10` is True."],
 "explain": "A **counter** is a variable the program adds 1 to. `count` starts at 0, and "
            "`count = count + 1` runs once for each score where `s >= 10` is True: 12, 10 "
            "and 15."},

{"id": "lists-5", "round": "lists", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
heights = [120, 145, 132, 150, 128]
tallest = heights[0]
for h in heights:
    if h > tallest:
        tallest = h
print(tallest)
'''),
 "wrong": [
    ["128", "128 is the last item, but `tallest` only changes when `h > tallest`. When h "
            "is 128, tallest is already 150."],
    ["120", "`tallest` starts at 120, then changes each time a taller height comes along."],
    ["145", "After 145, the loop keeps going. `150 > 145` is True, so `tallest` changes "
            "again."],
 ],
 "hints": ["Go through the list one height at a time. Does tallest change?"],
 "explain": "`tallest` starts as the first item, 120. The `if` line compares each height "
            "with `tallest`: 120 is not bigger than itself; 145 is, so tallest becomes 145; "
            "132 is not; 150 is, so tallest becomes 150; 128 is not. Keeping the biggest "
            "value seen so far in a variable like this is called **best so far**."},

# ---------------------------------------------------------------- functions
{"id": "functions-1", "round": "functions", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
def double(n):
    return n * 2

double(4)
print(double(5))
'''),
 "wrong": [
    ["8\n10", "`double(4)` returns 8, but line 4 does nothing with it: no print, and no "
              "name to store it under. So the 8 is lost."],
    ["8", "Nothing prints the 8 from `double(4)`. The print line calls `double(5)`."],
    ["None", "`double` has a `return` line, so it returns `n * 2`. None is what a function "
             "returns when it has no `return` line."],
 ],
 "hints": ["Which lines print something? A return value does not print by itself."],
 "explain": "A function returns a value to the line that called it. On line 4, the return "
            "value of `double(4)`, 8, is not printed or stored, so nothing appears. Line 5 "
            "prints the value `double(5)` returns: 10."},

{"id": "functions-2", "round": "functions", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
def greet(name):
    print(f"Hi {name}")

result = greet("Ada")
print(result)
'''),
 "wrong": [
    ["Hi Ada\nHi Ada", "`greet` prints, but it has no `return` line. A function with no "
                       "`return` line returns None, so `result` holds None."],
    ["None", "Calling `greet` runs its print line first, so Hi Ada appears before None."],
    ["Hi Ada", "The last line prints `result` too. `result` holds what `greet` returned."],
 ],
 "hints": ["greet has a print line but no return line. What does a function with no "
           "return line return?"],
 "explain": "Calling `greet(\"Ada\")` runs its print line, so Hi Ada appears. `greet` has no "
            "`return` line, so it returns **None**, Python's value for nothing. That is "
            "what `result` holds, and what line 5 prints."},

{"id": "functions-3", "round": "functions", "kind": "blank",
 "ask": "Which fills the blank so the program prints 12, and only 12?",
 "code": c('''
def area(width, height):
    ___

print(area(3, 4))
'''),
 "target": "12",
 "fills": [
    ["return width * height", None],
    ["print(width * height)", "This prints 12 inside the function, then the function "
                              "returns None, and the last line prints that too."],
    ["width * height", "This works out 12 and then does nothing with it. With no `return` "
                       "line, the function returns None."],
    ["return width + height", "`+` adds: 3 + 4 = 7. An area is width times height."],
 ],
 "hints": ["The last line prints whatever area returns."],
 "explain": "`return width * height` returns 12 to the line that called `area`, and that "
            "line prints it."},

{"id": "functions-4", "round": "functions", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
def label(name, score):
    return f"{name}: {score}"

print(label(7, "Mo"))
'''),
 "wrong": [
    ["Mo: 7", "Arguments fill the parameters in order. The first argument, 7, goes into "
              "`name`, and \"Mo\" goes into `score`."],
    ["~It stops with an error", "Python does not check what type of value a parameter "
                                "gets. The f-string puts the 7 into the text without a "
                                "problem."],
    ["name: score", "The `f` in front of the quote makes Python put in the values, not the "
                    "names."],
 ],
 "hints": ["The first value in the brackets of the call goes into the first name in the "
           "brackets of the def."],
 "explain": "The names in the `def` line are **parameters**. The values in the call are "
            "**arguments**, and they fill the parameters in order: `name` gets 7 and `score` "
            "gets \"Mo\". So the function returns the text `7: Mo`."},

{"id": "functions-5", "round": "functions", "kind": "order",
 "ask": "Put the lines in order so the program prints 12.",
 "lines": [
    'def triple(n):',
    '    return n * 3',
    'answer = triple(4)',
    'print(answer)',
 ],
 "target": "12",
 "ways": 1,
 "hints": ["The `def` has to run before any line that calls the function."],
 "explain": "The `def` and its indented `return` line go first, because Python runs the "
            "file from the top, and the `def` has to run before a line can call `triple`. "
            "Then `answer` stores what `triple(4)` returns, and the last line prints it."},

# ---------------------------------------------------------------- strings
{"id": "strings-1", "round": "strings", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
word = "python"
print(word[0])
print(word[1:4])
'''),
 "wrong": [
    ["y\nyth", "The first character of a string is at index 0, so `word[0]` is p."],
    ["p\nytho", "A slice stops before its second number. `word[1:4]` takes index 1, 2 and "
                "3: y, t, h."],
    ["p\npyth", "A slice starts at its first number. Index 1 is y, the second letter."],
 ],
 "hints": ["Write the index under each letter: p is 0, y is 1, and so on."],
 "explain": "A string is a row of characters, each with an index starting at 0: p is 0, y "
            "is 1, t is 2, h is 3. `word[1:4]` is a **slice**: it takes index 1 up to, but "
            "not including, index 4. So `word[0]` prints p, and `word[1:4]` prints yth."},

{"id": "strings-2", "round": "strings", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
name = "  ada  "
name.strip()
print(f"[{name}]")
'''),
 "wrong": [
    ["[ada]", "`strip` returns a new string without the spaces, but line 2 does not store "
              "it. `name` has not changed."],
    ["~It stops with an error", "A line that works out a value and does not store it is "
                                "allowed. Python makes the new string on line 2, then it "
                                "is lost."],
    ["ada", "The square brackets are inside the quote marks, so they print as text. And "
            "line 2 does not store what `strip` returns, so the spaces stay."],
 ],
 "hints": ["Line 2 has no `=`. Is the result stored anywhere?"],
 "explain": "`name.strip()` returns a new string with the spaces taken off both ends, but "
            "line 2 does not store it, so it is lost. `name` does not change. To keep the "
            "result, the line has to be `name = name.strip()`."},

{"id": "strings-3", "round": "strings", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
print("cat" in "concatenate")
print("Cat" in "concatenate")
'''),
 "wrong": [
    ["True\nTrue", "A capital C and a small c are different characters, and concatenate "
                   "has no capital C."],
    ["False\nFalse", "`in` checks whether the characters appear together, in order, "
                     "anywhere in the string. c, a, t appear together in the middle of "
                     "concatenate."],
    ["False\nTrue", "This is the wrong way round: the small cat is in concatenate; the "
                    "capital Cat is not."],
 ],
 "hints": ["Look for c, a, t side by side in concatenate."],
 "explain": "`in` checks whether one string is located in another, with its characters "
            "side by side and in the same order. concatenate has c, a, t side by side, so "
            "the first line is True. Python treats C and c as different, so the second "
            "line is False."},

{"id": "strings-4", "round": "strings", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
msg = "a banana"
msg = msg.replace("a", "o")
print(msg)
'''),
 "wrong": [
    ["o banana", "`replace` swaps every copy, not only the first one."],
    ["a banana", "Line 2 stores the result back under `msg`, so `msg` changes."],
    ["a bonono", "The first a is a copy of \"a\" too. `replace` swaps every one."],
 ],
 "hints": ["Line 2 has an `=`, so the result is stored."],
 "explain": "`replace(\"a\", \"o\")` returns a new string with every a swapped for o. Line 2 "
            "stores it back under `msg`, so the print shows the new string."},

{"id": "strings-5", "round": "strings", "kind": "order",
 "ask": "Put the lines in order so the program prints the word backwards.",
 "lines": [
    'word = "stressed"',
    'backwards = ""',
    'for letter in word:',
    '    backwards = letter + backwards',
    'print(backwards)',
 ],
 "target": "desserts",
 "ways": 2,
 "hints": ["The loop uses both word and backwards, so both need values before it."],
 "explain": "The first two lines can go in either order, because each one only stores a "
            "value. The loop comes after them, because it uses both names. Each pass puts "
            "the new letter in front of what is already in `backwards`, so the word comes "
            "out reversed."},

# ---------------------------------------------------------------- remainders
{"id": "remainders-1", "round": "remainders", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
print(17 % 5)
print(20 % 5)
print(3 % 5)
'''),
 "wrong": [
    ["3.4\n4.0\n0.6", "`%` does not give the answer to the division: 17 divided by 5 is "
                      "3.4. It gives the remainder: what is left over after taking out as "
                      "many fives as fit."],
    ["2\n0\n0", "5 does not fit into 3 at all, so all 3 is left over. `3 % 5` is 3."],
    ["2\n5\n3", "20 is exactly four fives, with nothing left over. `20 % 5` is 0."],
 ],
 "hints": ["`17 % 5` asks: after taking out as many fives as fit into 17, what is left?"],
 "explain": "`%` gives the **remainder**, what is left over after dividing. 17 is three "
            "fives with 2 left over. 20 is four fives with 0 left over. 3 is zero fives "
            "with 3 left over."},

{"id": "remainders-2", "round": "remainders", "kind": "output",
 "ask": "A clock uses the hours 0 to 23. It is 22:00. What hour does the program print "
        "for 5 hours later?",
 "code": c('''
hour = 22
hour = (hour + 5) % 24
print(hour)
'''),
 "wrong": [
    ["27", "`% 24` wraps the number around. 27 is one 24 with 3 left over."],
    ["1", "`% 24` gives what is left over, not how many 24s fit. One 24 fits into 27, "
          "with 3 left over."],
    ["2", "Count on from 22: 23, 0, 1, 2, 3. That is five steps, not four."],
 ],
 "hints": ["Work out the brackets first. Then find what is left over after taking out as "
           "many 24s as fit."],
 "explain": "Brackets go first: 22 + 5 = 27. Then `% 24` gives the remainder after taking "
            "out 24: 27 is one 24 with 3 left over. So the clock goes past midnight to 3."},

{"id": "remainders-3", "round": "remainders", "kind": "blank",
 "ask": "Which fills the blank so the program prints only the even numbers: 2, 4 and 6?",
 "code": c('''
for n in range(1, 7):
    if n % 2 ___ 0:
        print(n)
'''),
 "target": "2\n4\n6",
 "fills": [
    ["==", None],
    ["!=", "`n % 2 != 0` is True for the odd numbers, so this prints 1, 3 and 5."],
    ["<", "A remainder is never less than 0, so this prints nothing."],
    ["=", "One equals sign stores a value. It cannot go in a condition, so Python stops "
          "with a SyntaxError."],
 ],
 "hints": ["What is the remainder when an even number is divided by 2?"],
 "explain": "An even number divided by 2 leaves nothing over, so `n % 2` is 0. The check "
            "`n % 2 == 0` is True for 2, 4 and 6."},

{"id": "remainders-4", "round": "remainders", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
colours = ["red", "green", "blue"]
for i in range(5):
    print(colours[i % 3])
'''),
 "wrong": [
    ["~It stops with an IndexError", "`i % 3` is always 0, 1 or 2, so the index never goes "
                                     "past the end of the list."],
    ["red\ngreen\nblue", "`range(5)` gives five numbers, 0 to 4, so the loop makes five "
                         "passes."],
    ["green\nblue\nred\ngreen\nblue", "On the first pass i is 0, and `0 % 3` is 0, so the "
                                      "first colour is red."],
 ],
 "hints": ["Work out `i % 3` for i = 0, 1, 2, 3 and 4."],
 "explain": "i goes 0, 1, 2, 3, 4. `i % 3` gives 0, 1, 2, 0, 1, so the colours go round: "
            "red, green, blue, then back to red and green."},

# ---------------------------------------------------------------- dictionaries
{"id": "dicts-1", "round": "dicts", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
ages = {"Ada": 11, "Mo": 12}
ages["Mo"] = 13
ages["Zed"] = 10
print(ages["Mo"])
print(len(ages))
'''),
 "wrong": [
    ["12\n3", "Line 2 changes the value stored under the key \"Mo\" to 13."],
    ["13\n2", "Storing a value under a key that is not there yet adds a new pair. \"Zed\" "
              "is added on line 3."],
    ["13\n4", "Line 2 changes the value under \"Mo\". It does not add a second \"Mo\". A "
              "dictionary holds each key once."],
 ],
 "hints": ["Line 2 uses a key that is already there. Line 3 uses a key that is not."],
 "explain": "A **dictionary** pairs each **key** with a value. Line 2 changes the value "
            "under \"Mo\" to 13. Line 3 adds a new pair, because \"Zed\" was not a key yet. "
            "That makes 3 pairs, so `len` gives 3."},

{"id": "dicts-2", "round": "dicts", "kind": "error",
 "ask": ERROR_ASK,
 "code": c('''
ages = {"Ada": 11, "Mo": 12}
print(ages["ada"])
'''),
 "wrong": [
    ["No error. It prints 11", "Keys must match exactly. \"ada\" with a small a is not the "
                               "same key as \"Ada\"."],
    ["IndexError", "IndexError is for an index number past the end of a list or a string. "
                   "A dictionary looks things up by key, and a missing key gives a "
                   "different error."],
    ["NameError", "The name `ages` is known. It is the key \"ada\" that is missing."],
 ],
 "hints": ["Compare the key on line 2 with the keys on line 1, letter by letter."],
 "explain": "The dictionary's keys are \"Ada\" and \"Mo\". \"ada\" with a small a is a "
            "different string, so Python stops with a KeyError."},

{"id": "dicts-3", "round": "dicts", "kind": "output",
 "ask": "What does this program print?",
 "code": c('''
stock = {"apples": 5, "pears": 0}
print("pears" in stock)
print(5 in stock)
'''),
 "wrong": [
    ["False\nFalse", "\"pears\" is a key, even though its value is 0. `in` checks the keys."],
    ["True\nTrue", "`in` checks the keys, not the values. 5 is a value, not a key."],
    ["False\nTrue", "This is the wrong way round: \"pears\" is a key; 5 is only a value."],
 ],
 "hints": ["On a dictionary, `in` looks at the keys only."],
 "explain": "On a dictionary, `in` checks the keys. \"pears\" is a key, so the first line "
            "is True. 5 is a value, not a key, so the second line is False."},

{"id": "dicts-4", "round": "dicts", "kind": "type",
 "ask": "Type exactly what this program prints.",
 "code": c('''
tally = {}
for letter in "banana":
    if letter in tally:
        tally[letter] = tally[letter] + 1
    else:
        tally[letter] = 1
print(tally["a"])
'''),
 "common": [
    ["1", "The line under `else` runs only the first time a letter is seen. After that, "
          "the line under `if` adds 1 each time."],
    ["6", "`tally[\"a\"]` counts only the letter a. banana has 6 letters, but not all of "
          "them are a."],
 ],
 "hints": ["The first a stores 1. What happens the next time an a comes along?"],
 "explain": "The first time a letter comes along, it is not a key yet, so the line under "
            "`else` stores 1. Each time after, the line under `if` adds 1. banana has three "
            "a's, so `tally[\"a\"]` is 3. Counting like this is called a **tally**."},

# ---------------------------------------------------------------- reading errors
{"id": "errors-1", "round": "errors", "kind": "line",
 "ask": "This program stops with an error. Which line does the error message name?",
 "code": c('''
x = 5
y = "3"
total = x + y
print(total)
'''),
 "wrong": [
    ["Line 1", "`x = 5` is fine: it stores a whole number."],
    ["Line 2", "Storing text under a name is allowed. The problem shows up when `y` is "
               "used in arithmetic."],
    ["Line 4", "Python never gets to line 4. It stops at the first line it cannot run."],
 ],
 "hints": ["Which line tries to add a number and text?"],
 "explain": "Line 3 tries a number plus text: `5 + \"3\"`. Python stops there with a "
            "TypeError, and the error message names line 3."},

{"id": "errors-2", "round": "errors", "kind": "line",
 "ask": "The mistake is a spelling mistake on line 1. Which line does the error message "
        "name?",
 "code": c('''
totl = 0
for n in [4, 5, 6]:
    total = total + n
print(total)
'''),
 "wrong": [
    ["Line 1", "Line 1 is allowed in Python: it stores 0 under the name `totl`. Python has "
               "no way to know you meant `total`."],
    ["Line 2", "The `for` line is fine. The trouble starts inside the loop, the first time "
               "`total` is used."],
    ["Line 4", "Python never gets to line 4. It stops on the first pass of the loop."],
 ],
 "hints": ["Line 1 runs without a problem. Which is the first line that asks for the "
           "value of `total`?"],
 "explain": "Python names the line where it could not go on, which is not always the line "
            "with the mistake. Line 3 asks for the value of `total` before anything was "
            "stored under that name, so Python stops there with a NameError."},

{"id": "errors-3", "round": "errors", "kind": "error",
 "ask": ERROR_ASK,
 "code": c('''
for i in range(3):
print(i)
'''),
 "wrong": [
    ["No error. It prints 0, 1 and 2", "Python uses indentation to know which lines belong "
                                       "to the loop. A line ending in a colon must have an "
                                       "indented line under it, so Python stops before "
                                       "running any line."],
    ["NameError", "`i` is the loop variable, so it is a known name. The problem is the "
                  "missing indentation."],
    ["TypeError", "No values are being combined here. Python stops before running any line."],
 ],
 "hints": ["Look at the start of line 2."],
 "explain": "A line ending in a colon must have at least one indented line under it. Here "
            "`print(i)` is not indented, so Python stops with an IndentationError."},

{"id": "errors-4", "round": "errors", "kind": "output",
 "ask": "This program is meant to print the total of the list, 10. It has a bug but no "
        "error message. What does it print?",
 "code": c('''
nums = [1, 2, 3, 4]
total = 0
for n in nums:
    total = n
print(total)
'''),
 "wrong": [
    ["10", "`total = n` replaces `total` with `n` on each pass. Nothing is added."],
    ["0", "`total` changes on every pass of the loop, so it does not stay 0."],
    ["1\n2\n3\n4", "`print(total)` is not indented, so it runs once, after the loop."],
 ],
 "hints": ["Write down total after each pass."],
 "explain": "`total = n` stores the loop variable, replacing what was there. After the last "
            "pass, `total` holds 4. A bug like this gives a wrong answer with no error "
            "message, so the way to catch it is to know what the answer should be before "
            "you run it."},

{"id": "errors-5", "round": "errors", "kind": "blank",
 "ask": "This program should print the total of the list, 10. Which fills the blank so "
        "it does?",
 "code": c('''
nums = [1, 2, 3, 4]
total = 0
for n in nums:
    ___
print(total)
'''),
 "target": "10",
 "fills": [
    ["total = total + n", None],
    ["total = total + nums", "`nums` is the list itself, not one number. Python cannot add a "
                             "list to a number, so it stops with a TypeError. The loop "
                             "variable `n` holds one number on each pass."],
    ["total + n", "This works out a sum but never stores it, so `total` stays 0."],
    ["total = total + 1", "This adds 1 on each pass, so it counts the items instead of "
                          "adding them up."],
 ],
 "hints": ["The new total is the old total plus the loop variable."],
 "explain": "`total = total + n` takes the total so far, adds the loop variable, and stores "
            "the answer back in `total`."},

{"id": "errors-6", "round": "errors", "kind": "error",
 "ask": ERROR_ASK,
 "code": c('''
print(double(4))

def double(n):
    return n * 2
'''),
 "wrong": [
    ["No error. It prints 8", "Python runs the lines from top to bottom. When line 1 runs, "
                              "the `def` lines below it have not run yet, so there is no "
                              "function called `double`."],
    ["SyntaxError", "Every line is written correctly. The problem is the order of the lines."],
    ["TypeError", "Python never gets as far as multiplying. It stops because there is no "
                  "function called `double` yet."],
 ],
 "hints": ["Python runs the file from the top. Which lines have run when line 1 runs?"],
 "explain": "Python runs a file from the top. Line 1 calls `double` before the `def` that "
            "makes it has run, so Python stops with a NameError. A `def` has to come before "
            "any line that calls its function. Putting every `def` at the top of the file "
            "makes sure of that."},
]
