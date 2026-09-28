# icon-rs

Original SVG icons for CAD feature tools (extrude, revolve, sweep, loft, thicken, enclose, fillet,

Browse the icons: https://rvdende.github.io/icon-rs/
chamfer, shell, pattern, boolean), embedded as Rust constants.

```rust
let svg: &str = icon_rs::EXTRUDE.svg;
let loft = icon_rs::get("loft");
```

- `icons/*.svg`: 24x24, dark outline, light/mid/dark grey face shading.
- `tools/gen_icons.py`: computes the isometric geometry and regenerates the SVGs.
- `tools/build_site.py`: builds the icon browser into `site/`; GitHub Actions deploys it on every push to `main`.
- `cargo run --example preview [out.png] [scale]`: renders a contact sheet (default `target/preview.png`).
