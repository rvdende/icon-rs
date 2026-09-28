//! SVG icons for CAD feature tools, embedded at compile time.
//!
//! Every icon uses a 24x24 view box, a dark outline and three grey fills (light, mid and dark
//! shading) so faces read as solid geometry at toolbar size.

/// One icon: its file stem and its SVG source.
#[derive(Clone, Copy, Debug)]
pub struct Icon {
    pub name: &'static str,
    pub svg: &'static str,
}

macro_rules! icons {
    ($($konst:ident => $file:literal),* $(,)?) => {
        $(pub const $konst: Icon = Icon {
            name: $file,
            svg: include_str!(concat!("../icons/", $file, ".svg")),
        };)*

        /// Every icon, in toolbar order.
        pub const ALL: &[Icon] = &[$($konst),*];
    };
}

icons! {
    EXTRUDE => "extrude",
    REVOLVE => "revolve",
    SWEEP => "sweep",
    LOFT => "loft",
    THICKEN => "thicken",
    ENCLOSE => "enclose",
    FILLET => "fillet",
    CHAMFER => "chamfer",
    SHELL => "shell",
    PATTERN => "pattern",
    BOOLEAN => "boolean",
}

/// Looks an icon up by its file stem, such as `"extrude"`.
pub fn get(name: &str) -> Option<Icon> {
    ALL.iter().copied().find(|icon| icon.name == name)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_icon_is_a_24px_svg() {
        for icon in ALL {
            assert!(icon.svg.starts_with("<svg"), "{} is not an svg", icon.name);
            assert!(icon.svg.contains(r#"viewBox="0 0 24 24""#), "{} is not 24x24", icon.name);
        }
    }

    #[test]
    fn every_svg_file_is_registered() {
        let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("icons");
        for entry in std::fs::read_dir(dir).unwrap() {
            let path = entry.unwrap().path();
            let stem = path.file_stem().unwrap().to_str().unwrap();
            assert!(get(stem).is_some(), "icons/{stem}.svg is missing from the icons! list");
        }
    }

    #[test]
    fn lookup_by_name() {
        assert_eq!(get("loft").unwrap().name, "loft");
        assert!(get("nope").is_none());
    }
}
