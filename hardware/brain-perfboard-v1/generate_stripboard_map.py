#!/usr/bin/env python3
"""Generate the exact component-side BU-22 Brain stripboard coordinate map."""

from pathlib import Path


COLS = 56
ROWS = 24
PITCH = 18
OX = 78
OY = 92


def xy(col, row):
    return OX + (col - 1) * PITCH, OY + row * PITCH


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


svg = []
svg.append(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="1320" height="700" viewBox="0 0 1320 700">'
)
svg.append('<rect width="1320" height="700" fill="#f7f5ef"/>')
svg.append('<style>.t{font-family:Arial,sans-serif;fill:#172033}.m{font-family:monospace;fill:#172033}.b{font-weight:700}.cut{stroke:#d62828;stroke-width:2}.j{fill:none;stroke-width:2.5;opacity:.72}</style>')
svg.append('<text x="58" y="38" class="t b" font-size="25">BU-22 Brain - exact 24 x 56 stripboard map</text>')
svg.append('<text x="58" y="64" class="t" font-size="14">Component side; long copper strips run left-right. Copper side is horizontally mirrored.</text>')

# Board and strips.
board_w = (COLS - 1) * PITCH
board_h = (ROWS - 1) * PITCH
svg.append(f'<rect x="{OX-10}" y="{OY-10}" width="{board_w+20}" height="{board_h+20}" rx="8" fill="#d6aa69" stroke="#684a25" stroke-width="3"/>')
for r in range(ROWS):
    _, y = xy(1, r)
    svg.append(f'<line x1="{OX}" y1="{y}" x2="{OX+board_w}" y2="{y}" stroke="#b07c3d" stroke-width="4" opacity=".45"/>')
    svg.append(f'<text x="{OX-28}" y="{y+5}" class="m b" font-size="13">{chr(65+r)}</text>')
for c in range(1, COLS + 1):
    x, _ = xy(c, 0)
    for r in range(ROWS):
        _, y = xy(c, r)
        svg.append(f'<circle cx="{x}" cy="{y}" r="2.8" fill="#f6ebd5" stroke="#756046" stroke-width="1"/>')
    if c == 1 or c % 5 == 0 or c == COLS:
        svg.append(f'<text x="{x}" y="{OY-22}" text-anchor="middle" class="m" font-size="11">{c}</text>')

# Module outlines.
def rect(c1, r1, c2, r2, color, label):
    x1, y1 = xy(c1, r1)
    x2, y2 = xy(c2, r2)
    svg.append(f'<rect x="{x1-10}" y="{y1-10}" width="{x2-x1+20}" height="{y2-y1+20}" rx="6" fill="{color}" fill-opacity=".18" stroke="{color}" stroke-width="3"/>')
    svg.append(f'<text x="{(x1+x2)/2}" y="{y1+18}" text-anchor="middle" class="t b" font-size="14">{esc(label)}</text>')

rect(3, 3, 13, 23, "#226d9b", "AUDIO FX - USB DOWN")
rect(16, 3, 26, 23, "#263f78", "FEATHER BRAIN - USB DOWN")
rect(29, 3, 34, 12, "#344b3e", "DS3231 RTC")

# Socket/header holes.
def header(col, row_start, row_end, color, label):
    for r in range(row_start, row_end + 1):
        x, y = xy(col, r)
        svg.append(f'<rect x="{x-5}" y="{y-5}" width="10" height="10" fill="{color}" stroke="#111827" stroke-width="1.2"/>')
    x, y = xy(col, row_start)
    svg.append(f'<text x="{x}" y="{y-10}" text-anchor="middle" class="m b" font-size="10">{esc(label)}</text>')

header(4, 7, 20, "#68b8de", "GPIO")
header(12, 7, 20, "#68b8de", "CTRL")
header(17, 5, 20, "#7187d8", "1x16")
header(25, 5, 16, "#7187d8", "1x12")
header(31, 4, 11, "#75a884", "RTC")
header(38, 13, 20, "#e3b341", "BUTTONS")
header(42, 13, 14, "#d95d5d", "HB")
header(46, 13, 16, "#d781c4", "ANT")
header(50, 13, 16, "#7ab4a9", "SENSOR")
header(54, 13, 17, "#8f95a3", "SPARE")
header(54, 3, 4, "#e35c42", "5V")

# Cuts.
cuts = [(14, 0, 23), (27, 0, 23), (35, 3, 20), (40, 3, 20), (44, 3, 20), (48, 3, 20), (52, 3, 20), (8, 7, 20), (21, 5, 20)]
for col, rs, re in cuts:
    for r in range(rs, re + 1):
        x, y = xy(col, r)
        svg.append(f'<line x1="{x-5}" y1="{y-5}" x2="{x+5}" y2="{y+5}" class="cut"/>')
        svg.append(f'<line x1="{x-5}" y1="{y+5}" x2="{x+5}" y2="{y-5}" class="cut"/>')

# Selected primary jumpers; the document contains the complete point list.
colors = {
    "audio": "#7c3aed",
    "i2c": "#168aad",
    "hb": "#d62828",
    "power": "#e85d04",
    "button": "#2a9d3f",
    "antenna": "#c0268d",
    "sensor": "#008b8b",
    "spare": "#52606d",
    "ground": "#111827",
    "3v3": "#c08a00",
}
jumpers = [
    ((12, 16), (17, 7), "audio"),  # Q -> H
    ((12, 15), (17, 6), "audio"),  # P -> G
    ((4, 8), (17, 12), "audio"),   # I -> M
    ((4, 20), (17, 11), "audio"),  # U -> L
    ((31, 6), (25, 6), "i2c"),     # G -> G SCL
    ((31, 7), (25, 5), "i2c"),     # H -> F SDA
    ((31, 10), (25, 13), "hb"),    # K -> N
    ((31, 10), (42, 13), "hb"),
    ((31, 10), (33, 13), "hb"),
    ((33, 17), (17, 18), "3v3"),

    # Buttons.
    ((38, 14), (17, 5), "button"),
    ((38, 15), (25, 7), "button"),
    ((38, 16), (25, 8), "button"),
    ((38, 17), (25, 9), "button"),
    ((38, 18), (25, 10), "button"),
    ((38, 19), (25, 11), "button"),
    ((38, 20), (25, 12), "button"),

    # Antenna.
    ((46, 13), (17, 16), "antenna"),
    ((46, 14), (17, 15), "antenna"),
    ((46, 15), (17, 14), "antenna"),

    # Sensor.
    ((50, 15), (17, 13), "sensor"),
    ((50, 16), (17, 8), "sensor"),

    # Spare GPIO header.
    ((54, 13), (17, 10), "spare"),
    ((54, 14), (17, 9), "spare"),
    ((54, 15), (17, 8), "spare"),
    ((54, 16), (17, 11), "spare"),

    # 3.3 V distribution.
    ((17, 18), (31, 4), "3v3"),
    ((17, 18), (50, 13), "3v3"),

    # Protected 5 V: J_POWER -> D1 -> Feather VBUS and Audio VIN.
    # The first short segment is D1, drawn separately and labelled below.
    ((51, 3), (25, 14), "power"),
    ((51, 3), (12, 20), "power"),

    # Explicit ground distribution. These are insulated jumpers, not an
    # assumption that the isolation grooves somehow share ground.
    ((54, 4), (51, 4), "ground"),
    ((51, 4), (50, 14), "ground"),
    ((50, 14), (46, 16), "ground"),
    ((46, 16), (42, 14), "ground"),
    ((42, 14), (38, 13), "ground"),
    ((38, 13), (31, 5), "ground"),
    ((31, 5), (17, 17), "ground"),
    ((17, 17), (12, 19), "ground"),
    ((12, 19), (4, 7), "ground"),
    ((54, 17), (50, 14), "ground"),
]
for (c1, r1), (c2, r2), kind in jumpers:
    x1, y1 = xy(c1, r1)
    x2, y2 = xy(c2, r2)
    mid = min(y1, y2) - 8
    svg.append(f'<path d="M{x1},{y1} C{x1},{mid} {x2},{mid} {x2},{y2}" class="j" stroke="{colors[kind]}"/>')

# Draw D1 in series from the external input at 54-D to protected LOGIC_5V at
# 51-D. Its banded cathode is on the 51-D side.
d1x1, d1y = xy(54, 3)
d1x2, _ = xy(51, 3)
svg.append(f'<line x1="{d1x1}" y1="{d1y}" x2="{d1x2+13}" y2="{d1y}" stroke="{colors["power"]}" stroke-width="4"/>')
svg.append(f'<polygon points="{d1x2+13},{d1y-8} {d1x2-2},{d1y} {d1x2+13},{d1y+8}" fill="{colors["power"]}"/>')
svg.append(f'<line x1="{d1x2-3}" y1="{d1y-10}" x2="{d1x2-3}" y2="{d1y+10}" stroke="#172033" stroke-width="3"/>')
svg.append(f'<text x="{(d1x1+d1x2)/2}" y="{d1y-13}" text-anchor="middle" class="m b" font-size="10">D1 1N5817</text>')

# Optional 10k pull-up from the RTC SQW/heartbeat net to 3.3 V.
rhbx, rhby1 = xy(33, 13)
_, rhby2 = xy(33, 17)
svg.append(f'<line x1="{rhbx}" y1="{rhby1}" x2="{rhbx}" y2="{rhby1+12}" stroke="{colors["hb"]}" stroke-width="3"/>')
svg.append(f'<rect x="{rhbx-6}" y="{rhby1+12}" width="12" height="{rhby2-rhby1-24}" fill="#f8e3a1" stroke="#5f4800" stroke-width="2"/>')
svg.append(f'<line x1="{rhbx}" y1="{rhby2-12}" x2="{rhbx}" y2="{rhby2}" stroke="{colors["3v3"]}" stroke-width="3"/>')
svg.append(f'<text x="{rhbx+10}" y="{(rhby1+rhby2)/2+4}" class="m b" font-size="10">RHB 10k</text>')

# Legend.
lx = 1098
svg.append(f'<rect x="{lx}" y="92" width="190" height="520" rx="8" fill="#fff" stroke="#64748b" stroke-width="2"/>')
svg.append(f'<text x="{lx+18}" y="122" class="t b" font-size="17">Legend</text>')
legend = [
    ("#d62828", "Red X: copper cut"),
    (colors["power"], "Orange: LOGIC_5V"),
    (colors["audio"], "Purple: audio UART"),
    (colors["i2c"], "Blue: I2C"),
    (colors["hb"], "Red line: heartbeat"),
    (colors["button"], "Green: buttons"),
    (colors["antenna"], "Magenta: antenna"),
    (colors["sensor"], "Teal: sensor"),
    (colors["spare"], "Gray: spare GPIO"),
    (colors["ground"], "Black: ground"),
    (colors["3v3"], "Gold: 3.3 V"),
]
for i, (color, text) in enumerate(legend):
    yy = 156 + i * 34
    svg.append(f'<line x1="{lx+18}" y1="{yy}" x2="{lx+50}" y2="{yy}" stroke="{color}" stroke-width="4"/>')
    svg.append(f'<text x="{lx+60}" y="{yy+5}" class="t" font-size="13">{esc(text)}</text>')
svg.append(f'<text x="{lx+18}" y="545" class="t" font-size="12">Coordinate cross-check:</text>')
svg.append(f'<text x="{lx+18}" y="566" class="m b" font-size="11">cuts-and-jumpers.md</text>')
svg.append(f'<text x="{lx+18}" y="588" class="t" font-size="11">Dry-fit real modules first.</text>')

svg.append('<text x="78" y="565" class="t b" font-size="15">USB / ACCESS EDGE</text>')
svg.append('<text x="78" y="590" class="t" font-size="13">All functional jumpers are shown. Use the coordinate table while assembling; the drawing is a visual cross-check.</text>')
svg.append('</svg>')

Path(__file__).with_name("stripboard-map.svg").write_text("\n".join(svg), encoding="utf-8")
