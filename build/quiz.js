(function () {
  "use strict";

  var D = JSON.parse(document.getElementById("quiz-data").textContent);
  var ROUNDS = D.rounds;
  var QS = D.questions;
  var ROUND = {};
  var QIDX = {};
  ROUNDS.forEach(function (r, i) { r.n = i + 1; ROUND[r.id] = r; });
  QS.forEach(function (q, i) { QIDX[q.id] = i; });
  var LETTERS = "ABCDEF";
  var app = document.getElementById("app");

  // Choices on the start screen. Nothing is saved: closing the page starts fresh.
  var pick = { rounds: new Set(ROUNDS.map(function (r) { return r.id; })), mode: "solo", shuffle: false };
  (function readLink() {
    var p = new URLSearchParams(location.search);
    var want = (p.get("rounds") || "").split(",").filter(function (id) { return ROUND[id]; });
    if (want.length) pick.rounds = new Set(want);
    if (p.get("mode") === "class") pick.mode = "class";
    if (p.get("shuffle") === "1") pick.shuffle = true;
  })();

  var S = null; // the quiz in progress

  // ---------------------------------------------------------------- helpers
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function outHTML(s) {
    return s === "" ? '<span class="empty">(nothing: the program prints no lines)</span>' : esc(s);
  }
  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function range(n) { var a = []; for (var i = 0; i < n; i++) a.push(i); return a; }
  function current() { return QS[QIDX[S.queue[S.pos]]]; }
  function plural(n, word) { return n + " " + word + (n === 1 ? "" : "s"); }
  function toTop() {
    var y = app.getBoundingClientRect().top + window.scrollY - 8;
    if (window.scrollY > y || S) window.scrollTo(0, Math.max(0, y));
  }
  function focusEl(el) { if (el) el.focus({ preventScroll: true }); }

  // On a narrow screen, make the type in a code box or line tile smaller until its
  // longest line fits, down to 11px. A box that still would not fit keeps its size
  // and scrolls sideways inside itself instead (long error messages do this).
  function fitCode() {
    app.querySelectorAll("pre, .tile").forEach(function (el) {
      el.style.fontSize = "";
      if (el.scrollWidth <= el.clientWidth + 1) return;
      var cs = getComputedStyle(el);
      var pad = parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight);
      var size = parseFloat(cs.fontSize);
      var want = size * (el.clientWidth - pad) / (el.scrollWidth - pad);
      want = Math.floor(want * 2) / 2;
      if (want < 11) return;
      el.style.fontSize = want + "px";
      while (el.scrollWidth > el.clientWidth + 1 && want > 11) { want -= 0.5; el.style.fontSize = want + "px"; }
    });
    // every line tile in a question shares the smallest size, so the lines line up
    var tiles = app.querySelectorAll(".tile"), min = Infinity;
    tiles.forEach(function (t) { min = Math.min(min, parseFloat(getComputedStyle(t).fontSize)); });
    tiles.forEach(function (t) { if (parseFloat(getComputedStyle(t).fontSize) !== min) t.style.fontSize = min + "px"; });
  }
  function paint(html) { app.innerHTML = html; fitCode(); }
  var resizeTimer = null;
  window.addEventListener("resize", function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(fitCode, 150); });

  function copyText(text, btn) {
    var label = btn.getAttribute("data-label") || btn.textContent;
    btn.setAttribute("data-label", label);
    function done() { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = label; }, 1500); }
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", "");
      ta.style.position = "fixed"; ta.style.top = "0"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); done(); } catch (e) { btn.textContent = "Select the code and copy it"; }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, fallback);
    else fallback();
  }

  // ---------------------------------------------------------------- start screen
  function selectedCount() {
    return QS.filter(function (q) { return pick.rounds.has(q.round); }).length;
  }

  function renderStart() {
    S = null;
    document.body.classList.remove("classmode");
    var rounds = ROUNDS.map(function (r) {
      return '<label class="round"><input type="checkbox" value="' + r.id + '"' +
        (pick.rounds.has(r.id) ? " checked" : "") + '>' +
        '<span class="n">' + r.n + '</span><span><b>' + esc(r.title) + '</b>' +
        '<span class="about">' + esc(r.about) + '</span>' +
        '<span class="count">' + plural(r.count, "question") + '</span></span></label>';
    }).join("");
    paint(
      '<section class="intro"><h2>How it works</h2><ol>' +
      '<li>Each question shows a short Python program. Work out what it will do before you look at the answers.</li>' +
      '<li>Pick an answer. Then press <b>Sure</b> or <b>Not sure</b> to check it.</li>' +
      '<li>Every wrong answer has its own reason, and every question shows what Python really printed.</li>' +
      '<li>At the end, look first at the questions you were sure about but got wrong.</li>' +
      '</ol></section>' +
      '<section class="pick"><h2>Choose the rounds</h2>' +
      '<div class="row"><button class="small" data-act="all">Select all</button>' +
      '<button class="small" data-act="none">Clear</button></div>' +
      '<div class="rounds">' + rounds + '</div></section>' +
      '<section class="pick"><h2>Who is taking it?</h2><div class="modes">' +
      '<label class="mode"><input type="radio" name="mode" value="solo"' + (pick.mode === "solo" ? " checked" : "") + '>' +
      '<span><b>Me, on my own</b><span>You get a score at the end, and a list of the questions to look at again.</span></span></label>' +
      '<label class="mode"><input type="radio" name="mode" value="class"' + (pick.mode === "class" ? " checked" : "") + '>' +
      '<span><b>A class, on a projector</b><span>Bigger text and no score. Everyone picks an answer, then the teacher shows the right one and the reason for every wrong one.</span></span></label>' +
      '</div><label class="check"><input type="checkbox" id="shuffle"' + (pick.shuffle ? " checked" : "") + '> Mix up the order of the questions</label>' +
      '</section>' +
      '<div class="row"><button class="btn big" data-act="start" id="startbtn">Start</button>' +
      '<button class="btn quiet" data-act="quick">Quick quiz: one question from each round</button></div>' +
      '<p class="note" id="startnote"></p>');
    updateStart();
  }

  function updateStart() {
    var n = selectedCount();
    var btn = document.getElementById("startbtn");
    if (!btn) return;
    btn.textContent = n ? "Start: " + plural(n, "question") : "Pick at least one round";
    btn.disabled = n === 0;
    var k = ROUNDS.filter(function (r) { return pick.rounds.has(r.id); }).length;
    document.getElementById("startnote").textContent = n
      ? "Allow about a minute a question. The quick quiz is " + (k === 1 ? "1 question from the chosen round." : k + " questions, one from each chosen round.")
      : "";
  }

  function begin(qids, mode) {
    S = { mode: mode, queue: qids, pos: 0, st: {}, log: [] };
    document.body.classList.toggle("classmode", mode === "class");
    renderQ();
  }

  // ---------------------------------------------------------------- one question
  function stateFor(q) {
    if (S.st[q.id]) return S.st[q.id];
    var st = { picked: null, checked: false, ok: null, hints: 0, sure: null, typed: "", tried: null };
    if (q.opts) st.order = q.fixed ? range(q.opts.length) : shuffle(range(q.opts.length));
    if (q.kind === "order") {
      var pool, tries = 0;
      do { pool = shuffle(range(q.lines.length)); tries++; }
      while (q.okKeys.indexOf(pool.join(",")) >= 0 && tries < 50);
      st.pool = pool; st.prog = [];
    }
    S.st[q.id] = st;
    return st;
  }

  function codeHead(copy) {
    return '<div class="codehead"><span class="fname">' + esc(D.file) + '</span>' +
      (copy ? '<button class="small" data-act="copy">Copy the code</button>' : '') + '</div>';
  }

  function bodyHTML(o) {
    if (o.s === "out") return "<pre>" + (o.h === "" ? '<span class="empty">(prints nothing)</span>' : o.h) + "</pre>";
    if (o.s === "code") return "<pre>" + o.h + "</pre>";
    if (o.s === "err") return '<span class="err">' + o.h + "</span>";
    return "<span>" + o.h + "</span>";
  }

  function letterOf(st, oi) { return LETTERS[st.order.indexOf(oi)]; }
  function rightIndex(q) { for (var i = 0; i < q.opts.length; i++) if (q.opts[i].ok) return i; return -1; }

  function optsHTML(q, st) {
    return '<div class="opts" role="radiogroup" aria-label="Answers">' + st.order.map(function (oi, pos) {
      var o = q.opts[oi], checked = st.picked === oi, cls = "opt", tag = "";
      if (st.checked) {
        if (o.ok) { cls += " right"; tag = "Right answer"; }
        else if (checked) { cls += " wrong"; tag = S.mode === "class" ? "Picked" : "Your answer"; }
        else cls += " dim";
      }
      return '<button type="button" class="' + cls + '" role="radio" aria-checked="' + checked + '" data-act="pick" data-i="' + oi + '"' +
        (st.checked ? " disabled" : "") + '><span class="letter" aria-hidden="true">' + LETTERS[pos] + '</span>' +
        '<span class="body">' + bodyHTML(o) + '</span>' + (tag ? '<span class="tag">' + tag + '</span>' : "") + '</button>';
    }).join("") + "</div>";
  }

  function wellsHTML(q, st) {
    var dis = st.checked ? " disabled" : "";
    var pool = st.pool.length
      ? "<ol>" + st.pool.map(function (i) {
          return '<li><button type="button" class="tile" data-act="add" data-i="' + i + '"' + dis + '>' + q.lines[i] + '</button></li>';
        }).join("") + "</ol>"
      : '<p class="placeholder">Every line is in your program.</p>';
    var prog = st.prog.length
      ? "<ol>" + st.prog.map(function (i, k) {
          return '<li><span class="ln">' + (k + 1) + '</span><button type="button" class="tile" data-act="remove" data-i="' + i + '"' + dis + '>' + q.lines[i] + '</button></li>';
        }).join("") + "</ol>"
      : '<p class="placeholder">Tap the lines in the order they should run. They appear here, top to bottom.</p>';
    return '<div><p class="label">Lines to use</p><div class="well">' + pool + '</div></div>' +
      '<div><p class="label teal">Your program</p><div class="well prog">' + prog + '</div>' +
      (!st.checked && st.prog.length ? '<div class="row" style="margin:10px 0 0"><button type="button" class="small" data-act="reset">Put every line back</button></div>' : "") +
      "</div>";
  }

  function hintsHTML(q, st) {
    var h = '<div class="hints">';
    for (var i = 0; i < st.hints; i++) {
      h += '<div class="hintbox"><p class="label">Hint' + (q.hints.length > 1 ? " " + (i + 1) : "") + '</p><p>' + q.hints[i] + '</p></div>';
    }
    if (!st.checked && st.hints < q.hints.length) {
      h += '<button type="button" class="btn hint" data-act="hint">' + (st.hints ? "Show the next hint" : "Show a hint") + '</button>';
    }
    return h + "</div>";
  }

  function ready(q, st) {
    if (q.opts) return st.picked !== null;
    if (q.kind === "order") return st.pool.length === 0;
    if (q.kind === "type") return st.typed.trim() !== "";
    return false;
  }

  function actionsHTML(q, st) {
    if (st.checked) return "";
    var dis = ready(q, st) ? "" : " disabled";
    if (S.mode === "class") {
      return '<div class="row">' +
        (q.kind === "order" ? '<button type="button" class="btn quiet" data-act="try"' + dis + '>Check this order</button>' : "") +
        '<button type="button" class="btn" data-act="reveal">Show the answer</button></div>' +
        '<div id="trybox">' + (st.tried !== null ? triedHTML(q, st) : "") + '</div>';
    }
    return '<div class="sure"><p>How sure are you?</p><div class="row">' +
      '<button type="button" class="btn" data-act="check" data-sure="1"' + dis + '>Sure: check it</button>' +
      '<button type="button" class="btn quiet" data-act="check" data-sure="0"' + dis + '>Not sure: check it</button></div></div>';
  }

  function renderQ() {
    var q = current(), r = ROUND[q.round], st = stateFor(q);
    var n = S.pos + 1, N = S.queue.length;
    var h = '<div class="qmeta"><span class="where">Round ' + r.n + ' · ' + esc(r.title) + '</span>' +
      '<span class="row" style="margin:0"><span class="where">Question ' + n + ' of ' + N + '</span>' +
      '<button type="button" class="small" data-act="end">End the quiz</button></span></div>' +
      '<div class="progress" role="progressbar" aria-label="Questions done" aria-valuemin="0" aria-valuemax="' + N + '" aria-valuenow="' + S.pos + '">' +
      '<i style="width:' + (S.pos / N * 100).toFixed(1) + '%"></i></div>' +
      '<section class="q"><h2 class="ask" tabindex="-1">' + q.ask + '</h2>';
    if (q.stdin !== null && q.stdin !== undefined) {
      h += '<p class="stdin">When the program asks, the person types <kbd>' + esc(q.stdin) + '</kbd> and presses Enter.</p>';
    }
    if (q.kind === "order") {
      h += '<p class="label">It should print exactly this</p><pre class="target">' + outHTML(q.target) + '</pre>' +
        '<p class="note">The spaces at the start of each line are already right. Only the order is up to you.</p>' +
        '<div class="parsons" id="parsons">' + wellsHTML(q, st) + '</div>';
    } else {
      h += codeHead(q.kind !== "blank") + '<pre class="num">' + q.code + "</pre>";
      if (q.kind === "blank") {
        h += '<p class="label">It should print exactly this</p><pre class="target">' + outHTML(q.target) + '</pre>';
      }
      if (q.opts) h += optsHTML(q, st);
      if (q.kind === "type") {
        h += '<label class="label" for="typed">Your answer</label><input class="typed" id="typed" type="text" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" value="' +
          esc(st.typed) + '"' + (st.checked ? " disabled" : "") + '>';
      }
    }
    h += hintsHTML(q, st) + '<div id="actions">' + actionsHTML(q, st) + '</div>';
    if (st.checked) h += feedbackHTML(q, st);
    h += "</section>";
    if (!st.checked) {
      h += '<p class="keys">Keys: ' + (q.opts ? "<kbd>A</kbd> to <kbd>" + LETTERS[q.opts.length - 1] + "</kbd> pick an answer · " : "") +
        (S.mode === "class" ? "<kbd>R</kbd> show the answer" : "<kbd>S</kbd> sure · <kbd>N</kbd> not sure") +
        (q.hints.length ? " · <kbd>H</kbd> hint" : "") + "</p>";
    } else {
      h += '<p class="keys">Keys: <kbd>Enter</kbd> ' + (S.pos + 1 < S.queue.length ? "next question" : "finish") + "</p>";
    }
    paint(h);
  }

  function refreshActions() {
    var q = current(), st = stateFor(q);
    var box = document.getElementById("actions");
    if (!box) return;
    var dis = !ready(q, st);
    box.querySelectorAll('[data-act="check"],[data-act="try"]').forEach(function (b) { b.disabled = dis; });
  }

  // ---------------------------------------------------------------- feedback
  function realHTML(q) {
    var h = "";
    if (q.kind === "blank" || q.kind === "order") {
      h += '<p class="label teal">The finished program</p>' + codeHead(true) + '<pre class="num">' + q.finished + "</pre>";
    }
    return h + '<p class="label green">What Python really prints</p><pre class="out">' + outHTML(q.real) + "</pre>";
  }

  function yourProgram(q, st) {
    return st.prog.map(function (i) { return '<span class="cl">' + q.lines[i] + "</span>"; }).join("\n");
  }

  function triedHTML(q, st) {
    var ok = q.okKeys.indexOf(st.tried) >= 0;
    return '<div class="why' + (ok ? " good" : "") + '"><p class="label ' + (ok ? "green" : "clay") + '">This order prints</p>' +
      '<pre class="out">' + outHTML(q.outs[q.perms[st.tried]]) + '</pre><p>' +
      (ok ? "That matches what it should print." : "That does not match what it should print.") + "</p></div>";
  }

  function typedWhy(q, typed) {
    var t = typed.trim();
    for (var i = 0; i < q.common.length; i++) if (q.common[i].t === t) return q.common[i].why;
    var bare = t.replace(/^["']|["']$/g, "");
    if (bare === q.answer) return "Those are the right characters, but print does not show quote marks around text.";
    if (t.toLowerCase() === q.answer.toLowerCase()) return "Check the capital and small letters. Python prints them exactly as they are.";
    if (t.replace(/\s+/g, "") === q.answer.replace(/\s+/g, "")) return "Check the spaces. Python prints every space exactly.";
    return "Compare what you typed with what Python really prints, below, one character at a time.";
  }

  function feedbackHTML(q, st) {
    var h = '<div class="fb">';
    var rl, i;
    if (S.mode === "class") {
      if (q.opts) {
        rl = letterOf(st, rightIndex(q));
        h += '<div class="verdict plain" tabindex="-1">The answer is ' + rl + '.</div>';
      } else if (q.kind === "type") {
        h += '<div class="verdict plain" tabindex="-1">The answer</div><pre class="out">' + outHTML(q.answer) + '</pre>';
      } else {
        h += '<div class="verdict plain" tabindex="-1">' + (q.okKeys.length > 1 ? "One order that works" : "The order that works") + '</div>';
      }
      h += '<div class="why good"><p class="label green">Why</p><p>' + q.explain + '</p></div>' + realHTML(q);
      if (q.opts) {
        h += "<h3>The other answers</h3>";
        st.order.forEach(function (oi) {
          var o = q.opts[oi];
          if (o.ok) return;
          h += '<div class="why"><p class="label clay">Why not ' + letterOf(st, oi) + '</p><p>' + o.why + '</p>' +
            (o.out !== null ? '<p class="label clay">With this, the program prints</p><pre class="out">' + outHTML(o.out) + '</pre>' : "") + '</div>';
        });
      } else if (q.kind === "type" && q.common.length) {
        h += "<h3>Answers people often give</h3>";
        q.common.forEach(function (c) {
          h += '<div class="why"><p class="label clay">' + esc(c.t) + '</p><p>' + c.why + '</p></div>';
        });
      }
    } else {
      h += '<div class="verdict ' + (st.ok ? "good" : "bad") + '" tabindex="-1">' + (st.ok ? "Right." : "Not this time.") + '</div>';
      if (!st.ok) {
        if (q.opts) {
          var o = q.opts[st.picked];
          h += '<div class="why"><p class="label clay">Why not ' + letterOf(st, st.picked) + '</p><p>' + o.why + '</p>' +
            (o.out !== null ? '<p class="label clay">With this, the program prints</p><pre class="out">' + outHTML(o.out) + '</pre>' : "") + '</div>';
        } else if (q.kind === "order") {
          h += '<div class="why"><p class="label clay">Your order</p><pre class="num">' + yourProgram(q, st) + '</pre>' +
            '<p class="label clay">Your order prints</p><pre class="out">' + outHTML(q.outs[q.perms[st.prog.join(",")]]) + '</pre></div>';
        } else if (q.kind === "type") {
          h += '<div class="why"><p class="label clay">You typed</p><pre>' + esc(st.typed.trim()) + '</pre><p>' + typedWhy(q, st.typed) + '</p></div>';
        }
      }
      if (q.opts) {
        h += '<div class="why good"><p class="label green">The answer is ' + letterOf(st, rightIndex(q)) + '</p><p>' + q.explain + '</p></div>';
      } else if (q.kind === "type") {
        h += '<div class="why good"><p class="label green">The answer</p><pre class="out">' + outHTML(q.answer) + '</pre><p>' + q.explain + '</p></div>';
      } else {
        h += '<div class="why good"><p class="label green">Why</p><p>' + q.explain + '</p></div>';
      }
      h += realHTML(q);
    }
    var last = S.pos + 1 >= S.queue.length;
    h += '<div class="row" style="margin-top:8px"><button type="button" class="btn big" data-act="next">' +
      (last ? (S.mode === "class" ? "Finish" : "See my results") : "Next question") + '</button></div>';
    return h + "</div>";
  }

  // ---------------------------------------------------------------- actions
  function pickOption(oi) {
    var q = current(), st = stateFor(q);
    if (st.checked) return;
    st.picked = oi;
    app.querySelectorAll(".opt").forEach(function (b) {
      b.setAttribute("aria-checked", String(Number(b.getAttribute("data-i")) === oi));
    });
    refreshActions();
  }

  function check(sure) {
    var q = current(), st = stateFor(q);
    if (st.checked || !ready(q, st)) return;
    var ans;
    if (q.opts) { st.ok = q.opts[st.picked].ok; ans = q.opts[st.picked].t; }
    else if (q.kind === "order") {
      st.ok = q.okKeys.indexOf(st.prog.join(",")) >= 0;
      ans = st.prog.map(function (i) { return q.plain[i]; }).join("\n");
    } else { st.ok = st.typed.trim() === q.answer; ans = st.typed.trim(); }
    st.checked = true; st.sure = sure;
    S.log.push({ id: q.id, ok: st.ok, sure: sure, hints: st.hints, ans: ans });
    renderQ();
    focusEl(app.querySelector(".verdict"));
  }

  function reveal() {
    var q = current(), st = stateFor(q);
    if (st.checked) return;
    st.checked = true;
    S.log.push({ id: q.id, shown: true });
    renderQ();
    focusEl(app.querySelector(".verdict"));
  }

  function next() {
    S.pos++;
    if (S.pos >= S.queue.length) { renderResults(); return; }
    renderQ();
    toTop();
    focusEl(app.querySelector(".ask"));
  }

  function moveTile(act, i) {
    var q = current(), st = stateFor(q);
    if (st.checked) return;
    if (act === "add") { st.pool.splice(st.pool.indexOf(i), 1); st.prog.push(i); }
    else if (act === "remove") { st.prog.splice(st.prog.indexOf(i), 1); st.pool.push(i); }
    else { st.pool = st.pool.concat(st.prog); st.prog = []; }
    st.tried = null;
    document.getElementById("parsons").innerHTML = wellsHTML(q, st);
    var tb = document.getElementById("trybox"); if (tb) tb.innerHTML = "";
    fitCode();
    refreshActions();
    var nextTile = app.querySelector('#parsons [data-act="' + (act === "remove" ? "remove" : "add") + '"]') ||
      app.querySelector('#parsons .tile') || app.querySelector('[data-act="check"],[data-act="reveal"]');
    focusEl(nextTile);
  }

  // ---------------------------------------------------------------- results
  function reviewItem(e) {
    var q = QS[QIDX[e.id]], r = ROUND[q.round];
    var h = '<details class="rev"><summary><span class="meta">Round ' + r.n + '</span>' + q.ask +
      '<span class="peek">' + esc(q.peek) + '</span></summary><div class="in">';
    if (q.kind === "order") {
      h += '<p class="label clay">' + (e.ok ? "Your order (right)" : "Your order") + '</p><pre>' + esc(e.ans) + "</pre>" +
        '<p class="label green">' + (q.okKeys.length > 1 ? "One order that works" : "The order that works") + '</p><pre class="num">' + q.finished + "</pre>";
    } else {
      h += codeHead(false) + '<pre class="num">' + (q.kind === "blank" ? q.finished : q.code) + "</pre>";
      var right = q.opts ? q.opts[rightIndex(q)].t : q.answer;
      h += '<p class="label clay">' + (e.ok ? "Your answer (right)" : "Your answer") + '</p><pre>' + outHTML(e.ans) + "</pre>";
      if (!e.ok) h += '<p class="label green">The right answer</p><pre>' + outHTML(right) + "</pre>";
    }
    h += '<div class="why good"><p class="label green">Why</p><p>' + q.explain + "</p></div>" +
      '<p class="label green">What Python really prints</p><pre class="out">' + outHTML(q.real) + "</pre></div></details>";
    return h;
  }


  // ---------------------------------------------------------------- the strengths and weaknesses infographic
  // Every mark carries its meaning twice: a tick or a cross for right or wrong, and a
  // filled or outlined square for sure or not sure. Colour is a third, extra signal.
  var MARK = {
    sr: { label: "Sure, and right", fill: "#1D5B39", stroke: "#1D5B39", ink: "#FFFFFF", tick: true },
    nr: { label: "Not sure, but right", fill: "#FFFFFF", stroke: "#1D5B39", ink: "#1D5B39", tick: true },
    nw: { label: "Not sure, and wrong", fill: "#FFFFFF", stroke: "#8A5A00", ink: "#8A5A00", tick: false },
    sw: { label: "Sure, but wrong", fill: "#9C2B22", stroke: "#9C2B22", ink: "#FFFFFF", tick: false }
  };
  var SKILLS = [
    { title: "Predicting what code prints", kinds: ["output", "last", "type"] },
    { title: "Reading error messages", kinds: ["error", "line"] },
    { title: "Choosing the missing code", kinds: ["blank"] },
    { title: "Putting lines in order", kinds: ["order"] }
  ];
  var BAND = {
    strong: { label: "Strong", svg: '<circle cx="11" cy="11" r="9" fill="#1D5B39"/><path d="M6.6 11.4l3 3 5.8-6.2" fill="none" stroke="#fff" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>' },
    mid: { label: "Nearly there", svg: '<circle cx="11" cy="11" r="8" fill="#fff" stroke="#8A5A00" stroke-width="2"/><path d="M11 3a8 8 0 0 0 0 16z" fill="#8A5A00"/>' },
    weak: { label: "Work on this", svg: '<circle cx="11" cy="11" r="9" fill="#9C2B22"/><path d="M11 6.2v6.3" stroke="#fff" stroke-width="2.4" stroke-linecap="round"/><circle cx="11" cy="15.6" r="1.4" fill="#fff"/>' },
    few: { label: "Too few to tell", svg: '<circle cx="11" cy="11" r="8" fill="#fff" stroke="#6E6858" stroke-width="2"/><circle cx="7.4" cy="11" r="1.3" fill="#6E6858"/><circle cx="11" cy="11" r="1.3" fill="#6E6858"/><circle cx="14.6" cy="11" r="1.3" fill="#6E6858"/>' }
  };
  var MIN_TO_RATE = 3; // a round needs this many answers before it is called strong or weak

  function markKind(e) { return (e.sure ? "s" : "n") + (e.ok ? "r" : "w"); }

  function markSVG(k, label) {
    var m = MARK[k];
    var path = m.tick ? "M6 11.5l3.3 3.3L16.2 7.8" : "M7.3 7.3l7.4 7.4M14.7 7.3l-7.4 7.4";
    return '<svg class="mk" width="22" height="22" viewBox="0 0 22 22" role="img" aria-label="' + esc(label) + '">' +
      '<rect x="1.5" y="1.5" width="19" height="19" rx="4" fill="' + m.fill + '" stroke="' + m.stroke + '" stroke-width="2"/>' +
      '<path d="' + path + '" fill="none" stroke="' + m.ink + '" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  }

  function bandOf(n, ok) {
    if (n < MIN_TO_RATE) return "few";
    if (ok / n >= 0.8) return "strong";
    if (ok / n >= 0.5) return "mid";
    return "weak";
  }

  function badge(k) {
    return '<span class="band ' + k + '"><svg width="20" height="20" viewBox="0 0 22 22" aria-hidden="true">' + BAND[k].svg +
      '</svg>' + BAND[k].label + '</span>';
  }

  function listNames(names) {
    if (names.length < 2) return names.join("");
    return names.slice(0, -1).join(", ") + " and " + names[names.length - 1];
  }

  function pct(ok, n) { return Math.round(ok / n * 100); }

  function infographicHTML(log, g) {
    var right = log.filter(function (e) { return e.ok; }).length;
    var hinted = log.filter(function (e) { return e.hints > 0; }).length;
    var today = new Date().toLocaleDateString(undefined, { day: "numeric", month: "long", year: "numeric" });

    var rows = ROUNDS.map(function (r) {
      var es = log.filter(function (e) { return QS[QIDX[e.id]].round === r.id; });
      var ok = es.filter(function (e) { return e.ok; }).length;
      return { r: r, es: es, n: es.length, ok: ok, band: bandOf(es.length, ok) };
    }).filter(function (x) { return x.n > 0; });
    var rated = rows.filter(function (x) { return x.band !== "few"; });
    var byScoreDown = function (a, b) { return b.ok / b.n - a.ok / a.n || b.n - a.n; };
    var strong = rated.filter(function (x) { return x.band === "strong"; }).sort(byScoreDown).slice(0, 3);
    var work = rated.filter(function (x) { return x.band === "weak"; }).sort(byScoreDown).reverse().slice(0, 3);
    var workIsNear = false;
    if (!work.length) {
      work = rated.filter(function (x) { return x.band === "mid"; }).sort(byScoreDown).reverse().slice(0, 2);
      workIsNear = work.length > 0;
    }

    function item(x, practise) {
      return '<li><span class="nm">' + esc(x.r.title) + '</span><span class="sc">' + x.ok + ' of ' + x.n + '</span>' +
        (practise ? '<button type="button" class="small noprint" data-act="practise" data-round="' + x.r.id + '">Practise this round</button>' : "") + '</li>';
    }

    var h = '<div class="row noprint cardtools"><label class="namebox">Your name for the picture <input id="cardname" type="text" autocomplete="off" maxlength="40"></label>' +
      '<button type="button" class="btn quiet" data-act="print">Print this picture</button></div>';

    h += '<section class="infocard" aria-labelledby="cardtitle">';
    // header
    h += '<div class="ihead"><div class="ititle"><p class="eyebrow">Beginner Python Quiz · Results</p>' +
      '<h2 id="cardtitle" class="ask" tabindex="-1">Strengths and weaknesses</h2>' +
      '<p class="who"><span>Name: <b id="cardnameout" class="nameline"></b></span><span>' + esc(today) + '</span></p></div>' +
      '<div class="hero"><span class="big">' + right + '</span><span class="of">of ' + log.length + ' right</span>' +
      '<span class="pc">' + pct(right, log.length) + '% · ' + (hinted ? plural(hinted, "hint") + " used" : "no hints used") + '</span></div></div>';

    // summary
    h += '<div class="ipart isum"><div class="sumcol good"><p class="label green">Strongest topics</p>';
    if (strong.length) h += '<ul class="sumlist">' + strong.map(function (x) { return item(x, false); }).join("") + '</ul>';
    else h += '<p class="note">No topic reached 4 in 5 right yet.</p>';
    h += '</div><div class="sumcol bad"><p class="label clay">' + (workIsNear ? "Nearly there: work on next" : "Work on next") + '</p>';
    if (work.length) h += '<ul class="sumlist">' + work.map(function (x) { return item(x, true); }).join("") + '</ul>';
    else if (rated.length) h += '<p class="note">Every topic had 4 in 5 right or better.</p>';
    else h += '<p class="note">Each round had fewer than ' + MIN_TO_RATE + ' questions, which is not enough to tell. Try whole rounds to find your strengths and weaknesses.</p>';
    h += '</div></div>';

    // the ideas to fix first
    var swCount = {};
    g.sw.forEach(function (e) { var t = ROUND[QS[QIDX[e.id]].round].title; swCount[t] = (swCount[t] || 0) + 1; });
    var swRounds = Object.keys(swCount).sort(function (a, b) { return swCount[b] - swCount[a]; });
    var where = swRounds.length <= 3
      ? "in " + listNames(swRounds.map(function (t) { return t + " (" + swCount[t] + ")"; }))
      : "across " + plural(swRounds.length, "topic") + ": they are the filled squares with a cross in the chart below";
    h += '<p class="fixfirst">' + markSVG("sw", MARK.sw.label) + '<span>' + (g.sw.length
      ? 'You were sure but wrong on ' + plural(g.sw.length, "question") + ', ' + esc(where) + '. Those show ideas about Python to fix first.'
      : 'None of your wrong answers were ones you felt sure about.') + '</span></p>';

    // topic by topic
    h += '<div class="ipart"><p class="label teal">Topic by topic: one square for each question</p><div class="tmap">';
    rows.forEach(function (x) {
      h += '<div class="trow"><span class="tn"><span class="tnum">' + x.r.n + '</span>' + esc(x.r.title) + '</span>' +
        '<span class="dots">' + x.es.map(function (e, i) {
          var k = markKind(e);
          return markSVG(k, "Question " + (i + 1) + ": " + MARK[k].label);
        }).join("") + '</span><span class="tsc">' + x.ok + ' of ' + x.n + '</span>' + badge(x.band) + '</div>';
    });
    h += '</div><ul class="ilegend">' + ["sr", "nr", "nw", "sw"].map(function (k) {
      return '<li>' + markSVG(k, MARK[k].label) + '<b>' + g[k].length + '</b> ' + MARK[k].label + '</li>';
    }).join("") + '</ul></div>';

    // skills
    var skillRows = SKILLS.map(function (sk) {
      var es = log.filter(function (e) { return sk.kinds.indexOf(QS[QIDX[e.id]].kind) >= 0; });
      if (!es.length) return "";
      var ok = es.filter(function (e) { return e.ok; }).length;
      return '<div class="bar"><span class="t">' + sk.title + '</span><span class="v">' + ok + ' of ' + es.length + '</span>' +
        '<span class="track"><i style="width:' + pct(ok, es.length) + '%"></i></span></div>';
    }).join("");
    h += '<div class="ipair"><div class="ipart"><p class="label teal">Skills: the kind of question</p><div class="bars">' + skillRows + '</div></div>';

    // how sure
    var sure = log.filter(function (e) { return e.sure; });
    var unsure = log.filter(function (e) { return !e.sure; });
    function tile(title, es) {
      var ok = es.filter(function (e) { return e.ok; }).length;
      return '<div class="stat"><span class="tl">' + title + '</span>' + (es.length
        ? '<span class="big">' + pct(ok, es.length) + '%</span><span class="tsub">right: ' + ok + ' of ' + es.length + '</span>'
        : '<span class="big">none</span><span class="tsub">no answers</span>') + '</div>';
    }
    var sureOk = sure.filter(function (e) { return e.ok; }).length;
    var verdict = !sure.length ? "You did not mark any answer as sure."
      : sureOk / sure.length >= 0.8 ? "When you felt sure, you were right at least 4 times in 5."
      : "When you felt sure, you were wrong more than 1 time in 5. Before you press Sure, trace the code line by line.";
    h += '<div class="ipart"><p class="label teal">How sure you were</p><div class="stats">' +
      tile("When you pressed Sure", sure) + tile("When you pressed Not sure", unsure) + '</div><p class="note">' + verdict + '</p></div></div>';

    h += '</section>';
    return h;
  }

  function renderResults() {
    var log = S.log;
    if (S.mode === "class") {
      paint('<section class="res"><p class="chunk-no">Finished</p><h2 class="ask" tabindex="-1">That was the last question.</h2>' +
        '<p>The class went through ' + plural(log.length, "question") + '.</p>' +
        '<div class="row"><button type="button" class="btn" data-act="restart">Back to the start</button></div></section>');
      toTop(); focusEl(app.querySelector(".ask"));
      return;
    }
    if (!log.length) {
      paint('<section class="res"><h2 class="ask" tabindex="-1">No questions answered yet.</h2>' +
        '<div class="row"><button type="button" class="btn" data-act="restart">Back to the start</button></div></section>');
      toTop(); focusEl(app.querySelector(".ask"));
      return;
    }
    var g = { sw: [], nw: [], nr: [], sr: [] };
    log.forEach(function (e) { g[markKind(e)].push(e); });
    var h = infographicHTML(log, g);

    var again = g.sw.concat(g.nw, g.nr);
    if (again.length) {
      h += '<section class="res"><h2>Look at these again</h2><p class="note">Tap a question to open it.</p>';
      [["sw", "Sure, but wrong"], ["nw", "Not sure, and wrong"], ["nr", "Not sure, but right"]].forEach(function (pair) {
        if (!g[pair[0]].length) return;
        h += "<h3>" + pair[1] + "</h3>" + g[pair[0]].map(reviewItem).join("");
      });
      h += "</section>";
    }
    h += '<div class="row">' + (again.length ? '<button type="button" class="btn" data-act="again">Try these ' + plural(again.length, "question") + ' again</button>' : "") +
      '<button type="button" class="btn quiet" data-act="restart">Back to the start</button></div>';
    S.again = again.map(function (e) { return e.id; });
    paint(h);
    toTop();
    focusEl(app.querySelector(".ask"));
  }

  // ---------------------------------------------------------------- events
  app.addEventListener("click", function (ev) {
    var b = ev.target.closest("[data-act]");
    if (!b || b.disabled) return;
    var act = b.getAttribute("data-act");
    if (act === "all" || act === "none") {
      pick.rounds = act === "all" ? new Set(ROUNDS.map(function (r) { return r.id; })) : new Set();
      app.querySelectorAll('.round input').forEach(function (c) { c.checked = act === "all"; });
      updateStart();
    } else if (act === "start") {
      var ids = QS.filter(function (q) { return pick.rounds.has(q.round); }).map(function (q) { return q.id; });
      if (pick.shuffle) shuffle(ids);
      begin(ids, pick.mode);
      toTop(); focusEl(app.querySelector(".ask"));
    } else if (act === "quick") {
      var chosen = ROUNDS.filter(function (r) { return pick.rounds.has(r.id); });
      if (!chosen.length) chosen = ROUNDS;
      var qids = chosen.map(function (r) {
        var inRound = QS.filter(function (q) { return q.round === r.id; });
        return inRound[Math.floor(Math.random() * inRound.length)].id;
      });
      if (pick.shuffle) shuffle(qids);
      begin(qids, pick.mode);
      toTop(); focusEl(app.querySelector(".ask"));
    } else if (act === "pick") pickOption(Number(b.getAttribute("data-i")));
    else if (act === "check") check(b.getAttribute("data-sure") === "1");
    else if (act === "reveal") reveal();
    else if (act === "try") {
      var q = current(), st = stateFor(q);
      if (!ready(q, st)) return;
      st.tried = st.prog.join(",");
      document.getElementById("trybox").innerHTML = triedHTML(q, st);
      fitCode();
    } else if (act === "hint") {
      var qh = current(), sh = stateFor(qh);
      sh.hints = Math.min(sh.hints + 1, qh.hints.length);
      var wrap = b.parentNode;
      wrap.outerHTML = hintsHTML(qh, sh);
      var nb = app.querySelector('[data-act="hint"]');
      focusEl(nb || app.querySelectorAll(".hintbox")[sh.hints - 1]);
    } else if (act === "add" || act === "remove" || act === "reset") moveTile(act, Number(b.getAttribute("data-i")));
    else if (act === "next") next();
    else if (act === "end") {
      if (S.mode === "class") renderStart(); else renderResults();
    } else if (act === "again") begin(S.again.slice(), "solo");
    else if (act === "restart") { renderStart(); toTop(); }
    else if (act === "copy") copyText(current() ? current().copy : "", b);
    else if (act === "practise") {
      var rid = b.getAttribute("data-round");
      begin(QS.filter(function (q) { return q.round === rid; }).map(function (q) { return q.id; }), "solo");
      toTop(); focusEl(app.querySelector(".ask"));
    } else if (act === "print") {
      document.body.classList.add("printcard");
      window.print();
    }
  });

  app.addEventListener("change", function (ev) {
    var t = ev.target;
    if (t.matches(".round input")) {
      if (t.checked) pick.rounds.add(t.value); else pick.rounds.delete(t.value);
      updateStart();
    } else if (t.name === "mode") pick.mode = t.value;
    else if (t.id === "shuffle") pick.shuffle = t.checked;
  });

  app.addEventListener("toggle", fitCode, true);

  window.addEventListener("afterprint", function () { document.body.classList.remove("printcard"); });

  app.addEventListener("input", function (ev) {
    if (ev.target.id === "cardname") {
      document.getElementById("cardnameout").textContent = ev.target.value;
      return;
    }
    if (ev.target.id !== "typed" || !S) return;
    stateFor(current()).typed = ev.target.value;
    refreshActions();
  });

  document.addEventListener("keydown", function (ev) {
    if (!S || S.pos >= S.queue.length || !app.querySelector("section.q")) return;
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    var tag = ev.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA") return;
    var q = current(), st = stateFor(q), k = ev.key.toLowerCase();
    if (st.checked) {
      if (k === "enter" && tag !== "BUTTON" && tag !== "A" && tag !== "SUMMARY") { ev.preventDefault(); next(); }
      return;
    }
    if (q.opts) {
      var pos = LETTERS.toLowerCase().indexOf(k);
      if (pos < 0 && /^[1-6]$/.test(k)) pos = Number(k) - 1;
      if (pos >= 0 && pos < st.order.length && k.length === 1) { ev.preventDefault(); pickOption(st.order[pos]); return; }
    }
    if (k === "h" && st.hints < q.hints.length) {
      var hb = app.querySelector('[data-act="hint"]'); if (hb) hb.click(); return;
    }
    if (S.mode === "class") { if (k === "r") reveal(); return; }
    if (k === "s") check(true);
    else if (k === "n") check(false);
  });

  renderStart();
})();
