//! SVG icons for CAD feature tools, embedded at compile time.
//!
//! Every icon uses a 24x24 view box, an outline and four face shades so faces read as solid
//! geometry at toolbar size. Each icon ships a light-theme and a dark-theme SVG; for any other
//! theme, [`Icon::recolor`] swaps in your own [`Palette`].

/// One icon: its file stem and its SVG source for light and dark backgrounds.
#[derive(Clone, Copy, Debug)]
pub struct Icon {
    pub name: &'static str,
    /// For light backgrounds: dark outline, white to mid-grey faces.
    pub svg: &'static str,
    /// For dark backgrounds: light outline, darker faces, same lighting direction.
    pub svg_dark: &'static str,
}

impl Icon {
    /// The SVG for a light or dark background.
    pub fn themed(&self, dark: bool) -> &'static str {
        if dark { self.svg_dark } else { self.svg }
    }

    /// The light SVG with every palette colour replaced by the matching slot in `palette`.
    pub fn recolor(&self, palette: &Palette) -> String {
        Palette::LIGHT
            .slots()
            .into_iter()
            .zip(palette.slots())
            .fold(self.svg.to_owned(), |svg, (from, to)| svg.replace(from, to))
    }
}

/// The five colours an icon is drawn with, as `#rrggbb` strings.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Palette {
    /// Outlines and arrow heads.
    pub ink: &'static str,
    /// Faces that point up, and profile caps.
    pub top: &'static str,
    /// Bevel faces between top and side.
    pub soft: &'static str,
    /// Right-hand side faces and swept bodies.
    pub mid: &'static str,
    /// Left-hand side faces, in shadow.
    pub shade: &'static str,
}

impl Palette {
    /// The colours `Icon::svg` is drawn with.
    pub const LIGHT: Palette = Palette {
        ink: "#262626",
        top: "#ffffff",
        soft: "#d4d4d4",
        mid: "#a3a3a3",
        shade: "#737373",
    };

    /// The colours `Icon::svg_dark` is drawn with.
    pub const DARK: Palette = Palette {
        ink: "#e4e4e7",
        top: "#a1a1aa",
        soft: "#8b8b94",
        mid: "#71717a",
        shade: "#52525b",
    };

    fn slots(&self) -> [&'static str; 5] {
        [self.ink, self.top, self.soft, self.mid, self.shade]
    }
}

macro_rules! icons {
    ($($konst:ident => $file:literal),* $(,)?) => {
        $(pub const $konst: Icon = Icon {
            name: $file,
            svg: include_str!(concat!("../icons/", $file, ".svg")),
            svg_dark: include_str!(concat!("../icons/dark/", $file, ".svg")),
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
            for svg in [icon.svg, icon.svg_dark] {
                assert!(svg.starts_with("<svg"), "{} is not an svg", icon.name);
                assert!(svg.contains(r#"viewBox="0 0 24 24""#), "{} is not 24x24", icon.name);
            }
        }
    }

    #[test]
    fn every_svg_file_is_registered() {
        let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("icons");
        for entry in std::fs::read_dir(dir).unwrap() {
            let path = entry.unwrap().path();
            if path.is_dir() {
                continue;
            }
            let stem = path.file_stem().unwrap().to_str().unwrap();
            assert!(get(stem).is_some(), "icons/{stem}.svg is missing from the icons! list");
        }
    }

    #[test]
    fn dark_variant_is_the_light_svg_recoloured() {
        for icon in ALL {
            assert_eq!(icon.recolor(&Palette::DARK), icon.svg_dark, "{}", icon.name);
            assert_eq!(icon.recolor(&Palette::LIGHT), icon.svg, "{}", icon.name);
        }
    }

    #[test]
    fn light_svgs_only_use_palette_colours() {
        for icon in ALL {
            let mut rest = icon.svg;
            while let Some(at) = rest.find("=\"#") {
                let hex = &rest[at + 2..at + 9];
                assert!(Palette::LIGHT.slots().contains(&hex), "{} uses {hex}", icon.name);
                rest = &rest[at + 9..];
            }
        }
    }

    #[test]
    fn lookup_by_name() {
        assert_eq!(get("loft").unwrap().name, "loft");
        assert!(get("nope").is_none());
    }
}
