"""Regenerates icons/*.svg and icons/dark/*.svg. Run from anywhere: python3 tools/gen_icons.py

Icons are drawn with the light palette. The dark variant swaps each palette colour for its
counterpart in DARK_PALETTE; src/lib.rs's Palette uses the same five slots, in the same order.
"""
import math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")
# Palette slots: outline ink, top face, soft face, mid face, shaded face.
INK, LIGHT, SOFT, MID, DARK = "#262626", "#ffffff", "#d4d4d4", "#a3a3a3", "#737373"
DARK_PALETTE = {INK: "#e4e4e7", LIGHT: "#a1a1aa", SOFT: "#8b8b94", MID: "#71717a", DARK: "#52525b"}
os.makedirs(os.path.join(OUT, "dark"), exist_ok=True)
C, S = math.cos(math.pi / 6), 0.5


def iso(o, x, y, z):
    return (o[0] + (x - y) * C, o[1] + (x + y) * S - z)


def pts(ps):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in ps)


def poly(ps, fill, extra=""):
    return f'<polygon points="{pts(ps)}" fill="{fill}"{extra}/>'


def box(o, x0, x1, y0, y1, z0, z1, top=LIGHT, right=MID, left=DARK, extra=""):
    P = lambda x, y, z: iso(o, x, y, z)
    return "\n  ".join([
        poly([P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], top, extra),
        poly([P(x1, y0, z1), P(x1, y1, z1), P(x1, y1, z0), P(x1, y0, z0)], right, extra),
        poly([P(x0, y1, z1), P(x1, y1, z1), P(x1, y1, z0), P(x0, y1, z0)], left, extra),
    ])


def arrow(x0, y0, x1, y1, head=3.2, width=2.6):
    """Straight arrow shaft plus a filled head at (x1, y1)."""
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    bx, by = x1 - ux * head, y1 - uy * head
    nx, ny = -uy * width / 2, ux * width / 2
    return (f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{bx:.2f}" y2="{by:.2f}"/>\n  '
            f'<polygon points="{pts([(x1, y1), (bx + nx, by + ny), (bx - nx, by - ny)])}" fill="{INK}"/>')


def ellipse_pt(cx, cy, rx, ry, deg):
    a = math.radians(deg)
    return (cx + rx * math.cos(a), cy + ry * math.sin(a))


def svg(name, body):
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" '
           f'fill="none" stroke="{INK}" stroke-width="1.1" stroke-linejoin="round" stroke-linecap="round">\n'
           f'  {body}\n</svg>\n')
    with open(os.path.join(OUT, f"{name}.svg"), "w") as f:
        f.write(doc)
    for light, dark in DARK_PALETTE.items():
        doc = doc.replace(light, dark)
    with open(os.path.join(OUT, "dark", f"{name}.svg"), "w") as f:
        f.write(doc)


# Extrude: a solid slab grown from its footprint, dashed ghost of the target height, arrow up.
o = (12, 13.5)
P = lambda x, y, z: iso(o, x, y, z)
ghost = [P(0, 0, 9), P(7, 0, 9), P(7, 7, 9), P(0, 7, 9)]
svg("extrude", "\n  ".join([
    box(o, 0, 7, 0, 7, 0, 3.5),
    f'<polygon points="{pts(ghost)}" stroke-dasharray="1.4 1.2"/>',
    *[f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke-dasharray="1.4 1.2"/>'
      for a, b in [(P(7, 0, 3.5), P(7, 0, 9)), (P(7, 7, 3.5), P(7, 7, 9)), (P(0, 7, 3.5), P(0, 7, 9))]],
    arrow(*P(3.5, 3.5, 3.5), *P(3.5, 3.5, 11.2)),
]))

# Revolve: dash-dot axis, a flat profile beside it, and a sweep arrow wrapping the axis.
a0, a1 = 200, 500  # degrees swept by the arrow
arc_pts = [ellipse_pt(9, 12, 6.5, 2.4, d) for d in range(a0, a1 - 20, 5)]
tip = ellipse_pt(9, 12, 6.5, 2.4, a1 - 5)
base = arc_pts[-1]
dx, dy = tip[0] - base[0], tip[1] - base[1]
L = math.hypot(dx, dy); ux, uy = dx / L, dy / L
tip = (base[0] + ux * 3.2, base[1] + uy * 3.2)
nx, ny = -uy * 1.3, ux * 1.3
svg("revolve", "\n  ".join([
    '<path d="M11.5 5.5 h7 v10 l-3 3 h-4 z" fill="' + MID + '"/>',
    '<line x1="9" y1="2" x2="9" y2="22" stroke-dasharray="3 1.2 0.6 1.2" stroke-width="0.9"/>',
    f'<polyline points="{pts(arc_pts)}"/>',
    f'<polygon points="{pts([tip, (base[0] + nx, base[1] + ny), (base[0] - nx, base[1] - ny)])}" fill="{INK}"/>',
]))

# Sweep: one thick tube with an S bend, its round profile showing as a light cap at the near end.
# The outline is offset from the spine, so it stays crisp at 1x.
def cubic(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(p0, p1, p2, p3))

spine = [(19, 5.5), (10, 4.5), (15, 18.5), (5.5, 18)]
r = 2.7
samples = [cubic(*spine, i / 40) for i in range(41)]
def tangent(i):
    a, b = samples[max(i - 1, 0)], samples[min(i + 1, len(samples) - 1)]
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    return (b[0] - a[0]) / L, (b[1] - a[1]) / L
def offset(k):
    return [(x - tangent(i)[1] * k, y + tangent(i)[0] * k) for i, (x, y) in enumerate(samples)]
def cap(i, fill):
    (x, y), (tx, ty) = samples[i], tangent(i)
    angle = math.degrees(math.atan2(ty, tx)) + 90
    return f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{r}" ry="1.25" transform="rotate({angle:.1f} {x:.2f} {y:.2f})" fill="{fill}"/>'
left, right = offset(r), offset(-r)
svg("sweep", "\n  ".join([
    cap(len(samples) - 1, MID),  # far end: only the outer half shows past the tube body
    poly(left + right[::-1], MID, ' stroke="none"'),
    f'<polyline points="{pts(offset(-r * 0.45))}" stroke="{DARK}" stroke-width="1.3" stroke-opacity="0.55"/>',
    f'<polyline points="{pts(offset(r * 0.4))}" stroke="{LIGHT}" stroke-width="1" stroke-opacity="0.6"/>',
    f'<polyline points="{pts(left)}"/>',
    f'<polyline points="{pts(right)}"/>',
    cap(0, LIGHT),
]))

# Loft: square section at the bottom blended into a round section at the top.
bot = [(5, 18), (12, 21.5), (19, 18), (12, 14.5)]
svg("loft", "\n  ".join([
    f'<path d="M5 18 L7.5 6.5 A4.5 1.8 0 0 0 16.5 6.5 L19 18 L12 21.5 Z" fill="{MID}"/>',
    f'<path d="M12 21.5 C12 15, 12 11, 12 8.3" stroke-width="0.8"/>',
    f'<polygon points="{pts(bot)}" stroke-dasharray="1.4 1.2" stroke-width="0.9"/>',
    f'<ellipse cx="12" cy="6.5" rx="4.5" ry="1.8" fill="{LIGHT}"/>',
]))

# Thicken: a curved sheet with a thickness grown underneath and a down arrow through it.
svg("thicken", "\n  ".join([
    f'<path d="M3 9 C7 6, 11 12, 15 9 L21 12 L21 16 C17 19, 13 13, 9 16 L3 13 Z" fill="{DARK}"/>',
    f'<path d="M3 9 C7 6, 11 12, 15 9 L21 12 C17 15, 13 9, 9 12 Z" fill="{LIGHT}"/>',
    f'<path d="M9 12 L9 16"/>',
    arrow(12, 3, 12, 11.6),
]))

# Enclose: three bounding surfaces (thin, light) with the enclosed volume filled.
svg("enclose", "\n  ".join([
    f'<path d="M7 7 C10 5.5, 14 5.5, 17 7 L18.5 17 C14 19, 10 19, 5.5 17 Z" fill="{MID}" stroke="none"/>',
    f'<path d="M3.5 6 C9 3.5, 15 3.5, 20.5 6" stroke-width="1.3"/>',
    f'<path d="M6.5 4.5 L4.5 20"/>',
    f'<path d="M17.5 4.5 L19.5 20"/>',
    f'<path d="M3 17.5 C9 20.2, 15 20.2, 21 17.5" stroke-width="1.3"/>',
]))

# Fillet: box with a rounded top-right edge.
o = (12, 12)
P = lambda x, y, z: iso(o, x, y, z)
r = 4
def fillet_pts(y):
    return [P(8 - r + r * math.sin(math.radians(t)), y, 8 - r + r * math.cos(math.radians(t))) for t in range(0, 91, 10)]
fa, fb = fillet_pts(0), fillet_pts(8)
svg("fillet", "\n  ".join([
    poly([P(0, 0, 8), fa[0], fb[0], P(0, 8, 8)], LIGHT),
    poly(fa + fb[::-1], MID),
    poly([fa[-1], P(8, 0, 0), P(8, 8, 0), fb[-1]], MID),
    poly([P(0, 8, 8)] + fb + [P(8, 8, 0), P(0, 8, 0)], DARK),
]))

# Chamfer: box with the top-right edge cut flat.
c = 3.5
svg("chamfer", "\n  ".join([
    poly([P(0, 0, 8), P(8 - c, 0, 8), P(8 - c, 8, 8), P(0, 8, 8)], LIGHT),
    poly([P(8 - c, 0, 8), P(8, 0, 8 - c), P(8, 8, 8 - c), P(8 - c, 8, 8)], SOFT),
    poly([P(8, 0, 8 - c), P(8, 0, 0), P(8, 8, 0), P(8, 8, 8 - c)], MID),
    poly([P(0, 8, 8), P(8 - c, 8, 8), P(8, 8, 8 - c), P(8, 8, 0), P(0, 8, 0)], DARK),
]))

# Shell: an open box with its top face removed; floor and back walls show through the opening.
t = 1.4
rim = [P(t, t, 8), P(8 - t, t, 8), P(8 - t, 8 - t, 8), P(t, 8 - t, 8)]
svg("shell", "\n  ".join([
    box(o, 0, 8, 0, 8, 0, 8),
    f'<clipPath id="opening"><polygon points="{pts(rim)}"/></clipPath>',
    '<g clip-path="url(#opening)">',
    poly([P(t, t, t), P(8 - t, t, t), P(8 - t, 8 - t, t), P(t, 8 - t, t)], LIGHT, ' stroke-width="0.7"'),
    poly([P(t, t, 8), P(8 - t, t, 8), P(8 - t, t, t), P(t, t, t)], DARK, ' stroke-width="0.7"'),
    poly([P(t, t, 8), P(t, 8 - t, 8), P(t, 8 - t, t), P(t, t, t)], MID, ' stroke-width="0.7"'),
    '</g>',
    f'<polygon points="{pts(rim)}"/>',
]))

# Linear pattern: one seed cube and two light copies along a dashed direction.
o = (5, 11)
P = lambda x, y, z: iso(o, x, y, z)
svg("pattern", "\n  ".join([
    f'<line x1="{P(2.5,2.5,0)[0]:.2f}" y1="{P(2.5,2.5,0)[1]:.2f}" x2="{P(17,2.5,0)[0]:.2f}" y2="{P(17,2.5,0)[1]:.2f}" stroke-dasharray="1.4 1.2" stroke-width="0.8"/>',
    box(o, 12, 17, 0, 5, 0, 5, LIGHT, LIGHT, LIGHT, ' stroke-dasharray="1.2 0.9"'),
    box(o, 6, 11, 0, 5, 0, 5, LIGHT, LIGHT, LIGHT, ' stroke-dasharray="1.2 0.9"'),
    box(o, 0, 5, 0, 5, 0, 5),
]))

# Boolean: two overlapping disks, the overlap shaded.
svg("boolean", "\n  ".join([
    f'<path d="M12 7.2 A6 6 0 0 1 12 16.8 A6 6 0 0 1 12 7.2 Z" fill="{MID}" stroke="none"/>',
    f'<circle cx="8.5" cy="12" r="6"/>',
    f'<circle cx="15.5" cy="12" r="6"/>',
]))
print("ok")
