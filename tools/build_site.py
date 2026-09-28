"""Builds the GitHub Pages site into site/. Run from anywhere: python3 tools/build_site.py

The icon list, order and constant names come from the icons! macro in src/lib.rs, so the page
always matches what the crate exports.
"""
import html, json, os, re, shutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "site")

lib = open(os.path.join(ROOT, "src", "lib.rs")).read()
icons = [{"konst": k, "name": n} for k, n in re.findall(r'(\w+)\s*=>\s*"([\w-]+)"', lib)]
cargo = open(os.path.join(ROOT, "Cargo.toml")).read()
crate = re.search(r'^name\s*=\s*"([^"]+)"', cargo, re.M).group(1)
version = re.search(r'^version\s*=\s*"([^"]+)"', cargo, re.M).group(1)

shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(os.path.join(OUT, "icons", "dark"))
for icon in icons:
    for sub in ("", "dark"):
        shutil.copy(os.path.join(ROOT, "icons", sub, f"{icon['name']}.svg"), os.path.join(OUT, "icons", sub))
open(os.path.join(OUT, ".nojekyll"), "w").close()

tiles = "\n".join(
    f'      <button class="tile" data-name="{html.escape(i["name"])}">'
    f'<picture><source srcset="icons/dark/{html.escape(i["name"])}.svg" media="(prefers-color-scheme: dark)">'
    f'<img src="icons/{html.escape(i["name"])}.svg" alt="" width="85" height="85"></picture>'
    f'<span>{html.escape(i["name"])}</span></button>'
    for i in icons
)

page = """<!doctype html>
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
<style>
  :root {
    --bg: #fafafa; --surface: #ffffff; --tile: #ffffff; --tile-hover: #f4f4f5; --tile-text: #3f3f46; --preview-bg: #ffffff;
    --border: #e4e4e7; --text: #18181b; --muted: #71717a; --accent: #2563eb;
    --code-bg: #f4f4f5; --code-text: #27272a; --code-comment: #8a8a93; --code-string: #0f766e;
    --scrim: rgba(24, 24, 27, 0.45);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0f0f11; --surface: #18181b;
      --border: #2e2e33; --text: #f4f4f5; --muted: #a1a1aa; --accent: #60a5fa;
      --tile: #18181b; --tile-hover: #222226; --tile-text: #d4d4d8; --preview-bg: #0f0f11;
      --code-bg: #0f0f11; --code-text: #e4e4e7; --code-comment: #71717a; --code-string: #5eead4;
      --scrim: rgba(0, 0, 0, 0.6);
    }
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--text);
    font: 15px/1.5 Inter, system-ui, sans-serif; -webkit-font-smoothing: antialiased;
  }
  .container { max-width: 1040px; margin: 0 auto; padding: 56px 16px 80px; }
  header { margin-bottom: 36px; }
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
  .tile:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  .tile:active { transform: scale(0.98); }
  .tile picture { display: contents; }
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
  .sheet-body h3 { margin: 16px 0 8px; font-size: 13px; font-weight: 600; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }
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
  footer a { color: inherit; }
</style>
</head>
<body>
  <main class="container">
    <header>
      <h1>icon-rs<small>v__VERSION__</small></h1>
      <p>SVG icons for CAD feature tools, embedded as Rust constants. Click an icon to see how to use it.</p>
      <div class="links">
        <code class="install">cargo add __CRATE__</code>
        <a href="https://crates.io/crates/__CRATE__">crates.io</a>
        <a href="https://docs.rs/__CRATE__">docs.rs</a>
        <a href="https://github.com/rvdende/icon-rs">GitHub</a>
      </div>
    </header>
    <section class="grid" aria-label="Icons">
__TILES__
    </section>
    <footer>__COUNT__ icons · MIT or Apache-2.0</footer>
  </main>

  <dialog id="sheet" aria-labelledby="sheet-title">
    <div class="sheet-head">
      <div class="preview"><picture><source id="sheet-img-dark" media="(prefers-color-scheme: dark)"><img id="sheet-img" alt=""></picture></div>
      <div>
        <h2 id="sheet-title"></h2>
        <code id="sheet-const"></code>
        <div class="actions"><a id="sheet-download" download>Download SVG</a><a id="sheet-download-dark" download>Dark SVG</a></div>
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
const CRATE = "__CRATE__", VERSION = "__DEP_VERSION__";
const byName = Object.fromEntries(ICONS.map(i => [i.name, i]));
const sheet = document.getElementById("sheet");

function rustSnippet(i) {
  return `// Cargo.toml: ${CRATE} = "${VERSION}"
use icon_rs::{Palette, ${i.konst}};

// SVG source for light and dark themes, embedded at compile time.
let light: &str = ${i.konst}.svg;
let dark: &str = ${i.konst}.svg_dark;

// Or look it up by name and pick the variant for the theme.
let svg = icon_rs::get("${i.name}").unwrap().themed(is_dark);

// Or recolour it for your own theme.
let custom: String = ${i.konst}.recolor(&Palette {
    ink: "#1e293b", top: "#f8fafc", soft: "#cbd5e1",
    mid: "#94a3b8", shade: "#64748b",
});`;
}

function resvgSnippet(i) {
  return `// Cargo.toml: resvg = "0.48"
use resvg::{tiny_skia, usvg};

let opts = usvg::Options::default();
let tree = usvg::Tree::from_str(icon_rs::${i.konst}.svg, &opts)?;

// 48px output from the 24px view box.
let mut pixmap = tiny_skia::Pixmap::new(48, 48).unwrap();
let transform = tiny_skia::Transform::from_scale(2.0, 2.0);
resvg::render(&tree, transform, &mut pixmap.as_mut());
pixmap.save_png("${i.name}.png")?;`;
}

function highlight(src) {
  const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  return src.split("\\n").map(line => {
    const at = line.indexOf("//");
    const code = at < 0 ? line : line.slice(0, at);
    const comment = at < 0 ? "" : `<span class="c">${esc(line.slice(at))}</span>`;
    return esc(code).replace(/"[^"]*"/g, m => `<span class="s">${m}</span>`) + comment;
  }).join("\\n");
}

function open(name) {
  const i = byName[name];
  if (!i) return;
  document.getElementById("sheet-title").textContent = i.name;
  document.getElementById("sheet-const").textContent = `icon_rs::${i.konst}`;
  document.getElementById("sheet-img").src = `icons/${i.name}.svg`;
  document.getElementById("sheet-img-dark").srcset = `icons/dark/${i.name}.svg`;
  const dl = document.getElementById("sheet-download");
  dl.href = `icons/${i.name}.svg`;
  dl.setAttribute("download", `${i.name}.svg`);
  const dld = document.getElementById("sheet-download-dark");
  dld.href = `icons/dark/${i.name}.svg`;
  dld.setAttribute("download", `${i.name}-dark.svg`);
  for (const [id, fn] of [["code-rust", rustSnippet], ["code-resvg", resvgSnippet]]) {
    const pre = document.getElementById(id);
    pre.dataset.raw = fn(i);
    pre.innerHTML = highlight(pre.dataset.raw);
  }
  if (!sheet.open) sheet.showModal();
  if (location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
}

function close() {
  if (sheet.open) sheet.close();
}

sheet.addEventListener("close", () => history.replaceState(null, "", location.pathname + location.search));
sheet.addEventListener("click", e => { if (e.target === sheet) close(); });
sheet.querySelector(".close").addEventListener("click", close);
document.querySelectorAll(".tile").forEach(t => t.addEventListener("click", () => open(t.dataset.name)));
document.querySelectorAll(".copy").forEach(b => b.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(document.getElementById(b.dataset.for).dataset.raw);
    b.textContent = "Copied";
  } catch { b.textContent = "Copy failed"; }
  setTimeout(() => (b.textContent = "Copy"), 1400);
}));
window.addEventListener("hashchange", () => location.hash ? open(location.hash.slice(1)) : close());
if (location.hash) open(decodeURIComponent(location.hash.slice(1)));
</script>
</body>
</html>
"""

dep_version = version if version.startswith("0.0.") else ".".join(version.split(".")[:2])
page = (page.replace("__TILES__", tiles)
            .replace("__ICONS__", json.dumps(icons))
            .replace("__COUNT__", str(len(icons)))
            .replace("__VERSION__", version)
            .replace("__DEP_VERSION__", dep_version)
            .replace("__CRATE__", crate))
with open(os.path.join(OUT, "index.html"), "w") as f:
    f.write(page)
print(f"site/ built with {len(icons)} icons")
