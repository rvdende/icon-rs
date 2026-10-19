//! Builds the GitHub Pages site into site/:
//!
//!     cargo xtask site
//!
//! Everything the page knows comes from the crate: the icon list, order and constant names from
//! src/generated.rs, the LIGHT and DARK palettes and the Palette::new tint factors from
//! src/palette.rs, and the SVG sources from icons/. The page recolours icons in the browser with
//! a port of Icon::recolor and Palette::new.

use crate::palette::Palette;
use std::fmt::Write;
use std::path::Path;

const TEMPLATE: &str = include_str!("../site/index.html");

const KIND_TITLES: [(&str, &str); 4] =
    [("Solid", "Features and assembly"), ("Sketch", "Sketch"), ("Glyph", "Constraints and markers"), ("Line", "Interface")];

struct Icon {
    konst: String,
    name: String,
    kind: String,
    title: String,
    svg: String,
}

/// HTML text and attribute escaping: & < > " and '.
fn escape(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.chars() {
        match c {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\'' => out.push_str("&#x27;"),
            c => out.push(c),
        }
    }
    out
}

/// A JSON string literal, ASCII only (other characters as \u escapes).
fn json_str(s: &str) -> String {
    let mut out = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            '\u{8}' => out.push_str("\\b"),
            '\u{c}' => out.push_str("\\f"),
            ' '..='~' => out.push(c),
            c => {
                for unit in c.encode_utf16(&mut [0; 2]) {
                    write!(out, "\\u{unit:04x}").unwrap();
                }
            }
        }
    }
    out.push('"');
    out
}

/// A JSON object from (key, already-encoded value) pairs.
fn json_obj(fields: &[(&str, String)]) -> String {
    let fields: Vec<String> = fields.iter().map(|(k, v)| format!("{}: {v}", json_str(k))).collect();
    format!("{{{}}}", fields.join(", "))
}

fn json_list(items: impl IntoIterator<Item = String>) -> String {
    format!("[{}]", items.into_iter().collect::<Vec<_>>().join(", "))
}

fn palette_json(p: &Palette) -> String {
    let names = ["ink", "top", "soft", "mid", "shade", "accent"];
    let fields: Vec<(&str, String)> = names.iter().zip(p.slots()).map(|(n, c)| (*n, json_str(&c.to_hex()))).collect();
    json_obj(&fields)
}

/// The `name = "..."` and `version = "..."` of the root package.
fn package_field(cargo: &str, key: &str) -> Result<String, String> {
    cargo
        .lines()
        .find_map(|l| {
            let rest = l.strip_prefix(key)?.trim_start().strip_prefix('=')?.trim();
            Some(rest.strip_prefix('"')?.strip_suffix('"')?.to_owned())
        })
        .ok_or_else(|| format!("Cargo.toml has no {key}"))
}

/// The icons listed in src/generated.rs, with their light SVGs.
fn icons(root: &Path) -> Result<Vec<Icon>, String> {
    let generated = read(&root.join("src/generated.rs"))?;
    let mut out = Vec::new();
    for l in generated.lines() {
        // KONST => ("name", Kind, "title"),
        let Some((konst, rest)) = l.trim().split_once(" => (\"") else { continue };
        let (name, rest) = rest.split_once("\", ").ok_or_else(|| format!("bad line: {l}"))?;
        let (kind, rest) = rest.split_once(", \"").ok_or_else(|| format!("bad line: {l}"))?;
        let title = rest.strip_suffix("\"),").ok_or_else(|| format!("bad line: {l}"))?.replace("\\\"", "\"");
        let svg = read(&root.join("icons").join(format!("{name}.svg")))?;
        out.push(Icon { konst: konst.into(), name: name.into(), kind: kind.into(), title, svg });
    }
    Ok(out)
}

fn read(p: &Path) -> Result<String, String> {
    std::fs::read_to_string(p).map_err(|e| format!("{}: {e}", p.display()))
}

fn tile(i: &Icon) -> String {
    format!(
        r#"      <button class="tile" data-name="{}" data-search="{}" title="{}"><img alt="" width="85" height="85"><span>{}</span></button>"#,
        escape(&i.name),
        escape(&format!("{} {}", i.name, i.title).to_lowercase()),
        escape(&i.title),
        escape(&i.name)
    )
}

pub fn main(root: &Path) -> Result<(), String> {
    let out = root.join("site");
    let cargo = read(&root.join("Cargo.toml"))?;
    let (krate, version) = (package_field(&cargo, "name")?, package_field(&cargo, "version")?);
    let dep_version = if version.starts_with("0.0.") { version.clone() } else { version.split('.').take(2).collect::<Vec<_>>().join(".") };
    let icons = icons(root)?;

    let io = |e: std::io::Error| e.to_string();
    if out.exists() {
        std::fs::remove_dir_all(&out).map_err(io)?;
    }
    std::fs::create_dir_all(out.join("icons/dark")).map_err(io)?;
    for icon in &icons {
        for sub in ["", "dark"] {
            let file = format!("{}.svg", icon.name);
            std::fs::copy(root.join("icons").join(sub).join(&file), out.join("icons").join(sub).join(&file)).map_err(io)?;
        }
    }
    std::fs::write(out.join(".nojekyll"), "").map_err(io)?;

    let mut groups = Vec::new();
    for (kind, heading) in KIND_TITLES {
        let members: Vec<&Icon> = icons.iter().filter(|i| i.kind == kind).collect();
        if !members.is_empty() {
            groups.push(format!(
                "    <div class=\"group\" data-kind=\"{kind}\">\n    <h2>{heading} <small>{}</small></h2>\n    \
                 <section class=\"grid\" aria-label=\"{heading}\">\n{}\n    </section>\n    </div>",
                members.len(),
                members.iter().map(|i| tile(i)).collect::<Vec<_>>().join("\n")
            ));
        }
    }

    let icons_json = json_list(icons.iter().map(|i| {
        json_obj(&[
            ("konst", json_str(&i.konst)),
            ("name", json_str(&i.name)),
            ("kind", json_str(&i.kind)),
            ("title", json_str(&i.title)),
            ("svg", json_str(&i.svg)),
        ])
    }));
    let palettes = json_obj(&[("light", palette_json(&Palette::LIGHT)), ("dark", palette_json(&Palette::DARK))]);
    let tints_list = |t: [u32; 4]| json_list(t.map(|v| v.to_string()));
    let tints = json_obj(&[("dark", tints_list(Palette::TINTS_LIGHT_INK)), ("light", tints_list(Palette::TINTS_DARK_INK))]);

    let page = TEMPLATE
        .replace("__TILES__", &groups.join("\n"))
        .replace("__ICONS__", &icons_json.replace("</", "<\\/"))
        .replace("__PALETTES__", &palettes)
        .replace("__TINTS__", &tints)
        .replace("__COUNT__", &icons.len().to_string())
        .replace("__VERSION__", &version)
        .replace("__DEP_VERSION__", &dep_version)
        .replace("__CRATE__", &krate);
    std::fs::write(out.join("index.html"), page).map_err(io)?;
    println!("site/ built with {} icons", icons.len());
    Ok(())
}
