// THE MIC - the ACTXION app on a phone, rebuilt in HTML to look like the real app (layouts copied from the owner's
// screen recordings, Nov 2026) with the content rewritten for each episode: the club, the match, real players and the
// episode's own fan lines as the comments (fictional usernames). No invented vote totals, percentages or message counts.
// buildPhone(tl, f, s, e): f = EP.feature, s/e = start/end seconds of the #phone clip.
(function () {
  const css = `
#phone{position:absolute;left:0;top:0;width:1080px;height:1920px;pointer-events:none}
#phone .dim{position:absolute;inset:0;background:radial-gradient(70% 55% at 50% 40%,rgba(8,9,16,.55),rgba(5,6,12,.88))}
#phone .ph{position:absolute;left:224px;top:180px;zoom:1.24;width:436px;height:920px;border-radius:58px;background:#0c0c0e;padding:12px;
  box-shadow:0 40px 90px rgba(0,0,0,.7),0 0 0 3px #2a2a30,0 0 60px rgba(230,30,40,.25)}
#phone .scr{position:relative;width:100%;height:100%;border-radius:46px;overflow:hidden;background:#fff;color:#111;font-family:Inter,sans-serif}
#phone .sb{height:50px;display:flex;justify-content:space-between;align-items:center;padding:6px 26px 0 30px;font:700 16px Inter}
#phone .isl{width:112px;height:32px;border-radius:18px;background:#000}
#phone .sig{font:700 13px Inter;letter-spacing:.5px}
#phone .hd{display:flex;align-items:center;justify-content:space-between;padding:6px 18px 12px;font:500 19px Inter}
#phone .hd .bk{display:flex;gap:16px;align-items:center}
#phone .badge{position:relative}#phone .badge i{position:absolute;right:-10px;top:-8px;background:#ee3b4f;color:#fff;font:700 10px/16px Inter;padding:0 5px;border-radius:9px;font-style:normal}
#phone .tabs{display:flex;gap:26px;padding:10px 18px 0;font:500 16px Inter;color:#666;border-bottom:1px solid #eee;white-space:nowrap}
#phone .tabs span{padding-bottom:10px}#phone .tabs b{color:#111;font-weight:600;border-bottom:3px solid #111;padding-bottom:9px}
#phone .seg{display:flex;background:#eee;border-radius:12px;padding:4px;margin:12px 14px}
#phone .seg div{flex:1;text-align:center;padding:9px 0;font:500 14px Inter;color:#777;border-radius:9px}
#phone .seg .on{background:#fff;color:#111;font-weight:700;box-shadow:0 1px 4px rgba(0,0,0,.12)}
#phone .cm{padding:8px 14px 2px}
#phone .cm .u{display:flex;align-items:center;gap:7px;font:700 15px Inter}
#phone .av{display:inline-block;width:22px;height:22px;border-radius:50%;color:#fff;font:800 10px/22px Inter;text-align:center;flex:none}
#phone .pill{font:500 12px Inter;padding:1px 6px;border-radius:4px;background:#e2dcfb;color:#333}
#phone .pill.g{background:#d9f3d6}
#phone .cm .t{font:400 15px/1.35 Inter;margin:4px 0 4px;color:#222}
#phone .cm .m{display:flex;gap:16px;font:400 12px Inter;color:#555;align-items:center}
#phone .cm .m .r{margin-left:auto;color:#777}
#phone .tagrow{display:flex;gap:8px;align-items:center;padding:10px 14px 6px;border-top:2px solid #eee;font:600 17px Inter}
#phone .chip{border:1px solid #bbb;border-radius:999px;padding:7px 13px;font:500 13px Inter;background:#fff;color:#111}
#phone .comp{display:flex;align-items:center;gap:10px;padding:4px 14px 10px}
#phone .plus{width:40px;height:40px;border-radius:50%;background:#efefef;font:400 26px/40px Inter;text-align:center;flex:none}
#phone .inp{flex:1;border:1px solid #bbb;border-radius:12px;min-height:44px;padding:9px 12px;font:400 15px/1.35 Inter;color:#222}
#phone .snd{font:700 24px Inter;flex:none}
#phone .kb{position:absolute;left:0;right:0;bottom:0;height:285px;background:#d4d6dc;padding:10px 4px 0;border-radius:0 0 46px 46px}
#phone .kr{display:flex;justify-content:center;gap:6px;margin-bottom:11px}
#phone .k{width:33px;height:44px;border-radius:7px;background:#fff;font:400 21px/44px Inter;text-align:center;box-shadow:0 1px 0 #999}
#phone .k.w{width:46px;background:#adb2bb;font-size:15px}#phone .k.sp{width:190px}
#phone .nav{position:absolute;left:0;right:0;bottom:0;height:74px;border-top:1px solid #eee;background:#fff;display:flex;justify-content:space-around;align-items:center;font:22px Inter;color:#222;border-radius:0 0 46px 46px;z-index:5}
#phone .nav .me{width:30px;height:30px;border-radius:50%;background:#4a6b3a}
#phone .toast{position:absolute;left:24px;right:24px;bottom:300px;background:#1aa35a;color:#fff;border-radius:16px;padding:15px 18px;font:700 17px Inter;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,.25);opacity:0;z-index:9}
#phone .mc{margin:10px 14px;border:1px solid #e3e3e3;border-radius:16px;padding:13px 16px}
#phone .mc .a{font:600 16px Inter}#phone .mc .b{font:400 14px Inter;color:#555;margin-top:4px}#phone .mc .c{font:700 14px Inter;color:#d9822b;margin-top:4px}
#phone .xtabs{display:flex;gap:24px;padding:4px 18px 10px;font:500 15px Inter;color:#666}#phone .xtabs b{color:#111;border-bottom:3px solid #111;padding-bottom:6px}
#phone .pitch{position:relative;margin:0 14px;height:440px;border-radius:4px;background:#2c6b2a}
#phone .slot{position:absolute;width:70px;margin-left:-35px;text-align:center;font:600 11px/1.25 Inter;color:#fff}
#phone .slot .c{display:block;width:44px;height:44px;margin:0 auto 3px;border-radius:50%;background:#f1e3d3;color:#333;font:800 13px/44px Inter;border:2px solid #fff}
#phone .slot .c.e{background:transparent;border:2px dashed rgba(255,255,255,.75);color:#fff;font-size:12px}
#phone .slot small{display:block;font:500 10px Inter;color:#cfe3cf}
#phone .btn{position:absolute;left:14px;right:14px;bottom:86px;border-radius:14px;background:#ef4a62;color:#fff;text-align:center;padding:15px 0;font:600 18px Inter}
#phone .sheet{position:absolute;left:0;right:0;bottom:0;background:#fff;border-radius:22px 22px 0 0;box-shadow:0 -12px 34px rgba(0,0,0,.28);padding:10px 16px 90px;z-index:6}
#phone .sheet .gr{width:44px;height:5px;border-radius:3px;background:#ccc;margin:0 auto 10px}
#phone .sheet .h{text-align:center;font:600 17px Inter;margin:6px 0 10px}
#phone .sheet .sec{font:600 15px Inter;margin:6px 0 4px}
#phone .row{display:flex;align-items:center;gap:12px;padding:9px 4px;border-bottom:1px solid #f0f0f0;font:400 16px Inter}
#phone .row .n{width:26px;color:#666;font-size:15px}
#phone .row .ph2{width:34px;height:34px;border-radius:50%;background:#e8dccd;font:800 11px/34px Inter;text-align:center;color:#444;flex:none}
#phone .row .ok{margin-left:auto;color:#1aa35a;font-weight:800;opacity:0}
#phone .row .sub{display:block;font-size:13px;color:#888}
#phone .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px 4px;padding:16px 10px 8px;text-align:center;font:400 13px/1.2 Inter;color:#333}
#phone .grid .p{position:relative}
#phone .grid .ring{width:62px;height:62px;margin:0 auto 4px;border-radius:50%;border:3px solid var(--c);background:#f1e3d3;font:800 16px/56px Inter;color:#444}
#phone .grid .ring.crest{background:#fff;color:var(--c);font-size:14px}
#phone .grid .dn{position:absolute;left:4px;top:34px;width:20px;height:20px;border-radius:50%;background:#fbe1e4;color:#e0405a;font:700 13px/20px Inter}
#phone .rate{text-align:center;font:500 15px Inter;color:#333;padding:10px 0 4px}#phone .stars{text-align:center;color:#ddd;font-size:22px;letter-spacing:4px}
#phone .potm{display:flex;align-items:center;gap:10px;margin:10px 14px;font:500 15px Inter}
#phone .blue{background:#1736d6;color:#fff;text-align:center;font:500 15px/1.35 Inter;padding:9px 12px}
#phone .twc{margin:12px 14px;border-radius:16px;background:#f4f4f4;padding:12px 14px}
#phone .twc .top{display:flex;justify-content:space-between;align-items:center;font:600 13px Inter;letter-spacing:.06em}
#phone .tog{display:flex;background:#fff;border-radius:999px;padding:3px;font:500 12px Inter;letter-spacing:0}
#phone .tog span{padding:5px 10px;border-radius:999px;color:#666}#phone .tog .on{background:#f1f1f1;color:#111;box-shadow:0 1px 3px rgba(0,0,0,.15)}
#phone .twc p{font:400 14px/1.35 Inter;margin-top:8px;color:#333}
#phone .pos{display:flex;gap:8px;padding:2px 14px 8px;white-space:nowrap}
#phone .pos span{border:1px solid #ddd;border-radius:10px;padding:8px 13px;font:500 14px Inter}#phone .pos .on{background:#111;color:#fff;border-color:#111}
#phone .pc{margin:8px 14px;border:1px solid #eee;border-radius:16px;padding:12px 14px}
#phone .pc .nm{display:flex;align-items:center;gap:10px;font:500 16px Inter}#phone .pc .nm .n{color:#666;width:22px}
#phone .kls{display:flex;border-radius:10px;overflow:hidden;margin-top:10px;font:500 15px Inter;text-align:center}
#phone .kls div{flex:1;padding:11px 0}#phone .kls .k1{background:#dcf5df}#phone .kls .l1{background:#e8e8e8}#phone .kls .s1{background:#fbdfe3}
#phone .bar{height:4px;border-radius:2px;margin-top:10px;background:linear-gradient(90deg,#2aa34a 0 33%,#555 33% 66%,#d22a3a 66%)}
#phone .sug{display:flex;justify-content:space-between;background:#ececec;border-radius:10px;padding:11px 12px;margin-top:10px;font:400 15px Inter}
#phone .wallTop{background:linear-gradient(160deg,#2a5d8a,#2fa3a1);color:#fff;padding:14px 16px 16px}
#phone .wallTop .cmp{background:rgba(255,255,255,.18);border-radius:14px;padding:8px;text-align:center;font:400 12px/1.5 Inter}
#phone .wallTop .vs{display:flex;justify-content:space-between;align-items:center;margin-top:12px;font:600 14px Inter;text-align:center}
#phone .crest{display:block;width:46px;height:46px;border-radius:50%;margin:0 auto 6px;border:3px solid #fff}
#phone .post{margin:10px 14px;border:1px solid #eee;border-radius:14px;padding:12px}
#phone .post .who{display:flex;align-items:center;gap:10px;font:600 15px Inter}#phone .post .who small{display:block;font:400 12px Inter;color:#777}
#phone .post .fol{margin-left:auto;border:1px solid #ccc;border-radius:999px;padding:5px 14px;font:500 13px Inter}
#phone .rep{background:#171717;color:#fff;border-radius:16px;padding:14px;text-align:center;margin-top:10px}
#phone .rep .tt{font:700 15px Inter}#phone .rep .row2{display:flex;justify-content:space-around;align-items:center;margin:10px 0;font:500 13px Inter}
#phone .rep .dl{position:relative;border-radius:12px;padding:11px;font:600 15px Inter;background:#3a3a3a;color:#bbb}
#phone .rep .dl .ok2{position:absolute;inset:0;border-radius:12px;padding:11px;background:#d8f5df;color:#1b7a35;opacity:0}
#phone .cap{position:absolute;left:0;right:0;top:1395px;padding:0 70px;text-align:center;font:800 40px Inter;color:#fff;text-shadow:0 4px 18px rgba(0,0,0,.8)}
#phone .cap b{color:#ff5a64}
#phone .tag{position:absolute;left:0;right:0;top:160px;text-align:center}
#phone .tag span{display:inline-block;font:800 26px Inter;letter-spacing:.16em;color:#fff;background:#E61E28;padding:10px 22px;border-radius:8px}`;
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const ini = n => esc(String(n).split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase());
  const last = n => esc(String(n).split(' ').slice(-1)[0]);
  const AVC = ['#2f7de1', '#e1662f', '#1aa35a', '#8b4fd6', '#d63f6c', '#2fa3a1'];
  const NAME = { fan_voice: 'FAN VOICE', starting_11: 'STARTING 11', fan_wall: 'FAN WALL', live_subs: 'LIVE SUBSTITUTIONS', transfer_window: 'TRANSFER WINDOW' };
  const LINE = {
    fan_voice: f => `Tell <b>${esc(f.club)}</b> what to keep doing and what to fix`,
    starting_11: f => `Pick your XI. It goes to <b>${esc(f.club)}</b> before kick-off`,
    fan_wall: f => `Your message, delivered to <b>${esc(f.club)}</b> six hours before kick-off`,
    live_subs: f => `Make your subs live. Show the manager what fans want`,
    transfer_window: f => `Buy, sell, keep or loan. Build the <b>${esc(f.club)}</b> you want`,
  };
  const top = f => `<div class="sb"><span>${esc(f.clock || '13:58')}</span><span class="isl"></span><span class="sig">▂▄▆ 5G ▭</span></div>`;
  const nav = `<div class="nav"><span>⌂</span><span>⊳</span><span>＋</span><span>💬</span><span class="me"></span></div>`;
  const kb = () => `<div class="kb">${['qwertyuiop', 'asdfghjkl', '⇧zxcvbnm⌫'].map(r => `<div class="kr">${[...r].map(k => `<div class="k${'⇧⌫'.includes(k) ? ' w' : ''}">${k}</div>`).join('')}</div>`).join('')}<div class="kr"><div class="k w">123</div><div class="k w">☺</div><div class="k sp"></div><div class="k w">↵</div></div></div>`;
  const cmt = (c, i) => `<div class="cm"><div class="u"><span class="av" style="background:${AVC[i % AVC.length]}">${ini(c.user)}</span>${esc(c.user)} <span class="pill${/motiv/i.test(c.tag || '') ? ' g' : ''}">${esc(c.tag || 'Both')}</span></div>
    <div class="t">${esc(c.text)}</div><div class="m"><span>0 👍</span><span>0 👎</span><span>Reply</span><span class="r">${esc(c.ago || 'just now')}</span></div></div>`;
  const FORM = [[50, 8], [14, 31], [38, 31], [62, 31], [86, 31], [32, 54], [68, 54], [50, 60], [18, 79], [50, 86], [82, 79]];   // GK at the top, as in the app

  function screen(f) {
    const C = esc(f.colour || '#c4121d');
    if (f.type === 'fan_voice') {
      const tags = ['Keep Doing', 'Improve', 'Both'];
      return top(f) + `<div class="hd"><span class="bk">‹ <span>What's On</span></span><span>☆</span></div>
        <div style="position:absolute;left:0;right:0;top:96px;bottom:420px;overflow:hidden">
          <div class="mine" style="height:0;overflow:hidden;opacity:0">${cmt({ user: f.me || 'you', tag: f.tag || 'Improve', text: f.text, ago: 'now' }, 3)}</div>
          ${(f.comments || []).slice(0, 4).map(cmt).join('')}</div>
        <div style="position:absolute;left:0;right:0;bottom:285px;background:#fff">
          <div class="tagrow">Tag it: ${tags.map(t => `<span class="chip" data-t="${t}">${t}</span>`).join('')}</div>
          <div class="comp"><span class="plus">+</span><div class="inp"><span class="typed"></span><span>|</span></div><span class="snd">➤</span></div></div>
        ${kb()}<div class="toast" data-layout-allow-overlap>✓ Delivered to ${esc(f.club)}</div>`;
    }
    if (f.type === 'fan_wall') {
      return top(f) + `<div class="hd"><span class="bk">‹ <span>What's On</span></span><span>☆</span></div>
        <div class="wallTop"><div class="cmp">${esc(f.comp || '')}<br>${esc(f.when || '')}</div>
          <div class="vs"><div><span class="crest" style="background:${C}"></span>${esc(f.club)}</div><div style="font:700 18px Inter">VS</div><div><span class="crest" style="background:${esc(f.oppColour || '#888')}"></span>${esc(f.opponent || '')}</div></div></div>
        <div class="tabs"><span>Fan Voice</span><b>Fan Wall</b><span>Posts</span><span>Line Ups</span></div>
        <div class="seg"><div class="on">${esc(f.club)}</div><div>${esc(f.opponent || '')}</div></div>
        <div style="position:absolute;left:0;right:0;top:400px;bottom:74px;overflow:hidden">
          <div class="post"><div class="who"><span class="av" style="width:34px;height:34px;line-height:34px;background:#E61E28">A</span><div>ACTXION<small>@actxion</small></div><span class="fol">Follow</span></div>
          <div class="rep"><div class="tt">Fan Wall Report</div><div class="row2"><div><span class="crest" style="background:${C}"></span>${esc(f.club)}</div><div>${esc(f.comp || '')}</div><div><span class="crest" style="background:${esc(f.oppColour || '#888')}"></span>${esc(f.opponent || '')}</div></div>
          <div class="dl">Delivering six hours before kick-off<div class="ok2">✓ Delivered to ${esc(f.club)}</div></div></div></div>
          <div class="mine" style="height:0;overflow:hidden;opacity:0">${cmt({ user: f.me || 'you', tag: 'Motivational', text: f.text, ago: 'now' }, 3)}</div>
          ${(f.comments || []).slice(0, 3).map((c, i) => cmt({ ...c, tag: c.tag || 'Motivational' }, i)).join('')}</div>
        ${nav}<div class="toast" data-layout-allow-overlap>✓ Delivered to ${esc(f.club)}</div>`;
    }
    if (f.type === 'starting_11') {
      const xi = (f.xi || []).slice(0, 11), pos = f.pos || [], empty = f.empty || [9, 10], pick = f.pick || [];
      return top(f) + `<div class="hd"><span class="bk">‹ <span>Starting XI</span></span><span></span></div>
        <div class="mc"><div class="a">${esc(f.club)} VS ${esc(f.opponent || '')}</div><div class="b">${esc(f.comp || '')} • ${esc(f.when || '')}</div><div class="c">Locks before kick-off ⓘ</div></div>
        <div class="seg"><div class="on">${esc(f.club)}</div><div>${esc(f.opponent || '')}</div></div>
        <div class="xtabs"><b>My pick</b><span>Fan consensus</span><span>Manager's XI</span></div>
        <div class="pitch">${FORM.map(([x, y], i) => { const isE = empty.includes(i), full = `<span class="c">${ini(xi[i] || '')}</span>${last(xi[i] || '')}<small>${esc(pos[i] || '')}</small>`;
          return `<div class="slot" style="left:${x}%;top:${y}%;transform:translateY(-50%)">${isE ? `<span class="c e">${esc(pos[i] || '')}</span><div class="fill" style="position:absolute;left:0;right:0;top:0;opacity:0">${full}</div>` : full}</div>`; }).join('')}</div>
        <div class="btn">Submit my XI</div>${nav}
        <div class="sheet"><div class="gr"></div><div class="h">Pick ${esc(pos[empty[0]] || 'ST')}</div><div class="sec">Forward</div>
          ${pick.slice(0, 5).map(p => `<div class="row"><span class="n">${esc(p.num || '')}</span><span class="ph2">${ini(p.name)}</span><span>${esc(p.name)}${p.note ? `<span class="sub">${esc(p.note)}</span>` : ''}</span><span class="ok">✓</span></div>`).join('')}</div>
        <div class="toast" data-layout-allow-overlap>✓ Sent to ${esc(f.club)}</div>`;
    }
    if (f.type === 'live_subs') {
      const sq = (f.squad || []).slice(0, 7);
      return top(f) + `<div class="hd"><span class="bk">‹ <span>What's On</span></span><span>☆</span></div>
        <div class="tabs"><b>Fan Voice</b><span>Fan Wall</span><span>Posts</span><span>Line Ups</span></div>
        <div class="grid" style="--c:${C}"><div class="p"><div class="ring crest">${ini(f.club)}</div><b>${esc(f.club)}</b></div>
          ${sq.map(n => `<div class="p"><div class="ring">${ini(n)}</div>${n === f.off ? '<span class="dn">↓</span>' : ''}${esc(n).replace(' ', '<br>')}</div>`).join('')}</div>
        <div class="rate">Rate ${esc(f.club)}'s Performance</div><div class="stars">★★★★★</div>
        <div class="potm"><span style="color:#e5a52a">🏅</span>Choose Player of the Match</div>
        ${nav}
        <div class="sheet"><div class="gr"></div><div class="h">Substitute ${esc(f.off)} with</div>
          ${(f.options || []).slice(0, 4).map(o => `<div class="row"><span class="n">${esc(o.num || '')}</span><span class="ph2">${ini(o.name)}</span>${esc(o.name)}<span class="ok">✓</span></div>`).join('')}</div>
        <div class="toast" data-layout-allow-overlap>✓ Your sub is in: ${esc(((f.options || []).find(o => o.pick) || {}).name || '')}</div>`;
    }
    if (f.type === 'transfer_window') {
      const ps = (f.players || []).slice(0, 2);
      return top(f) + `<div class="hd"><span class="bk">‹ <span>Transfer window</span></span><span class="badge">💬<i>9+</i></span></div>
        <div class="blue">${esc(f.banner || 'Make your calls for the next window.')}</div>
        <div class="twc"><div class="top">${esc(f.club).toUpperCase()}<span class="tog"><span class="on">By player</span><span>All targets</span></span></div>
          <p>Select the players that you want ${esc(f.club)} to buy, sell and keep.</p></div>
        <div class="pos"><span>Goalkeepers</span><span>Defenders</span><span>Midfielders</span><span class="on">Forwards</span></div>
        ${ps.map(p => `<div class="pc"><div class="nm"><span class="n">${esc(p.num || '')}</span><span class="ph2" style="width:38px;height:38px;border-radius:50%;background:#e8dccd;font:800 12px/38px Inter;text-align:center">${ini(p.name)}</span>${esc(p.name)}</div>
          <div class="kls"><div class="k1" data-c="keep">Keep</div><div class="l1" data-c="loan">Loan</div><div class="s1" data-c="sell">Sell</div></div>
          <div class="bar"></div><div class="sug">Suggest a replacement <span>›</span></div></div>`).join('')}
        ${nav}<div class="toast" data-layout-allow-overlap>✓ Your window is saved</div>`;
    }
    return top(f) + nav;
  }

  window.buildPhone = function (tl, f, s, e) {
    const st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);
    const root = document.getElementById('phone');
    root.innerHTML = `<div class="dim"></div><div class="tag"><span>ON ACTXION · ${NAME[f.type] || ''}</span></div><div class="ph"><div class="scr">${screen(f)}</div></div><div class="cap">${(LINE[f.type] || (() => ''))(f)}</div>`;
    const q = sel => root.querySelector(sel), qa = sel => [...root.querySelectorAll(sel)];
    const d = e - s, toastAt = s + Math.min(d - 1.1, d * .74);
    tl.fromTo(root, { opacity: 0 }, { opacity: 1, duration: .25 }, s);
    tl.to('#brand', { opacity: 0, duration: .2 }, s); tl.to('#brand', { opacity: 1, duration: .2 }, e - .2);
    tl.fromTo(q('.ph'), { y: 900, rotation: 6 }, { y: 0, rotation: 0, duration: .6, ease: 'expo.out' }, s);
    tl.fromTo(q('.tag'), { y: -40, opacity: 0 }, { y: 0, opacity: 1, duration: .35, ease: 'back.out(2)' }, s + .25);
    tl.fromTo(q('.cap'), { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: .35 }, s + .5);
    const toast = () => tl.fromTo(q('.toast'), { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: .3, ease: 'back.out(2)' }, toastAt);
    const reveal = el => tl.fromTo(el, { height: 0, opacity: 0 }, { height: 'auto', opacity: 1, duration: .35, ease: 'power2.out' }, toastAt - .1);
    if (f.type === 'fan_voice') {
      const chip = qa('.chip').find(c => c.dataset.t === (f.tag || 'Improve')) || qa('.chip')[1];
      tl.fromTo(chip, { backgroundColor: '#ffffff', color: '#111111' }, { backgroundColor: '#111111', color: '#ffffff', duration: .15 }, s + .9);
      const txt = String(f.text || ''), o = { n: 0 }, span = q('.typed');
      tl.to(o, { n: txt.length, duration: Math.max(1, toastAt - .5 - (s + 1.1)), ease: 'none', onUpdate: () => span.textContent = txt.slice(0, Math.round(o.n)) }, s + 1.1);
      tl.fromTo(q('.inp'), { opacity: 1 }, { opacity: .25, duration: .1 }, toastAt - .15);
      reveal(q('.mine')); toast();
    } else if (f.type === 'fan_wall') {
      reveal(q('.mine'));
      tl.fromTo(q('.rep .ok2'), { opacity: 0 }, { opacity: 1, duration: .25 }, toastAt + .3);
      toast();
    } else if (f.type === 'starting_11') {
      const sh = q('.sheet'), rows = qa('.sheet .row'), pi = Math.max(0, (f.pick || []).findIndex(p => p.chosen));
      tl.fromTo(sh, { yPercent: 110 }, { yPercent: 0, duration: .4, ease: 'power3.out' }, s + 1.0);
      if (rows[pi]) { tl.fromTo(rows[pi], { backgroundColor: 'rgba(0,0,0,0)' }, { backgroundColor: '#ededed', duration: .15 }, s + 2.0); tl.fromTo(rows[pi].querySelector('.ok'), { opacity: 0 }, { opacity: 1, duration: .15 }, s + 2.05); }
      tl.to(sh, { yPercent: 110, duration: .35, ease: 'power2.in' }, s + 2.5);
      qa('.fill').forEach((fl, i) => tl.fromTo(fl, { opacity: 0, scale: .3 }, { opacity: 1, scale: 1, duration: .25, ease: 'back.out(3)' }, s + 2.9 + i * .45));
      tl.fromTo(q('.btn'), { scale: 1 }, { scale: .94, duration: .1, yoyo: true, repeat: 1 }, toastAt - .25);
      toast();
    } else if (f.type === 'live_subs') {
      const sh = q('.sheet'), rows = qa('.sheet .row'), pi = Math.max(0, (f.options || []).findIndex(o => o.pick));
      tl.fromTo(sh, { yPercent: 110 }, { yPercent: 0, duration: .4, ease: 'power3.out' }, s + 1.2);
      if (rows[pi]) { tl.fromTo(rows[pi], { backgroundColor: 'rgba(0,0,0,0)' }, { backgroundColor: '#ededed', duration: .15 }, toastAt - .7); tl.fromTo(rows[pi].querySelector('.ok'), { opacity: 0 }, { opacity: 1, duration: .15 }, toastAt - .6); }
      toast();
    } else if (f.type === 'transfer_window') {
      const cards = qa('.pc'), span = (toastAt - s - 1.4) / Math.max(1, cards.length);
      cards.forEach((c, i) => { const ch = ((f.players || [])[i] || {}).choice || 'keep', b = [...c.querySelectorAll('[data-c]')].find(x => x.dataset.c === ch);
        if (b) { const t = s + 1.2 + i * span; tl.fromTo(b, { boxShadow: 'inset 0 0 0 0px #111' }, { boxShadow: 'inset 0 0 0 3px #111', duration: .12 }, t); tl.fromTo(b, { scale: 1 }, { scale: .92, duration: .1, yoyo: true, repeat: 1 }, t); } });
      toast();
    }
    tl.to(root, { opacity: 0, duration: .3 }, e - .3);
  };
})();
