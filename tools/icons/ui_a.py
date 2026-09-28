"""Interface navigation, action and status icons (kind "line").

All strokes use the root width (1.75) so the app can raise the weight by rewriting it. Filled
shapes with knocked-out marks use stroke="none" and are drawn 0.875 larger than their outline
counterparts, so the knock-outs never close up when the root stroke gets heavier.
"""
import math
from common import *

HEAD = 5  # open arrowhead: each leg runs 5 back along the shaft and 5 out to the side
R_OUT = 9.875  # a filled circle as large as a stroked r 9 circle


# ---------------------------------------------------------------------------------------------
# Private helpers


def _head(tip, frm, s=HEAD):
    """An open 45-degree arrowhead at `tip`, pointing away from `frm`."""
    dx, dy = tip[0] - frm[0], tip[1] - frm[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    a = (tip[0] - s * ux + s * nx, tip[1] - s * uy + s * ny)
    b = (tip[0] - s * ux - s * nx, tip[1] - s * uy - s * ny)
    return polyline([a, tip, b])


def _arrow(x0, y0, x1, y1, s=HEAD):
    return [line(x0, y0, x1, y1), _head((x1, y1), (x0, y0), s)]


def _acc(el):
    """The element (or list of elements) in ACCENT: stroke, and fill where it was INK."""
    if isinstance(el, (list, tuple)):
        return [_acc(e) for e in el]
    el = el.replace(f'fill="{INK}"', f'fill="{ACCENT}"')
    return el[:-2] + f' stroke="{ACCENT}"/>'


def _d(ps, close=True):
    d = "M" + " L".join(f"{f(x)} {f(y)}" for x, y in ps)
    return d + (" Z" if close else "")


def _circle_d(cx, cy, r):
    return (f"M{f(cx - r)} {f(cy)} A{f(r)} {f(r)} 0 1 0 {f(cx + r)} {f(cy)} "
            f"A{f(r)} {f(r)} 0 1 0 {f(cx - r)} {f(cy)} Z")


def _stroke_outline(ps, w):
    """The outline of polyline `ps` stroked at width w with round caps, as a closed point list."""
    h = w / 2
    left, right = offset_polyline(ps, h), offset_polyline(ps, -h)

    def cap(p, q):  # a semicircle at p, bulging away from q
        a = math.atan2(p[1] - q[1], p[0] - q[0])
        return [(p[0] + h * math.cos(a + math.radians(t)), p[1] + h * math.sin(a + math.radians(t)))
                for t in range(90, -91, -15)]

    c_end = cap(ps[-1], ps[-2])
    c_start = cap(ps[0], ps[1])
    return left + c_end[1:-1] + right[::-1] + c_start[1:-1]


def _stem(x, y0, y1, w=1.9):
    return _stroke_outline([(x, y0), (x, y1)], w)


def _rounded(ps, r, n=6):
    """Convex polygon `ps` with every corner rounded to radius r."""
    out = []
    k = len(ps)
    for i in range(k):
        p0, p1, p2 = ps[i - 1], ps[i], ps[(i + 1) % k]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        u1, u2 = (v1[0] / l1, v1[1] / l1), (v2[0] / l2, v2[1] / l2)
        ang = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        t = r / math.tan(ang / 2)
        a = (p1[0] + u1[0] * t, p1[1] + u1[1] * t)
        b = (p1[0] + u2[0] * t, p1[1] + u2[1] * t)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        bl = math.hypot(*bis)
        dc = r / math.sin(ang / 2)
        c = (p1[0] + bis[0] / bl * dc, p1[1] + bis[1] / bl * dc)
        a0 = math.atan2(a[1] - c[1], a[0] - c[0])
        a1 = math.atan2(b[1] - c[1], b[0] - c[0])
        while a1 - a0 > math.pi:
            a1 -= 2 * math.pi
        while a0 - a1 > math.pi:
            a1 += 2 * math.pi
        out += [(c[0] + r * math.cos(a0 + (a1 - a0) * j / n), c[1] + r * math.sin(a0 + (a1 - a0) * j / n))
                for j in range(n + 1)]
    return out


def _knockout(outer_d, holes):
    """One solid shape with holes (point lists or path strings), no stroke."""
    parts = [outer_d] + [h if isinstance(h, str) else _d(h) for h in holes]
    return path(" ".join(parts), INK, 'fill-rule="evenodd" stroke="none"')


def _gapped(ps, a, b, gap, closed=False):
    """Polylines for `ps` with the points within `gap` of segment a-b removed."""
    def dist(p):
        dx, dy = b[0] - a[0], b[1] - a[1]
        t = max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
        return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

    runs, cur = [], []
    for p in ps:
        if dist(p) > gap:
            cur.append(p)
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        if closed and runs and dist(ps[0]) > gap:
            runs[0] = cur + runs[0]
        else:
            runs.append(cur)
    return [polyline(r) for r in runs if len(r) > 1]


def _eye_pts(n=32):
    top = sample_cubic((2.75, 12), (6, 5.75), (18, 5.75), (21.25, 12), n)
    bot = sample_cubic((21.25, 12), (18, 18.25), (6, 18.25), (2.75, 12), n)
    return top + bot[1:]


def _question_pts():
    # The hook of the "?" from its upper-left end to the bottom of the stem.
    return (arc_points(12, 9.5, 2.75, 2.75, 180, 395, 5)
            + sample_cubic((14.1, 11.3), (12.6, 12.1), (12, 12.6), (12, 13.9), 8)[1:])


def _trash_body(lid_accent=False):
    lid = [
        line(4, 7, 20, 7),
        path("M9 7 V5 A1.25 1.25 0 0 1 10.25 3.75 H13.75 A1.25 1.25 0 0 1 15 5 V7"),
    ]
    body = path("M6 7 L6.85 18.2 A2 2 0 0 0 8.85 20.25 H15.15 A2 2 0 0 0 17.15 18.2 L18 7")
    return [body] + (_acc(lid) if lid_accent else lid)


# ---------------------------------------------------------------------------------------------
# History


@icon("undo", "line", "Undo")
def undo():
    return [
        path("M4 9.5 H15 A4.75 4.75 0 0 1 15 19 H11"),
        _acc(_head((4, 9.5), (10, 9.5), 4.5)),
    ]


@icon("redo", "line", "Redo")
def redo():
    return [
        path("M20 9.5 H9 A4.75 4.75 0 0 0 9 19 H13"),
        _acc(_head((20, 9.5), (14, 9.5), 4.5)),
    ]


# ---------------------------------------------------------------------------------------------
# Chevrons and carets


@icon("chevron-down", "line", "Chevron down")
def chevron_down():
    return polyline([(8, 10), (12, 14), (16, 10)])


@icon("chevron-up", "line", "Chevron up")
def chevron_up():
    return polyline([(8, 14), (12, 10), (16, 14)])


@icon("chevron-left", "line", "Chevron left")
def chevron_left():
    return polyline([(14, 8), (10, 12), (14, 16)])


@icon("chevron-right", "line", "Chevron right")
def chevron_right():
    return polyline([(10, 8), (14, 12), (10, 16)])


# Carets: a triangle 8 wide and 4.5 deep (pointing down around the origin), centred on 12,12.
CARET = [(-4, -2), (4, -2), (0, 2.5)]


def _caret(rot, fill=None):
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    return poly([(12 + x * c - y * s, 12 + x * s + y * c) for x, y in CARET], fill)


@icon("caret-down", "line", "Caret down")
def caret_down():
    return _caret(0)


@icon("caret-right", "line", "Caret right")
def caret_right():
    return _caret(-90)


@icon("caret-up-filled", "line", "Caret up (filled)")
def caret_up_filled():
    return _caret(180, INK)


@icon("caret-down-filled", "line", "Caret down (filled)")
def caret_down_filled():
    return _caret(0, INK)


@icon("caret-left-filled", "line", "Caret left (filled)")
def caret_left_filled():
    return _caret(90, INK)


@icon("caret-right-filled", "line", "Caret right (filled)")
def caret_right_filled():
    return _caret(-90, INK)


# ---------------------------------------------------------------------------------------------
# Actions


@icon("close", "line", "Close")
def close():
    return [line(6, 6, 18, 18), line(18, 6, 6, 18)]


@icon("check", "line", "Check")
def check():
    return polyline([(4.5, 12.5), (9.5, 17.5), (19.5, 6.5)])


@icon("plus", "line", "Add")
def plus():
    return [line(12, 5, 12, 19), line(5, 12, 19, 12)]


@icon("delete", "line", "Delete")
def delete():
    return _trash_body(True) + [line(10, 11, 10, 16.25), line(14, 11, 14, 16.25)]


@icon("remove-circle", "line", "Remove")
def remove_circle():
    return [circle(12, 12, 9), *_acc([line(9, 9, 15, 15), line(15, 9, 9, 15)])]


@icon("search", "line", "Search")
def search():
    return [circle(10.5, 10.5, 6.5), _acc(line(15.25, 15.25, 20, 20))]


@icon("filter", "line", "Filter")
def filter_():
    return [path("M10 11.75 L4 4.5 H20 L14 11.75"), _acc(path("M10 11.75 V20 L14 18 V11.75"))]


@icon("sort-descending", "line", "Sort descending")
def sort_descending():
    return [
        line(4, 6, 12, 6), line(4, 12, 10, 12), line(4, 18, 8, 18),
        *_acc(_arrow(17, 5, 17, 19, 3.5)),
    ]


@icon("reorder", "line", "Reorder")
def reorder():
    # Up and down arrows side by side: toggles reordering a list. A control, so ink only.
    return [*_arrow(8.5, 19, 8.5, 5, 3.5), *_arrow(15.5, 5, 15.5, 19, 3.5)]


@icon("drag-handle", "line", "Drag handle")
def drag_handle():
    # Two columns of three dots: grab here to drag. Filled dots, so they stay solid at 12 px.
    return [circle(x, y, 1.6, INK, 'stroke="none"') for x in (9, 15) for y in (6, 12, 18)]


@icon("arrow-up", "line", "Arrow up")
def arrow_up():
    return _arrow(12, 19, 12, 5)


@icon("arrow-down", "line", "Arrow down")
def arrow_down():
    return _arrow(12, 5, 12, 19)


@icon("arrow-up-right", "line", "Arrow up-right")
def arrow_up_right():
    return _arrow(6.5, 17.5, 17, 7, HEAD * math.sqrt(0.5))


@icon("arrow-down-right", "line", "Arrow down-right")
def arrow_down_right():
    return _arrow(6.5, 6.5, 17, 17, HEAD * math.sqrt(0.5))


@icon("menu", "line", "Menu")
def menu():
    return [line(4, 6, 20, 6), line(4, 12, 20, 12), line(4, 18, 20, 18)]


@icon("open-external", "line", "Open")
def open_external():
    return [
        path("M10.5 4 H6.5 A2.5 2.5 0 0 0 4 6.5 V17.5 A2.5 2.5 0 0 0 6.5 20 H17.5 A2.5 2.5 0 0 0 20 17.5 V13.5"),
        *_acc(_arrow(11, 13, 20, 4, HEAD * math.sqrt(0.5) + 0.5)),
    ]


@icon("link", "line", "Link")
def link():
    # Two open U-shaped links on the diagonal, joined by a short bar.
    def half(cx, cy, s):
        r, leg = 3.6, 3.2
        ux, uy = s * math.sqrt(0.5), -s * math.sqrt(0.5)  # outward along the diagonal
        nx, ny = -uy, ux
        arc = [(cx + r * (math.cos(t) * ux + math.sin(t) * nx), cy + r * (math.cos(t) * uy + math.sin(t) * ny))
               for t in [math.radians(a) for a in range(-90, 91, 6)]]
        a0 = (arc[0][0] - leg * ux, arc[0][1] - leg * uy)
        a1 = (arc[-1][0] - leg * ux, arc[-1][1] - leg * uy)
        return polyline([a0] + arc + [a1])

    return [_acc(half(15.75, 8.25, 1)), half(8.25, 15.75, -1), line(9.75, 14.25, 14.25, 9.75)]


@icon("copy", "line", "Copy")
def copy():
    return [
        rect(8.5, 8.5, 11.5, 11.5, 2.5),
        _acc(path("M15.5 8.5 V6.5 A2.5 2.5 0 0 0 13 4 H6.5 A2.5 2.5 0 0 0 4 6.5 V13 A2.5 2.5 0 0 0 6.5 15.5 H8.5")),
    ]


@icon("edit", "line", "Edit")
def edit():
    # A pencil on the diagonal: pointed tip at the lower left, rounded end at the upper right.
    ux, uy = math.sqrt(0.5), -math.sqrt(0.5)  # along the pencil, toward the end
    nx, ny = -uy, ux
    tip, w, tip_len = (4, 20), 2.4, 4.2
    end = (17.6, 6.4)
    sh = (tip[0] + tip_len * ux, tip[1] + tip_len * uy)
    cap = [(end[0] + w * (math.cos(t) * ux + math.sin(t) * nx), end[1] + w * (math.cos(t) * uy + math.sin(t) * ny))
           for t in [math.radians(a) for a in range(90, -91, -10)]]
    s1, s2 = (sh[0] + w * nx, sh[1] + w * ny), (sh[0] - w * nx, sh[1] - w * ny)
    body = [s1] + cap + [s2]
    band = (end[0] - 3.2 * ux, end[1] - 3.2 * uy)
    return [
        poly(body),
        _acc(polyline([s1, tip, s2])),
        line(band[0] + w * nx, band[1] + w * ny, band[0] - w * nx, band[1] - w * ny),
    ]


@icon("restore", "line", "Restore")
def restore():
    return _trash_body() + _acc(_arrow(12, 17, 12, 10.5, 2.5))


@icon("history", "line", "History")
def history():
    ring = arc_points(12, 12, 9, 9, 215, 505, 5)
    tip, nxt = ring[0], ring[1]
    return [
        polyline(ring),
        _head(tip, nxt, 3.5),
        _acc(polyline([(12, 7.5), (12, 12), (15, 14)])),
    ]


@icon("stopwatch", "line", "Regeneration time")
def stopwatch():
    return [
        circle(12, 13.25, 7.75),
        line(10, 3, 14, 3), line(12, 3, 12, 5.5),
        line(18, 6.75, 19.5, 5.25),
        _acc(line(12, 13.25, 12, 9.25)),
    ]


@icon("pause", "line", "Pause")
def pause():
    return [rect(6.5, 5, 3.5, 14, 1.25), rect(14, 5, 3.5, 14, 1.25)]


@icon("stop", "line", "Stop")
def stop():
    # A filled square, as a media player's stop button (the same height as Pause).
    return [rect(6, 6, 12, 12, 1.5, INK)]


@icon("visible", "line", "Visible")
def visible():
    return [path(_d(_eye_pts())), _acc(circle(12, 12, 3))]


@icon("hidden", "line", "Hidden")
def hidden():
    a, b = (4, 4), (20, 20)
    pupil = arc_points(12, 12, 3, 3, 0, 360, 4)
    return [*_gapped(_eye_pts(64), a, b, 2.2, closed=True), *_gapped(pupil, a, b, 2.2, closed=True),
            _acc(line(*a, *b))]


@icon("lock-filled", "line", "Locked")
def lock_filled():
    body = _rounded([(4.1, 10.1), (19.9, 10.1), (19.9, 21.4), (4.1, 21.4)], 3)
    keyhole = _stroke_outline([(12, 14.5), (12, 17)], 2.5)
    return [
        _acc(path("M8 10.5 V8 A4 4 0 0 1 16 8 V10.5")),
        _knockout(_d(body), [keyhole]),
    ]


# ---------------------------------------------------------------------------------------------
# Status


@icon("info", "line", "Info")
def info():
    return [circle(12, 12, 9), *_acc([line(12, 8, 12, 8.01), line(12, 11.25, 12, 16.5)])]


@icon("info-filled", "line", "Info (filled)")
def info_filled():
    return _knockout(_circle_d(12, 12, R_OUT), [_circle_d(12, 8, 1.15), _stem(12, 11.25, 16.5)])


@icon("help", "line", "Help")
def help_():
    return [circle(12, 12, 9), *_acc([polyline(_question_pts()), line(12, 17, 12, 17.01)])]


@icon("help-filled", "line", "Help (filled)")
def help_filled():
    return _knockout(_circle_d(12, 12, R_OUT), [_stroke_outline(_question_pts(), 1.9), _circle_d(12, 17, 1.15)])


@icon("error-filled", "line", "Error")
def error_filled():
    return _knockout(_circle_d(12, 12, R_OUT), [_stem(12, 7.25, 12.75), _circle_d(12, 16.5, 1.15)])


@icon("warning-filled", "line", "Warning")
def warning_filled():
    tri = _rounded([(12, 2.4), (22.2, 20.6), (1.8, 20.6)], 2.4)
    return _knockout(_d(tri), [_stem(12, 9.5, 14.25), _circle_d(12, 17.25, 1.15)])


# ---------------------------------------------------------------------------------------------
# Places and sharing


@icon("home", "line", "Home")
def home():
    return [
        polyline([(3.5, 11), (12, 3.75), (20.5, 11)]),
        path("M6 9.25 V18 A2 2 0 0 0 8 20 H16 A2 2 0 0 0 18 18 V9.25"),
        _acc(path("M10 20 V15.5 A1 1 0 0 1 11 14.5 H13 A1 1 0 0 1 14 15.5 V20")),
    ]


@icon("notifications", "line", "Notifications")
def notifications():
    return [
        path("M6.5 16.5 V10.5 A5.5 5.5 0 0 1 17.5 10.5 V16.5"),
        line(4.5, 16.5, 19.5, 16.5),
        line(12, 3, 12, 5),
        _acc(path("M10 19.25 A2 2 0 0 0 14 19.25")),
    ]


@icon("settings", "line", "Settings")
def settings():
    # Eight-toothed gear with rounded teeth; the hub (the part you "adjust") is accent.
    pts = []
    for k in range(8):
        c = k * 45
        for r, da in ((6.9, -22.5 + 7), (9, -9.5), (9, 9.5), (6.9, 22.5 - 7)):
            a = math.radians(c + da)
            pts.append((12 + r * math.cos(a), 12 + r * math.sin(a)))
    return [path(_d(pts)), _acc(circle(12, 12, 2.9))]


@icon("share", "line", "Share")
def share():
    nodes = [(6, 12), (17.5, 5.75), (17.5, 18.25)]
    r = 2.5
    out = [_acc(circle(*nodes[0], r))] + [circle(x, y, r) for x, y in nodes[1:]]
    for n in nodes[1:]:
        (x0, y0), (x1, y1) = nodes[0], n
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        g = r + 1.1
        out.append(line(x0 + ux * g, y0 + uy * g, x1 - ux * g, y1 - uy * g))
    return out


@icon("public", "line", "Public")
def public():
    return [circle(12, 12, 9), ellipse(12, 12, 3.75, 9), _acc(line(3, 12, 21, 12))]


@icon("cloud-upload", "line", "Upload to cloud")
def cloud_upload():
    return [
        path("M9 18.5 H7 A4.25 4.25 0 0 1 6.35 10.05 A6 6 0 0 1 17.75 9.1 A4.75 4.75 0 0 1 17 18.5 H15"),
        *_acc(_arrow(12, 20.5, 12, 12, 3)),
    ]


@icon("upload", "line", "Upload")
def upload():
    return [
        path("M4 15 V17.5 A2.5 2.5 0 0 0 6.5 20 H17.5 A2.5 2.5 0 0 0 20 17.5 V15"),
        *_acc(_arrow(12, 15.5, 12, 4)),
    ]


# ---------------------------------------------------------------------------------------------
# Flip direction: a bold diagonal arrow with a filled head (an allowed exception; it sits in a
# small ghost button). The two icons are exact 180-degree rotations about 12,12.


def _flip(sign):
    def p(x, y):  # the down-left arrow; sign -1 rotates it 180 degrees about 12,12
        return (12 + sign * (x - 12), 12 + sign * (y - 12))

    tip, tail = (4.5, 19.5), (18.5, 5.5)
    ux, uy = -math.sqrt(0.5), math.sqrt(0.5)
    nx, ny = -uy, ux
    hl, hw = 6.5, 4  # head length along the shaft, half width
    base = (tip[0] - hl * ux, tip[1] - hl * uy)
    head = [tip, (base[0] + hw * nx, base[1] + hw * ny), (base[0] - hw * nx, base[1] - hw * ny)]
    shaft_end = (base[0] + 1 * ux, base[1] + 1 * uy)
    return [line(*p(*tail), *p(*shaft_end)), _acc(poly([p(*q) for q in head], INK))]


@icon("flip-direction", "line", "Flip direction")
def flip_direction():
    return _flip(1)


@icon("flip-direction-up", "line", "Flip direction (flipped)")
def flip_direction_up():
    return _flip(-1)
