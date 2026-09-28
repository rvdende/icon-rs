//! Renders every icon into one contact sheet: `cargo run --example preview [out.png] [scale]`.

use resvg::{tiny_skia, usvg};

fn main() {
    let mut args = std::env::args().skip(1);
    let out = args.next().unwrap_or_else(|| "target/preview.png".into());
    let scale: f32 = args.next().map_or(4.0, |s| s.parse().expect("scale must be a number"));

    let cell = 24.0 * scale + 16.0;
    let cols = 6u32;
    let rows = (icon_rs::ALL.len() as u32).div_ceil(cols);
    let mut sheet = tiny_skia::Pixmap::new(cols * cell as u32, rows * cell as u32).unwrap();
    sheet.fill(tiny_skia::Color::WHITE);

    for (i, icon) in icon_rs::ALL.iter().enumerate() {
        let tree = usvg::Tree::from_str(icon.svg, &usvg::Options::default())
            .unwrap_or_else(|e| panic!("{}: {e}", icon.name));
        let (col, row) = (i as u32 % cols, i as u32 / cols);
        let transform = tiny_skia::Transform::from_scale(scale, scale)
            .post_translate(col as f32 * cell + 8.0, row as f32 * cell + 8.0);
        resvg::render(&tree, transform, &mut sheet.as_mut());
    }
    sheet.save_png(&out).unwrap();
    println!("wrote {out}");
}
