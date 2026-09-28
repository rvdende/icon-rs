"""Shared palette, geometry helpers and the icon registry.

Every icon is a function decorated with @icon(name, kind, title) that returns its SVG body: a
string or a list of element strings. gen.py wraps the body in the <svg> root for its kind,
validates it, and writes the light and dark files.

Conventions (all icons):
- 24x24 view box. Keep drawing inside 1.5..22.5 so strokes are not clipped.
- Coordinates are written with f() so files stay small and diffs stay stable.
- Colours come only from the palette constants below. The dark variant is made by swapping them.

Kinds:
- "solid":  isometric CAD geometry. Outline INK at the root stroke width (1.1). Faces lit from
            above-right: TOP on faces pointing up, MID on right-facing sides, SHADE on left-facing
            sides, SOFT on bevels and secondary faces. ACCENT marks what the tool acts on (the edge
            being filleted, the direction of an extrude, the moving part of a mate). Use it
            sparingly: one idea per icon.
- "sketch": flat 2D sketch geometry. INK lines at 1.5. ACCENT for the points or entity the user
            picks (the three points of a 3-point arc, the centre of a centre rectangle). TOP or
            SOFT fills are allowed for closed regions; no isometric shading.
- "glyph":  constraint and viewport markers shown at 10-16 px. Stroke 2, bold simple shapes, no
            detail smaller than 2 units.
- "line":   general UI icons (undo, folder, search...). Stroke 1.75, round caps and joins,
            optically centred, consistent with each other.

Glyph and line icons are INK plus a little ACCENT. Apps tint the INK (Icon::tinted) and keep the
accent, so the accent must never carry the icon's meaning alone. Accent the modifier, not the
object: the plus in file-new, the arrow in upload, the slash in hidden, the contact point in
tangent, the shared point in coincident. One accent element (or one group) per icon. Icons that
are a single mark (chevrons, carets, close, check, menu, plus, plain arrows) stay INK only, and so
do the layered viewport markers (manipulator arrow and halo, centre-of-mass layers), which the app
colours per state.
"""
import math

# Palette slots, light theme. src/lib.rs's Palette::LIGHT must match (gen.py checks).
INK = "#262626"
TOP = "#ffffff"
SOFT = "#d4d4d4"
MID = "#a3a3a3"
SHADE = "#737373"
ACCENT = "#2563eb"
# Old names, kept for part.py.
LIGHT, DARK = TOP, SHADE

DARK_PALETTE = {
    INK: "#e4e4e7",
    TOP: "#a1a1aa",
    SOFT: "#8b8b94",
    MID: "#71717a",
    SHADE: "#52525b",
    ACCENT: "#60a5fa",
}

KINDS = {
    # kind: (root stroke width, colours allowed)
    "solid": ("1.1", {INK, TOP, SOFT, MID, SHADE, ACCENT}),
    "sketch": ("1.5", {INK, TOP, SOFT, MID, SHADE, ACCENT}),
    "glyph": ("2", {INK, ACCENT}),
    "line": ("1.75", {INK, ACCENT}),
}

REGISTRY = []  # dicts: name, kind, title, module, fn


def icon(name, kind, title):
    """Registers the decorated function as the icon `name`."""
    assert kind in KINDS, f"{name}: unknown kind {kind}"

    def wrap(fn):
        REGISTRY.append({"name": name, "kind": kind, "title": title, "module": fn.__module__, "fn": fn})
        return fn

    return wrap


# ---------------------------------------------------------------------------------------------
# Formatting


def f(v):
    """A coordinate with at most two decimals and no trailing zeros."""
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def pts(ps):
    return " ".join(f"{f(x)},{f(y)}" for x, y in ps)


def attrs(fill=None, extra=""):
    a = f' fill="{fill}"' if fill else ""
    return a + (" " + extra.strip() if extra.strip() else "")


# ---------------------------------------------------------------------------------------------
# Primitives. `fill` is a palette colour or None (the root default, no fill). `extra` is raw
# attributes such as 'stroke-dasharray="1.4 1.2"' or 'stroke="none"'.


def poly(ps, fill=None, extra=""):
    return f'<polygon points="{pts(ps)}"{attrs(fill, extra)}/>'


def polyline(ps, extra=""):
    return f'<polyline points="{pts(ps)}"{attrs(None, extra)}/>'


def line(x1, y1, x2, y2, extra=""):
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}"{attrs(None, extra)}/>'


def path(d, fill=None, extra=""):
    return f'<path d="{d}"{attrs(fill, extra)}/>'


def circle(cx, cy, r, fill=None, extra=""):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}"{attrs(fill, extra)}/>'


def ellipse(cx, cy, rx, ry, fill=None, extra="", rotate=0):
    rot = f' transform="rotate({f(rotate)} {f(cx)} {f(cy)})"' if rotate else ""
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}"{rot}{attrs(fill, extra)}/>'


def rect(x, y, w, h, rx=0, fill=None, extra=""):
    r = f' rx="{f(rx)}"' if rx else ""
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}"{r}{attrs(fill, extra)}/>'


# Dashes. With round caps each dash grows by the stroke width and each gap shrinks by it, so
# a fixed dasharray looks cramped on thick strokes. dash() and dash_dot() compensate: every
# dashed line shows about DASH_ON-long dashes and DASH_GAP-wide gaps whatever its width. They
# return the stroke-width attribute too, so don't set it again.
DASH_ON, DASH_GAP = 2.2, 1.6


def dash(sw=1.0, on=DASH_ON, gap=DASH_GAP):
    return f'stroke-width="{f(sw)}" stroke-dasharray="{f(max(on - sw, 0.05))} {f(gap + sw)}"'


def dash_dot(sw=1.0, on=3.2, gap=DASH_GAP):
    """Centre-line pattern: long dash, gap, dot, gap."""
    return (f'stroke-width="{f(sw)}" stroke-dasharray="{f(max(on - sw, 0.05))} {f(gap + sw)} '
            f'0.01 {f(gap + sw)}"')


# Plain patterns for strokes about 1 wide, where the caller sets the width itself.
DASH = f'stroke-dasharray="{f(DASH_ON - 1)} {f(DASH_GAP + 1)}"'
DASH_DOT = f'stroke-dasharray="{f(3.2 - 1)} {f(DASH_GAP + 1)} 0.01 {f(DASH_GAP + 1)}"'


# ---------------------------------------------------------------------------------------------
# Isometric projection. x runs down-right, y down-left, z up; one unit is one SVG unit along
# each axis. The camera looks from +x +y +z, so visible faces of a box are its top (z max),
# right side (x max) and left side (y max).

C30, S30 = math.cos(math.pi / 6), 0.5


def iso(o, x, y, z):
    return (o[0] + (x - y) * C30, o[1] + (x + y) * S30 - z)


def projector(o):
    """Returns P(x, y, z) -> screen point, for origin `o`."""
    return lambda x, y, z: iso(o, x, y, z)


def box(o, x0, x1, y0, y1, z0, z1, top=TOP, right=MID, left=SHADE, extra=""):
    """The three visible faces of an axis-aligned box."""
    P = projector(o)
    return "\n  ".join([
        poly([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], top, extra),
        poly([P(x1, y0, z1), P(x1, y1, z1), P(x1, y1, z0), P(x1, y0, z0)], right, extra),
        poly([P(x0, y1, z1), P(x1, y1, z1), P(x1, y1, z0), P(x0, y1, z0)], left, extra),
    ])


def iso_circle(o, cx, cy, z, r, n=48):
    """A horizontal circle (in the xy plane at height z) as a projected point list."""
    P = projector(o)
    return [P(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z) for i in range(n)]


def cylinder(o, cx, cy, z0, z1, r, top=TOP, side=MID, extra=""):
    """An upright cylinder: side silhouette plus top ellipse. A horizontal circle of radius r
    projects to an ellipse with rx = r*sqrt(1.5) and ry = r*sqrt(0.5)."""
    P = projector(o)
    rx, ry = r * math.sqrt(1.5), r * math.sqrt(0.5)
    (bx, by), (tx, ty) = P(cx, cy, z0), P(cx, cy, z1)
    side_d = (f"M{f(tx - rx)} {f(ty)} L{f(bx - rx)} {f(by)} A{f(rx)} {f(ry)} 0 0 0 {f(bx + rx)} {f(by)} "
              f"L{f(tx + rx)} {f(ty)} Z")
    return "\n  ".join([path(side_d, side, extra), ellipse(tx, ty, rx, ry, top, extra)])


# ---------------------------------------------------------------------------------------------
# Curves and arrows


def cubic(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def sample_cubic(p0, p1, p2, p3, n=32):
    return [cubic(p0, p1, p2, p3, i / n) for i in range(n + 1)]


def arc_points(cx, cy, rx, ry, deg0, deg1, step=5):
    """Points on an ellipse from deg0 to deg1 (degrees, clockwise on screen since y is down)."""
    n = max(2, int(abs(deg1 - deg0) / step))
    return [(cx + rx * math.cos(math.radians(deg0 + (deg1 - deg0) * i / n)),
             cy + ry * math.sin(math.radians(deg0 + (deg1 - deg0) * i / n))) for i in range(n + 1)]


def offset_polyline(ps, k):
    """The polyline offset by k to its left (screen coordinates)."""
    out = []
    for i, (x, y) in enumerate(ps):
        a, b = ps[max(i - 1, 0)], ps[min(i + 1, len(ps) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        out.append((x - ty / L * k, y + tx / L * k))
    return out


def arrow_head(tip, frm, length=3.2, width=2.8, fill=INK):
    """A filled triangular head at `tip`, pointing away from `frm`."""
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    bx, by = tip[0] - ux * length, tip[1] - uy * length
    nx, ny = -uy * width / 2, ux * width / 2
    return poly([tip, (bx + nx, by + ny), (bx - nx, by - ny)], fill, 'stroke-width="0.6"' if fill == INK else "")


def arrow(x0, y0, x1, y1, head=3.2, width=2.8, color=INK, extra=""):
    """A straight arrow from (x0, y0) to a filled head at (x1, y1)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    bx, by = x1 - dx / L * head * 0.8, y1 - dy / L * head * 0.8
    stroke = f' stroke="{color}"' if color != INK else ""
    return "\n  ".join([
        f'<line x1="{f(x0)}" y1="{f(y0)}" x2="{f(bx)}" y2="{f(by)}"{stroke}{attrs(None, extra)}/>',
        arrow_head((x1, y1), (x0, y0), head, width, color).replace("/>", f' stroke="{color}"/>') if color != INK
        else arrow_head((x1, y1), (x0, y0), head, width, color),
    ])


def curved_arrow(ps, head=3.2, width=2.8, color=INK, extra=""):
    """An arrow along the point list `ps`, with the head at the last point."""
    stroke = f' stroke="{color}"' if color != INK else ""
    tip = ps[-1]
    # Stop the shaft inside the head so the round cap doesn't poke out.
    shaft = ps[:-1]
    while len(shaft) > 1 and math.hypot(shaft[-1][0] - tip[0], shaft[-1][1] - tip[1]) < head * 0.7:
        shaft = shaft[:-1]
    head_el = arrow_head(tip, shaft[-1], head, width, color)
    if color != INK:
        head_el = head_el.replace("/>", f' stroke="{color}"/>')
    return "\n  ".join([f'<polyline points="{pts(shaft)}"{stroke}{attrs(None, extra)}/>', head_el])


def clip(subject, convex):
    """Clips polygon `subject` to the convex polygon `convex` (Sutherland-Hodgman). Use this
    instead of <clipPath>, which needs ids."""
    def inside(p, a, b):
        return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= 0

    def cross(p, q, a, b):
        x1, y1, x2, y2, x3, y3, x4, y4 = *p, *q, *a, *b
        d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(d) < 1e-12:  # edge parallel to the clip edge (only reached through rounding)
            return q
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    # Orient the clip polygon counter-clockwise in screen space (y down).
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(convex, convex[1:] + convex[:1]))
    if area < 0:
        convex = convex[::-1]
    out = list(subject)
    for a, b in zip(convex, convex[1:] + convex[:1]):
        src, out = out, []
        for p, q in zip(src, src[1:] + src[:1]):
            if inside(q, a, b):
                if not inside(p, a, b):
                    out.append(cross(p, q, a, b))
                out.append(q)
            elif inside(p, a, b):
                out.append(cross(p, q, a, b))
        if not out:
            break
    return out
