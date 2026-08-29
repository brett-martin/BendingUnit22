#!/usr/bin/env python3
"""Generate readable, single-purpose BU-22 Brain stripboard wiring maps."""

import base64
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COLS, ROWS, PITCH = 56, 24, 17
OX, OY = 62, 78
W, H = 1120, 565


def pt(col, row):
    return OX + (col - 1) * PITCH, OY + row * PITCH


def svg_start(title, subtitle):
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    out += [
        '<rect width="1120" height="565" fill="#f7f5ef"/>',
        '<style>.t{font-family:Arial,sans-serif;fill:#172033}.m{font-family:monospace;fill:#172033}.b{font-weight:700}.w{fill:none;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}.cut{stroke:#d94848;stroke-width:1.5;opacity:.42}</style>',
        f'<text x="45" y="31" class="t b" font-size="23">{title}</text>',
        f'<text x="45" y="53" class="t" font-size="12">{subtitle}</text>',
    ]
    bw, bh = (COLS - 1) * PITCH, (ROWS - 1) * PITCH
    out.append(f'<rect x="{OX-9}" y="{OY-9}" width="{bw+18}" height="{bh+18}" rx="7" fill="#d9af70" stroke="#684a25" stroke-width="3"/>')
    for r in range(ROWS):
        _, y = pt(1, r)
        out.append(f'<line x1="{OX}" y1="{y}" x2="{OX+bw}" y2="{y}" stroke="#a87335" stroke-width="3" opacity=".28"/>')
        out.append(f'<text x="{OX-25}" y="{y+4}" class="m b" font-size="10">{chr(65+r)}</text>')
    for c in range(1, COLS + 1):
        x, _ = pt(c, 0)
        for r in range(ROWS):
            _, y = pt(c, r)
            out.append(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#f7ecd7" stroke="#756046" stroke-width=".8"/>')
        if c == 1 or c % 5 == 0 or c == COLS:
            out.append(f'<text x="{x}" y="{OY-16}" text-anchor="middle" class="m" font-size="9">{c}</text>')
    return out


def base_components(out, active=()):
    def module(c1, r1, c2, r2, label, key):
        x1, y1 = pt(c1, r1); x2, y2 = pt(c2, r2)
        opacity = .18 if key in active else .07
        stroke = "#274c77" if key in active else "#857c6c"
        out.append(f'<rect x="{x1-8}" y="{y1-8}" width="{x2-x1+16}" height="{y2-y1+16}" rx="6" fill="#274c77" fill-opacity="{opacity}" stroke="{stroke}" stroke-width="2"/>')
        out.append(f'<text x="{(x1+x2)/2}" y="{y1+16}" text-anchor="middle" class="t b" font-size="12">{label}</text>')
    module(3, 3, 13, 23, "AUDIO FX", "audio")
    module(16, 3, 26, 23, "FEATHER BRAIN", "feather")
    module(29, 3, 34, 12, "DS3231 RTC", "rtc")

    def header(col, start, end, label, key):
        fill = "#f0b44d" if key in active else "#c5bba9"
        for r in range(start, end + 1):
            x, y = pt(col, r)
            out.append(f'<rect x="{x-4}" y="{y-4}" width="8" height="8" fill="{fill}" stroke="#172033" stroke-width="1"/>')
        x, y = pt(col, start)
        out.append(f'<text x="{x}" y="{y-8}" text-anchor="middle" class="m b" font-size="8">{label}</text>')
    header(4, 7, 20, "GPIO", "audio")
    header(12, 7, 20, "CTRL", "audio")
    header(17, 5, 20, "1x16", "feather")
    header(25, 5, 16, "1x12", "feather")
    header(31, 4, 11, "RTC", "rtc")
    header(38, 13, 20, "BUTTONS", "buttons")
    header(42, 13, 14, "HB", "heartbeat")
    header(46, 13, 16, "ANT", "antenna")
    header(50, 13, 16, "SENSOR", "sensor")
    header(54, 3, 4, "5V", "power")

    for col, rs, re in [(14,0,23),(27,0,23),(35,3,20),(40,3,20),(44,3,20),(48,3,20),(52,3,20),(8,7,20),(21,5,20)]:
        for r in range(rs, re + 1):
            x, y = pt(col, r)
            out.append(f'<path d="M{x-4},{y-4} L{x+4},{y+4} M{x-4},{y+4} L{x+4},{y-4}" class="cut"/>')


def path(out, points, color, width=3, dash=None):
    # Wiring is drawn as a direct cubic Bezier between its two electrical
    # endpoints. Curves remain visually distinct from the straight horizontal
    # copper strips and avoid implying connections at every crossed hole.
    c1, r1 = points[0]
    c2, r2 = points[-1]
    x1, y1 = pt(c1, r1)
    x2, y2 = pt(c2, r2)
    dx, dy = x2 - x1, y2 - y1
    if abs(dx) < 1:
        bend = 18 if dy >= 0 else -18
        cx1, cy1 = x1 + bend, y1 + dy * .33
        cx2, cy2 = x2 + bend, y2 - dy * .33
    else:
        cx1, cy1 = x1 + dx * .34, y1
        cx2, cy2 = x2 - dx * .34, y2
    d = f"M{x1},{y1} C{cx1},{cy1} {cx2},{cy2} {x2},{y2}"
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    out.append(f'<path d="{d}" class="w" stroke="{color}" stroke-width="{width}"{extra}/>')
    # Endpoint rings make the actual electrical terminations unambiguous.
    out.append(f'<circle cx="{x1}" cy="{y1}" r="4.2" fill="#f7f5ef" stroke="{color}" stroke-width="2"/>')
    out.append(f'<circle cx="{x2}" cy="{y2}" r="4.2" fill="#f7f5ef" stroke="{color}" stroke-width="2"/>')


def label(out, col, row, text, color="#172033", anchor="start"):
    x, y = pt(col, row)
    out.append(f'<text x="{x}" y="{y-7}" text-anchor="{anchor}" class="m b" font-size="9" fill="{color}">{text}</text>')


def finish(out, filename, legend):
    out.append(f'<rect x="865" y="500" width="220" height="45" rx="6" fill="#fff" stroke="#64748b"/>')
    out.append(f'<text x="975" y="518" text-anchor="middle" class="t b" font-size="11">{legend}</text>')
    out.append('<text x="975" y="535" text-anchor="middle" class="t" font-size="9">Component side; coordinate table is authoritative.</text>')
    out.append('</svg>')
    text = "\n".join(out)
    (ROOT / filename).write_text(text, encoding="utf-8")
    return text


# Power layer: clean shared buses on V/W and protected 5 V on C.
o = svg_start("BU-22 Brain - Power layer", "5 V, 3.3 V, ground, D1 isolation, and module/header power")
base_components(o, {"audio","feather","rtc","power","buttons","heartbeat","antenna","sensor"})
gnd, v33, v5 = "#20252d", "#c18b00", "#e55b00"
path(o, [(3,22),(55,22)], gnd, 4); label(o, 28,22,"GND BUS",gnd,"middle")
path(o, [(15,21),(51,21)], v33, 4); label(o, 34,21,"3.3 V BUS",v33,"middle")
path(o, [(3,2),(51,2)], v5, 4); label(o, 28,2,"PROTECTED LOGIC 5 V",v5,"middle")
# Bridge full-width isolation cuts on buses.
for c,r,color in [(14,22,gnd),(27,22,gnd),(27,21,v33),(14,2,v5),(27,2,v5)]:
    path(o, [(c-1,r-1),(c+1,r-1)], color, 2)
# External power through D1 to 5 V bus.
path(o, [(54,3),(53,3)], v5); path(o, [(51,3),(51,2)], v5)
x1,y1=pt(53,3); x2,_=pt(51,3)
o.append(f'<polygon points="{x1},{y1-6} {x2+5},{y1} {x1},{y1+6}" fill="{v5}"/><line x1="{x2+4}" y1="{y1-8}" x2="{x2+4}" y2="{y1+8}" stroke="#172033" stroke-width="2"/><text x="{(x1+x2)/2}" y="{y1-10}" text-anchor="middle" class="m b" font-size="8">D1</text>')
# 5 V drops.
for p in [(12,20),(25,14)]: path(o,[p,(p[0],2)],v5)
# 3.3 V drops.
for p in [(17,18),(31,4),(50,13)]: path(o,[p,(p[0],21)],v33)
# Ground drops.
for p in [(4,7),(12,19),(17,17),(31,5),(38,13),(42,14),(46,16),(50,14),(54,4)]: path(o,[p,(p[0],22)],gnd)
power_svg = finish(o,"brain-layer-power.svg","Orange 5 V | Gold 3.3 V | Black ground")

# Buttons.
o = svg_start("BU-22 Brain - Buttons layer", "Seven active-low button inputs; daughterboard supplies one shared ground")
base_components(o,{"feather","buttons"})
green="#248a3d"
targets=[(17,5),(25,7),(25,8),(25,9),(25,10),(25,11),(25,12)]
for idx,(src_row,target) in enumerate(zip(range(14,21),targets),1):
    lane=36-idx
    path(o,[(38,src_row),(lane,src_row),(lane,target[1]),target],green)
    label(o,38,src_row,f"B{idx}",green,"end")
path(o,[(38,13),(38,22),(17,22),(17,17)],"#20252d")
buttons_svg=finish(o,"brain-layer-buttons.svg","Green: button signals | Black: shared ground")

# Audio FX control/UART.
o = svg_start("BU-22 Brain - Audio FX control layer", "UART control, activity feedback, reset, and the UART-mode strap")
base_components(o,{"audio","feather"})
purple="#7138b7"; blue="#1769aa"; red="#c53b3b"; gray="#29313d"
path(o,[(12,16),(17,7)],purple); label(o,12,16,"TX",purple,"end"); label(o,17,7,"RX",purple)
path(o,[(12,15),(17,6)],blue); label(o,12,15,"RX",blue,"end"); label(o,17,6,"TX",blue)
path(o,[(4,8),(17,12)],red); label(o,4,8,"ACT",red,"end"); label(o,17,12,"D24",red)
path(o,[(4,20),(17,11)],"#d46a1f"); label(o,4,20,"RST","#d46a1f","end"); label(o,17,11,"D25","#d46a1f")
path(o,[(12,14),(12,19)],gray); label(o,12,14,"UG",gray,"end"); label(o,12,19,"GND",gray,"end")
audio_svg=finish(o,"brain-layer-audio-control.svg","Purple/blue: UART | Red: ACT | Orange: reset | Black: UG strap")

# RTC and heartbeat.
o = svg_start("BU-22 Brain - RTC and heartbeat layer", "I2C plus DS3231 SQW heartbeat fan-out and optional 10 kOhm pull-up")
base_components(o,{"feather","rtc","heartbeat"})
blue="#087ca7"; red="#c92d39"; gold="#c18b00"; black="#20252d"
path(o,[(31,6),(28,6),(28,6),(25,6)],blue); label(o,31,6,"SCL",blue)
path(o,[(31,7),(29,7),(29,5),(25,5)],"#1e9bb8"); label(o,31,7,"SDA","#1e9bb8")
path(o,[(31,10),(34,10),(34,13),(42,13)],red); path(o,[(31,10),(27,10),(27,13),(25,13)],red)
label(o,31,10,"SQW",red)
path(o,[(31,4),(31,21),(17,21),(17,18)],gold)
path(o,[(31,5),(31,22),(17,22),(17,17)],black)
# Pull-up resistor below RTC.
path(o,[(31,10),(33,13)],red); path(o,[(33,17),(33,21)],gold)
x,y1=pt(33,13); _,y2=pt(33,17)
o.append(f'<rect x="{x-5}" y="{y1+8}" width="10" height="{y2-y1-16}" fill="#f4dda0" stroke="#574200"/><text x="{x+8}" y="{(y1+y2)/2}" class="m b" font-size="8">10k</text>')
rtc_svg=finish(o,"brain-layer-rtc-heartbeat.svg","Blue: I2C | Red: heartbeat | Gold/black: RTC power")

# Antenna and sensor.
o = svg_start("BU-22 Brain - Antenna and sensor layer", "Three antenna outputs plus powered sensor input and optional second signal")
base_components(o,{"feather","antenna","sensor"})
mag="#bf2b87"; teal="#008b8b"; gold="#c18b00"; black="#20252d"
for src,target,name in [((46,13),(17,16),"R"),((46,14),(17,15),"G"),((46,15),(17,14),"B")]:
    path(o,[src,(43,src[1]),(43,target[1]),target],mag); label(o,*src,name,mag,"end")
path(o,[(46,16),(46,22),(17,22),(17,17)],black)
path(o,[(50,13),(50,21),(17,21),(17,18)],gold); label(o,50,13,"3V3",gold,"end")
path(o,[(50,14),(50,22)],black); label(o,50,14,"GND",black,"end")
path(o,[(50,15),(45,15),(45,13),(17,13)],teal); label(o,50,15,"SIG",teal,"end")
path(o,[(50,16),(47,16),(47,8),(17,8)],teal,dash="5 4"); label(o,50,16,"OPT",teal,"end")
ant_svg=finish(o,"brain-layer-antenna-sensor.svg","Magenta: antenna | Teal: sensor | Gold/black: power")

# Inline four-panel visualization fragment, embedding the exact SVGs.
panels = [
    ("Power", power_svg),
    ("Audio FX", audio_svg),
    ("Buttons", buttons_svg),
    ("RTC + Heartbeat", rtc_svg),
    ("Antenna + Sensor", ant_svg),
]
html=[]
html.append('<div id="bu22-layer-viewer"><style>#bu22-layer-viewer{font-family:ui-sans-serif,system-ui;color:var(--foreground)}#bu22-layer-viewer .tabs{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 10px}#bu22-layer-viewer button{border:1px solid var(--border);background:transparent;color:var(--foreground);padding:7px 10px;border-radius:6px;cursor:pointer}#bu22-layer-viewer button[aria-pressed="true"]{background:var(--accent);color:var(--accent-foreground)}#bu22-layer-viewer .panel{display:none}#bu22-layer-viewer .panel.on{display:block}#bu22-layer-viewer img{display:block;width:100%;height:auto;border:1px solid var(--border);border-radius:6px}</style><div class="tabs" role="tablist">')
for i,(name,_) in enumerate(panels):
    html.append(f'<button type="button" data-i="{i}" aria-pressed="{"true" if i==0 else "false"}">{name}</button>')
html.append('</div>')
for i,(name,svg) in enumerate(panels):
    data=base64.b64encode(svg.encode()).decode()
    html.append(f'<div class="panel {"on" if i==0 else ""}" data-panel="{i}"><img alt="BU-22 Brain {name} stripboard wiring layer" src="data:image/svg+xml;base64,{data}"></div>')
html.append('<script>(()=>{const r=document.getElementById("bu22-layer-viewer");const b=[...r.querySelectorAll("button[data-i]")];const p=[...r.querySelectorAll("[data-panel]")];b.forEach(x=>x.addEventListener("click",()=>{b.forEach(y=>y.setAttribute("aria-pressed",String(y===x)));p.forEach(y=>y.classList.toggle("on",y.dataset.panel===x.dataset.i));}));})();</script></div>')
viz=Path('/Users/brett/.codex/visualizations/2026/07/28/019fa94d-231c-7c71-865f-3dba7354d487/bu22-brain-wiring-layers.html')
viz.write_text('\n'.join(html),encoding='utf-8')
