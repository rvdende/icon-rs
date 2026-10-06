"""Electronics design: the schematic editor and the PCB layout editor of a PCB Studio.

Three kinds, chosen as in the rest of the set:
- "sketch" for the drawing and placement tools (wire, bus, labels, pins, tracks, vias, zones,
  board outline): flat geometry at 1.5 with the points the user picks as ACCENT dots (DOT), as in
  sketch.py. Where the placed object is itself a mark (a junction dot, a no-connect cross, a bus
  entry) that mark is the accent instead.
- "line" for the documents, library objects and commands (schematic, symbol, footprint, rule
  checks, annotate, layers, outputs...): ink at 1.75 plus one accent modifier, as in ui_b.py.
  Plain objects (symbol, footprint) keep the accent on one small detail or none.
- "solid" for board-3d, the 3D board view, drawn like the document types in assembly.py.

Shared vocabulary:
- Schematic wires are thin strokes; a bus is a thick (BUS) stroke.
- PCB tracks are thick (TRACK) round-capped strokes; pads are filled ink in line icons and SOFT
  regions with a TOP drill hole in sketch icons.
- The op-amp triangle stands for a schematic symbol, the zigzag for a resistor.
"""
import math
from common import *

# ---------------------------------------------------------------------------------------------
# Sketch helpers (as in sketch.py; not imported from it, so --only eda renders just this module)

DOT = 1.45
CON = dash(1)
ACC = f'stroke="{ACCENT}"'
FILL = SOFT
REGION = 'fill-opacity="0.45"'
MUTED = 'stroke-opacity="0.5"'
BUS = 3.2  # schematic bus stroke width
TRACK = 2.6  # PCB track stroke width in sketch icons


def _dot(x, y):
    return circle(x, y, DOT, ACCENT, 'stroke="none"')


def _dots(*ps):
    return [_dot(x, y) for x, y in ps]


def _clip_seg(a, b, convex):
    """The part of segment a-b inside the convex polygon, or None."""
    t0, t1 = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    area = sum(p[0] * q[1] - q[0] * p[1] for p, q in zip(convex, convex[1:] + convex[:1]))
    sgn = 1 if area > 0 else -1
    for p, q in zip(convex, convex[1:] + convex[:1]):
        # Inside is to the left of p->q for a positive (clockwise on screen) polygon.
        ex, ey = q[0] - p[0], q[1] - p[1]
        num = sgn * (ex * (a[1] - p[1]) - ey * (a[0] - p[0]))
        den = sgn * (ex * dy - ey * dx)
        if abs(den) < 1e-12:
            if num < 0:
                return None
            continue
        t = -num / den
        if den > 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 >= t1:
            return None
    return (a[0] + t0 * dx, a[1] + t0 * dy), (a[0] + t1 * dx, a[1] + t1 * dy)


def _hatch(convex, step=3.2, extra='stroke-width="1"'):
    """45-degree hatch lines across the convex polygon."""
    out = []
    for k in range(-30, 60):
        c = k * step
        seg = _clip_seg((c - 30, 30), (c + 30, -30), convex)
        if seg and math.hypot(seg[1][0] - seg[0][0], seg[1][1] - seg[0][1]) > 0.8:
            out.append(line(*seg[0], *seg[1], extra))
    return out


# ---------------------------------------------------------------------------------------------
# Line helpers (as in ui_b.py)

R = 2.5


def _acc(els):
    """An element (or a list of them) in ACCENT: the stroke, and the fill where it was INK."""
    if isinstance(els, list):
        return [_acc(e) for e in els]
    return els.replace(f'fill="{INK}"', f'fill="{ACCENT}"').replace("/>", f' stroke="{ACCENT}"/>', 1)


def _plus(cx, cy, arm=2.5):
    return path(f"M{f(cx - arm)} {f(cy)} H{f(cx + arm)} M{f(cx)} {f(cy - arm)} V{f(cy + arm)}")


def _arrow(x0, y0, x1, y1, head=2.5):
    """A straight arrow with an open head, `head` along and 2*head across."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    bx, by = x1 - ux * head, y1 - uy * head
    nx, ny = -uy * head, ux * head
    return [line(x0, y0, x1, y1), polyline([(bx + nx, by + ny), (x1, y1), (bx - nx, by - ny)])]


def _head_at(tip, frm, s=2.5):
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    return polyline([(tip[0] - s * ux + s * nx, tip[1] - s * uy + s * ny), tip,
                     (tip[0] - s * ux - s * nx, tip[1] - s * uy - s * ny)])


def _d(ps, close=False):
    return "M" + " L".join(f"{f(x)} {f(y)}" for x, y in ps) + (" Z" if close else "")


def _opamp(x0, y0, h, pins=2.5):
    """An op-amp triangle, `h` tall with its left side at x0 from y0, and its three pins."""
    w = h * 0.87
    cy = y0 + h / 2
    yi = (y0 + h * 0.27, y0 + h * 0.73)
    return [
        poly([(x0, y0), (x0 + w, cy), (x0, y0 + h)]),
        path(f"M{f(x0 - pins)} {f(yi[0])} H{f(x0)} M{f(x0 - pins)} {f(yi[1])} H{f(x0)} "
             f"M{f(x0 + w)} {f(cy)} H{f(x0 + w + pins)}"),
    ]


def _check(x, y, s=1.0):
    """A check mark with its lowest point at (x, y)."""
    return polyline([(x - 3.5 * s, y - 3.5 * s), (x, y), (x + 7 * s, y - 7 * s)])


def _doc(x0=5, x1=19, y0=3, y1=21, fold=5):
    fx, fy = x1 - fold, y0 + fold
    d = (f"M{f(fx)} {f(y0)} H{f(x0 + R)} A{R} {R} 0 0 0 {f(x0)} {f(y0 + R)} V{f(y1 - R)} "
         f"A{R} {R} 0 0 0 {f(x0 + R)} {f(y1)} H{f(x1 - R)} A{R} {R} 0 0 0 {f(x1)} {f(y1 - R)} V{f(fy)} Z")
    fold_d = f"M{f(fx)} {f(y0)} V{f(fy - 1.5)} A1.5 1.5 0 0 0 {f(fx + 1.5)} {f(fy)} H{f(x1)}"
    return [path(d), path(fold_d)]


def _pad(x, y, w=3.5, h=2.5):
    """A filled SMD pad centred on (x, y) (ink, drawn with the root stroke)."""
    return rect(x - w / 2, y - h / 2, w, h, 0.4, INK, 'stroke-width="1"')


# =============================================================================================
# Schematic


@icon("schematic", "line", "Schematic")
def schematic():
    # A drawing sheet with its title block (lower right) and a resistor drawn on it (accent).
    zig = [(6, 10), (8, 10), (9, 7.5), (11, 12.5), (13, 7.5), (15, 12.5), (16, 10), (18, 10)]
    return [rect(3, 4, 18, 16, R), path("M13 20 V16 H21"), _acc(polyline(zig))]


@icon("symbol", "line", "Symbol")
def symbol():
    # A library symbol: an op-amp with its two inputs and output.
    return [*_opamp(6.5, 4, 16, 3.5), path("M8.5 9.75 H11 M8.5 16.25 H11 M9.75 15 V17.5")]


@icon("add-symbol", "line", "Add symbol")
def add_symbol():
    return [*_opamp(5, 3, 12.5, 2.75), _acc(_plus(18, 18))]


@icon("add-power", "line", "Add power symbol")
def add_power():
    # A ground symbol: a wire into three shrinking bars.
    return [path("M9.5 3.5 V11.5 M3 11.5 H16 M5.75 15.25 H13.25 M8 19 H11"), _acc(_plus(18.5, 5.5))]


@icon("wire", "sketch", "Wire")
def wire():
    a, b, c, d = (3.5, 17.5), (11, 17.5), (11, 6.5), (20.5, 6.5)
    return [polyline([a, b, c, d]), *_dots(a, d)]


@icon("bus", "sketch", "Bus")
def bus():
    a, b, c = (3.5, 7), (17, 7), (17, 20)
    return [polyline([a, b, c], f'stroke-width="{f(BUS)}"'), *_dots(a, c)]


@icon("bus-entry", "sketch", "Bus entry")
def bus_entry():
    # A bus (thick, context) and the 45-degree entry (accent) that joins a wire to it.
    return [
        line(6, 3.5, 6, 20.5, f'stroke-width="{f(BUS)}" {MUTED}'),
        line(12, 12, 20.5, 12),
        line(6, 18, 12, 12, ACC + ' stroke-width="2"'),
    ]


@icon("junction", "sketch", "Junction")
def junction():
    return [line(3.5, 12, 20.5, 12), line(12, 12, 12, 20.5), line(12, 3.5, 12, 12),
            circle(12, 12, 2.6, ACCENT, 'stroke="none"')]


@icon("no-connect", "sketch", "No connection flag")
def no_connect():
    # A pin leaving a symbol's body (left), its free end crossed out (accent).
    c, a = (15.5, 12), 3.25
    return [
        path("M3.5 4.5 H8.5 V19.5 H3.5", FILL, REGION),
        line(8.5, 12, c[0], c[1]),
        path(f"M{f(c[0] - a)} {f(c[1] - a)} L{f(c[0] + a)} {f(c[1] + a)} "
             f"M{f(c[0] + a)} {f(c[1] - a)} L{f(c[0] - a)} {f(c[1] + a)}", None, ACC + ' stroke-width="2"'),
    ]


@icon("pin", "sketch", "Pin")
def pin():
    # A pin on the edge of a symbol's body; its free end is the connection point.
    return [
        path("M20.5 4.5 H13 V19.5 H20.5", FILL, REGION),
        line(4, 12, 13, 12, 'stroke-width="2"'),
        _dot(4, 12),
    ]


@icon("net-label", "sketch", "Net label")
def net_label():
    # A name (an "A") written on a wire, anchored at its lower left.
    return [
        line(3.5, 16.5, 20.5, 16.5),
        polyline([(6.5, 13.5), (10, 4.5), (13.5, 13.5)]),
        line(7.9, 10.4, 12.1, 10.4),
        _dot(6.5, 16.5),
    ]


@icon("global-label", "sketch", "Global label")
def global_label():
    # A wire ending in a pointed tag: the net name, shared across every sheet.
    tag = [(9, 12), (12.5, 7.5), (20.5, 7.5), (20.5, 16.5), (12.5, 16.5)]
    return [line(3.5, 12, 9, 12), poly(tag, FILL, REGION), _dot(9, 12)]


@icon("hierarchical-label", "sketch", "Hierarchical label")
def hierarchical_label():
    # A wire ending in an arrow-shaped port inside a sheet (dashed), leading up to its parent.
    port = [(9, 8.5), (14, 8.5), (17.5, 12), (14, 15.5), (9, 15.5)]
    return [
        rect(1.75, 3.5, 18, 17, 0, None, CON),
        line(4, 12, 9, 12),
        poly(port, FILL, REGION),
        _dot(9, 12),
    ]


@icon("hierarchical-sheet", "sketch", "Hierarchical sheet")
def hierarchical_sheet():
    # A sheet symbol placed by two corners, with sheet pins on its left and right edges.
    x0, y0, x1, y1 = 6, 4, 18, 20
    return [
        rect(x0, y0, x1 - x0, y1 - y0, 0, FILL, REGION),
        path(f"M{f(x0 - 3)} 9 H{f(x0)} M{f(x0 - 3)} 15 H{f(x0)} M{f(x1)} 12 H{f(x1 + 3)}"),
        rect(9, 8, 6, 8, 0, None, 'stroke-width="1"'),
        *_dots((x0, y0), (x1, y1)),
    ]


@icon("annotate", "line", "Annotate")
def annotate():
    # A resistor and its reference designator, R and a number (accent): annotation numbers it.
    return [
        path("M3 17 H6.5 M17.5 17 H21"),
        rect(6.5, 14.25, 11, 5.5, 1),
        path("M6.5 11 V3.5 H9.75 A2.1 2.1 0 0 1 9.75 7.7 H6.5 M9.6 7.7 L12 11"),
        _acc(polyline([(15, 5.25), (17.25, 3.5), (17.25, 11)])),
    ]


@icon("erc", "line", "Electrical rules check")
def erc():
    zig = [(3, 7.5), (5.5, 7.5), (6.75, 4.5), (9.25, 10.5), (11.75, 4.5), (14.25, 10.5), (16.75, 4.5),
           (18, 7.5), (21, 7.5)]
    return [polyline(zig), _acc(_check(10.5, 19.5))]


@icon("assign-footprints", "line", "Assign footprints")
def assign_footprints():
    # A resistor symbol (top) becomes its footprint, two pads (bottom): the arrow (accent).
    zig = [(3, 5.5), (5.5, 5.5), (6.75, 3), (9.25, 8), (11.75, 3), (14.25, 8), (16.75, 3), (18, 5.5), (21, 5.5)]
    return [polyline(zig), *_acc(_arrow(12, 10, 12, 15.5, 2.5)), _pad(6, 18.5, 4, 3.5), _pad(18, 18.5, 4, 3.5)]


@icon("update-pcb", "line", "Update PCB from schematic")
def update_pcb():
    # The board (as in `board`) with the schematic's changes arriving from the left (accent).
    d = (f"M8 9.5 V7.5 A2.5 2.5 0 0 1 10.5 5 H18.5 A2.5 2.5 0 0 1 21 7.5 V16.5 "
         f"A2.5 2.5 0 0 1 18.5 19 H10.5 A2.5 2.5 0 0 1 8 16.5 V14.5")
    return [path(d), circle(17.5, 8.5, 1), circle(17.5, 15.5, 1), *_acc(_arrow(2.5, 12, 14, 12, 3))]


# =============================================================================================
# Layout


@icon("footprint", "line", "Footprint")
def footprint():
    # A footprint: the package outline between two rows of pads, with the pin 1 mark (accent).
    pads = [_pad(x, y) for x in (4.5, 19.5) for y in (6, 12, 18)]
    return [rect(8.5, 3.5, 7, 17, 1.25), *pads, _acc(circle(11.25, 6.25, 0.5, INK))]


@icon("pad", "sketch", "Pad")
def pad():
    # A through-hole pad placed by its centre: copper (region) around a drill hole.
    return [rect(4.5, 4.5, 15, 15, 3.5, FILL, REGION), circle(12, 12, 3.6, TOP), _dot(12, 12)]


@icon("route-track", "sketch", "Route tracks")
def route_track():
    # A track leaving a pad with a 45-degree bend; picked points at the start and the end.
    pad_c, b, c = (5, 18), (10.5, 12.5), (19.5, 12.5)
    return [
        circle(*pad_c, 2.9, FILL),
        polyline([pad_c, b, c], f'stroke-width="{f(TRACK)}"'),
        circle(*pad_c, 1, TOP, 'stroke="none"'),
        *_dots(b, c),
    ]


@icon("via", "sketch", "Via")
def via():
    # A via joins a track on this layer (solid) to one on another (faded); placed by its centre.
    w = f'stroke-width="{f(TRACK)}"'
    return [
        polyline([(3.5, 16.5), (7.5, 16.5), (12, 12)], w),
        polyline([(12, 12), (16.5, 7.5), (20.5, 7.5)], f"{w} {MUTED}"),
        circle(12, 12, 4.2, FILL),
        circle(12, 12, 2, TOP),
        _dot(12, 12),
    ]


_ZONE = [(4, 4.5), (19, 3.5), (20.5, 17.5), (6, 20.5)]


@icon("copper-zone", "sketch", "Copper zone")
def copper_zone():
    # A filled zone drawn by its corners, poured around a pad with a clearance gap.
    return [
        poly(_ZONE, MID, 'fill-opacity="0.7"'),
        circle(13, 12.5, 2.8, TOP, 'stroke="none"'),
        circle(13, 12.5, 1.2, INK, 'stroke="none"'),
        *_dots(*_ZONE),
    ]


@icon("keepout-zone", "sketch", "Keepout zone")
def keepout_zone():
    # A hatched zone drawn by its corners: nothing may be placed or routed inside it.
    return [*_hatch(_ZONE), poly(_ZONE), *_dots(*_ZONE)]


@icon("fill-zones", "line", "Fill zones")
def fill_zones():
    # A zone outline poured with copper (accent), the copper keeping clear of a pad.
    outline = [(3, 4), (21, 4), (21, 20), (3, 20)]
    inset = _d([(6.25, 7.25), (17.75, 7.25), (17.75, 16.75), (6.25, 16.75)], True)
    hole = (f"M8.75 12 A3.25 3.25 0 1 0 15.25 12 A3.25 3.25 0 1 0 8.75 12 Z")
    return [
        path(_d(outline, True), None, 'stroke-dasharray="3 2.6"'),
        path(f"{inset} {hole}", ACCENT, f'fill-rule="evenodd" stroke="none"'),
        circle(12, 12, 1.25, INK, 'stroke="none"'),
    ]


@icon("board-outline", "sketch", "Board outline")
def board_outline():
    # The board's edge drawn as a closed outline (a chamfered corner), with two mounting holes.
    pts = [(3.5, 5), (20.5, 5), (20.5, 14), (15, 19.5), (3.5, 19.5)]
    return [
        poly(pts, FILL, REGION),
        circle(7, 8.5, 1.3, TOP, 'stroke-width="1"'),
        circle(7, 16, 1.3, TOP, 'stroke-width="1"'),
        *_dots(pts[0], pts[2], pts[3]),
    ]


@icon("ratsnest", "line", "Ratsnest")
def ratsnest():
    # Unrouted connections: straight accent lines between the pads of two parts.
    a, b, c, d = (5, 6), (5, 18), (19, 6), (19, 18)
    pads = [rect(x - 2, y - 2, 4, 4, 0.75, INK, 'stroke-width="1"') for x, y in (a, b, c, d)]
    wires = path("M7.5 6.75 L16.5 16.75 M7.5 18 H16.5", None, f'stroke="{ACCENT}" stroke-width="1.25"')
    return [wires, *pads]


@icon("drc", "line", "Design rules check")
def drc():
    # Two tracks side by side (the clearance between them is what the rules check) and a check.
    return [path("M3 4.5 H10 L13 7.5 H21 M3 10 H8 L11 13 H21", None, ""), _acc(_check(10.5, 20))]


@icon("layers", "line", "Layers")
def layers():
    # A stack of board layers; the active one on top (accent).
    return [
        polyline([(3, 12.5), (12, 17), (21, 12.5)]),
        polyline([(3, 16.5), (12, 21), (21, 16.5)]),
        _acc(poly([(12, 3.5), (21, 8), (12, 12.5), (3, 8)])),
    ]


@icon("flip-side", "line", "Flip to other side")
def flip_side():
    # The board edge-on, a part on top, and the arrow round the board's edge that puts it on the
    # bottom (faded).
    ring = arc_points(15.5, 12, 5.5, 5.5, -90, 90, 10)
    return [
        line(3, 12, 15.5, 12, 'stroke-width="2.5"'),
        rect(5, 5.75, 7, 3.5, 0.75),
        rect(5, 14.75, 7, 3.5, 0.75, None, 'stroke-opacity="0.45"'),
        *_acc([polyline(ring), _head_at(ring[-1], ring[-2], 2.25)]),
    ]


@icon("highlight-net", "line", "Highlight net")
def highlight_net():
    # Three nets; the highlighted one (accent) stands out while the others fade.
    faded = 'stroke-opacity="0.4"'
    return [
        path("M3 5 H21", None, faded),
        path("M3 19 H21", None, faded),
        _acc(path("M3 12 H8 L11 9 H21")),
    ]


@icon("select-connected", "line", "Select connected")
def select_connected():
    # A click (the pointer) on a track selects everything connected to it (accent).
    tip = (6, 8.5)
    cursor = [(0, 0), (0, 10.5), (2.7, 7.9), (4.6, 11.4), (6.4, 10.5), (4.5, 7.1), (8.2, 7.1)]
    return [
        _acc(path("M3 5 H13.5 L17.5 9 V20.5")),
        poly([(tip[0] + x, tip[1] + y) for x, y in cursor], None, 'stroke-width="1.5"'),
    ]


@icon("plot-gerbers", "line", "Plot fabrication outputs")
def plot_gerbers():
    # A fabrication file: a document with copper artwork on it, a track between two pads (accent).
    return _doc() + _acc([path("M8.75 15.75 L12.25 12.25 H13.5"), circle(8.25, 17, 1.4), circle(15, 12.25, 1.4)])


@icon("drill-file", "line", "Drill file")
def drill_file():
    # A drill file: a document listing holes (accent rings).
    holes = [circle(x, y, 1.4) for x, y in ((9.25, 12), (14.75, 12), (9.25, 17), (14.75, 17))]
    return _doc() + _acc(holes)


@icon("board-3d", "solid", "3D board view")
def board_3d():
    # A populated board in 3D (a chip and a capacitor on a thin board) and the orbit arrow
    # around it (accent).
    o = (12, 9)
    P = projector(o)
    t = 1.2
    rx, ry = 7.6 * math.sqrt(1.5), 7.6 * math.sqrt(0.5)
    cx, cy = P(5.5, 5.5, 0)
    ring = arc_points(cx, cy + 1.4, rx, ry, 160, 20, 5)
    return [
        box(o, 0, 11, 0, 11, 0, t, SOFT, MID, SHADE),
        box(o, 1.5, 6.5, 4.5, 9.5, t, t + 1.8),
        cylinder(o, 8, 3, t, t + 4.5, 1.7),
        curved_arrow(ring, 2.8, 2.6, ACCENT),
    ]
