# icon-rs

Original SVG icons for CAD feature tools (extrude, revolve, sweep, loft, thicken, enclose, fillet,
chamfer, shell, pattern, boolean), embedded as Rust constants.

Browse the icons: https://rvdende.github.io/icon-rs/

```rust
use icon_rs::{Palette, EXTRUDE};

let light: &str = EXTRUDE.svg;       // for light backgrounds
let dark: &str = EXTRUDE.svg_dark;   // for dark backgrounds
let svg = icon_rs::get("loft").unwrap().themed(is_dark);

// Any other theme: swap the five palette colours.
let custom: String = EXTRUDE.recolor(&Palette { ink: "#1e293b", ..Palette::LIGHT });
```

- `icons/*.svg`, `icons/dark/*.svg`: 24x24, outline plus four face shades, lit from the same
  direction in both themes.
- `tools/gen_icons.py`: computes the isometric geometry and regenerates both sets.
- `tools/build_site.py`: builds the icon browser into `site/`; GitHub Actions deploys it on every push to `main`.
- `cargo run --example preview [out.png] [scale]`: renders a contact sheet (default `target/preview.png`).
