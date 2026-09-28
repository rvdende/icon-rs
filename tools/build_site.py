"""Builds the GitHub Pages site into site/. Run from anywhere: python3 tools/build_site.py

Everything the page knows comes from the crate: the icon list, order and constant names from the
icons! macro in src/lib.rs, the LIGHT and DARK palettes and the from_spot tint factors from the
same file, and the SVG sources from icons/. The page recolours icons in the browser with a port
of Icon::recolor and Palette::from_spot.
"""
import html, json, os, re, shutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "site")

lib = open(os.path.join(ROOT, "src", "lib.rs")).read()
cargo = open(os.path.join(ROOT, "Cargo.toml")).read()
crate = re.search(r'^name\s*=\s*"([^"]+)"', cargo, re.M).group(1)
version = re.search(r'^version\s*=\s*"([^"]+)"', cargo, re.M).group(1)
dep_version = version if version.startswith("0.0.") else ".".join(version.split(".")[:2])


def palette(name):
    body = re.search(rf"pub const {name}: Palette = Palette \{{(.*?)\}};", lib, re.S).group(1)
    return {slot: "#" + r + g + b for slot, r, g, b in
            re.findall(r"(\w+): Rgb\(0x(\w\w), 0x(\w\w), 0x(\w\w)\)", body)}


tints = re.search(r"\{ \((\d+), (\d+), (\d+)\) \} else \{ \((\d+), (\d+), (\d+)\) \}", lib).groups()
tints = {"dark": list(map(int, tints[:3])), "light": list(map(int, tints[3:]))}
icons = [
    {"konst": k, "name": n, "svg": open(os.path.join(ROOT, "icons", f"{n}.svg")).read()}
    for k, n in re.findall(r'(\w+)\s*=>\s*"([\w-]+)"', lib)
]

shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(os.path.join(OUT, "icons", "dark"))
for icon in icons:
    for sub in ("", "dark"):
        shutil.copy(os.path.join(ROOT, "icons", sub, f"{icon['name']}.svg"), os.path.join(OUT, "icons", sub))
open(os.path.join(OUT, ".nojekyll"), "w").close()

tiles = "\n".join(
    f'      <button class="tile" data-name="{html.escape(i["name"])}">'
    f'<img alt="" width="85" height="85"><span>{html.escape(i["name"])}</span></button>'
    for i in icons
)

page = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>icon-rs</title>
<meta name="description" content="SVG icons for CAD feature tools, embedded as Rust constants.">
<link rel="icon" href="icons/extrude.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script>
  // Set the theme before first paint: a saved choice wins, otherwise follow the system.
  (function () {
    let saved = null;
    try { saved = localStorage.getItem("icon-rs:theme"); } catch {}
    const dark = saved ? saved === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  })();
</script>
<style>
  :root {
    --bg: #fafafa; --surface: #ffffff; --tile: #ffffff; --tile-hover: #f4f4f5; --tile-text: #3f3f46;
    --border: #e4e4e7; --text: #18181b; --muted: #71717a; --accent: #2563eb; --preview-bg: #ffffff;
    --code-bg: #f4f4f5; --code-text: #27272a; --code-comment: #8a8a93; --code-string: #0f766e;
    --scrim: rgba(24, 24, 27, 0.45); --chip: #f4f4f5;
    color-scheme: light;
  }
  :root[data-theme="dark"] {
    --bg: #0f0f11; --surface: #18181b; --tile: #18181b; --tile-hover: #222226; --tile-text: #d4d4d8;
    --border: #2e2e33; --text: #f4f4f5; --muted: #a1a1aa; --accent: #60a5fa; --preview-bg: #0f0f11;
    --code-bg: #0f0f11; --code-text: #e4e4e7; --code-comment: #71717a; --code-string: #5eead4;
    --scrim: rgba(0, 0, 0, 0.6); --chip: #222226;
    color-scheme: dark;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--text);
    font: 15px/1.5 Inter, system-ui, sans-serif; -webkit-font-smoothing: antialiased;
  }
  button { font: inherit; color: inherit; }
  .container { max-width: 1040px; margin: 0 auto; padding: 56px 16px 80px; }
  header { display: flex; gap: 16px; align-items: flex-start; margin-bottom: 28px; }
  header .intro { flex: 1; min-width: 0; }
  h1 { margin: 0 0 6px; font-size: 32px; font-weight: 700; letter-spacing: -0.02em; }
  h1 small { font-size: 14px; font-weight: 500; color: var(--muted); margin-left: 8px; letter-spacing: 0; }
  header p { margin: 0 0 18px; color: var(--muted); max-width: 60ch; }
  .links { display: flex; flex-wrap: wrap; gap: 8px 16px; align-items: center; }
  .links a { color: var(--accent); text-decoration: none; font-weight: 500; }
  .links a:hover { text-decoration: underline; }
  .install {
    font: 13px/1 "JetBrains Mono", ui-monospace, monospace; background: var(--surface);
    border: 1px solid var(--border); border-radius: 8px; padding: 8px 12px; color: var(--text);
  }
  .icon-btn {
    flex: none; display: inline-grid; place-items: center; width: 38px; height: 38px; border-radius: 10px;
    border: 1px solid var(--border); background: var(--surface); color: var(--muted); cursor: pointer;
  }
  .icon-btn:hover { color: var(--text); border-color: var(--accent); }
  .icon-btn svg { width: 18px; height: 18px; }
  :root[data-theme="dark"] .sun, :root[data-theme="light"] .moon { display: none; }

  /* Palette playground */
  .palette {
    margin-bottom: 24px; padding: 16px; border: 1px solid var(--border); border-radius: 14px;
    background: var(--surface); display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.25fr); gap: 16px 24px;
  }
  @media (max-width: 760px) { .palette { grid-template-columns: minmax(0, 1fr); } }
  .palette h2 { margin: 0 0 4px; font-size: 15px; font-weight: 600; }
  .palette .hint { margin: 0 0 14px; color: var(--muted); font-size: 13px; }
  .pickers { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 14px; }
  .picker { display: flex; align-items: center; gap: 8px; }
  .picker label { font-size: 13px; font-weight: 500; min-width: 30px; }
  .picker input[type=color] {
    width: 36px; height: 32px; padding: 2px; border: 1px solid var(--border); border-radius: 8px;
    background: var(--surface); cursor: pointer;
  }
  .picker input[type=text] {
    width: 86px; height: 32px; padding: 0 8px; border: 1px solid var(--border); border-radius: 8px;
    background: var(--bg); color: var(--text); font: 13px "JetBrains Mono", ui-monospace, monospace;
  }
  .picker input[type=text]:invalid { border-color: #dc2626; }
  .presets { display: flex; flex-wrap: wrap; gap: 6px; }
  .chip {
    display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px 4px 6px; border-radius: 999px;
    border: 1px solid var(--border); background: var(--chip); font-size: 12px; font-weight: 500; cursor: pointer;
  }
  .chip:hover { border-color: var(--accent); }
  .chip[aria-pressed="true"] { border-color: var(--accent); box-shadow: inset 0 0 0 1px var(--accent); }
  .chip i { width: 14px; height: 14px; border-radius: 50%; border: 2px solid; display: inline-block; }
  .swatches { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 6px; margin-bottom: 12px; }
  .swatch { font-size: 11px; color: var(--muted); }
  .swatch b {
    display: block; height: 28px; border-radius: 6px; border: 1px solid var(--border); margin-bottom: 4px;
  }
  .swatch code { display: block; font: 11px "JetBrains Mono", ui-monospace, monospace; color: var(--text); }

  .grid { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 12px; }
  @media (max-width: 900px) { .grid { grid-template-columns: repeat(5, minmax(0, 1fr)); } }
  @media (max-width: 640px) { .grid { grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; } }
  @media (max-width: 420px) { .grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
  .tile {
    display: flex; flex-direction: column; align-items: center; gap: 10px;
    padding: 18px 6px 12px; border: 1px solid var(--border); border-radius: 12px;
    background: var(--tile); color: var(--tile-text); font: 500 13px/1.2 Inter, system-ui, sans-serif;
    cursor: pointer; transition: background .12s, border-color .12s, transform .12s;
  }
  .tile:hover { background: var(--tile-hover); border-color: var(--accent); }
  .tile:focus-visible, .chip:focus-visible, .icon-btn:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .tile:active { transform: scale(0.98); }
  .tile img { width: clamp(44px, 8.2vw, 85px); height: auto; aspect-ratio: 1; }
  .tile span { overflow-wrap: anywhere; text-align: center; }

  dialog {
    width: min(620px, calc(100vw - 32px)); padding: 0; border: 1px solid var(--border);
    border-radius: 14px; background: var(--surface); color: var(--text);
    box-shadow: 0 24px 64px rgba(0, 0, 0, 0.25);
  }
  dialog::backdrop { background: var(--scrim); }
  .sheet-head { display: flex; align-items: center; gap: 16px; padding: 20px 20px 0; }
  .sheet-head .preview {
    flex: none; width: 96px; height: 96px; border-radius: 12px; background: var(--preview-bg);
    border: 1px solid var(--border); display: grid; place-items: center;
  }
  .sheet-head .preview img { width: 72px; height: 72px; }
  .sheet-head h2 { margin: 0; font-size: 20px; }
  .sheet-head code { font: 13px "JetBrains Mono", ui-monospace, monospace; color: var(--muted); }
  .sheet-head .actions { margin-top: 8px; display: flex; gap: 12px; }
  .sheet-head .actions a { color: var(--accent); font-weight: 500; text-decoration: none; font-size: 14px; }
  .close {
    margin-left: auto; align-self: flex-start; width: 32px; height: 32px; border-radius: 8px;
    border: 0; background: transparent; color: var(--muted); font-size: 22px; line-height: 1; cursor: pointer;
  }
  .close:hover { background: var(--code-bg); color: var(--text); }
  .sheet-body { padding: 16px 20px 20px; }
  h3 { margin: 16px 0 8px; font-size: 13px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
  .palette h3 { margin-top: 0; }
  .code { position: relative; }
  pre {
    margin: 0; padding: 14px 16px; overflow-x: auto; border-radius: 10px; border: 1px solid var(--border);
    background: var(--code-bg); color: var(--code-text); font: 13px/1.6 "JetBrains Mono", ui-monospace, monospace;
  }
  pre .c { color: var(--code-comment); } pre .s { color: var(--code-string); }
  .copy {
    position: absolute; top: 8px; right: 8px; padding: 4px 10px; border-radius: 6px; cursor: pointer;
    border: 1px solid var(--border); background: var(--surface); color: var(--muted); font: 500 12px Inter, sans-serif;
  }
  .copy:hover { color: var(--text); }
  footer { margin-top: 48px; color: var(--muted); font-size: 13px; }
</style>
</head>
<body>
  <main class="container">
    <header>
      <div class="intro">
        <h1>icon-rs<small>v__VERSION__</small></h1>
        <p>SVG icons for CAD feature tools, embedded as Rust constants. Click an icon to see how to use it.</p>
        <div class="links">
          <code class="install">cargo add __CRATE__</code>
          <a href="https://crates.io/crates/__CRATE__">crates.io</a>
          <a href="https://docs.rs/__CRATE__">docs.rs</a>
          <a href="https://github.com/rvdende/icon-rs">GitHub</a>
        </div>
      </div>
      <button class="icon-btn" id="theme" aria-label="Toggle light and dark theme" title="Toggle theme">
        <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>
        <svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>
      </button>
    </header>

    <section class="palette" aria-label="Palette playground">
      <div>
        <h2>Palette</h2>
        <p class="hint">Pick a line colour and a spot colour; the face shades are derived from the spot, the same way <code>Palette::from_spot</code> does it.</p>
        <div class="pickers">
          <div class="picker">
            <label for="ink-hex">Line</label>
            <input type="color" id="ink-color" aria-label="Line colour">
            <input type="text" id="ink-hex" pattern="#?[0-9a-fA-F]{6}" spellcheck="false">
          </div>
          <div class="picker">
            <label for="spot-hex">Spot</label>
            <input type="color" id="spot-color" aria-label="Spot colour">
            <input type="text" id="spot-hex" pattern="#?[0-9a-fA-F]{6}" spellcheck="false">
          </div>
        </div>
        <div class="presets" id="presets"></div>
      </div>
      <div>
        <h3>Derived palette</h3>
        <div class="swatches" id="swatches"></div>
        <div class="code"><pre id="code-palette"></pre><button class="copy" data-for="code-palette">Copy</button></div>
      </div>
    </section>

    <section class="grid" aria-label="Icons">
__TILES__
    </section>
    <footer>__COUNT__ icons · MIT or Apache-2.0</footer>
  </main>

  <dialog id="sheet" aria-labelledby="sheet-title">
    <div class="sheet-head">
      <div class="preview"><img id="sheet-img" alt=""></div>
      <div>
        <h2 id="sheet-title"></h2>
        <code id="sheet-const"></code>
        <div class="actions"><a id="sheet-download">Download SVG</a></div>
      </div>
      <button class="close" aria-label="Close">&times;</button>
    </div>
    <div class="sheet-body">
      <h3>Use in Rust</h3>
      <div class="code"><pre id="code-rust"></pre><button class="copy" data-for="code-rust">Copy</button></div>
      <h3>Rasterise with resvg</h3>
      <div class="code"><pre id="code-resvg"></pre><button class="copy" data-for="code-resvg">Copy</button></div>
    </div>
  </dialog>

<script>
const ICONS = __ICONS__;
const PALETTES = __PALETTES__;
const TINTS = __TINTS__;
const CRATE = "__CRATE__", VERSION = "__DEP_VERSION__";
const SLOTS = ["ink", "top", "soft", "mid", "shade"];
const PRESETS = [
  { name: "Default" },
  { name: "Slate", ink: "#0f172a", spot: "#94a3b8" },
  { name: "Sky", ink: "#0c4a6e", spot: "#38bdf8" },
  { name: "Teal", ink: "#134e4a", spot: "#2dd4bf" },
  { name: "Amber", ink: "#451a03", spot: "#f59e0b" },
  { name: "Rose", ink: "#4c0519", spot: "#fb7185" },
  { name: "Night", ink: "#e0f2fe", spot: "#1e40af" },
];
const byName = Object.fromEntries(ICONS.map(i => [i.name, i]));
const $ = id => document.getElementById(id);

const store = {
  get(key) { try { return localStorage.getItem(`icon-rs:${key}`); } catch { return null; } },
  set(key, value) {
    try { value == null ? localStorage.removeItem(`icon-rs:${key}`) : localStorage.setItem(`icon-rs:${key}`, value); } catch {}
  },
};

// Ports of Rgb::mix, Rgb::luma and Palette::from_spot; integer maths so results match exactly.
const parse = hex => { const m = /^#?([0-9a-f]{6})$/i.exec(hex.trim()); return m ? "#" + m[1].toLowerCase() : null; };
const rgb = hex => [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16));
const toHex = c => "#" + c.map(v => v.toString(16).padStart(2, "0")).join("");
const mix = (a, b, pct) => toHex(rgb(a).map((v, i) => Math.floor((v * (100 - pct) + rgb(b)[i] * pct + 50) / 100)));
const luma = hex => { const [r, g, b] = rgb(hex); return Math.floor((r * 299 + g * 587 + b * 114) / 1000); };
function fromSpot(ink, spot) {
  const [top, soft, shade] = luma(ink) > luma(spot) ? TINTS.dark : TINTS.light;
  return { ink, top: mix(spot, "#ffffff", top), soft: mix(spot, "#ffffff", soft), mid: spot, shade: mix(spot, "#000000", shade) };
}

// Port of Icon::recolor: every light-palette colour maps to its slot in one pass.
function recolor(svg, palette) {
  const map = Object.fromEntries(SLOTS.map(s => [PALETTES.light[s], palette[s]]));
  return svg.replace(/#[0-9a-f]{6}/g, m => map[m] ?? m);
}
const dataUri = svg => "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);

const state = {
  theme: document.documentElement.dataset.theme,
  custom: (() => { try { return JSON.parse(store.get("palette")); } catch { return null; } })(),
};
const current = () => state.custom ? fromSpot(state.custom.ink, state.custom.spot) : PALETTES[state.theme];
const rgbLit = hex => `Rgb(${rgb(hex).map(v => "0x" + v.toString(16).padStart(2, "0")).join(", ")})`;

function paletteExpr() {
  if (state.custom) return `Palette::from_spot(
    ${rgbLit(state.custom.ink)},  // line
    ${rgbLit(state.custom.spot)}, // spot
)`;
  return state.theme === "dark" ? "Palette::DARK" : "Palette::LIGHT";
}

function render() {
  const palette = current();
  document.querySelectorAll(".tile").forEach(t => { t.querySelector("img").src = dataUri(recolor(byName[t.dataset.name].svg, palette)); });

  const ink = state.custom ? state.custom.ink : palette.ink;
  const spot = state.custom ? state.custom.spot : palette.mid;
  for (const [key, value] of [["ink", ink], ["spot", spot]]) {
    $(`${key}-color`).value = value;
    if (document.activeElement !== $(`${key}-hex`)) $(`${key}-hex`).value = value;
  }
  $("swatches").innerHTML = SLOTS.map(s => `<div class="swatch"><b style="background:${palette[s]}"></b>${s}<code>${palette[s]}</code></div>`).join("");
  document.querySelectorAll(".chip").forEach(c => {
    const p = PRESETS[+c.dataset.i];
    const on = p.ink ? state.custom?.ink === p.ink && state.custom?.spot === p.spot : !state.custom;
    c.setAttribute("aria-pressed", on);
  });
  setCode("code-palette", `use icon_rs::{Palette, Rgb};

let palette = ${paletteExpr()};
let svg: String = icon_rs::EXTRUDE.recolor(&palette);`);
  if (sheet.open) open(sheet.dataset.name);
}

function setCode(id, src) {
  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  const pre = $(id);
  pre.dataset.raw = src;
  pre.innerHTML = src.split("\n").map(line => {
    const at = line.indexOf("//");
    const code = at < 0 ? line : line.slice(0, at);
    const comment = at < 0 ? "" : `<span class="c">${esc(line.slice(at))}</span>`;
    return esc(code).replace(/"[^"]*"/g, m => `<span class="s">${m}</span>`) + comment;
  }).join("\n");
}

function setCustom(ink, spot) {
  state.custom = ink && spot ? { ink, spot } : null;
  store.set("palette", state.custom ? JSON.stringify(state.custom) : null);
  render();
}

// Theme toggle
$("theme").addEventListener("click", () => {
  state.theme = state.theme === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = state.theme;
  store.set("theme", state.theme);
  render();
});
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", e => {
  if (store.get("theme")) return;
  state.theme = e.matches ? "dark" : "light";
  document.documentElement.dataset.theme = state.theme;
  render();
});

// Palette inputs
function currentPair() {
  const p = current();
  return state.custom ? { ...state.custom } : { ink: p.ink, spot: p.mid };
}
for (const key of ["ink", "spot"]) {
  $(`${key}-color`).addEventListener("input", e => { const pair = currentPair(); pair[key] = e.target.value; setCustom(pair.ink, pair.spot); });
  $(`${key}-hex`).addEventListener("input", e => {
    const hex = parse(e.target.value);
    if (!hex) return;
    const pair = currentPair(); pair[key] = hex; setCustom(pair.ink, pair.spot);
  });
  $(`${key}-hex`).addEventListener("blur", render);
}
$("presets").innerHTML = PRESETS.map((p, i) => {
  const dot = p.ink ? `<i style="background:${p.spot};border-color:${p.ink}"></i>` : `<i style="background:${PALETTES.light.mid};border-color:${PALETTES.light.ink}"></i>`;
  return `<button class="chip" data-i="${i}" aria-pressed="false">${dot}${p.name}</button>`;
}).join("");
document.querySelectorAll(".chip").forEach(c => c.addEventListener("click", () => {
  const p = PRESETS[+c.dataset.i];
  setCustom(p.ink, p.spot);
}));

// Icon sheet
const sheet = $("sheet");
function rustSnippet(i) {
  if (state.custom) return `// Cargo.toml: ${CRATE} = "${VERSION}"
use icon_rs::{Palette, Rgb, ${i.konst}};

// The palette picked on this page.
let palette = ${paletteExpr()};
let svg: String = ${i.konst}.recolor(&palette);`;
  return `// Cargo.toml: ${CRATE} = "${VERSION}"
use icon_rs::${i.konst};

// SVG source for light and dark themes, embedded at compile time.
let light: &str = ${i.konst}.svg;
let dark: &str = ${i.konst}.svg_dark;

// Or look it up by name and pick the variant for the theme.
let svg = icon_rs::get("${i.name}").unwrap().themed(is_dark);`;
}

function resvgSnippet(i) {
  const src = state.custom ? `&${i.konst}.recolor(&palette)` : `icon_rs::${i.konst}.svg`;
  return `// Cargo.toml: resvg = "0.48"
use resvg::{tiny_skia, usvg};

let opts = usvg::Options::default();
let tree = usvg::Tree::from_str(${src}, &opts)?;

// 48px output from the 24px view box.
let mut pixmap = tiny_skia::Pixmap::new(48, 48).unwrap();
let transform = tiny_skia::Transform::from_scale(2.0, 2.0);
resvg::render(&tree, transform, &mut pixmap.as_mut());
pixmap.save_png("${i.name}.png")?;`;
}

function open(name) {
  const i = byName[name];
  if (!i) return;
  const uri = dataUri(recolor(i.svg, current()));
  sheet.dataset.name = name;
  $("sheet-title").textContent = i.name;
  $("sheet-const").textContent = `icon_rs::${i.konst}`;
  $("sheet-img").src = uri;
  $("sheet-download").href = uri;
  $("sheet-download").setAttribute("download", `${i.name}.svg`);
  setCode("code-rust", rustSnippet(i));
  setCode("code-resvg", resvgSnippet(i));
  if (!sheet.open) sheet.showModal();
  if (location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
}
function close() { if (sheet.open) sheet.close(); }

sheet.addEventListener("close", () => history.replaceState(null, "", location.pathname + location.search));
sheet.addEventListener("click", e => { if (e.target === sheet) close(); });
sheet.querySelector(".close").addEventListener("click", close);
document.querySelectorAll(".tile").forEach(t => t.addEventListener("click", () => open(t.dataset.name)));
document.querySelectorAll(".copy").forEach(b => b.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText($(b.dataset.for).dataset.raw);
    b.textContent = "Copied";
  } catch { b.textContent = "Copy failed"; }
  setTimeout(() => (b.textContent = "Copy"), 1400);
}));
window.addEventListener("hashchange", () => location.hash ? open(decodeURIComponent(location.hash.slice(1))) : close());

render();
if (location.hash) open(decodeURIComponent(location.hash.slice(1)));
</script>
</body>
</html>
"""

page = (page.replace("__TILES__", tiles)
            .replace("__ICONS__", json.dumps(icons).replace("</", "<\\/"))
            .replace("__PALETTES__", json.dumps({"light": palette("LIGHT"), "dark": palette("DARK")}))
            .replace("__TINTS__", json.dumps(tints))
            .replace("__COUNT__", str(len(icons)))
            .replace("__VERSION__", version)
            .replace("__DEP_VERSION__", dep_version)
            .replace("__CRATE__", crate))
with open(os.path.join(OUT, "index.html"), "w") as f:
    f.write(page)
print(f"site/ built with {len(icons)} icons")
