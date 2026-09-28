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
        // Two passes through placeholders, so a new colour that equals a later light slot is
        // not replaced again.
        let placeholder = |slot: usize| format!("#\0{slot}");
        let mut svg = self.svg.to_owned();
        for (slot, from) in Palette::LIGHT.slots().into_iter().enumerate() {
            svg = svg.replace(&from.to_hex(), &placeholder(slot));
        }
        for (slot, to) in palette.slots().into_iter().enumerate() {
            svg = svg.replace(&placeholder(slot), &to.to_hex());
        }
        svg
    }
}

/// An sRGB colour.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Rgb(pub u8, pub u8, pub u8);

impl Rgb {
    pub const WHITE: Rgb = Rgb(0xff, 0xff, 0xff);
    pub const BLACK: Rgb = Rgb(0, 0, 0);

    /// Parses `#rrggbb` or `rrggbb`.
    pub fn from_hex(hex: &str) -> Option<Rgb> {
        let hex = hex.strip_prefix('#').unwrap_or(hex);
        if hex.len() != 6 || !hex.is_ascii() {
            return None;
        }
        let channel = |i: usize| u8::from_str_radix(&hex[i..i + 2], 16).ok();
        Some(Rgb(channel(0)?, channel(2)?, channel(4)?))
    }

    /// Lowercase `#rrggbb`, the form the SVGs use.
    pub fn to_hex(self) -> String {
        format!("#{:02x}{:02x}{:02x}", self.0, self.1, self.2)
    }

    /// Moves `percent` of the way towards `other`, rounding to the nearest channel value.
    pub fn mix(self, other: Rgb, percent: u32) -> Rgb {
        let percent = percent.min(100);
        let channel = |a: u8, b: u8| ((a as u32 * (100 - percent) + b as u32 * percent + 50) / 100) as u8;
        Rgb(channel(self.0, other.0), channel(self.1, other.1), channel(self.2, other.2))
    }

    /// Perceived brightness, 0 to 255 (Rec. 601 weights).
    pub fn luma(self) -> u32 {
        (self.0 as u32 * 299 + self.1 as u32 * 587 + self.2 as u32 * 114) / 1000
    }
}

/// The five colours an icon is drawn with.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Palette {
    /// Outlines and arrow heads.
    pub ink: Rgb,
    /// Faces that point up, and profile caps.
    pub top: Rgb,
    /// Bevel faces between top and side.
    pub soft: Rgb,
    /// Right-hand side faces and swept bodies.
    pub mid: Rgb,
    /// Left-hand side faces, in shadow.
    pub shade: Rgb,
}

impl Palette {
    /// The colours `Icon::svg` is drawn with.
    pub const LIGHT: Palette = Palette {
        ink: Rgb(0x26, 0x26, 0x26),
        top: Rgb(0xff, 0xff, 0xff),
        soft: Rgb(0xd4, 0xd4, 0xd4),
        mid: Rgb(0xa3, 0xa3, 0xa3),
        shade: Rgb(0x73, 0x73, 0x73),
    };

    /// The colours `Icon::svg_dark` is drawn with.
    pub const DARK: Palette = Palette {
        ink: Rgb(0xe4, 0xe4, 0xe7),
        top: Rgb(0xa1, 0xa1, 0xaa),
        soft: Rgb(0x8b, 0x8b, 0x94),
        mid: Rgb(0x71, 0x71, 0x7a),
        shade: Rgb(0x52, 0x52, 0x5b),
    };

    /// Builds a palette from a line colour and one spot colour. The spot fills side faces; the
    /// top and bevel faces are tinted towards white and the shaded faces towards black. When the
    /// line is lighter than the spot (a dark theme) the tints are gentler, so top faces don't
    /// glare against a dark background.
    ///
    /// Takes anything that converts to [`Rgb`]; with the `bevy_color` feature that includes
    /// `bevy_color::Color` and `Srgba`.
    pub fn from_spot(ink: impl Into<Rgb>, spot: impl Into<Rgb>) -> Palette {
        let (ink, spot) = (ink.into(), spot.into());
        let (top, soft, shade) = if ink.luma() > spot.luma() { (35, 18, 28) } else { (85, 45, 30) };
        Palette {
            ink,
            top: spot.mix(Rgb::WHITE, top),
            soft: spot.mix(Rgb::WHITE, soft),
            mid: spot,
            shade: spot.mix(Rgb::BLACK, shade),
        }
    }

    fn slots(&self) -> [Rgb; 5] {
        [self.ink, self.top, self.soft, self.mid, self.shade]
    }
}

#[cfg(feature = "bevy_color")]
mod bevy_color_impls {
    //! Alpha is dropped going to `Rgb` and set to opaque coming back; icons have no transparency.

    use super::Rgb;
    use bevy_color::{Color, ColorToPacked, Srgba};

    impl From<Rgb> for Srgba {
        fn from(c: Rgb) -> Srgba {
            Srgba::rgb_u8(c.0, c.1, c.2)
        }
    }

    impl From<Rgb> for Color {
        fn from(c: Rgb) -> Color {
            Color::Srgba(c.into())
        }
    }

    impl From<Srgba> for Rgb {
        fn from(c: Srgba) -> Rgb {
            let [r, g, b] = c.to_u8_array_no_alpha();
            Rgb(r, g, b)
        }
    }

    impl From<Color> for Rgb {
        fn from(c: Color) -> Rgb {
            c.to_srgba().into()
        }
    }

    #[cfg(test)]
    mod tests {
        use super::*;
        use crate::Palette;
        use bevy_color::palettes::tailwind;

        #[test]
        fn round_trips_through_bevy_color() {
            let sky = Rgb(0x38, 0xbd, 0xf8);
            assert_eq!(Rgb::from(Color::from(sky)), sky);
            assert_eq!(Rgb::from(Srgba::from(sky)), sky);
            // Linear colours convert back to sRGB first.
            assert_eq!(Rgb::from(Color::LinearRgba(Color::from(sky).to_linear())), sky);
        }

        #[test]
        fn from_spot_accepts_bevy_colors() {
            let from_bevy = Palette::from_spot(tailwind::SKY_900, Color::from(tailwind::SKY_400));
            let from_rgb = Palette::from_spot(Rgb::from(tailwind::SKY_900), Rgb::from(tailwind::SKY_400));
            assert_eq!(from_bevy, from_rgb);
        }
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
                let hex = Rgb::from_hex(&rest[at + 2..at + 9]).unwrap();
                assert!(Palette::LIGHT.slots().contains(&hex), "{} uses {hex:?}", icon.name);
                rest = &rest[at + 9..];
            }
        }
    }

    #[test]
    fn recolor_does_not_chain_replacements() {
        // The new ink equals the light palette's top colour; outlines must stay white.
        let palette = Palette { ink: Palette::LIGHT.top, top: Rgb(1, 2, 3), ..Palette::LIGHT };
        let svg = SHELL.recolor(&palette);
        assert!(svg.contains(r##"stroke="#ffffff""##));
        assert!(svg.contains(r##"fill="#010203""##));
    }

    #[test]
    fn hex_round_trip() {
        assert_eq!(Rgb::from_hex("#38bdf8"), Some(Rgb(0x38, 0xbd, 0xf8)));
        assert_eq!(Rgb::from_hex("38BDF8"), Some(Rgb(0x38, 0xbd, 0xf8)));
        assert_eq!(Rgb(0x38, 0xbd, 0xf8).to_hex(), "#38bdf8");
        assert_eq!(Rgb::from_hex("#38bdf"), None);
        assert_eq!(Rgb::from_hex("#38bdfg"), None);
    }

    #[test]
    fn from_spot_shades_the_spot() {
        // Values the site's JavaScript port also produces; keep the two in step.
        let light = Palette::from_spot(Rgb(0x26, 0x26, 0x26), Rgb(0xa3, 0xa3, 0xa3));
        assert_eq!(light.top, Rgb(0xf1, 0xf1, 0xf1));
        assert_eq!(light.soft, Rgb(0xcc, 0xcc, 0xcc));
        assert_eq!(light.shade, Rgb(0x72, 0x72, 0x72));

        let dark = Palette::from_spot(Rgb(0xe4, 0xe4, 0xe7), Rgb(0x71, 0x71, 0x7a));
        assert_eq!(dark.top, Rgb(0xa3, 0xa3, 0xa9));
        assert_eq!(dark.shade, Rgb(0x51, 0x51, 0x58));
    }

    #[test]
    fn lookup_by_name() {
        assert_eq!(get("loft").unwrap().name, "loft");
        assert!(get("nope").is_none());
    }
}
