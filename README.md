# icon-rs

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
```

### Bevy

Enable the `bevy_color` feature to pass Bevy colours straight in and get them back out:

```toml
icon-rs = { version = "0.2", features = ["bevy_color"] }
```

```rust
use bevy_color::{Color, palettes::tailwind};

let palette = Palette::new(tailwind::SLATE_800, Color::srgb(0.2, 0.7, 0.95));
let mid: Color = palette.mid.into();
```

Colours convert through sRGB; alpha is dropped, since icons are opaque.

- `icons/*.svg`, `icons/dark/*.svg`: 24x24, generated; don't edit by hand.
- `tools/icons/`: the generator. `common.py` holds the palette, conventions and geometry helpers;
  each family is one module (`part`, `assembly`, `sketch`, `glyphs`, `ui_a`, `ui_b`).
  `python3 tools/icons/gen.py` validates every icon and rewrites `icons/` and `src/generated.rs`.
- `cargo run --release --example sheet -- OUT.png icons [NAME...]`: a labelled review sheet at
  96, 24 and 16 px in both themes.
- `tools/build_site.py`: builds the icon browser into `site/`; GitHub Actions deploys it on every push to `main`.
- `cargo run --example preview [out.png] [scale]`: renders a contact sheet (default `target/preview.png`).
