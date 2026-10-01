"""Sheet metal features (kind "solid") and the sheet metal panels (kind "line").

House style for this module: sheets are drawn as a thin profile in the xz plane extruded along y
(`_sheet`): flat walls, round bends, a visible end cap on the near (y max) side. Grey faces are
context; ACCENT marks what the tool makes or acts on (the bend, the new wall, the hem, the relief
cut), one idea per icon, as in part.py.
"""
import math
from common import *

T = 1.3  # sheet thickness
RB = 1.6  # inner bend radius
W = 7.5  # sheet depth along y
HAIR = 'stroke-width="0.7"'


def _arc(cx, cz, r, a0, a1, n=8):
    """Points on a circle in the xz plane from angle a0 to a1 (degrees, counter-clockwise)."""
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def _face_fill(nx, nz):
    """Palette grey for a face whose outward normal in the xz plane is (nx, nz)."""
    if nz > 0.75:
        return TOP
    if nx > 0.75:
        return MID
    return SOFT


def _sheet(o, prof, w=W, accent=(), y0=0.0, cap=SHADE):
    """A sheet: the closed counter-clockwise profile `prof` [(x, z)] extruded from y0 to y0 + w.
    Edges listed in `accent` (indices into the profile) are filled with ACCENT. Returns the
    elements back to front: the faces you can see from the camera, then the near end cap."""
    P = projector(o)
    y1 = y0 + w
    n = len(prof)
    quads = []
    for i in range(n):
        (x0, z0), (x1, z1) = prof[i], prof[(i + 1) % n]
        dx, dz = x1 - x0, z1 - z0
        L = math.hypot(dx, dz)
        if L < 1e-9:
            continue
        nx, nz = dz / L, -dx / L  # outward for a counter-clockwise profile (x right, z up)
        if nx + nz <= 1e-6:
            continue  # faces away from the camera
        fill = ACCENT if i in accent else _face_fill(nx, nz)
        depth = (x0 + x1) / 2 + (z0 + z1) / 2
        quads.append((depth, poly([P(x0, y0, z0), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z0)], fill, HAIR)))
    quads.sort(key=lambda q: q[0])
    capfill = [poly([P(x, y1, z) for x, z in prof], cap)]
    return [q for _, q in quads] + capfill


def _l_profile(L=10.0, H=9.0, t=T, r=RB):
    """A base along x with a wall bent up at x = L: the closed outline, counter-clockwise, and the
    indices of the bend's edges (inner and outer arcs)."""
    prof = [(0, 0)] + _arc(L - t - r, t + r, r + t, 270, 360) + [(L, H), (L - t, H)] + _arc(L - t - r, t + r, r, 360, 270) + [(0, t)]
    # Edges: 0 base bottom, 1-8 outer arc, 9 outer wall, 10 top, 11 inner wall, 12-19 inner arc.
    bend = set(range(1, 9)) | set(range(12, 20))
    return prof, bend


@icon("sheet-metal-model", "solid", "Sheet metal model")
def sheet_metal_model():
    # A sheet bent up into an L; the bend is what makes it sheet metal (its end section in accent:
    # the bend's own faces turn away from the camera).
    o = (9.2, 9.8)
    prof, bend = _l_profile()
    P = projector(o)
    section = prof[1:10] + prof[12:21]  # outer arc, then inner arc back
    return _sheet(o, prof, accent=bend) + [poly([P(x, W, z) for x, z in section], ACCENT, HAIR)]


@icon("sheet-metal-finish", "solid", "Finish sheet metal model")
def sheet_metal_finish():
    # The finished L, with a check mark: no more sheet metal features.
    prof, _ = _l_profile(L=9, H=8)
    return _sheet((9.2, 11.5), prof) + [polyline([(4.2, 6.2), (6.4, 8.4), (10.6, 3.8)], f'stroke="{ACCENT}" stroke-width="1.8"')]


@icon("sheet-metal-flange", "solid", "Flange")
def sheet_metal_flange():
    # Context: the base. Output: the new wall and its bend (accent).
    prof, bend = _l_profile()
    wall = bend | {9, 10, 11}
    return _sheet((9.2, 9.8), prof, accent=wall)


@icon("sheet-metal-hem", "solid", "Hem")
def sheet_metal_hem():
    # The base's edge folded back over itself (accent).
    L, t, r, h = 11.0, T, 0.9, 5.0
    cx, cz = L - r - t, t + r
    prof = ([(0, 0), (cx, 0)] + _arc(cx, cz, r + t, 270, 450)[1:] + [(L - r - t - h, t + 2 * r + t), (L - r - t - h, 2 * r + t)]
            + _arc(cx, cz, r, 90, -90)[0:] + [(0, t)])
    hem = set(range(1, len(prof) - 2))  # all but the base's bottom, top and end
    return _sheet((8.6, 11.2), prof, accent=hem)


@icon("sheet-metal-tab", "solid", "Tab")
def sheet_metal_tab():
    # A wall with a tongue added on its top edge (accent).
    prof, _ = _l_profile(L=10, H=7.5)
    o = (9.2, 10.6)
    return _sheet(o, prof) + [box(o, 10 - T, 10, W * 0.3, W * 0.7, 7.5, 10.5, ACCENT, ACCENT, ACCENT, HAIR)]


@icon("sheet-metal-bend", "solid", "Bend")
def sheet_metal_bend():
    # A flat sheet folded along a bend line (accent dashes) on its top face.
    a = math.radians(50)
    L1, L2, t, r = 7.0, 7.0, T, RB
    c = (L1, t + r)  # bend centre
    p_in = _arc(c[0], c[1], r, 270, 270 + 50)
    p_out = _arc(c[0], c[1], r + t, 270, 270 + 50)
    ex, ez = math.cos(a), math.sin(a)
    tip_in = (p_in[-1][0] + L2 * ex, p_in[-1][1] + L2 * ez)
    tip_out = (p_out[-1][0] + L2 * ex, p_out[-1][1] + L2 * ez)
    prof = [(0, 0)] + p_out + [tip_out, tip_in] + p_in[::-1] + [(0, t)]
    o = (6.5, 13.5)
    P = projector(o)
    return _sheet(o, prof) + [line(*P(L1 - 2.2, 0, t), *P(L1 - 2.2, W, t), f'stroke="{ACCENT}" ' + dash(1.2))]


@icon("sheet-metal-jog", "solid", "Jog")
def sheet_metal_jog():
    # A Z-shaped step: two opposite bends offset the sheet (accent).
    t, r, L, d = T, 1.0, 5.0, 3.5
    c1 = (L, t + r)
    c2 = (L + r + t + r, t + d - r)
    prof = ([(0, 0)] + _arc(c1[0], c1[1], r + t, 270, 360) + _arc(c2[0], c2[1], r, 180, 90) + [(c2[0] + L, t + d), (c2[0] + L, 2 * t + d)]
            + _arc(c2[0], c2[1], r + t, 90, 180) + _arc(c1[0], c1[1], r, 360, 270) + [(0, t)])
    k = len(_arc(0, 0, 1, 0, 1))  # points per arc
    # Edges 1..2k-1: lower bend, riser, upper bend (outside); 2k+3..4k+1: the same inside.
    step = set(range(1, 2 * k)) | set(range(2 * k + 3, 4 * k + 2))
    return _sheet((7.5, 13.0), prof, accent=step)


@icon("sheet-metal-form", "solid", "Form")
def sheet_metal_form():
    # A flat sheet with a louver pressed into it (accent).
    o = (12.3, 9.6)
    P = projector(o)
    plate = box(o, 0, 11, 0, 9, 0, T)
    x0, x1, y0, y1, h = 3, 8, 3.2, 5.8, 1.9
    hood = [P(x0, y1, T), P(x0, y0, T + h), P(x1, y0, T + h), P(x1, y1, T)]
    side = [P(x1, y1, T), P(x1, y0, T + h), P(x1, y0, T)]
    return [plate, poly([P(x0, y0, T), P(x1, y0, T), P(x1, y0, T + h), P(x0, y0, T + h)], SHADE, HAIR), poly(hood, ACCENT, HAIR), poly(side, ACCENT, HAIR)]


@icon("sheet-metal-loft", "solid", "Sheet metal loft")
def sheet_metal_loft():
    # A duct from a square (bottom) to a circle (top): the lofted sheet, its top rim in accent.
    o = (12, 17.5)
    P = projector(o)
    s, r, h = 4.6, 3.0, 9
    sq = [P(-s, -s, 0), P(s, -s, 0), P(s, s, 0), P(-s, s, 0)]
    top = iso_circle(o, 0, 0, h, r)
    rx, ry = r * math.sqrt(1.5), r * math.sqrt(0.5)
    tx, ty = P(0, 0, h)
    left, right, front = (tx - rx, ty), (tx + rx, ty), (tx, ty + ry)
    return [
        poly([sq[2], sq[1], right, front], MID, HAIR),
        poly([sq[3], sq[2], front, left], SHADE, HAIR),
        poly(top, TOP, HAIR),
        poly(top, None, f'stroke="{ACCENT}" stroke-width="1.4"'),
    ]


@icon("sheet-metal-make-joint", "solid", "Make joint")
def sheet_metal_make_joint():
    # Two walls meeting at a corner; the seam between them is the joint (accent).
    o = (12, 13.2)
    H = 8.5
    return [
        box(o, 0, T, -6, 0, 0, H),
        box(o, 0.8, 7.2, 0, T, 0, H),
        line(*projector(o)(T + 0.4, T, 0), *projector(o)(T + 0.4, T, H), f'stroke="{ACCENT}" stroke-width="1.6"'),
    ]


@icon("sheet-metal-modify-joint", "solid", "Modify joint")
def sheet_metal_modify_joint():
    # The L with its bend dashed (accent): the joint being changed.
    prof, bend = _l_profile()
    o = (9.2, 9.8)
    P = projector(o)
    els = _sheet(o, prof)
    outer = [P(x, W, z) for x, z in prof[1:10]]
    return els + [polyline(outer, f'stroke="{ACCENT}" ' + dash(1.4))]


def _tray(o, flange=7.0, base=10.0, t=T):
    """A base plate with walls up along its x max and y max edges, meeting at a corner (x max, y
    max): the corner the corner tools act on."""
    return [
        box(o, 0, base, 0, base, 0, t),
        box(o, base - t, base, 0, base - t - 0.6, t, flange),
        box(o, 0, base - t - 0.6, base - t, base, t, flange),
    ]


@icon("sheet-metal-corner", "solid", "Corner")
def sheet_metal_corner():
    # Two walls meeting at a corner of the base; the round relief cut there (accent).
    o = (12, 9.2)
    P = projector(o)
    base = 10.0
    c = iso_circle(o, base - T - 0.3, base - T - 0.3, T, 1.8)
    return _tray(o, base=base) + [poly(c, ACCENT, HAIR)]


@icon("sheet-metal-bend-relief", "solid", "Bend relief")
def sheet_metal_bend_relief():
    # A wall covering part of the base's edge; the slot cut where its bend ends (accent).
    o = (11, 9.5)
    P = projector(o)
    L, D = 10.0, 10.0
    y0, y1 = 3.2, D
    slot = [P(L - T - 2.6, y0 - 1.0, T), P(L, y0 - 1.0, T), P(L, y0, T), P(L - T - 2.6, y0, T)]
    return [
        box(o, 0, L, 0, D, 0, T),
        box(o, L - T, L, y0, y1, T, 8),
        poly(slot, ACCENT, HAIR),
    ]


@icon("sheet-metal-corner-break", "solid", "Corner break")
def sheet_metal_corner_break():
    # A plate whose near corner is rounded off (accent: the rounded edge).
    o = (12.5, 8.8)
    P = projector(o)
    s, r, t = 10.0, 3.6, T
    arc = [(s - r + r * math.cos(math.radians(a)), s - r + r * math.sin(math.radians(a))) for a in range(0, 91, 10)]
    top = [P(0, 0, t), P(s, 0, t)] + [P(x, y, t) for x, y in arc] + [P(0, s, t)]
    right = [P(s, 0, t), P(s, 0, 0), P(s, s - r, 0), P(s, s - r, t)]
    left = [P(0, s, t), P(s - r, s, t), P(s - r, s, 0), P(0, s, 0)]
    band = [P(x, y, t) for x, y in arc] + [P(x, y, 0) for x, y in arc[::-1]]
    return [poly(right, MID, HAIR), poly(left, SHADE, HAIR), poly(band, ACCENT, HAIR), poly(top, TOP, HAIR)]


# ---------------------------------------------------------------------------------------------
# Panels (kind "line")


def _lacc(el):
    return el.replace("/>", f' stroke="{ACCENT}"/>', 1)


@icon("sheet-metal-table", "line", "Sheet metal table and flat view")
def sheet_metal_table():
    # A table (top) over a flat pattern with its bend line (accent dashes).
    return [
        rect(3, 3, 18, 7.5, 1.5),
        path("M3 6.75 H21 M9 3 V10.5"),
        rect(3, 13.5, 18, 7.5, 1.5),
        _lacc(line(12, 13.5, 12, 21, dash(1.75))),
    ]


@icon("flat-pattern", "line", "Flat pattern")
def flat_pattern():
    # An unfolded box: a cross-shaped outline with its bend lines dashed (accent).
    cross = path("M8 3 H16 V8 H21 V16 H16 V21 H8 V16 H3 V8 H8 Z")
    bends = path("M8 8 H16 M8 16 H16 M8 8 V16 M16 8 V16", None, f'stroke="{ACCENT}" ' + dash(1.5))
    return [cross, bends]
