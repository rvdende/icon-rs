"""Constraint glyphs and viewport markers (kind "glyph": INK only, stroke 2).

The constraint glyphs are shown at 12-20 px next to sketch geometry and get tinted by the app, so
they share a small symbolic vocabulary:
- entities (lines, curves) are 2-unit strokes;
- points are filled dots of radius DOT (the constrained point a little bigger, BIG);
- the sketch plane is one flat parallelogram (plane()), used by Pierce and Use;
- outside or reference geometry is a row of round dots (DOTS).

The viewport markers come in layered pairs that share their geometry:
- manipulator-arrow-halo (behind, dark translucent) + manipulator-arrow-line (on top, white or
  the hover colour). The arrow points up (the app rotates it) and spans the full height, so the
  node's centre is the arrow's midpoint.
- center-of-mass-disc (behind, white) + center-of-mass-quarters (on top, near black).
"""
import math
from common import *

DOT = 2.5  # radius of an end point
BIG = 3.3  # radius of the point a constraint is about
DOTS = 'stroke-dasharray="0.01 4"'  # round dots along a stroke (round caps make the dots)


AC = f'stroke="{ACCENT}"'  # an accent stroke


def dot(x, y, r=DOT, color=INK):
    return circle(x, y, r, color, 'stroke="none"')


def arc(cx, cy, r, a0, a1, extra=""):
    """An arc path from angle a0 to a1 (degrees, clockwise on screen)."""
    x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
    x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return path(f"M{f(x0)} {f(y0)} A{f(r)} {f(r)} 0 {large} {sweep} {f(x1)} {f(y1)}", None, extra)


def plane(y0, y1, x0=3, x1=21, skew=4.5):
    """The sketch plane: a flat parallelogram seen from slightly above."""
    return poly([(x0, y1), (x1 - skew, y1), (x1, y0), (x0 + skew, y0)])


# ---------------------------------------------------------------------------------------------
# Constraints


@icon("constraint-coincident", "glyph", "Coincident")
def constraint_coincident():
    # Two entities through one shared point.
    return [line(4, 19, 20, 5), line(4, 5, 20, 19), dot(12, 12, BIG + 0.3, ACCENT)]


@icon("constraint-concentric", "glyph", "Concentric")
def constraint_concentric():
    return [circle(12, 12, 9), circle(12, 12, 4.3, None, AC)]


@icon("constraint-parallel", "glyph", "Parallel")
def constraint_parallel():
    return [line(4.5, 19.5, 11, 4.5), line(13, 19.5, 19.5, 4.5, AC)]


@icon("constraint-tangent", "glyph", "Tangent")
def constraint_tangent():
    r = 6.2
    top = 7.5
    return [circle(12, top + r, r), line(3, top, 21, top), dot(12, top, 2.9, ACCENT)]


@icon("constraint-horizontal", "glyph", "Horizontal")
def constraint_horizontal():
    return [line(5, 12, 19, 12), dot(4.5, 12, DOT, ACCENT), dot(19.5, 12, DOT, ACCENT)]


@icon("constraint-vertical", "glyph", "Vertical")
def constraint_vertical():
    return [line(12, 5, 12, 19), dot(12, 4.5, DOT, ACCENT), dot(12, 19.5, DOT, ACCENT)]


@icon("constraint-perpendicular", "glyph", "Perpendicular")
def constraint_perpendicular():
    # The right-angle mark goes underneath, so the ink lines stay whole.
    return [polyline([(9, 13.5), (15, 13.5), (15, 19.5)], AC), line(3.5, 19.5, 20.5, 19.5), line(9, 4, 9, 19.5)]


@icon("constraint-equal", "glyph", "Equal")
def constraint_equal():
    w = 'stroke-width="2.4"'
    return [line(5, 8.5, 19, 8.5, w), line(5, 15.5, 19, 15.5, w + " " + AC)]


@icon("constraint-midpoint", "glyph", "Midpoint")
def constraint_midpoint():
    # A segment between end ticks, its centre marked.
    return [line(3, 12, 21, 12), line(3, 7.5, 3, 16.5), line(21, 7.5, 21, 16.5), dot(12, 12, BIG, ACCENT)]


@icon("constraint-normal", "glyph", "Normal")
def constraint_normal():
    # A line leaving a curve at a right angle.
    return [line(12, 3.5, 12, 17, AC), arc(12, 31, 14, 222, 318)]


@icon("constraint-pierce", "glyph", "Pierce")
def constraint_pierce():
    # A curve passing through the sketch plane; the pierce point marked.
    return [plane(10, 20), line(12, 2.5, 12, 10), line(12, 20, 12, 22), dot(12, 15, 2.8, ACCENT)]


@icon("constraint-symmetric", "glyph", "Symmetric")
def constraint_symmetric():
    # Two mirrored shapes about a dotted axis.
    return [line(12, 3, 12, 21, DOTS + " " + AC),
            poly([(8.5, 6.5), (8.5, 17.5), (3, 12)], INK),
            poly([(15.5, 6.5), (15.5, 17.5), (21, 12)], INK)]


@icon("constraint-fix", "glyph", "Fix")
def constraint_fix():
    # A fixed support, as in a structural diagram: a wedge on hatched ground.
    return [poly([(12, 4), (17.5, 13), (6.5, 13)], ACCENT, AC), line(3.5, 16.5, 20.5, 16.5),
            *[line(x, 16.5, x - 3.5, 21) for x in (8.5, 14.5, 20.5)]]


@icon("constraint-curvature", "glyph", "Curvature")
def constraint_curvature():
    # Two curves meeting at a point with matching curvature (a smooth S through the join).
    s = sample_cubic((3, 19), (9, 19), (8.5, 12), (12, 12), 16)[:-1] + \
        sample_cubic((12, 12), (15.5, 12), (15, 5), (21, 5), 16)
    return [polyline(s), dot(12, 12, BIG, ACCENT)]


@icon("constraint-offset", "glyph", "Offset")
def constraint_offset():
    # Two curves a constant distance apart.
    return [arc(20, 20, 16.5, 180, 270), arc(20, 20, 8.5, 180, 270, AC)]


@icon("constraint-use", "glyph", "Use (projected geometry)")
def constraint_use():
    # An outside edge brought down onto the sketch plane.
    return [line(7, 3.5, 17, 3.5), arrow(12, 7, 12, 12.5, 4.5, 6, ACCENT), plane(14, 20.5)]


# ---------------------------------------------------------------------------------------------
# Viewport markers

# The manipulator arrow's geometry, shared by both layers: tip up at (12, TIP), a filled head
# HEAD long and W wide, a shaft down to BASE. The halo is the same geometry stroked HALO wider on
# each side, so it rings the line layer exactly.
ARROW_TIP, ARROW_HEAD, ARROW_W, ARROW_BASE = 3.6, 8, 9, 19.8
ARROW_SHAFT = 2.4
HALO = 1.4


def _arrow(grow):
    hb = ARROW_TIP + ARROW_HEAD
    head = poly([(12, ARROW_TIP), (12 + ARROW_W / 2, hb), (12 - ARROW_W / 2, hb)], INK,
                f'stroke-width="{f(0.8 + 2 * grow)}"')
    shaft = line(12, hb - 1, 12, ARROW_BASE, f'stroke-width="{f(ARROW_SHAFT + 2 * grow)}"')
    return [shaft, head]


@icon("manipulator-arrow-line", "glyph", "Manipulator arrow")
def manipulator_arrow_line():
    return _arrow(0)


@icon("manipulator-arrow-halo", "glyph", "Manipulator arrow halo")
def manipulator_arrow_halo():
    return _arrow(HALO)


COM_R = 9.5  # the ring's centreline; its outer edge is at 10.5


@icon("center-of-mass-disc", "glyph", "Center of mass disc")
def center_of_mass_disc():
    # Ends inside the ring's outer edge so no light fringe shows around the symbol.
    return [circle(12, 12, COM_R + 0.5, INK, 'stroke="none"')]


@icon("center-of-mass-quarters", "glyph", "Center of mass quarters")
def center_of_mass_quarters():
    r = COM_R
    return [
        path(f"M12 12 V{f(12 - r)} A{f(r)} {f(r)} 0 0 1 {f(12 + r)} 12 Z", INK, 'stroke="none"'),
        path(f"M12 12 V{f(12 + r)} A{f(r)} {f(r)} 0 0 1 {f(12 - r)} 12 Z", INK, 'stroke="none"'),
        circle(12, 12, r),
    ]


@icon("origin", "glyph", "Origin")
def origin():
    # A ring on crossed axis ticks, the origin point filled.
    return [circle(12, 12, 6), dot(12, 12, 2.6, ACCENT),
            line(12, 2, 12, 5), line(12, 19, 12, 22), line(2, 12, 5, 12), line(19, 12, 22, 12)]


@icon("instance-dof", "glyph", "Under-constrained instance")
def instance_dof():
    # A small three-axis triad: the degrees of freedom an instance still has. The origin is
    # filled; X runs right, Y up and Z out toward the viewer (down and to the left).
    o = (10, 14)
    return [arrow(*o, 21, 14, 4.2, 4.2), arrow(*o, 10, 3, 4.2, 4.2), arrow(*o, 3.6, 20.4, 4.2, 4.2),
            dot(*o, BIG, ACCENT)]


@icon("mate-limits", "glyph", "Mate limits")
def mate_limits():
    # A range with stops: two short bars and a double arrow between them.
    return [line(6.5, 3, 17.5, 3), line(6.5, 21, 17.5, 21),
            arrow(12, 12, 12, 6.8, 3.6, 5, ACCENT), arrow(12, 12, 12, 17.2, 3.6, 5, ACCENT)]


@icon("origin-fastened", "glyph", "Fastened to origin")
def origin_fastened():
    # The origin (a ring round a filled point) standing on hatched ground: an assembly fixed in
    # place at the origin. The ground matches constraint-fix; the ring sets it apart.
    return [circle(12, 7.5, 5), dot(12, 7.5, 2.2, ACCENT), line(12, 12.5, 12, 16.5),
            line(3.5, 16.5, 20.5, 16.5), *[line(x, 16.5, x - 3.5, 21) for x in (8.5, 14.5, 20.5)]]
