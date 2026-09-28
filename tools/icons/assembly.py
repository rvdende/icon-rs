"""Assembly mates, relations and tools, and the document types (kind "solid").

Roles: context geometry is neutral (TOP/SOFT/MID/SHADE); ACCENT marks only what explains the tool.
Mates show two parts (the fixed one lit a step darker, SOFT top) and ACCENT for the motion the mate
allows or the faces it constrains. Relations accent the coupled motion. The document types share one
base, a square platform, with the type's emblem on it in ACCENT.
"""
import math
from common import *

R15, R05 = math.sqrt(1.5), math.sqrt(0.5)
GROUND = dict(top=SOFT, right=MID, left=SHADE)
THIN = 'stroke-width="0.8"'


def acc(extra=""):
    return f'stroke="{ACCENT}"' + (" " + extra if extra else "")


def hull(ps):
    """Convex hull (monotone chain) of screen points."""
    ps = sorted(set((round(x, 3), round(y, 3)) for x, y in ps))
    if len(ps) < 3:
        return ps

    def half(seq):
        out = []
        for p in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (p[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0])) <= 0:
                out.pop()
            out.append(p)
        return out

    lo, hi = half(ps), half(ps[::-1])
    return lo[:-1] + hi[:-1]


def ring(o, cx, cy, z, r, d0, d1, step=5):
    """Screen points on a horizontal circle, by ellipse angle (0 = screen right, 90 = front)."""
    x, y = projector(o)(cx, cy, z)
    return arc_points(x, y, r * R15, r * R05, d0, d1, step)


def spin(o, cx, cy, z, r, d0=165, d1=15, color=ACCENT, head=2.8, width=2.6):
    """A curved arrow around a vertical axis, across the front of it."""
    return curved_arrow(ring(o, cx, cy, z, r, d0, d1), head, width, color)


def darrow(a, b, color=ACCENT, head=2.8, width=2.6):
    """A double-headed arrow from a to b."""
    m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    return [arrow(*m, *a, head, width, color), arrow(*m, *b, head, width, color)]


def sphere(cx, cy, r, fill=TOP, shade=MID):
    """A sphere lit from above-right: a shaded crescent at the lower left."""
    n = 48
    body = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    k = r * 0.3
    lit = [(cx + k + r * 0.92 * math.cos(2 * math.pi * i / n), cy - k + r * 0.92 * math.sin(2 * math.pi * i / n))
           for i in range(n)]
    return [circle(cx, cy, r, shade, 'stroke="none"'), poly(clip(lit, body), fill, 'stroke="none"'),
            circle(cx, cy, r)]


def xcyl(o, x0, x1, cy, cz, r, side=TOP, cap=MID, extra=""):
    """A cylinder lying along x; the +x end cap is visible."""
    P = projector(o)
    n = 48
    end = lambda x: [P(x, cy + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n))
                     for i in range(n)]
    return [poly(hull(end(x0) + end(x1)), side, extra), poly(end(x1), cap, extra)]


def gear_outline(cx, cy, r_out, r_root, teeth, phase=0.0):
    """A gear outline in a plane, as (u, v) points."""
    out = []
    w = 2 * math.pi / teeth
    for k in range(teeth):
        a = w * (k + phase)
        for t, r in ((0.0, r_root), (0.18, r_out), (0.5, r_out), (0.68, r_root)):
            out.append((cx + r * math.cos(a + t * w), cy + r * math.sin(a + t * w)))
    return out


def flat_gear(o, cx, cy, z0, z1, r_out, r_root, teeth, phase=0.0, top=TOP, side=MID, hole=True):
    """A gear lying flat, extruded from z0 to z1."""
    P = projector(o)
    g = gear_outline(cx, cy, r_out, r_root, teeth, phase)
    els = [poly([P(u, v, z0) for u, v in g], side)]
    steps = 4
    for i in range(1, steps):
        z = z0 + (z1 - z0) * i / steps
        els.append(poly([P(u, v, z) for u, v in g], side, 'stroke="none"'))
    els.append(poly([P(u, v, z1) for u, v in g], top))
    if hole:
        els.append(poly(ring(o, cx, cy, z1, r_root * 0.32, 0, 360, 10), SHADE, THIN))
    return els


TINT = 'stroke="none" fill-opacity="0.45"'


def tint_box(o, x0, x1, y0, y1, z0, z1):
    """A box marked as the input or emblem: neutral faces under an accent wash."""
    return [box(o, x0, x1, y0, y1, z0, z1), box(o, x0, x1, y0, y1, z0, z1, ACCENT, ACCENT, ACCENT, TINT)]


def tint_cyl(o, cx, cy, z0, z1, r):
    return [cylinder(o, cx, cy, z0, z1, r), cylinder(o, cx, cy, z0, z1, r, ACCENT, ACCENT, TINT)]


def ground(o, x1, y1, z1=2.0):
    return box(o, 0, x1, 0, y1, 0, z1, **GROUND)


def ghost_cyl(o, cx, cy, z0, z1, r, extra):
    P = projector(o)
    rx, ry = r * R15, r * R05
    (bx, by), (tx, ty) = P(cx, cy, z0), P(cx, cy, z1)
    return [ellipse(tx, ty, rx, ry, None, extra),
            path(f"M{f(tx - rx)} {f(ty)} L{f(bx - rx)} {f(by)} A{f(rx)} {f(ry)} 0 0 0 {f(bx + rx)} {f(by)} "
                 f"L{f(tx + rx)} {f(ty)}", None, extra)]


# ---------------------------------------------------------------------------------------------
# Mates


@icon("mate-fastened", "solid", "Fastened mate")
def mate_fastened():
    o = (12, 9.6)
    P = projector(o)
    return [
        ground(o, 9, 9),
        box(o, 1.8, 7.2, 1.8, 7.2, 2, 7.4),
        polyline([P(1.8, 7.2, 2), P(7.2, 7.2, 2), P(7.2, 1.8, 2)], acc('stroke-width="2"')),
    ]


@icon("mate-revolute", "solid", "Revolute mate")
def mate_revolute():
    o = (12, 17)
    return [
        cylinder(o, 0, 0, 0, 11, 1.3, SOFT, MID),
        cylinder(o, 0, 0, 4, 6.8, 4.4),
        cylinder(o, 0, 0, 6.8, 11, 1.3, SOFT, MID),
        spin(o, 0, 0, 4.6, 5.9, 160, 25),
    ]


@icon("mate-slider", "solid", "Slider mate")
def mate_slider():
    o = (7.9, 8.5)
    P = projector(o)
    return [
        box(o, 0, 15, 0, 5, 0, 2, **GROUND),
        box(o, 5.5, 9.5, 0, 5, 2, 6),
        arrow(*P(10.3, 2.5, 2), *P(15.2, 2.5, 2), 2.8, 2.6, ACCENT),
        arrow(*P(4.7, 2.5, 2), *P(-0.2, 2.5, 2), 2.8, 2.6, ACCENT),
    ]


@icon("mate-planar", "solid", "Planar mate")
def mate_planar():
    o = (12, 8.3)
    P = projector(o)
    z, t = 2, 3.4
    return [
        ground(o, 10, 10, z),
        box(o, 1.5, 6.5, 1.5, 6.5, z, t),
        arrow(*P(7.2, 8.2, z), *P(-0.6, 8.2, z), 2.6, 2.4, ACCENT),
        arrow(*P(8.2, 7.2, z), *P(8.2, -0.6, z), 2.6, 2.4, ACCENT),
    ]


@icon("mate-cylindrical", "solid", "Cylindrical mate")
def mate_cylindrical():
    o = (10.3, 17.8)
    P = projector(o)
    ax = P(0, 0, 0)[0] + 6.9
    return [
        cylinder(o, 0, 0, 0, 13, 1.3, SOFT, MID),
        cylinder(o, 0, 0, 4.5, 8.5, 3),
        cylinder(o, 0, 0, 8.5, 13, 1.3, SOFT, MID),
        spin(o, 0, 0, 5.3, 4.4, 165, 30),
        *darrow((ax, P(0, 0, 1.5)[1]), (ax, P(0, 0, 13)[1]), ACCENT, 2.6, 2.4),
    ]


@icon("mate-pin-slot", "solid", "Pin slot mate")
def mate_pin_slot():
    o = (10, 8.5)
    P = projector(o)
    y, r = 3.5, 1.35
    slot = ([(2.5 + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in range(90, 271, 10)]
            + [(10 + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in range(-90, 91, 10)])
    return [
        box(o, 0, 12.5, 0, 7, 0, 2.5, **GROUND),
        poly([P(x, yy, 2.5) for x, yy in slot], SHADE, THIN),
        cylinder(o, 3.2, y, 2.5, 6.5, 1.2),
        arrow(*P(5.4, y, 2.5), *P(11, y, 2.5), 2.6, 2.4, ACCENT),
    ]


@icon("mate-ball", "solid", "Ball mate")
def mate_ball():
    o = (12, 10.9)
    P = projector(o)
    cx, cy = P(4.5, 4.5, 2 + 3.4)
    return [
        ground(o, 9, 9),
        *sphere(cx, cy, 3.6),
        curved_arrow(arc_points(cx, cy, 6.6, 2.6, 30, 165), 2.6, 2.4, ACCENT),
        curved_arrow(arc_points(cx, cy, 5.6, 5.6, 20, -95), 2.6, 2.4, ACCENT),
    ]


@icon("mate-parallel", "solid", "Parallel mate")
def mate_parallel():
    o = (12, 9.4)
    P = projector(o)
    face = lambda x0, x1, y0, y1, z: poly([P(x0, y0, z), P(x1, y0, z), P(x1, y1, z), P(x0, y1, z)], ACCENT,
                                          'stroke="none" fill-opacity="0.25"')
    return [
        ground(o, 10, 10, 1.8),
        face(0, 10, 0, 10, 1.8),
        box(o, 2.5, 7.5, 2.5, 7.5, 5.8, 7.4),
        face(2.5, 7.5, 2.5, 7.5, 7.4),
    ]


@icon("mate-tangent", "solid", "Tangent mate")
def mate_tangent():
    o = (10.1, 9.2)
    P = projector(o)
    r, y, z = 2.8, 3.8, 1.8
    return [
        box(o, 0, 12, 0, 7.6, 0, z, **GROUND),
        line(*P(0.2, y, z), *P(11.8, y, z), acc('stroke-width="1.6"')),
        *xcyl(o, 3, 8.6, y, z + r, r),
    ]


# ---------------------------------------------------------------------------------------------
# Relations


@icon("relations", "solid", "Relations")
def relations():
    o = (8.3, 11.1)
    P = projector(o)
    a, b = (0, 0, 3.9), (10, 0, 2.9)
    z0, z1 = 0, 2.6
    belt = hull(ring(o, a[0], a[1], 1.3, a[2] + 0.1, 0, 360) + ring(o, b[0], b[1], 1.3, b[2] + 0.1, 0, 360))
    return [
        cylinder(o, a[0], a[1], z0, z1, a[2]),
        cylinder(o, b[0], b[1], z0, z1, b[2]),
        poly(belt, None, acc('stroke-width="1.5"')),
        ellipse(*P(a[0], a[1], z1), a[2] * R15, a[2] * R05, TOP),
        ellipse(*P(b[0], b[1], z1), b[2] * R15, b[2] * R05, TOP),
    ]


@icon("gear-relation", "solid", "Gear relation")
def gear_relation():
    o = (9.4, 11.4)
    ra, rb = 5.6, 4.1
    return [
        *flat_gear(o, 0, 0, 0, 1.5, ra, ra - 1.7, 7),
        *flat_gear(o, ra + rb - 1.4, 0, 0, 1.5, rb, rb - 1.7, 5, 0.5),
        spin(o, 0, 0, 1.5, 2.6, 200, 20, ACCENT, 2.4, 2.4),
    ]


@icon("rack-pinion", "solid", "Rack and pinion relation")
def rack_pinion():
    o = (12.2, 6.4)
    P = projector(o)
    r, tooth = 4.3, 1.5
    rack_y, h = 7.6, 1.6
    edge = [(0, rack_y)]
    for x in (1.2, 4.6, 8, 11.4):
        edge += [(x, rack_y), (x + 0.5, rack_y - tooth), (x + 1.6, rack_y - tooth), (x + 2.1, rack_y)]
    edge += [(14, rack_y)]
    top = [P(u, v, h) for u, v in edge] + [P(14, rack_y + 3, h), P(0, rack_y + 3, h)]
    return [
        box(o, 0, 14, rack_y, rack_y + 3, 0, h, **GROUND),
        poly(top, SOFT),
        *flat_gear(o, 5.8, rack_y - r - 0.1, 0, h, r, r - tooth - 0.2, 6, 0.1),
        arrow(*P(9.4, rack_y + 1.5, h), *P(14.6, rack_y + 1.5, h), 2.6, 2.4, ACCENT),
    ]


def _runs(flags, pts2):
    runs, cur, cur_flag = [], [], None
    for flag, p in zip(flags, pts2):
        if flag != cur_flag and cur:
            runs.append((cur_flag, cur + [p]))
            cur = []
        cur_flag = flag
        cur.append(p)
    if cur:
        runs.append((cur_flag, cur))
    return runs


@icon("screw-relation", "solid", "Screw relation")
def screw_relation():
    o = (11, 18.8)
    P = projector(o)
    r_rod, r_h = 1.3, 3.2
    turns, z0, z1 = 1.6, 1.5, 13
    n = 90
    hel = [(r_h * math.cos(2 * math.pi * turns * i / n + 2.4), r_h * math.sin(2 * math.pi * turns * i / n + 2.4),
            z0 + (z1 - z0) * i / n) for i in range(n + 1)]
    runs = _runs([p[0] + p[1] > 0 for p in hel], [P(*p) for p in hel])
    els = [polyline(run, acc()) for front, run in runs if not front]
    els.append(cylinder(o, 0, 0, 0, 14.5, r_rod))
    fronts = [run for front, run in runs if front]
    els += [polyline(run, acc()) for run in fronts[:-1]]
    els.append(curved_arrow(fronts[-1], 2.6, 2.4, ACCENT))
    return els


@icon("linear-relation", "solid", "Linear relation")
def linear_relation():
    o = (10.8, 8.5)
    P = projector(o)
    els = []
    for y0 in (0, 6):
        els += [box(o, 0, 12, y0, y0 + 3, 0, 1.5, **GROUND), box(o, 1.5, 4.5, y0, y0 + 3, 1.5, 4.5),
                arrow(*P(5.3, y0 + 1.5, 1.5), *P(11.7, y0 + 1.5, 1.5), 2.6, 2.4, ACCENT)]
    return els


# ---------------------------------------------------------------------------------------------
# Assembly tools


@icon("group", "solid", "Group")
def group():
    o = (12, 10.2)
    P = projector(o)
    parts = [(0, 4, 0, 4, 0, 4), (5, 9, 0, 4, 0, 2.5), (0, 4, 5, 9, 0, 2.5)]
    corners = [P(x, y, z) for (x0, x1, y0, y1, z0, z1) in parts for x in (x0 - 1, x1 + 1)
               for y in (y0 - 1, y1 + 1) for z in (z0 - 0.8, z1 + 0.8)]
    return [
        poly(hull(corners), None, acc(dash(1.1))),
        box(o, *parts[0]),
        box(o, *parts[1]),
        box(o, *parts[2]),
    ]


@icon("replicate", "solid", "Replicate")
def replicate():
    o = (8.2, 9.6)
    xs = [2.5, 7, 11.5]
    y = 2.6
    copy = acc('fill-opacity="0.3"')
    els = [box(o, 0, 14, 0, 5.2, 0, 2, **GROUND)]
    for x in xs:
        els.append(poly(ring(o, x, y, 2, 1.3, 0, 360, 10), SHADE, THIN))
    els.append(cylinder(o, xs[0], y, 2, 6.5, 1.3))
    for x in xs[1:]:
        els.append(cylinder(o, x, y, 2, 6.5, 1.3, ACCENT, ACCENT, copy))
    return els


@icon("explode", "solid", "Explode")
def explode():
    o = (12, 13.3)
    P = projector(o)
    guide = acc(dash(0.9))
    return [
        box(o, 0, 7, 0, 7, 0, 3),
        box(o, 0, 7, 0, 7, 7.5, 10),
        line(*P(0, 7, 3.9), *P(0, 7, 6.6), guide),
        line(*P(7, 0, 3.9), *P(7, 0, 6.6), guide),
        arrow(*P(7, 7, 3.6), *P(7, 7, 7.2), 2.4, 2.3, ACCENT),
    ]


def mini_assembly(o):
    return [ground(o, 9, 9, 2), box(o, 1.8, 6.2, 1.8, 6.2, 2, 6.8)]


BADGE_O = (10.4, 11.4)


@icon("named-positions", "solid", "Named positions")
def named_positions():
    return [*mini_assembly(BADGE_O), path("M16.9 2.5 H21.3 V9.8 L19.1 8.1 L16.9 9.8 Z", ACCENT, acc())]


@icon("display-states", "solid", "Display states")
def display_states():
    eye = "M15.1 5.8 Q18.3 2 21.5 5.8 Q18.3 9.6 15.1 5.8 Z"
    return [*mini_assembly(BADGE_O), path(eye, TOP, acc()), circle(18.3, 5.8, 1.2, ACCENT, acc())]


@icon("assembly-properties", "solid", "Assembly properties")
def assembly_properties():
    return [
        *mini_assembly(BADGE_O),
        circle(18.6, 5.4, 3.1, ACCENT, acc()),
        line(18.6, 5.2, 18.6, 7, f'stroke="{TOP}" stroke-width="1.3"'),
        circle(18.6, 3.6, 0.75, TOP, 'stroke="none"'),
    ]


@icon("bill-of-materials", "solid", "Bill of materials")
def bill_of_materials():
    els = [rect(4, 2.5, 16, 19, 2, TOP),
           path("M6 2.5 H18 A2 2 0 0 1 20 4.5 V7.5 H4 V4.5 A2 2 0 0 1 6 2.5 Z", SOFT, THIN)]
    for i, yy in enumerate((11, 14.5, 18)):
        els.append(rect(6.5, yy - 1.1, 2.2, 2.2, 0.4, MID, THIN))
        els.append(line(10.5, yy, 17.5, yy, acc('stroke-width="1.4"') if i == 0 else ""))
    return els


# ---------------------------------------------------------------------------------------------
# Document types: an emblem on a square platform.


def platform(o):
    return box(o, 0, 10, 0, 10, 0, PZ, SOFT, MID, SHADE)


PZ = 1.8
DOC_O = (12, 10.2)


@icon("assembly", "solid", "Assembly")
def assembly():
    o = DOC_O
    return [platform(o), *tint_box(o, 1, 5.6, 4.4, 9, PZ, PZ + 4.6), *tint_cyl(o, 6.6, 3.4, PZ, PZ + 7, 2.3)]


@icon("part-studio", "solid", "Part Studio")
def part_studio():
    o = DOC_O
    return [platform(o), *tint_box(o, 1.5, 8.5, 1.5, 8.5, PZ, PZ + 7)]


@icon("material-library", "solid", "Material library")
def material_library():
    o = DOC_O
    cx, cy = projector(o)(5, 5, PZ + 4)
    return [platform(o), *sphere(cx, cy, 4.3, ACCENT, ACCENT),
            ellipse(cx + 1.5, cy - 1.6, 1.3, 0.8, TOP, 'stroke="none" fill-opacity="0.8"', -35)]


@icon("feature-studio", "solid", "Feature Studio")
def feature_studio():
    o = DOC_O
    code = acc('stroke-width="1.8"')
    return [platform(o),
            polyline([(8.8, 5), (5.4, 8.6), (8.8, 12.2)], code),
            polyline([(15.2, 5), (18.6, 8.6), (15.2, 12.2)], code),
            line(13, 4.2, 11, 13, code)]


@icon("cam-studio", "solid", "CAM Studio")
def cam_studio():
    o = DOC_O
    P = projector(o)
    z = PZ + 2.2
    return [
        platform(o),
        box(o, 1, 9, 1, 9, PZ, z),
        polyline([P(6.4, 2.8, z), P(3, 2.8, z)], acc('stroke-width="1.4"')),
        arrow(*P(6.4, 4.6, z), *P(6.4, 9.4, z), 2.6, 2.4, ACCENT),
        cylinder(o, 6.4, 2.8, z, z + 7, 1.7),
    ]


@icon("pcb-studio", "solid", "PCB Studio")
def pcb_studio():
    o = DOC_O
    P = projector(o)
    z = PZ
    trace = acc('stroke-width="1.4"')
    els = [platform(o)]
    for y in (2.4, 5.2):
        els += [line(*P(4.6, y, z), *P(8.6, y, z), trace), circle(*P(8.6, y, z), 0.95, ACCENT, 'stroke="none"')]
    els.append(box(o, 1, 4.6, 1, 6.6, z, z + 1.6))
    return els


@icon("render-studio", "solid", "Render Studio")
def render_studio():
    o = DOC_O
    P = projector(o)
    cx, cy = P(5, 5, PZ + 4)
    sx, sy = 18.7, 5.4
    rays = [line(sx + 2.2 * math.cos(math.radians(a)), sy + 2.2 * math.sin(math.radians(a)),
                 sx + 2.9 * math.cos(math.radians(a)), sy + 2.9 * math.sin(math.radians(a)), acc('stroke-width="1.3"'))
            for a in range(0, 360, 45)]
    return [platform(o), *sphere(cx, cy, 4.3), circle(sx, sy, 1.3, ACCENT, acc()), *rays]
