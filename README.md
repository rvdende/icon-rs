# icon-rs

Original SVG icons for CAD feature tools (extrude, revolve, sweep, loft, thicken, enclose, fillet,
chamfer, shell, pattern, boolean), embedded as Rust constants.

Browse the icons and try out palettes: https://rvdende.github.io/icon-rs/

```rust
use icon_rs::{Palette, Rgb, EXTRUDE};

let light: &str = EXTRUDE.svg;       // for light backgrounds
let dark: &str = EXTRUDE.svg_dark;   // for dark backgrounds
let svg = icon_rs::get("loft").unwrap().themed(is_dark);

// Any other theme: a line colour plus one spot colour, shaded automatically.
let palette = Palette::from_spot(Rgb(0x0c, 0x4a, 0x6e), Rgb(0x38, 0xbd, 0xf8));
let custom: String = EXTRUDE.recolor(&palette);
```


### Bevy

Enable the `bevy_color` feature to pass Bevy colours straight in and get them back out:

```toml
icon-rs = { version = "0.2", features = ["bevy_color"] }
```

```rust
use bevy_color::{Color, palettes::tailwind};

let palette = Palette::from_spot(tailwind::SKY_900, Color::srgb(0.2, 0.7, 0.95));
let mid: Color = palette.mid.into();
```

Colours convert through sRGB; alpha is dropped, since icons are opaque.

- `icons/*.svg`, `icons/dark/*.svg`: 24x24, outline plus four face shades, lit from the same
  direction in both themes.
- `tools/gen_icons.py`: computes the isometric geometry and regenerates both sets.
- `tools/build_site.py`: builds the icon browser into `site/`; GitHub Actions deploys it on every push to `main`.
- `cargo run --example preview [out.png] [scale]`: renders a contact sheet (default `target/preview.png`).
