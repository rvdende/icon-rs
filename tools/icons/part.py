"""Part Studio features, analysis tools and part/document objects (kind "solid").

House style for this module: one iso block of side 8 centred at (12, 12) is the reference size.
Grey faces are context; ACCENT marks the input (tint or stroke) and the output (dashed, faint).
"""
import math
from common import *

THIN = 'stroke-width="0.8"'
HAIR = 'stroke-width="0.7"'


def _acc(w=1.1, extra=""):
    """Stroke attributes for an ACCENT line."""
    return f'stroke="{ACCENT}" stroke-width="{f(w)}" {extra}'.strip()


def _ring(P, cx, cy, z, r, t0, t1, step=6):
    """Points on a horizontal circle from angle t0 to t1 (degrees, in the xy plane)."""
    n = max(2, int(abs(t1 - t0) / step))
    return [P(cx + r * math.cos(math.radians(t0 + (t1 - t0) * i / n)),
              cy + r * math.sin(math.radians(t0 + (t1 - t0) * i / n)), z) for i in range(n + 1)]


# The three roles. CONTEXT is neutral faces with INK outlines. INPUT (what the user selects) is
# an ACCENT tint over a neutral face, or an ACCENT stroke for an edge or path. OUTPUT (what the
# tool creates) is a dashed ACCENT outline with a faint ACCENT fill, or a solid ACCENT face when
# the new face is the point.
SEL = 'stroke="none" fill-opacity="0.45"'


def _out(w=1.1):
    return f'stroke="{ACCENT}" fill-opacity="0.15" ' + dash(w)


def _sel_edge(w=1.6):
    return f'stroke="{ACCENT}" stroke-width="{f(w)}"'


def _block_edge(o, s, cut):
    """Faces of a cube whose top-right edge (x=s, z=s) is replaced by `cut`, a list of (x, z)
    profile points from the top face to the right face."""
    P = projector(o)
    a, b = [P(x, 0, z) for x, z in cut], [P(x, s, z) for x, z in cut]
    return P, a, b, [
        poly([P(0, 0, s), a[0], b[0], P(0, s, s)], TOP),
        poly([a[-1], P(s, 0, 0), P(s, s, 0), b[-1]], MID),
        poly([P(0, s, s)] + b + [P(s, s, 0), P(0, s, 0)], SHADE),
    ]


def _ghost_box(o, x0, x1, y0, y1, z0, z1, w=1.1, inner=True):
    """An OUTPUT box: faint accent silhouette, dashed accent outline and the three edges that meet
    at the near top corner (no per-face outlines, which clutter at small sizes)."""
    P = projector(o)
    sil = [P(x0, y0, z1), P(x1, y0, z1), P(x1, y0, z0), P(x1, y1, z0), P(x0, y1, z0), P(x0, y1, z1)]
    c = P(x1, y1, z1)
    d = f'stroke="{ACCENT}" ' + dash(w)
    out = [poly(sil, ACCENT, 'stroke="none" fill-opacity="0.15"'), poly(sil, None, d)]
    if inner:
        out += [polyline([P(x0, y1, z1), c, P(x1, y0, z1)], d), line(*c, *P(x1, y1, z0), d)]
    else:  # small boxes: just a faint top face so they still read as boxes
        out.append(poly([P(x0, y0, z1), P(x1, y0, z1), c, P(x0, y1, z1)], ACCENT, 'stroke="none" fill-opacity="0.25"'))
    return "\n  ".join(out)


def _cube(o, s=8, **kw):
    return box(o, 0, s, 0, s, 0, s, **kw)


# ---------------------------------------------------------------------------------------------
# Features


@icon("extrude", "solid", "Extrude")
def extrude():
    # Context: the slab. Input: its top face (the profile). Output: the dashed volume the extrude
    # adds, with an INK arrow rising through it.
    o = (12, 13.9)
    P = projector(o)
    s, z0, z1 = 8, 4, 10
    edge = f'stroke="{ACCENT}" ' + dash(1.1)
    faint = 'stroke="none" fill-opacity="0.15"'
    return [
        box(o, 0, s, 0, s, 0, z0),
        poly([P(0, 0, z0), P(s, 0, z0), P(s, s, z0), P(0, s, z0)], ACCENT, SEL),
        poly([P(s, 0, z1), P(s, s, z1), P(s, s, z0), P(s, 0, z0)], ACCENT, faint),
        poly([P(0, s, z1), P(s, s, z1), P(s, s, z0), P(0, s, z0)], ACCENT, faint),
        poly([P(0, 0, z1), P(s, 0, z1), P(s, s, z1), P(0, s, z1)], None, edge),
        *[line(*P(x, y, z0), *P(x, y, z1), edge) for x, y in ((s, 0), (s, s), (0, s))],
        arrow(*P(s / 2, s / 2, z0), *P(s / 2, s / 2, z1 + 2.2), 3.2, 3),
    ]


@icon("revolve", "solid", "Revolve")
def revolve():
    # Input: the flat profile (tinted). Context: the dash-dot axis. The INK arrow wraps the axis,
    # behind the profile at the back and in front of it at the front.
    cx, cy, rx, ry = 9, 12, 6.5, 2.4
    arc = 'stroke-width="1.4"'
    prof = "M11.5 5.5 h7 v10 l-3 3 h-4 z"
    return [
        polyline(arc_points(cx, cy, rx, ry, 200, 340), arc),
        path(prof, TOP),
        path(prof, ACCENT, SEL),
        line(9, 2, 9, 22, dash_dot(0.9)),
        curved_arrow(arc_points(cx, cy, rx, ry, 340, 520), 3.2, 2.8, INK, arc),
    ]


@icon("sweep", "solid", "Sweep")
def sweep():
    # The swept tube is the whole point, so it is a solid body: neutral shading under a light
    # accent wash (output), with the round profile it was swept from as the accent input cap.
    tube = sample_cubic((5.4, 18.1), (14.6, 18.9), (9.4, 5.1), (18.6, 5.9), 48)
    r = 2.7
    left, right = offset_polyline(tube, r), offset_polyline(tube, -r)

    def cap(i, fill, extra=""):
        x, y = tube[i]
        a, b = tube[max(i - 1, 0)], tube[min(i + 1, len(tube) - 1)]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + 90
        return ellipse(x, y, r, 1.3, fill, extra, rotate=ang)

    body = left + right[::-1]
    return [
        poly(body, MID, 'stroke="none"'),
        polyline(offset_polyline(tube, -r * 0.45), f'stroke="{SHADE}" stroke-width="1.4" stroke-opacity="0.45"'),
        polyline(offset_polyline(tube, r * 0.42), f'stroke="{TOP}" stroke-width="1.2" stroke-opacity="0.75"'),
        poly(body, ACCENT, 'stroke="none" fill-opacity="0.2"'),
        polyline(left),
        polyline(right),
        cap(len(tube) - 1, MID),
        cap(0, TOP),
        cap(0, ACCENT, 'stroke="none" fill-opacity="0.45"'),
        cap(0, None, f'stroke="{ACCENT}" stroke-width="1.4"'),
    ]


@icon("loft", "solid", "Loft")
def loft():
    # X-ray view: the body blends a square base into a round top, and dashed hidden edges show
    # the whole base profile through it. Both profiles are accent: they are what the loft joins.
    base_front = [(5, 18), (12, 21.5), (19, 18)]
    base_back = [(5, 18), (12, 14.5), (19, 18)]
    return [
        path("M5 18 L7.5 6.5 A4.5 1.8 0 0 0 16.5 6.5 L19 18 L12 21.5 Z", MID),
        path("M12 21.5 C12 15, 12 11, 12 8.3", None, 'stroke-width="0.8"'),
        polyline(base_back, f'stroke="{ACCENT}" ' + dash(0.9)),
        polyline(base_front, f'stroke="{ACCENT}" stroke-width="1.4"'),
        ellipse(12, 6.5, 4.5, 1.8, TOP, f'stroke="{ACCENT}" stroke-width="1.4"'),
    ]


@icon("thicken", "solid", "Thicken")
def thicken():
    # Input: the wavy surface (tinted). Output: the thickness below it (dashed, faint).
    o = (9.4, 7.9)
    P = projector(o)
    L, W, t = 13, 7, 2.6
    z = lambda x: 1.8 * math.sin(x / L * 2 * math.pi) + t
    xs = [L * i / 30 for i in range(31)]
    front_top = [P(x, W, z(x)) for x in xs]
    front_bot = [P(x, W, z(x) - t) for x in xs]
    back_top = [P(x, 0, z(x)) for x in xs]
    end = [P(L, 0, z(L)), P(L, W, z(L)), P(L, W, z(L) - t), P(L, 0, z(L) - t)]
    sheet = back_top + front_top[::-1]
    return [
        poly(front_top + front_bot[::-1], ACCENT, _out()),
        poly(end, ACCENT, _out()),
        poly(sheet, TOP),
        poly(sheet, ACCENT, SEL),
    ]


@icon("enclose", "solid", "Enclose")
def enclose():
    # Input: an open tube of surface (tinted). Output: the cap that closes it into a solid.
    o = (12, 16.5)
    P = projector(o)
    r, h = 5, 9
    rx, ry = r * math.sqrt(1.5), r * math.sqrt(0.5)
    tx, ty = P(0, 0, h)
    return [
        cylinder(o, 0, 0, 0, h, r, SHADE, MID),
        path(f"M{f(tx - rx)} {f(ty)} L{f(tx - rx)} {f(ty + h)} A{f(rx)} {f(ry)} 0 0 0 {f(tx + rx)} {f(ty + h)} "
             f"L{f(tx + rx)} {f(ty)} A{f(rx)} {f(ry)} 0 0 1 {f(tx - rx)} {f(ty)} Z", ACCENT, SEL),
        ellipse(tx, ty, rx, ry, ACCENT, _out(1.2)),
    ]


@icon("fillet", "solid", "Fillet")
def fillet():
    o, s, r = (12, 12), 8, 4.2
    cut = [(s - r + r * math.sin(math.radians(t)), s - r + r * math.cos(math.radians(t))) for t in range(0, 91, 10)]
    P, a, b, faces = _block_edge(o, s, cut)
    return faces + [poly(a + b[::-1], ACCENT)]


@icon("chamfer", "solid", "Chamfer")
def chamfer():
    o, s, c = (12, 12), 8, 3.8
    P, a, b, faces = _block_edge(o, s, [(s - c, s), (s, s - c)])
    return faces + [poly(a + b[::-1], ACCENT)]


@icon("draft", "solid", "Draft")
def draft():
    # Context: the block. Output: the tapered face (solid accent). The dashed INK line is where
    # the face stood before, parallel to the pull direction.
    o, s, d = (12, 12), 8, 2.6
    P = projector(o)
    return [
        poly([P(0, 0, s), P(s - d, 0, s), P(s - d, s, s), P(0, s, s)], TOP),
        poly([P(0, s, s), P(s - d, s, s), P(s, s, 0), P(0, s, 0)], SHADE),
        poly([P(s - d, 0, s), P(s - d, s, s), P(s, s, 0), P(s, 0, 0)], ACCENT),
        line(*P(s, s, 0), *P(s, s, s + 1), dash(1)),
    ]


@icon("rib", "solid", "Rib")
def rib():
    # Context: the L-bracket. Output: the thin web between its faces.
    o = (10.9, 12.2)
    P = projector(o)
    L, W, T, H = 10, 7, 2, 9
    y0, y1 = W / 2 - 0.8, W / 2 + 0.8
    return [
        box(o, 0, L, 0, W, 0, T),
        box(o, 0, T, 0, W, T, H),
        poly([P(T, y0, H - 0.5), P(T, y1, H - 0.5), P(L - 0.5, y1, T), P(L - 0.5, y0, T)], ACCENT, 'fill-opacity="0.7"'),
        poly([P(T, y1, H - 0.5), P(L - 0.5, y1, T), P(T, y1, T)], ACCENT),
    ]


@icon("shell", "solid", "Shell")
def shell():
    # Context: the hollowed box. Input: the removed top face, tinted over the opening.
    o = (12, 12.2)
    P = projector(o)
    s, h, t = 8.5, 7, 1.5
    rim = [P(t, t, h), P(s - t, t, h), P(s - t, s - t, h), P(t, s - t, h)]
    return [
        box(o, 0, s, 0, s, 0, h),
        poly(clip([P(t, t, t), P(s - t, t, t), P(s - t, s - t, t), P(t, s - t, t)], rim), TOP, HAIR),
        poly(clip([P(t, t, h), P(s - t, t, h), P(s - t, t, t), P(t, t, t)], rim), SHADE, HAIR),
        poly(clip([P(t, t, h), P(t, s - t, h), P(t, s - t, t), P(t, t, t)], rim), MID, HAIR),
        poly(rim, ACCENT, 'stroke="none" fill-opacity="0.4"'),
        poly(rim, None, _sel_edge(1.3)),
    ]


@icon("hole", "solid", "Hole")
def hole():
    o = (12, 9)
    P = projector(o)
    s, h = 10, 4
    c, r1, r2, d1 = s / 2, 3.4, 1.9, 1.6
    e1 = iso_circle(o, c, c, h, r1)
    floor = iso_circle(o, c, c, h - d1, r1)
    e2 = iso_circle(o, c, c, h - d1, r2)
    deep = iso_circle(o, c, c, h - d1 - 4, r2)
    return [
        box(o, 0, s, 0, s, 0, h),
        poly(e1, ACCENT),
        poly(clip(floor, e1), TOP, HAIR),
        poly(clip(e2, e1), ACCENT, HAIR),
        poly(clip(clip(deep, e2), e1), SHADE, 'stroke="none"'),
        poly(e1, None),
    ]


@icon("thread", "solid", "Thread")
def thread():
    # Context: the plain rod. Output: the threaded band, a solid accent face with a toothed
    # silhouette.
    o = (12, 17.4)
    ox, oy = o
    r, k, h, zt, pitch = 4, 0.9, 11, 7.2, 1.8
    rx, ry = r * math.sqrt(1.5), r * math.sqrt(0.5)
    left, right = [], []
    z = 0.5
    while z + pitch <= zt + 0.01:
        right += [(ox + rx + k, oy - z - pitch / 4), (ox + rx, oy - z - pitch / 2)]
        left += [(ox - rx - k, oy - z - pitch * 3 / 4), (ox - rx, oy - z - pitch)]
        z += pitch
    band = ([(ox - rx, oy - zt)] + left[::-1] + [(ox - rx, oy)]
            + arc_points(ox, oy, rx, ry, 180, 0, 6)[1:] + [(ox + rx, oy)] + right + [(ox + rx, oy - zt)]
            + arc_points(ox, oy - zt, rx, ry, 0, 180, 6)[1:])
    return [
        cylinder(o, 0, 0, 0, h, r),
        poly(band, ACCENT),
    ]


@icon("linear-pattern", "solid", "Linear pattern")
def linear_pattern():
    # Context: the seed cube. Output: two dashed copies along x.
    o = (6.6, 8.9)
    c, p = 4.6, 6.2
    return [_ghost_box(o, i * p, i * p + c, 0, c, 0, c, inner=False) for i in (2, 1)] + [
        box(o, 0, c, 0, c, 0, c)]


@icon("circular-pattern", "solid", "Circular pattern")
def circular_pattern():
    # Context: the seed cube (front) and the axis. Output: three dashed copies at 90 degrees.
    o = (12, 13.4)
    P = projector(o)
    R, c = 5.4, 3.4
    items = sorted((math.cos(t) + math.sin(t), i, R * math.cos(t), R * math.sin(t))
                   for i, t in enumerate(math.radians(45 + 90 * i) for i in range(4)))
    out = [line(*P(0, 0, -2), *P(0, 0, 8), dash_dot(0.9))]
    for _, i, cx, cy in items:
        b = (cx - c / 2, cx + c / 2, cy - c / 2, cy + c / 2, 0, c)
        out.append(box(o, *b) if i == 0 else _ghost_box(o, *b, inner=False))
    return out


@icon("boolean", "solid", "Boolean")
def boolean():
    r, d, cy = 6.2, 7.4, 12
    c1, c2 = 12 - d / 2, 12 + d / 2
    h = math.sqrt(r * r - (d / 2) ** 2)  # half height of the lens

    def crescent(cx):
        # Inside the sphere, outside the same circle nudged up-right: the shadow side.
        ox, oy = cx + 1.7, cy - 1.7
        inside = lambda x, y, a, b: math.hypot(x - a, y - b) < r
        rim = [(cx + r * math.cos(math.radians(t)), cy + r * math.sin(math.radians(t))) for t in range(-45, 316, 3)]
        inner = [(ox + r * math.cos(math.radians(t)), oy + r * math.sin(math.radians(t))) for t in range(315, -46, -3)]
        return ([p for p in rim if not inside(*p, ox, oy)] + [p for p in inner if inside(*p, cx, cy)])

    lens = (f"M12 {f(cy - h)} A{f(r)} {f(r)} 0 0 1 12 {f(cy + h)} "
            f"A{f(r)} {f(r)} 0 0 1 12 {f(cy - h)} Z")
    return [
        circle(c1, cy, r, SOFT, 'stroke="none"'),
        poly(crescent(c1), MID, 'stroke="none"'),
        circle(c1 + 0.6, cy - 2.6, 1.8, TOP, 'stroke="none"'),
        circle(c2, cy, r, MID, 'stroke="none"'),
        poly(crescent(c2), SHADE, 'stroke="none"'),
        circle(c2 + 1.9, cy - 2.2, 2, TOP, 'stroke="none"'),
        path(lens, ACCENT, 'stroke="none" fill-opacity="0.7"'),
        circle(c1, cy, r),
        circle(c2, cy, r),
    ]


@icon("split", "solid", "Split")
def split():
    # Context: the two halves. Input: the splitting plane (tinted, accent edge).
    o = (11, 12)
    P = projector(o)
    s, g, cut = 8, 2.2, 3.6
    q = 2.2
    x = cut + g / 2
    plane = [P(x, -q, s + q), P(x, s + q, s + q), P(x, s + q, -q), P(x, -q, -q)]
    return [
        box(o, 0, cut, 0, s, 0, s),
        poly(plane, ACCENT, _sel_edge(1.2) + ' fill-opacity="0.3"'),
        box(o, cut + g, s + g, 0, s, 0, s),
    ]


@icon("transform", "solid", "Transform")
def transform():
    # Context: the part where it is. Output: where it goes (dashed). INK arrow for the move.
    o1, o2 = (7.2, 16.6), (16.8, 7.4)
    c = 4.6
    P1, P2 = projector(o1), projector(o2)
    return [
        _ghost_box(o2, 0, c, 0, c, 0, c, inner=False),
        box(o1, 0, c, 0, c, 0, c),
        arrow(*P1(c, c * 0.35, c * 0.9), *P2(c * 0.35, c, c * 0.15), 3, 2.8, INK, 'stroke-width="1.4"'),
    ]


@icon("composite-part", "solid", "Composite part")
def composite_part():
    # Context: a plate with two blocks on it, kept as they are. Output: the one part they make
    # (a dashed accent outline round all three, the silhouette of their bounding box).
    o = (11.6, 5.2)
    P = projector(o)
    x0, x1, y0, y1, z0, z1 = -1.2, 11.2, -1.2, 9.2, -1.0, 6.4
    sil = [P(x0, y0, z1), P(x1, y0, z1), P(x1, y0, z0), P(x1, y1, z0), P(x0, y1, z0), P(x0, y1, z1)]
    return [
        box(o, 0, 10, 0, 8, 0, 1.4),
        box(o, 1.2, 4.4, 1.0, 4.0, 1.4, 5.2),
        box(o, 5.4, 8.4, 4.0, 6.8, 1.4, 3.6),
        poly(sil, None, f'stroke="{ACCENT}" ' + dash(1.1)),
    ]


@icon("plane", "solid", "Plane")
def plane():
    # Context: a reference face. Output: the new plane offset above it (dashed, faint).
    o = (12, 5.6)
    P = projector(o)
    s = 10
    return [
        poly([P(0, 0, -6), P(s, 0, -6), P(s, s, -6), P(0, s, -6)], TOP),
        poly([P(0, 0, 0), P(s, 0, 0), P(s, s, 0), P(0, s, 0)], ACCENT, _out(1.2)),
    ]


@icon("mate-connector", "solid", "Mate connector")
def mate_connector():
    # Context: the connector symbol, a disc on the floor plane with one quarter filled. Output:
    # the accent triad rising from its centre (z up, x and y along the floor).
    o = (12, 14.6)
    P = projector(o)
    r = 6.6
    disc = iso_circle(o, 0, 0, 0, r)
    wedge = [P(0, 0, 0)] + [P(r * math.cos(math.radians(t)), r * math.sin(math.radians(t)), 0) for t in range(0, 91, 6)]
    w = 'stroke-width="1.4"'
    return [
        poly(disc, TOP),
        poly(wedge, MID, 'stroke-width="0.9"'),
        arrow(*P(0, 0, 0), *P(0, 0, 12), 3, 2.8, ACCENT, w),
        arrow(*P(0, 0, 0), *P(9.8, 0, 0), 3, 2.8, ACCENT, w),
        arrow(*P(0, 0, 0), *P(0, 9.8, 0), 3, 2.8, ACCENT, w),
        circle(*P(0, 0, 0), 1.3, ACCENT, 'stroke="none"'),
    ]


@icon("custom-feature", "solid", "Add custom feature")
def custom_feature():
    o = (10, 10.4)
    P = projector(o)
    s = 7.5
    h, m = s * 0.45, s * 0.5
    bx, by, a = 18.4, 18.4, 2.9
    return [
        poly([P(0, 0, s), P(m, 0, s), P(m, s, s), P(0, s, s)], TOP),
        poly([P(m, 0, s), P(m, s, s), P(m, s, h), P(m, 0, h)], MID),
        poly([P(m, 0, h), P(s, 0, h), P(s, s, h), P(m, s, h)], TOP),
        poly([P(s, 0, h), P(s, s, h), P(s, s, 0), P(s, 0, 0)], MID),
        poly([P(0, s, s), P(m, s, s), P(m, s, h), P(s, s, h), P(s, s, 0), P(0, s, 0)], SHADE),
        path(f"M{f(bx - a)} {f(by)} H{f(bx + a)} M{f(bx)} {f(by - a)} V{f(by + a)}", None, _acc(2.3)),
    ]


@icon("measure", "solid", "Measure")
def measure():
    # Context: the block. Output: the accent dimension between its end faces.
    o = (9.6, 12.4)
    P = projector(o)
    L, W, H, up = 12, 6, 4.5, 3.6
    return [
        box(o, 0, L, 0, W, 0, H),
        line(*P(0, 0, H + 1), *P(0, 0, H + up + 1.2), THIN),
        line(*P(L, 0, H + 1), *P(L, 0, H + up + 1.2), THIN),
        arrow(*P(L / 2, 0, H + up), *P(0, 0, H + up), 2.8, 2.6, ACCENT, 'stroke-width="1.4"'),
        arrow(*P(L / 2, 0, H + up), *P(L, 0, H + up), 2.8, 2.6, ACCENT, 'stroke-width="1.4"'),
    ]


@icon("section-view", "solid", "Section view")
def section_view():
    o = (10.3, 12)
    P = projector(o)
    L, D, H = 10, 6, 8
    w = 2  # wall
    cut = [P(0, D, H), P(L, D, H), P(L, D, 0), P(0, D, 0)]
    cav = [P(w, D, H - w), P(L - w, D, H - w), P(L - w, D, w), P(w, D, w)]
    d = lambda ps: "M" + " L".join(f"{f(x)} {f(y)}" for x, y in ps) + " Z"
    return [
        poly([P(0, 0, H), P(L, 0, H), P(L, D, H), P(0, D, H)], TOP),
        poly([P(L, 0, H), P(L, D, H), P(L, D, 0), P(L, 0, 0)], MID),
        poly(cav, SHADE, 'stroke="none"'),
        poly(clip([P(w, w, H - w), P(w, D + 1, H - w), P(w, D + 1, w), P(w, w, w)], cav), MID, HAIR),
        poly(clip([P(w, w, w), P(L - w, w, w), P(L - w, D + 1, w), P(w, D + 1, w)], cav), TOP, HAIR),
        path(d(cut) + " " + d(cav), ACCENT, 'fill-rule="evenodd"'),
    ]


@icon("mass-properties", "solid", "Mass properties")
def mass_properties():
    o = (12, 12)
    cx, cy, r = 12, 12, 3.6
    q = lambda a0: (f"M{f(cx)} {f(cy)} L{f(cx + r * math.cos(math.radians(a0)))} {f(cy + r * math.sin(math.radians(a0)))} "
                    f"A{f(r)} {f(r)} 0 0 1 {f(cx + r * math.cos(math.radians(a0 + 90)))} "
                    f"{f(cy + r * math.sin(math.radians(a0 + 90)))} Z")
    return [
        _cube(o, 8),
        circle(cx, cy, r, TOP, _acc(1.3)),
        path(q(-90) + " " + q(90), ACCENT, 'stroke="none"'),
    ]


@icon("part", "solid", "Part")
def part():
    return _cube((12, 12), 8.4)


@icon("sketch", "solid", "Sketch")
def sketch():
    # A sketch plane (context) with the profile drawn on it (output, accent) and the pencil
    # drawing it, its tip on the profile's far corner.
    o = (12, 8.8)
    P = projector(o)
    s, a, b, r = 11, 2.4, 8.6, 2.8
    plane = [P(0, 0, 0), P(s, 0, 0), P(s, s, 0), P(0, s, 0)]
    arc = [P(b - r + r * math.cos(math.radians(t)), b - r + r * math.sin(math.radians(t)), 0) for t in range(0, 91, 10)]
    prof = [P(a, a, 0), P(b, a, 0)] + arc + [P(a, b, 0)]
    tip = P(a, a, 0)
    ang = math.radians(-68)
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux
    L, w, cone = 6.4, 1.6, 2.4
    base = (tip[0] + ux * cone, tip[1] + uy * cone)
    end = (base[0] + ux * L, base[1] + uy * L)
    body = [(base[0] + nx * w, base[1] + ny * w), (end[0] + nx * w, end[1] + ny * w),
            (end[0] - nx * w, end[1] - ny * w), (base[0] - nx * w, base[1] - ny * w)]
    return [
        poly(plane, TOP),
        poly(prof, ACCENT, f'stroke="{ACCENT}" stroke-width="1.5" fill-opacity="0.15"'),
        poly(body, SOFT),
        poly([tip, body[0], body[3]], TOP),
    ]


@icon("surface", "solid", "Surface")
def surface():
    # A thin curved sheet with no real thickness: a surface body. Neutral, like part.
    top = "M2.5 9.5 C7 3.5, 11 13.5, 15.5 7.5 L21.5 11.5 C17 17.5, 13 7.5, 8.5 13.5 Z"
    edge = "M8.5 13.5 C13 7.5, 17 17.5, 21.5 11.5 L21.5 13.4 C17 19.4, 13 9.4, 8.5 15.4 Z"
    left = "M2.5 9.5 L8.5 13.5 L8.5 15.4 L2.5 11.4 Z"
    return [path(edge, SHADE), path(left, MID), path(top, TOP)]
