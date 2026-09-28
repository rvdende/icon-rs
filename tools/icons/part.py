"""Part Studio features, analysis tools and part/document objects (kind "solid").

House style for this module: one iso block of side 8 centred at (12, 12) is the reference size.
Grey faces are the part; ACCENT is the one thing the feature adds, removes or acts on.
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


def _cube(o, s=8, **kw):
    return box(o, 0, s, 0, s, 0, s, **kw)


# ---------------------------------------------------------------------------------------------
# Features


@icon("extrude", "solid", "Extrude")
def extrude():
    o = (12, 12.8)
    P = projector(o)
    return [
        box(o, 0, 8, 0, 8, 0, 4.5),
        circle(*P(4, 4, 4.5), 1, ACCENT, 'stroke="none"'),
        arrow(*P(4, 4, 4.5), *P(4, 4, 13.3), 3.4, 3.2, ACCENT, 'stroke-width="1.5"'),
    ]


@icon("revolve", "solid", "Revolve")
def revolve():
    o = (12, 16.7)
    P = projector(o)
    k = 1 / math.sqrt(2)
    # The profile lies in the plane through the axis that faces the viewer (direction x = -y).
    prof = [(0, 0), (5.6, 0), (5.6, 2.4), (2.6, 2.4), (2.6, 9), (0, 9)]
    zr, r = 5, 7
    back = _ring(P, 0, 0, zr, r, 160, 315)
    front = _ring(P, 0, 0, zr, r, 315, 465)
    return [
        polyline(back, _acc(1.5)),
        poly([P(u * k, -u * k, z) for u, z in prof], MID),
        line(*P(0, 0, -3), *P(0, 0, 12.4), dash_dot(0.9)),
        curved_arrow(front, 3.4, 3.2, ACCENT, 'stroke-width="1.5"'),
    ]


@icon("sweep", "solid", "Sweep")
def sweep():
    tube = sample_cubic((5.4, 18.1), (14.6, 18.9), (9.4, 5.1), (18.6, 5.9), 48)
    r = 2.7
    left, right = offset_polyline(tube, r), offset_polyline(tube, -r)

    def cap(i, fill, extra=""):
        x, y = tube[i]
        a, b = tube[max(i - 1, 0)], tube[min(i + 1, len(tube) - 1)]
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) + 90
        return ellipse(x, y, r, 1.3, fill, extra, rotate=ang)

    return [
        poly(left + right[::-1], MID, 'stroke="none"'),
        polyline(offset_polyline(tube, -r * 0.45), f'stroke="{SHADE}" stroke-width="1.4" stroke-opacity="0.45"'),
        polyline(offset_polyline(tube, r * 0.42), f'stroke="{TOP}" stroke-width="1.2" stroke-opacity="0.75"'),
        polyline(left),
        polyline(right),
        cap(len(tube) - 1, MID),
        cap(0, TOP, _acc(1.4)),
    ]


@icon("loft", "solid", "Loft")
def loft():
    o = (12, 11.6)
    P = projector(o)
    s = 9
    bot = [P(0, 0, 0), P(s, 0, 0), P(s, s, 0), P(0, s, 0)]
    c = (s / 2, s / 2)
    zt, rt = 10.5, 3.3
    top = iso_circle(o, *c, zt, rt, 48)
    tl = min(top, key=lambda p: p[0])
    tr = max(top, key=lambda p: p[0])
    front = P(s, s, 0)
    fe = max(top, key=lambda p: p[1])  # front of the top ellipse
    body = (f"M{f(bot[3][0])} {f(bot[3][1])} L{f(tl[0])} {f(tl[1])} L{f(tr[0])} {f(tr[1])} "
            f"L{f(bot[1][0])} {f(bot[1][1])} L{f(front[0])} {f(front[1])} Z")
    seam = (f"M{f(fe[0])} {f(fe[1])} C{f(fe[0])} {f(fe[1] + 4)} {f(front[0])} {f(front[1] - 4)} "
            f"{f(front[0])} {f(front[1])} L{f(bot[1][0])} {f(bot[1][1])} L{f(tr[0])} {f(tr[1])} Z")
    return [
        path(body, SHADE, 'stroke="none"'),
        path(seam, MID, 'stroke="none"'),
        path(body, None),
        poly(top, TOP, _acc(1.4)),
        polyline([bot[3], front, bot[1]], _acc(1.4)),
    ]


@icon("thicken", "solid", "Thicken")
def thicken():
    o = (9.4, 7.9)
    P = projector(o)
    L, W, t = 13, 7, 2.4
    z = lambda x: 1.8 * math.sin(x / L * 2 * math.pi)
    xs = [L * i / 30 for i in range(31)]
    front_top = [P(x, W, z(x) + t) for x in xs]
    front_bot = [P(x, W, z(x)) for x in xs]
    back_top = [P(x, 0, z(x) + t) for x in xs]
    end = [P(L, 0, z(L) + t), P(L, W, z(L) + t), P(L, W, z(L)), P(L, 0, z(L))]
    return [
        poly(front_top + front_bot[::-1], ACCENT),
        poly(end, ACCENT, 'fill-opacity="0.75"'),
        poly(back_top + front_top[::-1], TOP),
        polyline(front_top),
    ]


@icon("enclose", "solid", "Enclose")
def enclose():
    o = (12, 12)
    P = projector(o)
    s, e = 7.4, 2.1
    stubs = [
        ((0, 0, s), (-e, 0, s)), ((0, 0, s), (0, -e, s)),
        ((s, 0, s), (s + e, 0, s)), ((s, 0, s), (s, -e, s)), ((s, 0, 0), (s, 0, -e)), ((s, 0, 0), (s, -e, 0)),
        ((0, s, s), (0, s + e, s)), ((0, s, s), (-e, s, s)), ((0, s, 0), (0, s, -e)), ((0, s, 0), (-e, s, 0)),
        ((s, s, s), (s, s, s + e)), ((s, s, 0), (s, s, -e)), ((s, s, s), (s + e, s, s)), ((s, s, s), (s, s + e, s)),
        ((s, s, 0), (s + e, s, 0)), ((s, s, 0), (s, s + e, 0)),
    ]
    return [
        box(o, 0, s, 0, s, 0, s, ACCENT, ACCENT, ACCENT, 'stroke="none" fill-opacity="0.25"'),
        poly([P(0, s, s), P(s, s, s), P(s, s, 0), P(0, s, 0)], ACCENT, 'stroke="none" fill-opacity="0.35"'),
        poly([P(s, 0, s), P(s, s, s), P(s, s, 0), P(s, 0, 0)], ACCENT, 'stroke="none" fill-opacity="0.1"'),
        *[line(*P(*a), *P(*b), THIN) for a, b in stubs],
        box(o, 0, s, 0, s, 0, s, "none", "none", "none"),
    ]


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
    o, s, d = (12, 12), 8, 2.6
    P = projector(o)
    za = 5.2
    a0, a1 = P(s, s, za), P(s - d * za / s, s, za)
    return [
        poly([P(0, 0, s), P(s - d, 0, s), P(s - d, s, s), P(0, s, s)], TOP),
        poly([P(0, s, s), P(s - d, s, s), P(s, s, 0), P(0, s, 0)], SHADE),
        poly([P(s - d, 0, s), P(s - d, s, s), P(s, s, 0), P(s, 0, 0)], ACCENT),
        line(*P(s, s, 0), *P(s, s, s + 1), f'stroke="{TOP}" ' + dash(1)),
    ]


@icon("rib", "solid", "Rib")
def rib():
    o = (10.9, 12.2)
    P = projector(o)
    L, W, T, H = 10, 7, 2, 9
    y0, y1 = W / 2 - 0.7, W / 2 + 0.7
    return [
        box(o, 0, L, 0, W, 0, T),  # base
        box(o, 0, T, 0, W, T, H),  # wall
        poly([P(T, y0, H - 0.5), P(T, y1, H - 0.5), P(L - 0.5, y1, T), P(L - 0.5, y0, T)], ACCENT, 'fill-opacity="0.7"'),
        poly([P(T, y1, H - 0.5), P(L - 0.5, y1, T), P(T, y1, T)], ACCENT),
    ]


@icon("shell", "solid", "Shell")
def shell():
    o = (12, 12.8)
    P = projector(o)
    s, h, t = 8.5, 6, 1.5
    rim = [P(t, t, h), P(s - t, t, h), P(s - t, s - t, h), P(t, s - t, h)]
    lid = [P(0, 0, h + 3.2), P(s, 0, h + 3.2), P(s, s, h + 3.2), P(0, s, h + 3.2)]
    return [
        box(o, 0, s, 0, s, 0, h),
        poly(clip([P(t, t, t), P(s - t, t, t), P(s - t, s - t, t), P(t, s - t, t)], rim), TOP, HAIR),
        poly(clip([P(t, t, h), P(s - t, t, h), P(s - t, t, t), P(t, t, t)], rim), SHADE, HAIR),
        poly(clip([P(t, t, h), P(t, s - t, h), P(t, s - t, t), P(t, t, t)], rim), MID, HAIR),
        poly(rim),
        poly(lid, ACCENT, f'stroke="{ACCENT}" fill-opacity="0.18" ' + dash(1.1)),
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
    o = (12, 18.6)
    P = projector(o)
    r, k, zs, pitch = 3.3, 0.8, 8.2, 1.9
    rx, ry = r * math.sqrt(1.5), r * math.sqrt(0.5)
    ox, oy = o
    z0, n = 0.7, 4
    left, right, crests = [], [], []
    R = r + k / math.sqrt(1.5)
    for i in range(n):
        zr = z0 + i * pitch  # right tip
        right += [(ox + rx + k, oy - zr), (ox + rx, oy - zr - pitch / 2)]
        zl = zr + pitch / 2
        left += [(ox - rx - k, oy - zl), (ox - rx, oy - zl - pitch / 2)]
        crests.append([P(R * math.cos(math.radians(t)), R * math.sin(math.radians(t)), zr + pitch * (t + 45) / 360)
                       for t in range(-45, 136, 9)])
    side = ([(ox - rx, oy - zs)] + left[::-1] + [(ox - rx, oy)]
            + arc_points(ox, oy, rx, ry, 180, 0, 6)[1:] + right + [(ox + rx, oy - zs)])
    return [
        poly(side, MID),
        *[polyline(c, _acc(1.15)) for c in crests],
        cylinder(o, 0, 0, zs, zs + 3, 5.2),
    ]


@icon("linear-pattern", "solid", "Linear pattern")
def linear_pattern():
    o = (6.6, 8.9)
    c, p = 4.6, 6.2
    out = []
    for i in (2, 1):
        x = i * p
        out.append(box(o, x, x + c, 0, c, 0, c, ACCENT, ACCENT, ACCENT, _acc(1.1, 'fill-opacity="0.22"')))
    out.append(box(o, 0, c, 0, c, 0, c))
    return out


@icon("circular-pattern", "solid", "Circular pattern")
def circular_pattern():
    o = (12, 13.6)
    P = projector(o)
    R, c, n = 6.6, 2.9, 6
    items = []
    for i in range(n):
        t = math.radians(45 + 360 * i / n)
        items.append((math.cos(t) + math.sin(t), i, R * math.cos(t), R * math.sin(t)))
    out = [polyline(_ring(P, 0, 0, 0, R, 0, 360, 5), dash(0.8)),
           line(*P(0, 0, -1.5), *P(0, 0, 6), dash_dot(0.9))]
    for _, i, cx, cy in sorted(items):
        b = (cx - c / 2, cx + c / 2, cy - c / 2, cy + c / 2, 0, c)
        if i == 0:
            out.append(box(o, *b))
        else:
            out.append(box(o, *b, ACCENT, ACCENT, ACCENT, _acc(1, 'fill-opacity="0.22"')))
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
    o = (11, 12)
    P = projector(o)
    s, g, cut = 8, 2.2, 3.6
    q = 2.2
    x = cut + g / 2
    plane = [P(x, -q, s + q), P(x, s + q, s + q), P(x, s + q, -q), P(x, -q, -q)]
    return [
        box(o, 0, cut, 0, s, 0, s),
        poly(plane, ACCENT, _acc(1.1, 'fill-opacity="0.22"')),
        box(o, cut + g, s + g, 0, s, 0, s),
    ]


@icon("transform", "solid", "Transform")
def transform():
    o1, o2 = (8, 15.8), (16, 8.2)
    c = 5.5
    P1, P2 = projector(o1), projector(o2)
    return [
        box(o1, 0, c, 0, c, 0, c, "none", "none", "none", 'stroke-opacity="0.4" ' + THIN),
        box(o2, 0, c, 0, c, 0, c),
        arrow(*P1(c * 0.5, c * 0.5, c * 0.5), *P2(c * 0.25, c, c * 0.25), 3.4, 3.2, ACCENT, 'stroke-width="1.5"'),
    ]


@icon("plane", "solid", "Plane")
def plane():
    o = (12, 7)
    P = projector(o)
    s = 11
    return [
        poly([P(0, 0, 0), P(s, 0, 0), P(s, s, 0), P(0, s, 0)], ACCENT, _acc(1.3, 'fill-opacity="0.2"')),
        poly([P(0, 0, 0), P(2.8, 0, 0), P(0, 2.8, 0)], ACCENT, 'stroke="none"'),
    ]


@icon("mate-connector", "solid", "Mate connector")
def mate_connector():
    o = (12, 11.2)
    P = projector(o)
    s, h = 9.5, 2
    oc = (s / 2, s / 2, h)
    w = 'stroke-width="1.3"'
    return [
        box(o, 0, s, 0, s, 0, h),
        arrow(*P(*oc), *P(oc[0], oc[1], h + 8.8), 2.8, 2.6, ACCENT, w),
        arrow(*P(*oc), *P(oc[0] + 7, oc[1], h), 2.8, 2.6, ACCENT, w),
        arrow(*P(*oc), *P(oc[0], oc[1] + 7, h), 2.8, 2.6, ACCENT, w),
        circle(*P(*oc), 1.5, ACCENT, f'stroke="{TOP}" stroke-width="0.9"'),
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
    o = (9.6, 12.4)
    P = projector(o)
    L, W, H, up = 12, 6, 4.5, 3.6
    return [
        box(o, 0, L, 0, W, 0, H),
        line(*P(0, 0, H + 1), *P(0, 0, H + up + 1.2), _acc(0.9)),
        line(*P(L, 0, H + 1), *P(L, 0, H + up + 1.2), _acc(0.9)),
        arrow(*P(L / 2, 0, H + up), *P(0, 0, H + up), 2.8, 2.6, ACCENT, 'stroke-width="1.3"'),
        arrow(*P(L / 2, 0, H + up), *P(L, 0, H + up), 2.8, 2.6, ACCENT, 'stroke-width="1.3"'),
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
