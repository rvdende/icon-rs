"""Sketch tools (kind "sketch"): flat 2D geometry on the sketch plane.

Geometry is INK at 1.5. The points the user clicks, in order, are ACCENT dots of one size (DOT),
so every variant explains its own input method. Construction geometry is dashed and thinner.
Closed shapes may carry a light TOP fill.
"""
import math
from common import *

DOT = 1.45  # the one accent dot radius for the whole family
CON = dash(1)  # construction / reference geometry
ACC = f'stroke="{ACCENT}"'
FILL = SOFT  # light region fill for closed shapes, always with REGION
REGION = 'fill-opacity="0.45"'


def dot(x, y):
    return circle(x, y, DOT, ACCENT, 'stroke="none"')


def dots(*ps):
    return [dot(x, y) for x, y in ps]


def on(cx, cy, r, deg):
    a = math.radians(deg)
    return (cx + r * math.cos(a), cy + r * math.sin(a))


def arc_d(cx, cy, r, a0, a1):
    """SVG path data for a circular arc from angle a0 to a1 (degrees, clockwise on screen when
    a1 > a0)."""
    (x0, y0), (x1, y1) = on(cx, cy, r, a0), on(cx, cy, r, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return f"M{f(x0)} {f(y0)} A{f(r)} {f(r)} 0 {large} {sweep} {f(x1)} {f(y1)}"


def ngon(cx, cy, R, n, start):
    return [on(cx, cy, R, start + 360 * i / n) for i in range(n)]


def catmull(ps, n=12):
    """A Catmull-Rom spline through the points, sampled as a polyline."""
    ext = [ps[0]] + list(ps) + [ps[-1]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i - 1], ext[i], ext[i + 1], ext[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        seg = sample_cubic(p1, c1, c2, p2, n)
        out += seg if not out else seg[1:]
    return out


# ---------------------------------------------------------------------------------------------
# Lines and rectangles


@icon("line", "sketch", "Line")
def line_():
    a, b = (5, 19), (19, 5)
    return [line(*a, *b), *dots(a, b)]


@icon("midpoint-line", "sketch", "Midpoint line")
def midpoint_line():
    a, b, m = (4, 20), (20, 4), (12, 12)
    return [line(*a, *b), *dots(m, b)]


@icon("corner-rectangle", "sketch", "Corner rectangle")
def corner_rectangle():
    return [rect(4, 6, 16, 12, 0, FILL, REGION), *dots((4, 6), (20, 18))]


@icon("center-rectangle", "sketch", "Center rectangle")
def center_rectangle():
    return [
        rect(4, 6, 16, 12, 0, FILL, REGION),
        line(12, 12, 20, 18, CON),
        *dots((12, 12), (20, 18)),
    ]


@icon("aligned-rectangle", "sketch", "Aligned rectangle")
def aligned_rectangle():
    # Edge first (two clicks along the base), then the width (third click on the far side).
    ang = math.radians(-30)
    u = (math.cos(ang), math.sin(ang))
    v = (u[1], -u[0])  # perpendicular, pointing up-left
    L, W = 14.5, 7.5
    q = [(0, 0), (u[0] * L, u[1] * L), (u[0] * L + v[0] * W, u[1] * L + v[1] * W), (v[0] * W, v[1] * W)]
    cx = (min(p[0] for p in q) + max(p[0] for p in q)) / 2
    cy = (min(p[1] for p in q) + max(p[1] for p in q)) / 2
    p0, p1, p2, p3 = [(x - cx + 12, y - cy + 12) for x, y in q]
    mid = ((p2[0] + p3[0]) / 2, (p2[1] + p3[1]) / 2)
    return [poly([p0, p1, p2, p3], FILL, REGION), *dots(p0, p1, mid)]


# ---------------------------------------------------------------------------------------------
# Circles and ellipse


@icon("center-circle", "sketch", "Center circle")
def center_circle():
    c, r = (12, 12), 8.5
    p = on(*c, r, -40)
    return [circle(*c, r, FILL, REGION), line(*c, *p, CON), *dots(c, p)]


@icon("three-point-circle", "sketch", "3 point circle")
def three_point_circle():
    c, r = (12, 12), 8.5
    return [circle(*c, r, FILL, REGION), *dots(*[on(*c, r, a) for a in (160, 275, 25)])]


@icon("ellipse", "sketch", "Ellipse")
def ellipse_():
    c, rx, ry, rot = (12, 12), 9.3, 5.6, -30
    ma = on(*c, rx, rot)
    mi = on(*c, ry, rot - 90)
    return [
        ellipse(*c, rx, ry, FILL, REGION, rotate=rot),
        line(*c, *ma, CON),
        line(*c, *mi, CON),
        *dots(c, ma, mi),
    ]


# ---------------------------------------------------------------------------------------------
# Arcs


@icon("three-point-arc", "sketch", "3 point arc")
def three_point_arc():
    c, r = (12, 17.5), 9
    a0, a1 = 195, 345
    return [path(arc_d(*c, r, a0, a1)), *dots(on(*c, r, a0), on(*c, r, a1), on(*c, r, 250))]


@icon("tangent-arc", "sketch", "Tangent arc")
def tangent_arc():
    # An existing line runs right into (10.5, 19); the arc leaves it tangentially, turning up.
    c, r = (10.5, 11), 8
    a0, a1 = 90, -60
    return [
        line(3, 19, 10.5, 19, 'stroke-opacity="0.5"'),
        path(arc_d(*c, r, a0, a1)),
        *dots(on(*c, r, a0), on(*c, r, a1)),
    ]


@icon("center-arc", "sketch", "Center point arc")
def center_arc():
    c, r = (5.5, 18.5), 13.5
    a0, a1 = -80, 0
    s, e = on(*c, r, a0), on(*c, r, a1)
    return [
        line(*c, *s, CON),
        line(*c, *e, CON),
        path(arc_d(*c, r, a0, a1)),
        *dots(c, s, e),
    ]


# ---------------------------------------------------------------------------------------------
# Polygons, spline, point, slot, text


INNER = 'fill-opacity="0.6"'  # tint of the enclosed shape in the two polygon icons


@icon("inscribed-polygon", "sketch", "Inscribed polygon")
def inscribed_polygon():
    # The two polygon variants share one rule: the enclosed shape is tinted, the enclosing one is
    # only an outline, so which encloses which reads from the fill in both themes. Here a tinted
    # pentagon has its corners on the dashed construction circle.
    c, R = (12, 12), 9
    vs = ngon(*c, R, 5, -90)
    return [circle(*c, R, None, CON), poly(vs, MID, INNER), *dots(c, vs[1])]


@icon("circumscribed-polygon", "sketch", "Circumscribed polygon")
def circumscribed_polygon():
    # A tinted construction disc inside a pentagon, touching each side's midpoint. Centred
    # optically, since a pentagon reaches further above its centre (R) than below it (apothem).
    ap = 7
    R = ap / math.cos(math.pi / 5)
    c = (12, 12 + (R - ap) / 2)
    vs = ngon(*c, R, 5, -90)
    return [circle(*c, ap - 0.3, MID, INNER + " " + CON), poly(vs), *dots(c, on(*c, ap, 90))]


@icon("spline", "sketch", "Spline")
def spline():
    ps = [(3.8, 17.5), (9, 7.5), (15, 16.5), (20.2, 6.5)]
    return [polyline(catmull(ps)), *dots(*ps)]


@icon("point", "sketch", "Point")
def point():
    c = (12, 12)
    ticks = [line(c[0] + dx * 3.6, c[1] + dy * 3.6, c[0] + dx * 8.5, c[1] + dy * 8.5)
             for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    return [*ticks, dot(*c)]


@icon("slot", "sketch", "Slot")
def slot():
    a, b, r = (8, 16), (16, 8), 4.6
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    p1, p2 = on(*a, r, ang + 90), on(*b, r, ang + 90)
    p3, p4 = on(*b, r, ang - 90), on(*a, r, ang - 90)
    dd = (f"M{f(p1[0])} {f(p1[1])} L{f(p2[0])} {f(p2[1])} A{f(r)} {f(r)} 0 0 0 {f(p3[0])} {f(p3[1])} "
          f"L{f(p4[0])} {f(p4[1])} A{f(r)} {f(r)} 0 0 0 {f(p1[0])} {f(p1[1])} Z")
    return [path(dd, FILL, REGION), line(*a, *b, CON), *dots(a, b)]


@icon("text", "sketch", "Text")
def text():
    # The text box is placed by two opposite corners (like corner-rectangle); a T sits inside.
    x0, y0, x1, y1 = 3.5, 3.5, 20.5, 20.5
    t = [(7.5, 7), (16.5, 7), (16.5, 10.3), (13.7, 10.3), (13.7, 17.5), (10.3, 17.5), (10.3, 10.3), (7.5, 10.3)]
    return [
        rect(x0, y0, x1 - x0, y1 - y0, 0, None, CON),
        poly(t, FILL, REGION),
        *dots((x0, y0), (x1, y1)),
    ]


@icon("construction", "sketch", "Construction")
def construction():
    return [
        circle(12, 12, 8.5, None, dash(1.5)),
        line(5.5, 18.5, 18.5, 5.5, f'{ACC} ' + dash(1.5)),
    ]


@icon("image", "sketch", "Image")
def image():
    x0, y0, x1, y1 = 3.5, 5, 20.5, 19
    return [
        rect(x0, y0, x1 - x0, y1 - y0, 0, FILL, REGION),
        poly([(3.5, 19), (9.5, 11.5), (13.5, 16), (15.5, 13.8), (20.5, 19)], SOFT, 'stroke-width="1.2"'),
        circle(15.5, 9.2, 1.7, None, 'stroke-width="1.2"'),
        *dots((x0, y1), (x1, y0)),
    ]


# ---------------------------------------------------------------------------------------------
# Model references


@icon("use", "sketch", "Use")
def use():
    # A model body (muted, flat silhouette) whose picked edges become sketch geometry (accent).
    c, R = (12, 12.5), 9
    hexv = ngon(*c, R, 6, -90)
    top, rt, br, bot, bl, lt = hexv
    muted = 'stroke-width="1" stroke-opacity="0.45"'
    return [
        poly(hexv, FILL, REGION + " " + muted),
        polyline([lt, c, rt], muted),
        line(*c, *bot, muted),
        polyline([bl, bot, br], ACC),
        *dots(bl, bot, br),
    ]


@icon("intersection", "sketch", "Intersection")
def intersection():
    c, r = (12, 13), 7.5
    y = 11
    dx = math.sqrt(r * r - (y - c[1]) ** 2)
    return [
        circle(*c, r, FILL, REGION + ' stroke-width="1" stroke-opacity="0.5"'),
        line(2.5, y, 21.5, y, CON),
        line(c[0] - dx, y, c[0] + dx, y, ACC),
        *dots((c[0] - dx, y), (c[0] + dx, y)),
    ]


# ---------------------------------------------------------------------------------------------
# Modify


@icon("sketch-fillet", "sketch", "Sketch fillet")
def sketch_fillet():
    return [
        polyline([(5, 13), (5, 5), (13, 5)], CON),
        line(5, 20, 5, 13),
        line(13, 5, 20, 5),
        path("M5 13 A8 8 0 0 1 13 5", None, ACC),
    ]


@icon("sketch-chamfer", "sketch", "Sketch chamfer")
def sketch_chamfer():
    return [
        polyline([(5, 13), (5, 5), (13, 5)], CON),
        line(5, 20, 5, 13),
        line(13, 5, 20, 5),
        line(5, 13, 13, 5, ACC),
    ]


@icon("trim", "sketch", "Trim")
def trim():
    return [
        line(8, 4, 8, 20),
        line(16, 4, 16, 20),
        line(3.5, 12, 8, 12),
        line(16, 12, 20.5, 12),
        line(8, 12, 16, 12, f'{ACC} ' + dash(1.5)),
    ]


@icon("extend", "sketch", "Extend")
def extend():
    return [
        line(19, 4, 19, 20),
        line(3.5, 12, 10, 12),
        arrow(10, 12, 18.5, 12, 3.4, 3.2, ACCENT, dash(1.5)),
    ]


@icon("sketch-split", "sketch", "Split")
def sketch_split():
    c, r = (12, 20), 12
    return [
        path(arc_d(*c, r, 196, 248)),
        path(arc_d(*c, r, 292, 344)),
        dot(*on(*c, r, 270)),
    ]


@icon("offset", "sketch", "Offset")
def offset():
    return [
        rect(3.5, 3.5, 17, 17, 5),
        rect(8, 8, 8, 8, 1.5, None, ACC),
    ]


@icon("mirror", "sketch", "Mirror")
def mirror():
    left = [(9.5, 5), (9.5, 19), (3.5, 19)]
    right = [(24 - x, y) for x, y in left]
    return [
        poly(left, FILL, REGION),
        poly(right, FILL, REGION),
        line(12, 2.5, 12, 21.5, f'{ACC} ' + dash_dot(1.2)),
    ]


@icon("sketch-pattern", "sketch", "Sketch pattern")
def sketch_pattern():
    r = 3.3
    out = []
    for i, (x, y) in enumerate([(7, 7), (17, 7), (7, 17), (17, 17)]):
        out.append(circle(x, y, r, FILL, REGION + (" " + ACC if i == 0 else "")))
    return out


@icon("dxf-import", "sketch", "Import DXF")
def dxf_import():
    return [
        path("M3.5 2.5 H10.5 L14 6 V15 H3.5 Z", FILL, REGION),
        path("M10.5 2.5 V6 H14", None, 'stroke-width="1"'),
        circle(8.2, 10, 2.1, None, 'stroke-width="1"'),
        line(2.5, 20.5, 21.5, 20.5, CON),
        curved_arrow(arc_points(11, 17.5, 7.5, 12, -80, -5), 3.2, 3, ACCENT),
    ]


@icon("dimension", "sketch", "Dimension")
def dimension():
    y, yd = 18.5, 8
    return [
        line(4, y, 20, y),
        line(4, y - 2.5, 4, yd - 3, 'stroke-width="1"'),
        line(20, y - 2.5, 20, yd - 3, 'stroke-width="1"'),
        arrow(12, yd, 4.2, yd, 3, 3, INK, 'stroke-width="1"'),
        arrow(12, yd, 19.8, yd, 3, 3, INK, 'stroke-width="1"'),
        *dots((4, y), (20, y)),
    ]


@icon("diagnostics", "sketch", "Sketch diagnostics")
def diagnostics():
    v = (14.5, 13.5)
    return [
        poly([(3.5, 19), (8.5, 4.5), v], FILL, REGION),
        circle(*v, 4.6),
        line(v[0] + 3.3, v[1] + 3.3, 21.5, 20.5 + 1, 'stroke-width="2"'),
        dot(*v),
    ]
