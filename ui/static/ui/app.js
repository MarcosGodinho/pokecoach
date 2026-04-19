/* Minimal, dependency-free UI for building a team and calling Django API endpoints. */

function spriteUrl(id) {
  return `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`;
}

function parseIdFromUrl(url) {
  // Example: https://pokeapi.co/api/v2/pokemon/25/
  const m = url.match(/\/pokemon\/(\d+)\/?$/);
  return m ? Number(m[1]) : null;
}

function $(id) {
  return document.getElementById(id);
}

function setStatus(text) {
  $("status").textContent = text;
}

function pretty(obj) {
  try {
    return JSON.stringify(obj, null, 2);
  } catch {
    return String(obj);
  }
}

function escapeHtml(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function markdownToHtml(input) {
  // Safe, minimal markdown renderer (headings, bold/italic, lists, code).
  const text = String(input || "");
  const parts = text.split("```");
  let out = "";
  for (let i = 0; i < parts.length; i++) {
    const chunk = parts[i];
    if (i % 2 === 1) {
      out += `<pre><code>${escapeHtml(chunk.replace(/^\w+\n/, ""))}</code></pre>`;
      continue;
    }

    const lines = chunk.split(/\r?\n/);
    let inList = false;
    const inline = (raw) => {
      let html = escapeHtml(String(raw));
      html = html.replace(/`([^`]+)`/g, (_m, g1) => `<code>${escapeHtml(g1)}</code>`);
      html = html.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
      html = html.replace(/\*([^*]+)\*/g, "<em>$1</em>");
      return html;
    };
    for (const rawLine of lines) {
      const line = rawLine.trimEnd();
      const t = line.trim();

      const closeList = () => {
        if (inList) {
          out += "</ul>";
          inList = false;
        }
      };

      if (!t) {
        closeList();
        continue;
      }

      const h = t.match(/^(#{1,3})\s+(.*)$/);
      if (h) {
        closeList();
        const level = h[1].length;
        out += `<h${level}>${escapeHtml(h[2])}</h${level}>`;
        continue;
      }

      const li = t.match(/^[-*]\s+(.*)$/);
      if (li) {
        if (!inList) {
          out += "<ul>";
          inList = true;
        }
        out += `<li>${inline(li[1])}</li>`;
        continue;
      }

      closeList();
      out += `<p>${inline(t)}</p>`;
    }
    if (inList) out += "</ul>";
  }
  return out || "<p>(empty)</p>";
}

function csrfToken() {
  return window.__CSRF__ || "";
}

const _idCache = new Map();
async function resolvePokemonIdByName(name) {
  const nm = String(name || "").trim().toLowerCase().replaceAll(" ", "-");
  if (!nm) return null;
  if (_idCache.has(nm)) return _idCache.get(nm);
  try {
    const res = await fetch(`https://pokeapi.co/api/v2/pokemon/${encodeURIComponent(nm)}`);
    if (!res.ok) {
      _idCache.set(nm, null);
      return null;
    }
    const data = await res.json();
    const id = typeof data.id === "number" ? data.id : null;
    _idCache.set(nm, id);
    return id;
  } catch {
    _idCache.set(nm, null);
    return null;
  }
}

async function apiPost(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken(),
    },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({ ok: false, error: { code: "bad_response", message: "Response is not JSON" } }));
  if (!res.ok) {
    const msg = data && data.error ? `${data.error.code}: ${data.error.message}` : `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return data;
}

function buildSlot(slotIndex, pokemons, state, onChange) {
  const slot = document.createElement("div");
  slot.className = "slot";

  const top = document.createElement("div");
  top.className = "slot-top";

  const label = document.createElement("div");
  label.className = "slot-label";
  label.textContent = `Slot ${slotIndex + 1}`;

  const remove = document.createElement("button");
  remove.className = "remove";
  remove.type = "button";
  remove.textContent = "Remove";
  remove.addEventListener("click", () => {
    state.team[slotIndex] = null;
    onChange();
  });

  top.appendChild(label);
  top.appendChild(remove);
  slot.appendChild(top);

  const details = document.createElement("details");
  details.className = "picker";

  const summary = document.createElement("summary");
  const pill = document.createElement("div");
  pill.className = "pill";

  const img = document.createElement("img");
  img.alt = "";

  const name = document.createElement("div");
  name.className = "name";
  name.textContent = "Pick a Pokemon...";

  const chev = document.createElement("div");
  chev.className = "chev";
  chev.textContent = "▾";

  pill.appendChild(img);
  pill.appendChild(name);
  summary.appendChild(pill);
  summary.appendChild(chev);
  details.appendChild(summary);

  const menu = document.createElement("div");
  menu.className = "menu";

  const search = document.createElement("input");
  search.className = "search";
  search.placeholder = "Search...";
  search.type = "text";
  menu.appendChild(search);

  const list = document.createElement("div");
  list.className = "list";
  menu.appendChild(list);
  details.appendChild(menu);
  slot.appendChild(details);

  function updateSummary() {
    const chosen = state.team[slotIndex];
    if (!chosen) {
      img.src = "";
      img.style.visibility = "hidden";
      name.textContent = "Pick a Pokemon...";
      remove.disabled = true;
      remove.style.visibility = "hidden";
      return;
    }
    img.style.visibility = "visible";
    img.src = spriteUrl(chosen.id);
    name.textContent = chosen.name;
    remove.disabled = false;
    remove.style.visibility = "visible";
  }

function renderList(filter) {
    list.innerHTML = "";
    const usedIds = new Set(state.team.filter(Boolean).map((p) => p.id));
    const f = (filter || "").trim().toLowerCase();
    const items = f ? pokemons.filter((p) => p.name.includes(f) || String(p.id).includes(f)) : pokemons;

    for (const p of items.slice(0, 200)) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "opt";
      btn.disabled = usedIds.has(p.id) && (!state.team[slotIndex] || state.team[slotIndex].id !== p.id);

      const im = document.createElement("img");
      im.alt = "";
      im.src = spriteUrl(p.id);
      btn.appendChild(im);

      const meta = document.createElement("div");
      meta.className = "meta";
      const num = document.createElement("div");
      num.className = "num";
      num.textContent = `#${p.id}`;
      const nm = document.createElement("div");
      nm.className = "nm";
      nm.textContent = p.name;
      meta.appendChild(num);
      meta.appendChild(nm);
      btn.appendChild(meta);

      btn.addEventListener("click", () => {
        state.team[slotIndex] = p;
        details.open = false;
        onChange();
      });
      list.appendChild(btn);
    }
  }

  search.addEventListener("input", () => renderList(search.value));
  // Some browser/OS combos can get weird with styled <summary>; force the toggle.
  summary.addEventListener("click", (e) => {
    e.preventDefault();
    details.open = !details.open;
  });
  details.addEventListener("toggle", () => {
    if (details.open) {
      renderList(search.value);
      setTimeout(() => search.focus(), 0);
    }
  });

  slot._update = () => {
    updateSummary();
    renderList(search.value);
  };

  // Initial state
  updateSummary();
  img.style.visibility = "hidden";
  renderList("");
  return slot;
}

function collectTeam(state) {
  return state.team.filter(Boolean).map((p) => p.name);
}

function setButtonsEnabled(enabled) {
  $("btnSuggest").disabled = !enabled;
  $("btnAnalyze").disabled = !enabled;
  $("btnClear").disabled = !enabled;
}

function setActiveAction(action) {
  const suggest = $("btnSuggest");
  const analyze = $("btnAnalyze");
  suggest.classList.toggle("active", action === "suggest");
  analyze.classList.toggle("active", action === "analyze");
}

function setLoading(action, loading) {
  const btn = action === "suggest" ? $("btnSuggest") : $("btnAnalyze");
  btn.classList.toggle("loading", !!loading);
  btn.disabled = !!loading;
  // Avoid double-submit during requests.
  $("btnClear").disabled = !!loading;
  if (loading) {
    const other = action === "suggest" ? $("btnAnalyze") : $("btnSuggest");
    other.disabled = true;
  }
}

function renderResult(data) {
  $("resultRaw").textContent = pretty(data);
  const grid = $("resultGrid");
  grid.innerHTML = "";
  $("resultMeta").textContent = "";

  if (data && typeof data.analysis === "string") {
    $("resultMeta").textContent = "Team analysis (Gemini)";
    const box = document.createElement("div");
    box.className = "analysis md";
    box.innerHTML = markdownToHtml(data.analysis);
    grid.appendChild(box);
    return;
  }

  const suggestions = data && data.suggestions ? data.suggestions : null;
  const currentTeam = data && data.current_team ? data.current_team : null;
  if (!Array.isArray(suggestions) && !Array.isArray(currentTeam)) return;

  const dexByName = window.__DEX_BY_NAME__ || {};

  function badges(types) {
    const wrap = document.createElement("div");
    wrap.className = "badges";
    if (Array.isArray(types)) {
      for (const t of types) {
        const b = document.createElement("span");
        b.className = "badge";
        b.textContent = String(t);
        wrap.appendChild(b);
      }
    }
    return wrap;
  }

  if (Array.isArray(currentTeam)) {
    $("resultMeta").textContent = `Current team: ${currentTeam.length} member(s)`;
    for (const c of currentTeam) {
      const card = document.createElement("div");
      card.className = "suggest-card";

      const top = document.createElement("div");
      top.className = "suggest-top";

      const nm = String(c.name || "").toLowerCase();
      const guessId = dexByName[nm] || null;

      const im = document.createElement("img");
      im.alt = "";
      if (typeof c.id === "number") im.src = spriteUrl(c.id);
      else if (guessId) im.src = spriteUrl(guessId);
      else {
        // Try to resolve id lazily so we can show sprites even outside the first 151.
        resolvePokemonIdByName(c.name).then((id) => {
          if (id) im.src = spriteUrl(id);
        });
      }
      top.appendChild(im);

      const meta = document.createElement("div");
      const name = document.createElement("div");
      name.className = "suggest-name";
      name.textContent = c.name || "(unknown)";
      const types = document.createElement("div");
      types.className = "suggest-types";
      types.textContent = c.ability ? `Ability: ${c.ability}` : "";
      meta.appendChild(name);
      meta.appendChild(types);
      meta.appendChild(badges(c.types));
      top.appendChild(meta);

      card.appendChild(top);
      const kv = document.createElement("div");
      kv.className = "kv md";
      if (c.strengths) {
        const t = document.createElement("div");
        t.className = "kvt";
        t.textContent = "Strengths";
        const d = document.createElement("div");
        d.className = "kvd";
        d.innerHTML = markdownToHtml(c.strengths);
        kv.appendChild(t);
        kv.appendChild(d);
      }
      if (c.weaknesses) {
        const t = document.createElement("div");
        t.className = "kvt";
        t.textContent = "Weaknesses";
        const d = document.createElement("div");
        d.className = "kvd";
        d.innerHTML = markdownToHtml(c.weaknesses);
        kv.appendChild(t);
        kv.appendChild(d);
      }
      if (kv.children.length) card.appendChild(kv);
      grid.appendChild(card);
    }
  }

  if (!Array.isArray(suggestions)) return;
  if (Array.isArray(suggestions)) {
    $("resultMeta").textContent = `${$("resultMeta").textContent}${$("resultMeta").textContent ? " · " : ""}Suggestions: ${suggestions.length}`;
  }

  for (const s of suggestions) {
    const card = document.createElement("div");
    card.className = "suggest-card";

    const top = document.createElement("div");
    top.className = "suggest-top";

    const nm = String(s.name || "").toLowerCase();
    const guessId = dexByName[nm] || null;

    const im = document.createElement("img");
    im.alt = "";
    // If the model gives an id, use it; otherwise just leave the image blank.
    if (typeof s.id === "number") im.src = spriteUrl(s.id);
    else if (guessId) im.src = spriteUrl(guessId);
    else {
      resolvePokemonIdByName(s.name).then((id) => {
        if (id) im.src = spriteUrl(id);
      });
    }
    top.appendChild(im);

    const meta = document.createElement("div");
    const name = document.createElement("div");
    name.className = "suggest-name";
    name.textContent = s.name || "(unknown)";
    const types = document.createElement("div");
    types.className = "suggest-types";
    types.textContent = s.ability ? `Ability: ${s.ability}` : "";
    meta.appendChild(name);
    meta.appendChild(types);
    meta.appendChild(badges(s.types));
    top.appendChild(meta);

    const why = document.createElement("div");
    why.className = "suggest-why";
    why.classList.add("md");
    why.innerHTML = markdownToHtml(s.why || "");

    card.appendChild(top);
    const kv = document.createElement("div");
    kv.className = "kv md";
    if (s.strengths) {
      const t = document.createElement("div");
      t.className = "kvt";
      t.textContent = "Strengths";
      const d = document.createElement("div");
      d.className = "kvd";
      d.innerHTML = markdownToHtml(s.strengths);
      kv.appendChild(t);
      kv.appendChild(d);
    }
    if (s.weaknesses) {
      const t = document.createElement("div");
      t.className = "kvt";
      t.textContent = "Weaknesses";
      const d = document.createElement("div");
      d.className = "kvd";
      d.innerHTML = markdownToHtml(s.weaknesses);
      kv.appendChild(t);
      kv.appendChild(d);
    }
    if (kv.children.length) card.appendChild(kv);
    card.appendChild(why);
    grid.appendChild(card);
  }
}

async function main() {
  const state = { team: [null, null, null, null, null, null] };
  const teamEl = $("team");

  setButtonsEnabled(false);
  $("resultRaw").textContent = "";

  // Load a small dex list without N extra requests:
  // The list endpoint includes URLs with numeric ids; we build sprites from those ids.
  const res = await fetch("https://pokeapi.co/api/v2/pokemon?limit=151&offset=0");
  const data = await res.json();
  const pokemons = (data.results || [])
    .map((r) => {
      const id = parseIdFromUrl(r.url);
      if (!id) return null;
      return { id, name: String(r.name || "") };
    })
    .filter(Boolean);

  const dexByName = {};
  for (const p of pokemons) dexByName[p.name] = p.id;
  window.__DEX_BY_NAME__ = dexByName;

  setStatus(`Loaded ${pokemons.length} Pokemon`);

  function onChange() {
    // Update all slots so disabled/selected state stays consistent.
    for (const child of teamEl.children) {
      if (child && typeof child._update === "function") child._update();
    }
    const picked = collectTeam(state);
    setButtonsEnabled(picked.length > 0);
  }

  teamEl.innerHTML = "";
  for (let i = 0; i < 6; i++) {
    teamEl.appendChild(buildSlot(i, pokemons, state, onChange));
  }
  onChange();

  $("btnClear").addEventListener("click", () => {
    state.team = [null, null, null, null, null, null];
    $("resultRaw").textContent = "";
    $("resultGrid").innerHTML = "";
    onChange();
  });

  $("btnAnalyze").addEventListener("click", async () => {
    try {
      setActiveAction("analyze");
      setLoading("analyze", true);
      setStatus("Analyzing...");
      const payload = { team: collectTeam(state) };
      const res = await apiPost("/api/analyze", payload);
      renderResult(res.data);
      setStatus("Done");
    } catch (e) {
      setStatus(`Error: ${e.message}`);
    } finally {
      setLoading("analyze", false);
      onChange();
    }
  });

  $("btnSuggest").addEventListener("click", async () => {
    try {
      setActiveAction("suggest");
      setLoading("suggest", true);
      setStatus("Suggesting...");
      const payload = { team: collectTeam(state) };
      const res = await apiPost("/api/suggest", payload);
      renderResult(res.data);
      setStatus("Done");
    } catch (e) {
      setStatus(`Error: ${e.message}`);
    } finally {
      setLoading("suggest", false);
      onChange();
    }
  });
}

main().catch((e) => {
  setStatus(`Failed to load: ${e.message}`);
});
