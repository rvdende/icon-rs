//! Operating systems and devices, for download buttons and platform lists (kind Line).
//!
//! Simplified marks drawn on the line grid, not the vendors' artwork: each is one plain object, so
//! all stay INK only. Eyes and similar dots are zero-length round-capped strokes (`M x y h.01`),
//! as the keys of `keyboard` in ui_b.

use crate::common::*;
use Kind::Line;

pub fn icons() -> Vec<Def> {
    vec![
        def("platform-windows", Line, "Windows", windows),
        def("platform-macos", Line, "macOS", macos),
        def("platform-linux", Line, "Linux", linux),
        def("platform-android", Line, "Android", android),
        def("platform-ios", Line, "iPhone", ios),
    ]
}

fn windows() -> Vec<String> {
    // Four panes with a gap between them.
    let (lo, hi, s) = (4.0, 13.0, 7.0);
    els![
        rect(lo, lo, s, s, 1.0, "", ""),
        rect(hi, lo, s, s, 1.0, "", ""),
        rect(lo, hi, s, s, 1.0, "", ""),
        rect(hi, hi, s, s, 1.0, "", ""),
    ]
}

fn macos() -> Vec<String> {
    // An apple with a bite out of its right side, and a leaf.
    let body = "M12 8.3 C10.6 7.2 8.2 6.9 6.5 8.2 C4.6 9.7 4.3 12.6 5 15 C5.7 17.5 7.3 20.4 9 20.5 \
                C10.2 20.6 10.8 19.9 12 19.9 C13.2 19.9 13.8 20.6 15 20.5 C16.6 20.4 18 18.1 18.9 15.9 \
                C17.3 15.1 16.4 13.6 16.5 12 C16.6 10.6 17.4 9.7 18.3 9.2 C17.2 7.7 15.5 7.2 14.3 7.5 \
                C13.4 7.7 12.7 8 12 8.3 Z";
    let leaf = "M12.2 6.4 C12.3 4.7 13.4 3.4 15.2 3.1 C15.1 4.8 14 6.1 12.2 6.4 Z";
    els![path(body, "", ""), path(leaf, "", "")]
}

fn linux() -> Vec<String> {
    // A penguin: body, belly, eyes, beak and feet.
    let body = "M12 3 C9.2 3 8.3 5.3 8.3 7.6 C8.3 9.4 7.2 10.6 6.4 12.4 C5.5 14.5 5.6 17.2 7.4 18.7 \
                C8.7 19.8 10.3 20 12 20 C13.7 20 15.3 19.8 16.6 18.7 C18.4 17.2 18.5 14.5 17.6 12.4 \
                C16.8 10.6 15.7 9.4 15.7 7.6 C15.7 5.3 14.8 3 12 3 Z";
    els![
        path(body, "", ""),
        ellipse(12.0, 14.9, 2.9, 3.6, "", ""),
        path("M10.6 6.5 h.01 M13.4 6.5 h.01", "", ""),
        path("M11 8.6 L12 9.6 L13 8.6", "", ""),
        path("M6.5 21 H10 M14 21 H17.5", "", ""),
    ]
}

fn android() -> Vec<String> {
    // The robot's head: a dome with two antennae and two eyes.
    let (cx, cy, r) = (12.0, 17.0, 8.0);
    let dome = format!("M{} {} A{} {} 0 0 1 {} {} Z", f(cx - r), f(cy), f(r), f(r), f(cx + r), f(cy));
    // The antennae leave the dome at 60 degrees from the vertical.
    let (ax, ay) = (r * 0.5, r * 0.866);
    let antennae = format!(
        "M{} {} L{} {} M{} {} L{} {}",
        f(cx - ax),
        f(cy - ay),
        f(cx - ax - 1.4),
        f(cy - ay - 2.4),
        f(cx + ax),
        f(cy - ay),
        f(cx + ax + 1.4),
        f(cy - ay - 2.4)
    );
    els![path(&dome, "", ""), path(&antennae, "", ""), path("M9.2 14 h.01 M14.8 14 h.01", "", "")]
}

fn ios() -> Vec<String> {
    // A phone with the camera pill at the top of its screen.
    els![rect(6.5, 2.5, 11.0, 19.0, 2.5, "", ""), line(10.5, 5.5, 13.5, 5.5, "")]
}
