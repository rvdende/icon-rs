"""Interface objects, documents, panels and people (kind "line").

Shared shapes (keep in step with ui_a):
- Documents: 14 x 18 (x 5..19, y 3..21), corner radius 2.5, folded top-right corner of 5.
- Folders: 18 x 15 (x 3..21, y 4.5..19.5), corner radius 2.5, tab on the left.
- People: a round head over a domed shoulder curve (`_person`).
- Plus signs: arms of 2.5 (5 across). Arrowheads: open, 5 wide.
"""
import math
from common import *

R = 2.5  # corner radius shared by documents, folders, frames


def _a(x, y, r=R, sweep=0):
    return f"A{f(r)} {f(r)} 0 0 {sweep} {f(x)} {f(y)}"


# ---------------------------------------------------------------------------------------------
# Documents


def _doc(x0=5, x1=19, y0=3, y1=21, fold=5, gap_left=None, gap_right=None):
    """The document outline, optionally with a gap in the left or right edge (for arrows that
    pass through it), plus the fold line."""
    fx, fy = x1 - fold, y0 + fold
    left_down = f"V{f(y1 - R)} {_a(x0 + R, y1)} H{f(x1 - R)} {_a(x1, y1 - R)}"
    top = f"L{f(fx)} {f(y0)} H{f(x0 + R)} {_a(x0, y0 + R)}"
    if gap_left:
        g0, g1 = gap_left
        d = f"M{f(x0)} {f(g1)} {left_down} V{f(fy)} {top} V{f(g0)}"
    elif gap_right:
        g0, g1 = gap_right
        d = f"M{f(x1)} {f(g0)} V{f(fy)} {top} {left_down} V{f(g1)}"
    else:
        d = f"M{f(fx)} {f(y0)} H{f(x0 + R)} {_a(x0, y0 + R)} {left_down} V{f(fy)} Z"
    fold_d = f"M{f(fx)} {f(y0)} V{f(fy - 1.5)} {_a(fx + 1.5, fy, 1.5)} H{f(x1)}"
    return [path(d), path(fold_d)]


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


@icon("file", "line", "File")
def file():
    return _doc()


@icon("file-new", "line", "New file")
def file_new():
    return _doc() + [_plus(12, 14)]


@icon("file-import", "line", "Import")
def file_import():
    return _doc(7, 21, gap_left=(10.5, 17.5)) + _arrow(2.5, 14, 13, 14)


@icon("file-export", "line", "Export")
def file_export():
    return _doc(3, 17, gap_right=(10.5, 17.5)) + _arrow(9.5, 14, 21.5, 14)


@icon("details", "line", "Details")
def details():
    return _doc() + [path("M8.5 9 H11 M8.5 13 H15.5 M8.5 17 H15.5")]


# ---------------------------------------------------------------------------------------------
# Folders


def _folder(x0=3, x1=21, y0=4.5, y1=19.5):
    tab = 7  # width of the tab's flat top, from the left corner
    d = (f"M{f(x0)} {f(y1 - R)} V{f(y0 + R)} {_a(x0 + R, y0, sweep=1)} H{f(x0 + tab)} "
         f"L{f(x0 + tab + 2)} {f(y0 + 2.5)} H{f(x1 - R)} {_a(x1, y0 + 2.5 + R, sweep=1)} "
         f"V{f(y1 - R)} {_a(x1 - R, y1, sweep=1)} H{f(x0 + R)} {_a(x0, y1 - R, sweep=1)} Z")
    return [path(d)]


@icon("folder", "line", "Folder")
def folder():
    return _folder()


@icon("folder-new", "line", "New folder")
def folder_new():
    return _folder() + [_plus(12, 13.25)]


@icon("move-to-folder", "line", "Move to folder")
def move_to_folder():
    return _folder() + _arrow(8, 13.25, 16, 13.25)


# ---------------------------------------------------------------------------------------------
# Panels


@icon("apps", "line", "Apps")
def apps():
    s, a, b = 6.75, 3.5, 13.75
    return [rect(x, y, s, s, 1.75) for y in (a, b) for x in (a, b)]


@icon("custom-table", "line", "Custom tables")
def custom_table():
    return [rect(3, 4, 18, 16, R), path("M3 9.5 H21 M3 14.75 H21 M9.5 9.5 V20")]


@icon("configurations", "line", "Configurations")
def configurations():
    out = []
    for y, k in ((6, 15), (12, 8), (18, 13)):
        out.append(path(f"M3 {f(y)} H{f(k - 2.25)} M{f(k + 2.25)} {f(y)} H21"))
        out.append(circle(k, y, 2.25))
    return out


@icon("variables", "line", "Variables")
def variables():
    return [
        path("M14 4.6 C12.4 3.7 10.6 4.3 10.2 6.3 L8 17.7 C7.6 19.7 5.8 20.3 4.2 19.4"),
        path("M6.5 9.5 H13"),
        path("M14.5 12.5 L20 19 M20 12.5 L14.5 19"),
    ]


@icon("appearance", "line", "Appearances")
def appearance():
    d = ("M12 21 A9 9 0 0 1 12 3 A9 8.5 0 0 1 21 11.5 A4.25 4.25 0 0 1 16.75 15.75 H15 "
         "A1.75 1.75 0 0 0 13.6 18.55 L13.85 18.9 A1.35 1.35 0 0 1 12 21 Z")
    dots = [circle(x, y, 0.45, INK) for x, y in ((7.5, 12.25), (8.5, 8), (12.25, 6.5), (16, 8.25))]
    return [path(d)] + dots


@icon("properties", "line", "Properties")
def properties():
    return [rect(3.5, 3.5, 17, 17, R), path("M7.5 8.5 H9.5 M12.5 8.5 H16.5 M7.5 12 H9.5 M12.5 12 H16.5 "
                                            "M7.5 15.5 H9.5 M12.5 15.5 H16.5")]


@icon("comments", "line", "Comments")
def comments():
    d = (f"M7.5 17 V20.5 L11.75 17 H18.5 {_a(21, 14.5)} V6.5 {_a(18.5, 4)} H5.5 {_a(3, 6.5)} "
         f"V14.5 {_a(5.5, 17)} Z")
    return [path(d), path("M7.5 9 H16.5 M7.5 12.5 H13")]


@icon("find", "line", "Find in document")
def find():
    corners = "M3 7.5 V5.5 A2.5 2.5 0 0 1 5.5 3 H7.5 M16.5 3 H18.5 A2.5 2.5 0 0 1 21 5.5 V7.5 " \
              "M21 16.5 V18.5 A2.5 2.5 0 0 1 18.5 21 H16.5 M7.5 21 H5.5 A2.5 2.5 0 0 1 3 18.5 V16.5"
    return [path(corners), circle(11.25, 11.25, 3.75), line(14, 14, 16.5, 16.5)]


@icon("list", "line", "List view")
def list_view():
    return [path("M9 6 H21 M9 12 H21 M9 18 H21 M4 6 h.01 M4 12 h.01 M4 18 h.01")]


@icon("list-details", "line", "List with details")
def list_details():
    return [rect(3, 4, 6.5, 6.5, 1.5), rect(3, 13.5, 6.5, 6.5, 1.5),
            path("M13 5.5 H21 M13 9 H17.5 M13 15 H21 M13 18.5 H17.5")]


@icon("tab-manager", "line", "Tab manager")
def tab_manager():
    return [path("M3 5.5 H21 M3 11.5 H10 M3 17.5 H8.5"), circle(15.5, 14.5, 3.5), line(18.1, 17.1, 20.5, 19.5)]


# ---------------------------------------------------------------------------------------------
# Versioning and social


@icon("branches", "line", "Branches")
def branches():
    return [circle(7, 5.5, 2.25), circle(7, 18.5, 2.25), circle(17, 5.5, 2.25),
            line(7, 7.75, 7, 16.25), path("M17 7.75 V8.5 C17 12.5 14 14 11.5 14 C9 14 7 14.8 7 16.25")]


@icon("versions", "line", "Versions")
def versions():
    return [rect(10, 3.5, 11, 17, R), path("M6.5 6 V18 M3 8.5 V15.5")]


@icon("likes", "line", "Likes")
def likes():
    hand = ("M7.5 10.5 L10.6 4.3 A2.3 2.3 0 0 1 14.9 5.7 L14.2 10 H18.3 A2.2 2.2 0 0 1 20.45 12.7 "
            "L19.1 18.3 A2.2 2.2 0 0 1 16.95 20 H7.5 Z")
    cuff = "M7.5 10.5 H5 A2 2 0 0 0 3 12.5 V18 A2 2 0 0 0 5 20 H7.5"
    return [path(hand), path(cuff)]


def _person(cx, head_cy, head_r, half_w, top, bottom):
    """A head over a domed shoulder curve. The shoulders are a half-ellipse-ish curve from
    (cx - half_w, bottom) up to `top` and back down."""
    k = 0.55
    h = bottom - top
    d = (f"M{f(cx - half_w)} {f(bottom)} C{f(cx - half_w)} {f(bottom - h * k * 1.3)} "
         f"{f(cx - half_w * k)} {f(top)} {f(cx)} {f(top)} C{f(cx + half_w * k)} {f(top)} "
         f"{f(cx + half_w)} {f(bottom - h * k * 1.3)} {f(cx + half_w)} {f(bottom)}")
    return [circle(cx, head_cy, head_r), path(d)]


@icon("user", "line", "User")
def user():
    return _person(12, 7.5, 4, 7.5, 14.75, 20.5)


@icon("users", "line", "Teams")
def users():
    back_head = "M15.5 3.9 A3.6 3.6 0 0 1 15.5 10.9"
    back_body = "M18.5 14.9 C20.2 15.7 21 17.8 21 20.5"
    return _person(9, 7.4, 3.5, 6, 14.5, 20.5) + [path(back_head), path(back_body)]


@icon("owned-by-me", "line", "Owned by me")
def owned_by_me():
    return [circle(12, 12, 9), circle(12, 10, 3.25),
            path("M6.4 19 C7.5 16.8 9.6 15.5 12 15.5 C14.4 15.5 16.5 16.8 17.6 19")]


@icon("shared-with-me", "line", "Shared with me")
def shared_with_me():
    return [rect(3.5, 3.5, 17, 17, 3), circle(12, 10, 3.25),
            path("M6.6 20.5 C7.1 17.3 9.3 15.5 12 15.5 C14.7 15.5 16.9 17.3 17.4 20.5")]


# ---------------------------------------------------------------------------------------------
# Objects


@icon("screenshot", "line", "Camera")
def screenshot():
    d = (f"M3 9.5 {_a(5.5, 7, sweep=1)} H7.25 L8.9 4.5 H15.1 L16.75 7 H18.5 {_a(21, 9.5, sweep=1)} "
         f"V17.5 {_a(18.5, 20, sweep=1)} H5.5 {_a(3, 17.5, sweep=1)} Z")
    return [path(d), circle(12, 13.25, 3.5)]


@icon("code", "line", "Code")
def code():
    return [polyline([(7.5, 7.5), (3, 12), (7.5, 16.5)]), polyline([(16.5, 7.5), (21, 12), (16.5, 16.5)]),
            line(13.5, 5, 10.5, 19)]


@icon("chip", "line", "Chip")
def chip():
    pins = []
    for t in (9.5, 14.5):
        pins.append(f"M{f(t)} 3 V5.5 M{f(t)} 18.5 V21 M3 {f(t)} H5.5 M18.5 {f(t)} H21")
    return [rect(5.5, 5.5, 13, 13, R), rect(9.5, 9.5, 5, 5, 1), path(" ".join(pins))]


@icon("tool", "line", "Tool")
def tool():
    # Built along +x (head at the origin, handle towards +x, jaw towards -x), then rotated so
    # the handle runs down-left.
    Rh, h, s, depth, L = 5.25, 1.7, 1.9, 0.9, 12.4
    ang = math.radians(135)
    cx, cy = 14.9, 9.1
    xr = math.sqrt(Rh * Rh - h * h)
    xs = math.sqrt(Rh * Rh - s * s)
    a_h = math.degrees(math.atan2(h, xr))
    a_s = 180 - math.degrees(math.atan2(s, xs))
    ps = []
    ps += [(xr, -h), (L, -h)]
    ps += [(L + h * math.sin(math.radians(t)), -h * math.cos(math.radians(t))) for t in range(15, 180, 15)]
    ps += [(L, h), (xr, h)]
    ps += [(Rh * math.cos(math.radians(t)), Rh * math.sin(math.radians(t)))
           for t in [a_h + (a_s - a_h) * i / 16 for i in range(1, 16)]]
    ps += [(-xs, s), (-depth, s), (-depth, -s), (-xs, -s)]
    ps += [(Rh * math.cos(math.radians(-t)), Rh * math.sin(math.radians(-t)))
           for t in [a_s - (a_s - a_h) * i / 16 for i in range(1, 16)]]
    ca, sa = math.cos(ang), math.sin(ang)
    return [poly([(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in ps])]


@icon("books", "line", "Books")
def books():
    return [rect(3.5, 4, 4.5, 16, 1.25), rect(8, 7, 4.5, 13, 1.25),
            rect(13.6, 4.6, 4.5, 15.5, 1.25, extra='transform="rotate(-14 15.85 20.1)"'),
            path("M3.5 8 H8 M8 10.5 H12.5")]


@icon("idea", "line", "Explore")
def idea():
    return [path("M9.5 16 C9.5 13.9 6 12.6 6 9.25 A6 6 0 0 1 18 9.25 C18 12.6 14.5 13.9 14.5 16 Z"),
            path("M9.5 18.75 H14.5 M10.75 21 H13.25")]


@icon("keyboard", "line", "Keyboard shortcuts")
def keyboard():
    keys = " ".join(f"M{f(x)} 10 h.01" for x in (6.5, 10.17, 13.83, 17.5))
    return [rect(2.5, 6, 19, 12, R), path(keys + " M6.5 14 h.01 M17.5 14 h.01 M9.5 14 H14.5")]


def _tag(s=1.0, ox=0.0, oy=0.0):
    def p(x, y):
        return f"{f(ox + x * s)} {f(oy + y * s)}"
    r = 2.5 * s
    d = (f"M{p(3, 5.5)} V{f(oy + 11 * s)} {_a(*[ox + 3.73 * s, oy + 12.77 * s], r=2.5 * s)} "
         f"L{p(11.23, 20.27)} A{f(r)} {f(r)} 0 0 0 {p(14.77, 20.27)} L{p(20.27, 14.77)} "
         f"A{f(r)} {f(r)} 0 0 0 {p(20.27, 11.23)} L{p(12.77, 3.73)} A{f(r)} {f(r)} 0 0 0 {p(11, 3)} "
         f"H{f(ox + 5.5 * s)} A{f(r)} {f(r)} 0 0 0 {p(3, 5.5)} Z")
    return [path(d), circle(ox + 7.5 * s, oy + 7.5 * s, 0.6, INK)]


@icon("tag", "line", "Label")
def tag():
    return _tag()


@icon("tag-new", "line", "Add label")
def tag_new():
    return _tag(0.74, 0.9, 0.9) + [_plus(18.25, 18.25)]


@icon("location", "line", "Location")
def location():
    return [path("M12 21 C12 21 19 15 19 9.75 A7 7 0 0 0 5 9.75 C5 15 12 21 12 21 Z"), circle(12, 9.75, 2.5)]


@icon("note", "line", "Note")
def note():
    d = f"M14.5 20.5 H6 {_a(3.5, 18, sweep=1)} V6 {_a(6, 3.5, sweep=1)} H18 {_a(20.5, 6, sweep=1)} V14.5 Z"
    return [path(d), path("M14.5 20.5 V16.5 A2 2 0 0 1 16.5 14.5 H20.5"), path("M7.5 8.5 H16.5 M7.5 12 H12.5")]


# ---------------------------------------------------------------------------------------------
# Text and measurement


@icon("bold", "line", "Bold")
def bold():
    return [path("M7 4.5 H12.75 A3.75 3.75 0 0 1 12.75 12 H7 Z M7 12 H13.75 A3.75 3.75 0 0 1 13.75 19.5 H7 Z")]


@icon("italic", "line", "Italic")
def italic():
    return [path("M10 4.5 H19 M5 19.5 H14 M14.5 4.5 L9.5 19.5")]


@icon("flip-horizontal", "line", "Flip left to right")
def flip_horizontal():
    return [line(12, 3, 12, 21, 'stroke-dasharray="0.01 3.6"'),
            poly([(3, 18), (8.75, 6), (8.75, 18)]), poly([(21, 18), (15.25, 6), (15.25, 18)], None, 'stroke-opacity="0.45"')]


@icon("ruler", "line", "Measure a distance")
def ruler():
    ticks = "M-6 -3.5 V-0.5 M-3 -3.5 V-1.5 M0 -3.5 V-0.5 M3 -3.5 V-1.5 M6 -3.5 V-0.5"
    return [f'<g transform="translate(12 12) rotate(-45)">{rect(-9.5, -3.5, 19, 7, 2)}{path(ticks)}</g>']


@icon("clock", "line", "Clock")
def clock():
    return [circle(12, 12, 9), polyline([(12, 7), (12, 12), (15.25, 14)])]
