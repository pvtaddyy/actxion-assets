// ACTXION reel engine: builds every scene from window.TL and draws any moment with seek(t).
// Deterministic: the same t always gives the same frame, so render.mjs can step frame by frame.
// Motion rules (reel-edit style rules): fast in 0.2-0.35 s with ease-out, hold, clean out;
// one idea on screen at a time; push-ins at most 6%; no shake.
(function () {
  const TL = window.TL;
  const $ = (h) => { const d = document.createElement("div"); d.innerHTML = h.trim(); return d.firstChild; };
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const out3 = (x) => 1 - Math.pow(1 - clamp(x), 3);
  const back = (x) => { x = clamp(x); const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const IN = 0.3, OUT = 0.2;
  const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const tickSvg = '<svg viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  // static film grain
  const g = document.getElementById("grain").getContext("2d");
  const img = g.createImageData(540, 960);
  let seed = 9;
  for (let i = 0; i < img.data.length; i += 4) { seed = (seed * 16807) % 2147483647; const v = seed % 255; img.data[i] = img.data[i + 1] = img.data[i + 2] = v; img.data[i + 3] = 255; }
  g.putImageData(img, 0, 0);

  if (TL.accent) {
    document.documentElement.style.setProperty("--accent", TL.accent);
    document.documentElement.style.setProperty("--accent-hi", TL.accentHi || TL.accent);
  }
  if (TL.mark) document.getElementById("mark").innerHTML = `<img src="${TL.mark}">`;
  const header = document.getElementById("header");
  if (TL.header) header.innerHTML = TL.header.html;
  document.getElementById("credit").textContent = "";  // no photo credits on the video (owner, 5 Nov 2026); they go in the post text
  const caps = document.getElementById("caps");
  const root = document.getElementById("scenes");

  // fit a single line of text to a width by shrinking its font size
  // measures the inner <span> (a full-width block would always look too wide)
  function fit(el, maxW, maxPx) {
    const span = el.querySelector("span") || el;
    let px = maxPx; el.style.fontSize = px + "px";
    while (span.offsetWidth > maxW && px > 40) { px -= 6; el.style.fontSize = px + "px"; }
    return px;
  }

  const builders = {
    player(s) {
      const el = $(`<div class="layer">
        ${s.bgPhoto ? `<div class="bgph" style="background-image:url('${s.bgPhoto}')"></div>` : ""}
        <div class="stage">
        <div class="bigword"><span>${esc(s.word || "")}</span></div>
        <div class="cut" style="height:${s.height || 780}px"><img src="${s.photo}"></div>
        ${s.label ? `<div style="position:absolute;left:64px;top:700px;z-index:2"><span class="chip"><span class="dot"></span><span class="label" style="color:var(--text)">${esc(s.label)}</span></span></div>` : ""}
      </div></div>`);
      root.appendChild(el);
      const bw = el.querySelector(".bigword");
      bw.style.top = (s.wordY != null ? s.wordY : 120) + "px";
      fit(bw, 1000, s.wordSize || 330);
      return { el, bw, cut: el.querySelector(".cut"), bg: el.querySelector(".bgph") };
    },
    score(s) {
      const row = (crest, name, side) => `<div class="srow">${crest ? `<img src="${crest}">` : ""}<div class="n">${esc(name)}</div><div class="g" data-side="${side}"><div class="roll"></div></div></div>`;
      const el = $(`<div class="layer"><div class="stage"><div class="score">
        <div class="label" style="margin-bottom:26px">${esc(s.label || "")}</div>
        ${row(s.homeCrest, s.home, "h")}${row(s.awayCrest, s.away, "a")}
        <div class="label foot" style="margin-top:34px;color:var(--text)">${esc(s.foot || "")}</div>
      </div></div></div>`);
      root.appendChild(el);
      return { el, h: el.querySelector('[data-side="h"] .roll'), a: el.querySelector('[data-side="a"] .roll'), foot: el.querySelector(".foot") };
    },
    list(s) {
      const el = $(`<div class="layer"><div class="stage"><div class="list">
        ${s.title ? `<div class="label" style="margin-bottom:30px">${esc(s.title)}</div>` : ""}
        ${s.items.map((it) => `<div class="item"><div class="tick">${tickSvg}</div><div>${esc(it.text)}</div></div>`).join("")}
      </div></div></div>`);
      root.appendChild(el);
      return { el, items: [...el.querySelectorAll(".item")] };
    },
    stat(s) {
      const el = $(`<div class="layer"><div class="stage"><div class="stat">
        <div class="v">0</div><div class="u">${esc(s.unit || "")}</div><div class="l">${esc(s.label || "")}</div>
      </div></div></div>`);
      root.appendChild(el);
      return { el, v: el.querySelector(".v"), u: el.querySelector(".u"), l: el.querySelector(".l") };
    },
    card(s) {
      const el = $(`<div class="layer"><div class="stage">
        <div class="refcard ${s.colour === "yellow" ? "yellow" : ""}"></div>
        <div style="position:absolute;left:0;right:0;top:640px;text-align:center"><div class="bigword" style="position:static;color:var(--text);font-size:150px"><span>${esc(s.text || "")}</span></div></div>
      </div></div>`);
      root.appendChild(el);
      return { el, c: el.querySelector(".refcard"), t: el.querySelector(".bigword") };
    },
    versus(s) {
      const side = (o, left) => `<div class="side" style="${left ? "left:0" : "right:0"}">
          <div class="ph"><img src="${o.photo}"></div>
          <div class="tag"><span class="ab">${left ? "A" : "B"}</span><span class="t">${esc(o.label)}</span></div></div>`;
      const el = $(`<div class="layer"><div class="stage"><div class="vs">${side(s.a, true)}${side(s.b, false)}<div class="vsline"></div></div></div></div>`);
      root.appendChild(el);
      return { el, L: el.querySelectorAll(".side")[0], R: el.querySelectorAll(".side")[1] };
    },
    ask(s) {
      const el = $(`<div class="layer"><div class="stage"><div class="ask">
        <div class="label" style="margin-bottom:30px">${esc(s.label || "Pick your side")}</div>
        <div class="q">${s.html}</div><div class="sub">${esc(s.sub || "")}</div>
      </div></div></div>`);
      root.appendChild(el);
      return { el, q: el.querySelector(".q"), sub: el.querySelector(".sub") };
    },
    compare(s) {
      // head-to-head rows: label, A value, B value, bars that grow on their trigger word
      const rows = s.rows.map((r) => `<div class="crow"><div class="cl">${esc(r.label)}</div>
        <div class="cv"><span class="va">${esc(r.a)}</span><div class="bars"><div class="ba"></div><div class="bb"></div></div><span class="vb">${esc(r.b)}</span></div></div>`).join("");
      const el = $(`<div class="layer"><div class="stage"><div class="cmp">
        <div class="chead"><div class="na">${s.aPhoto ? `<img src="${s.aPhoto}">` : ""}<span>${esc(s.aName)}</span></div>
        <div class="nb"><span>${esc(s.bName)}</span>${s.bPhoto ? `<img src="${s.bPhoto}">` : ""}</div></div>${rows}</div></div></div>`);
      root.appendChild(el);
      return { el, rows: [...el.querySelectorAll(".crow")] };
    },
    pitch(s) {
      const pl = s.players.map((p) => `<div class="pl" style="left:${p.x}%;top:${p.y}%"><div class="d" style="background:${p.c || "var(--accent)"}"></div><div class="nm">${esc(p.n)}</div></div>`).join("");
      const el = $(`<div class="layer"><div class="stage"><div class="pitchwrap"><div class="pitch">
        <div class="ln" style="left:-3px;right:-3px;top:50%;height:0;border-width:3px 0 0 0"></div>
        <div class="ln" style="left:50%;top:50%;width:220px;height:220px;margin:-110px 0 0 -110px;border-radius:50%"></div>
        <div class="ln" style="left:25%;right:25%;top:-3px;height:15%"></div>
        <div class="ln" style="left:25%;right:25%;bottom:-3px;height:15%"></div>
        ${pl}</div></div>
        ${s.title ? `<div style="position:absolute;left:64px;top:-10px" class="label">${esc(s.title)}</div>` : ""}
      </div></div>`);
      root.appendChild(el);
      return { el, p: el.querySelector(".pitch"), pls: [...el.querySelectorAll(".pl")] };
    },
  };

  const scenes = TL.scenes.map((s) => {
    const b = builders[s.type](s);
    if (s.source) {
      const src = $(`<div class="source"><span class="chip"><span class="dot"></span><span class="label" style="color:var(--text)"></span></span></div>`);
      b.el.querySelector(".stage").appendChild(src);
      b.src = src.querySelector(".label");
    }
    return { s, b };
  });

  const capEls = TL.captions.map((c) => {
    const el = $(`<div class="cap">${c.parts.map((p) => p.k ? `<span class="k ${p.hot ? "hot" : ""}">${esc(p.t)}</span>` : `<span class="s">${esc(p.t)}</span>`).join(" ")}</div>`);
    el.style.display = "none";
    caps.appendChild(el);
    return { c, el };
  });

  function roll(el, n, prev, k) {
    // number slides up into place when it changes
    el.innerHTML = k < 1 && prev != null && prev !== n
      ? `<div style="transform:translateY(${-190 * out3(k)}px)"><div>${prev}</div><div>${n}</div></div>`
      : `<div>${n}</div>`;
  }

  window.seek = function (t) {
    // header (persistent title)
    if (TL.header) {
      const k = out3((t - TL.header.from) / IN);
      header.style.opacity = t >= TL.header.from ? k : 0;
      header.style.transform = `translateY(${(1 - k) * 24}px)`;
    }
    for (const { s, b } of scenes) {
      const L = t - s.s, D = s.e - s.s;
      const vis = L >= 0 && t < s.e + OUT;
      b.el.style.display = vis ? "block" : "none";
      if (!vis) continue;
      const kin = out3(L / IN), kout = clamp((t - s.e) / OUT);
      b.el.style.opacity = kin * (1 - kout);
      b.el.style.transform = `translateY(${(1 - kin) * 40 - kout * 30}px)`;
      const prog = clamp(L / Math.max(D, 0.01));
      if (s.type === "player") {
        b.bw.style.transform = `scale(${1.18 - 0.18 * out3(L / 0.35)})`;
        b.bw.style.opacity = out3(L / 0.3);
        const push = 1 + 0.05 * prog; // max 6%
        b.cut.style.transform = `translateX(-50%) translateY(${(1 - out3(L / 0.4)) * 80}px) scale(${push})`;
        if (b.bg) b.bg.style.transform = `scale(${1.1 + 0.04 * prog})`;
      } else if (s.type === "score") {
        const st = s.states.filter((x) => x.t <= t).pop() || s.states[0];
        const i = s.states.indexOf(st), pr = s.states[i - 1];
        const k = (t - st.t) / 0.28;
        roll(b.h, st.h, pr ? pr.h : null, k);
        roll(b.a, st.a, pr ? pr.a : null, k);
        if (st.foot) b.foot.textContent = st.foot;
      } else if (s.type === "list") {
        s.items.forEach((it, i) => {
          const k = out3((t - it.t) / 0.25);
          const el = b.items[i];
          el.style.opacity = t >= it.t ? k : 0;
          el.style.transform = `translateX(${(1 - k) * -60}px)`;
          el.querySelector(".tick").classList.toggle("on", t >= it.t + 0.08);
        });
      } else if (s.type === "stat") {
        const k = out3(L / (s.countFor || 0.9));
        const v = s.value * k;
        b.v.textContent = (s.decimals ? v.toFixed(s.decimals) : Math.round(v)) + (s.suffix || "");
        b.u.style.opacity = out3((L - 0.5) / 0.3);
        b.l.style.opacity = out3((L - 0.7) / 0.3);
      } else if (s.type === "card") {
        const k = back(L / 0.45);
        b.c.style.transform = `translateY(${(1 - k) * 900}px) rotate(${-28 + 20 * k}deg)`;
        b.t.style.opacity = out3((L - 0.35) / 0.25);
        b.t.style.transform = `scale(${1.2 - 0.2 * out3((L - 0.35) / 0.3)})`;
      } else if (s.type === "versus") {
        const kl = out3(L / 0.35), kr = out3((L - 0.25) / 0.35);
        b.L.style.transform = `translateX(${(1 - kl) * -200}px)`; b.L.style.opacity = kl;
        b.R.style.transform = `translateX(${(1 - kr) * 200}px)`; b.R.style.opacity = kr;
      } else if (s.type === "ask") {
        b.q.style.transform = `scale(${1.08 - 0.08 * out3(L / 0.3)})`;
        b.sub.style.opacity = out3((L - 0.6) / 0.3);
      } else if (s.type === "compare") {
        s.rows.forEach((r, i) => {
          const el = b.rows[i], k = out3((t - r.t) / 0.35);
          el.style.opacity = t >= r.t ? clamp((t - r.t) / 0.2) : 0;
          const na = parseFloat(r.a) || 0, nb = parseFloat(r.b) || 0, m = Math.max(na, nb, 1e-9);
          el.querySelector(".ba").style.width = (44 * k * na / m) + "%";
          el.querySelector(".bb").style.width = (44 * k * nb / m) + "%";
          el.querySelector(".va").classList.toggle("win", k > 0.9 && na > nb);
          el.querySelector(".vb").classList.toggle("win", k > 0.9 && nb > na);
        });
      } else if (s.type === "pitch") {
        const k = out3(L / 0.6);
        b.p.style.transform = `rotateX(${52 - 4 * k}deg) scale(${0.95 + 0.05 * k})`;
        b.pls.forEach((el, i) => { const kk = back((L - 0.3 - i * 0.07) / 0.3); el.style.opacity = clamp((L - 0.3 - i * 0.07) / 0.15); el.style.transform = `translate(-50%,-50%) rotateX(-48deg) scale(${kk})`; });
      }
      if (b.src) {
        const n = Math.floor(clamp((L - 0.4) / 0.5) * s.source.length);
        b.src.textContent = s.source.slice(0, n);
        b.src.parentNode.style.opacity = L > 0.4 ? 1 : 0;
      }
    }
    for (const { c, el } of capEls) {
      const on = t >= c.s && t < c.e;
      el.style.display = on ? "inline-block" : "none";
      if (on) {
        const k = out3((t - c.s) / 0.18);
        el.style.opacity = k;
        el.style.transform = `scale(${0.9 + 0.1 * k}) translateY(${(1 - k) * 14}px)`;
      }
    }
  };
  window.ready = document.fonts.ready.then(() => Promise.all([...document.images].map((i) => i.decode().catch(() => 0))));
})();
