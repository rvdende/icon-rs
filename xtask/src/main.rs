//! Repository tasks:
//!
//!     cargo xtask gen [--only MODULE] [--out DIR] [--check]   generate icons/ and src/generated.rs
//!     cargo xtask site                                        build the icon browser into site/

#[macro_use]
mod common;
mod generate;
mod icons;
#[allow(dead_code)]
#[path = "../../src/palette.rs"]
mod palette;
mod site;

use std::path::Path;

fn main() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).parent().unwrap();
    let args: Vec<String> = std::env::args().skip(1).collect();
    let result = match args.first().map(String::as_str) {
        Some("gen") => generate::main(root, &args[1..]),
        Some("site") => site::main(root),
        _ => Err("usage: cargo xtask gen [--only MODULE] [--out DIR] [--check] | cargo xtask site".to_owned()),
    };
    if let Err(e) = result {
        eprintln!("{e}");
        std::process::exit(1);
    }
}
