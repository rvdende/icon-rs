# icon-rs

![icon-rs icons in light and dark themes, each with a different accent colour](https://raw.githubusercontent.com/rvdende/icon-rs/main/assets/splash.png)

SVG icons for CAD apps, embedded as Rust constants. Four kinds, drawn procedurally so the set
stays consistent:

- **Solid**: shaded isometric features, mates, relations and document types.
- **Sketch**: flat sketch tools, with the points the user picks in the accent colour.
- **Glyph**: bold sketch constraints and viewport markers, legible at 10-16 px.
- **Line**: interface icons.

Glyph and line icons are drawn in ink with a small accent detail, so apps can tint them.

Browse the icons and try out palettes: https://rvdende.github.io/icon-rs/

```rust
use icon_rs::{Palette, Rgb, EXTRUDE, UNDO};

let light: &str = EXTRUDE.svg;       // for light backgrounds
let dark: &str = EXTRUDE.svg_dark;   // for dark backgrounds
let svg = icon_rs::get("loft").unwrap().themed(is_dark);

// Any other theme: a line colour and an accent. Faces are neutral tints of the line.
let palette = Palette::new(Rgb(0x0c, 0x4a, 0x6e), Rgb(0xf5, 0x9e, 0x0b));
let custom: String = EXTRUDE.recolor(&palette);

// Glyph and line icons are ink plus a little accent: paint the ink any colour.
assert!(UNDO.kind.is_tintable());
let white: String = UNDO.tinted(Rgb::WHITE);

// In HTML, let CSS colour the ink.
let html: String = UNDO.current_color();
```

### Bevy

Enable the `bevy_color` feature to pass Bevy colours straight in and get them back out:

```toml
icon-rs = { version = "0.4", features = ["bevy_color"] }
```

```rust
use bevy_color::{Color, palettes::tailwind};

let palette = Palette::new(tailwind::SLATE_800, Color::srgb(0.2, 0.7, 0.95));
let mid: Color = palette.mid.into();
```

Colours convert through sRGB; alpha is dropped, since icons are opaque.

## Development

The icons are drawn in Rust by the generator in `xtask/`, a workspace crate that is not published.

- `icons/*.svg`, `icons/dark/*.svg`: 24x24, generated; don't edit by hand.
- `xtask/src/common.rs`: the palette, the drawing conventions for each kind, and the SVG and
  geometry helpers. `src/palette.rs` holds the crate's `Rgb` and `Palette`; the generator includes
  it too, and a test keeps the two palettes in step.
- `xtask/src/icons/`: one module per family (`part`, `sheet_metal`, `assembly`, `sketch`, `glyphs`,
  `ui_a`, `ui_b`, `eda` for schematic and PCB layout, `cam` for machining, `platform` for operating systems and code hosting). Each icon is a function returning its SVG
  elements, listed in the module's `icons()` in toolbar order.

```sh
cargo xtask gen                          # validate, fit and rewrite icons/ and src/generated.rs
cargo xtask gen --check                  # fail if those are out of date (CI runs this)
cargo xtask gen --only sketch --out DIR  # render one module into DIR for review
cargo xtask site                         # build the icon browser into site/
```

`gen` checks every icon (kebab-case name, colours allowed for its kind, well-formed XML, no ids),
zooms solid and sketch icons to their ink, and writes each light SVG with its dark variant.
GitHub Actions builds the site and deploys it on every push to `main`.

To add an icon, write its function in the right module, add it to that module's `icons()`, and run
`cargo xtask gen`. [HOWTO.md](HOWTO.md) walks through it with examples.

Review and promo images:

- `cargo run --release --example sheet -- OUT.png icons [NAME...]`: a labelled review sheet at
  96, 24 and 16 px in both themes. Pass the `--out` directory of a `--only` run in place of `icons`
  to review a module before regenerating.
- `cargo run --example splash assets/splash.png`: the banner above, with the accent swept around the colour wheel.
- `cargo run --example preview [out.png] [scale]`: renders a contact sheet (default `target/preview.png`).
