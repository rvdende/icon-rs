//! Renders the README banner: a grid of icons whose accent sweeps around the colour wheel, light
//! theme above and dark theme below: `cargo run --example splash [out.png]`.

use icon_rs::{Palette, Rgb};
use resvg::{tiny_skia, usvg};

const COLS: usize = 12;
const CELL: f32 = 96.0;
const SCALE: f32 = 3.0;
const MARGIN: f32 = 32.0;

const ROWS: [[&str; COLS]; 6] = [
    ["extrude", "revolve", "sweep", "loft", "fillet", "chamfer", "shell", "hole", "thread", "linear-pattern", "circular-pattern", "boolean"],
    ["line", "corner-rectangle", "center-circle", "three-point-arc", "spline", "inscribed-polygon", "slot", "sketch-fillet", "trim", "offset", "mirror", "dimension"],
    ["constraint-coincident", "constraint-parallel", "constraint-tangent", "constraint-perpendicular", "constraint-symmetric", "undo", "redo", "search", "settings", "folder-new", "share", "visible"],
    ["mate-fastened", "mate-revolute", "mate-slider", "mate-ball", "gear-relation", "rack-pinion", "explode", "assembly", "part-studio", "section-view", "measure", "mass-properties"],
    ["ellipse", "tangent-arc", "center-rectangle", "point", "text", "sketch-pattern", "intersection", "extend", "sketch-split", "use", "construction", "diagnostics"],
    ["constraint-equal", "constraint-midpoint", "constraint-fix", "origin", "instance-dof", "history", "branches", "idea", "code", "tool", "location", "likes"],
];

/// An sRGB colour from a hue in degrees and saturation and lightness in 0..1.
fn hsl(h: f32, s: f32, l: f32) -> Rgb {
    let c = (1.0 - (2.0 * l - 1.0).abs()) * s;
    let x = c * (1.0 - ((h / 60.0) % 2.0 - 1.0).abs());
    let (r, g, b) = match (h / 60.0) as u32 % 6 {
        0 => (c, x, 0.0),
        1 => (x, c, 0.0),
        2 => (0.0, c, x),
        3 => (0.0, x, c),
        4 => (x, 0.0, c),
        _ => (c, 0.0, x),
    };
    let m = l - c / 2.0;
    let channel = |v: f32| ((v + m) * 255.0).round() as u8;
    Rgb(channel(r), channel(g), channel(b))
}

fn main() {
    let out = std::env::args().nth(1).unwrap_or_else(|| "target/splash.png".into());

    let w = (2.0 * MARGIN + COLS as f32 * CELL) as u32;
    let band = 3.0 * CELL + MARGIN;
    let mut sheet = tiny_skia::Pixmap::new(w, (2.0 * band) as u32).unwrap();
    sheet.fill(tiny_skia::Color::from_rgba8(0xfa, 0xfa, 0xfa, 0xff));
    let mut paint = tiny_skia::Paint::default();
    paint.set_color_rgba8(0x18, 0x18, 0x1b, 0xff);
    let dark_band = tiny_skia::Rect::from_xywh(0.0, band, w as f32, band).unwrap();
    sheet.fill_rect(dark_band, &paint, tiny_skia::Transform::identity(), None);

    let inset = (CELL - 24.0 * SCALE) / 2.0;
    for (row, names) in ROWS.iter().enumerate() {
        let dark = row >= 3;
        for (col, name) in names.iter().enumerate() {
            let icon = icon_rs::get(name).unwrap_or_else(|| panic!("no icon {name}"));
            // The hue sweeps along each row and drifts down the rows, so every icon differs.
            let hue = (220.0 + (col as f32 + 0.5 * row as f32) * 360.0 / COLS as f32) % 360.0;
            let palette = if dark {
                Palette::DARK.with_accent(hsl(hue, 0.9, 0.66))
            } else {
                Palette::LIGHT.with_accent(hsl(hue, 0.8, 0.48))
            };
            let tree = usvg::Tree::from_str(&icon.recolor(&palette), &usvg::Options::default()).unwrap();
            let top = if dark { band } else { 0.0 } + MARGIN / 2.0;
            let transform = tiny_skia::Transform::from_scale(SCALE, SCALE).post_translate(
                MARGIN + col as f32 * CELL + inset,
                top + (row % 3) as f32 * CELL + inset,
            );
            resvg::render(&tree, transform, &mut sheet.as_mut());
        }
    }
    sheet.save_png(&out).unwrap();
    println!("wrote {out}");
}

