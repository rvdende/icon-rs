//! Prints the ink bounds of SVG files, in view-box units, for the generator's fitting pass:
//!
//!     cargo run --release --example bbox -- FILE.svg...
//!
//! Each line is `name x0 y0 x1 y1`. Bounds come from rendering at 10x and finding pixels with
//! any coverage, so strokes, caps and joins are included exactly.

use resvg::{tiny_skia, usvg};

const SCALE: f32 = 10.0;

fn main() {
    for file in std::env::args().skip(1) {
        let svg = std::fs::read_to_string(&file).unwrap_or_else(|e| panic!("{file}: {e}"));
        let tree = usvg::Tree::from_str(&svg, &usvg::Options::default()).unwrap_or_else(|e| panic!("{file}: {e}"));
        let side = (24.0 * SCALE) as u32;
        let mut pixmap = tiny_skia::Pixmap::new(side, side).unwrap();
        resvg::render(&tree, tiny_skia::Transform::from_scale(SCALE, SCALE), &mut pixmap.as_mut());
        let (mut x0, mut y0, mut x1, mut y1) = (u32::MAX, u32::MAX, 0, 0);
        for (i, p) in pixmap.pixels().iter().enumerate() {
            if p.alpha() > 8 {
                let (x, y) = (i as u32 % side, i as u32 / side);
                x0 = x0.min(x);
                y0 = y0.min(y);
                x1 = x1.max(x + 1);
                y1 = y1.max(y + 1);
            }
        }
        let name = std::path::Path::new(&file).file_stem().unwrap().to_string_lossy();
        println!("{name} {} {} {} {}", x0 as f32 / SCALE, y0 as f32 / SCALE, x1 as f32 / SCALE, y1 as f32 / SCALE);
    }
}
