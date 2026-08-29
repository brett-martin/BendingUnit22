"""Generate a mechanical-only BU-22 eye motherboard quote PCB.

This is intentionally not the electrical eye motherboard.  It exists only to
obtain a fabrication price for the visor-sized carrier before tile sockets,
power distribution, or signal routing are designed.
"""

from pathlib import Path
import math

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "eye-motherboard-quote"
OUTPUT = OUT_DIR / "BU-22-Eye-Motherboard-Quote.kicad_pcb"
FP_ROOT = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")

WIDTH = 174.0
HEIGHT = 83.0
RADIUS = 30.0


def mm(value):
    return pcbnew.FromMM(value)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def text(board, value, x, y, size=1.5, layer=pcbnew.F_SilkS):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(value)
    item.SetPosition(pt(x, y))
    item.SetLayer(layer)
    item.SetTextSize(pt(size, size))
    item.SetTextThickness(mm(max(0.15, size * 0.15)))
    item.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    item.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    if layer in (pcbnew.B_SilkS, pcbnew.B_Cu):
        item.SetMirrored(True)
    board.Add(item)


def rounded_outline(board):
    """Draw a smooth segmented R30 rounded rectangle on Edge.Cuts."""
    points = []
    corners = (
        (WIDTH - RADIUS, RADIUS, -90, 0),
        (WIDTH - RADIUS, HEIGHT - RADIUS, 0, 90),
        (RADIUS, HEIGHT - RADIUS, 90, 180),
        (RADIUS, RADIUS, 180, 270),
    )
    # Thirty-two chords per quarter produces sub-0.04 mm radial deviation.
    for cx, cy, start_deg, end_deg in corners:
        for step in range(33):
            angle = math.radians(start_deg + (end_deg - start_deg) * step / 32)
            points.append((cx + RADIUS * math.cos(angle),
                           cy + RADIUS * math.sin(angle)))
    points.append(points[0])
    for start, end in zip(points, points[1:]):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetStart(pt(*start))
        edge.SetEnd(pt(*end))
        edge.SetWidth(mm(0.1))
        board.Add(edge)


def mounting_hole(board, ref, x, y):
    fp = pcbnew.FootprintLoad(
        str(FP_ROOT / "MountingHole.pretty"), "MountingHole_3.2mm_M3"
    )
    if fp is None:
        raise RuntimeError("Mounting-hole footprint unavailable")
    fp.SetReference(ref)
    fp.SetValue("M3 NPTH")
    fp.SetPosition(pt(x, y))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    board.Add(fp)


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    board = pcbnew.BOARD()
    board.GetDesignSettings().SetCopperLayerCount(2)
    board.GetDesignSettings().m_MinClearance = mm(0.20)
    board.GetDesignSettings().m_MinThroughDrill = mm(0.30)
    rounded_outline(board)

    # The 4 mm top/bottom lip hides these holes from the visible opening.  The
    # X positions remain on the long straight sections of the rounded outline.
    for ref, x, y in (
        ("H1", 42.0, 4.0),
        ("H2", 132.0, 4.0),
        ("H3", 42.0, HEIGHT - 4.0),
        ("H4", 132.0, HEIGHT - 4.0),
    ):
        mounting_hole(board, ref, x, y)

    text(board, "BU-22 EYE MOTHERBOARD — QUOTE ONLY", WIDTH / 2, 39.5, 2.0)
    text(board, "174 x 83 mm  •  R30  •  VERIFY AGAINST VISOR", WIDTH / 2,
         43.5, 1.25)

    # Small covered copper identifiers ensure both copper Gerbers are
    # recognized as intentional layers.  They are not functional circuitry.
    text(board, "QUOTE ONLY", WIDTH / 2, HEIGHT / 2, 1.0, pcbnew.F_Cu)
    text(board, "QUOTE ONLY", WIDTH / 2, HEIGHT / 2, 1.0, pcbnew.B_Cu)

    pcbnew.SaveBoard(str(OUTPUT), board)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    build()
