"""Localized cleanup after the manually adjusted Rev D placement."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"


def mm(value):
    return pcbnew.FromMM(value)


def point(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def coords(item):
    a, b = item.GetStart(), item.GetEnd()
    return (
        round(pcbnew.ToMM(a.x), 4), round(pcbnew.ToMM(a.y), 4),
        round(pcbnew.ToMM(b.x), 4), round(pcbnew.ToMM(b.y), 4),
    )


def track(board, net, start, end, layer, width):
    item = pcbnew.PCB_TRACK(board)
    item.SetNet(net)
    item.SetLayer(layer)
    item.SetWidth(mm(width))
    item.SetStart(point(*start))
    item.SetEnd(point(*end))
    board.Add(item)


def via(board, net, x, y, diameter=0.8, drill=0.4):
    item = pcbnew.PCB_VIA(board)
    item.SetNet(net)
    item.SetPosition(point(x, y))
    item.SetWidth(mm(diameter))
    item.SetDrill(mm(drill))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(item)


def main():
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    logic = board.FindNet("LOGIC_5V")
    system = board.FindNet("SYSTEM_5V")
    ground = board.FindNet("GND")
    original = list(board.GetTracks())

    # Remove the two incomplete C1 logic segments. They stop near, but do not
    # actually touch, the bottom-layer U1 supply via at (24, 29.5).
    for item in original:
        if item.GetNetname() != "LOGIC_5V" or item.GetLayer() != pcbnew.F_Cu:
            continue
        x1, y1, x2, y2 = coords(item)
        ends = {(x1, y1), (x2, y2)}
        if (21.55, 28.5) in ends or (23.05, 30.0) in ends or (24.5, 30.0) in ends:
            board.Remove(item)

    # Clear the winding top-layer ground trace from the immediate C1 area.
    # The replacement returns U1 and C1 independently to the B.Cu plane.
    for item in original:
        if item.GetNetname() != "GND" or item.GetLayer() != pcbnew.F_Cu:
            continue
        x1, y1, x2, y2 = coords(item)
        if (19.5 <= x1 <= 26.0 and 26.0 <= y1 <= 31.0 and
                19.5 <= x2 <= 26.0 and 26.0 <= y2 <= 31.0):
            board.Remove(item)

    # C1 power pad -> nearby via -> existing U1/main bottom-layer branch.
    via(board, logic, 20.5, 30.0)
    track(board, logic, (21.55, 28.5), (20.5, 30.0), pcbnew.F_Cu, 0.5)
    track(board, logic, (20.5, 30.0), (24.0, 29.5), pcbnew.B_Cu, 0.5)

    # Short, unambiguous local ground returns without crossing C1's power pad.
    via(board, ground, 20.025, 27.6)
    track(board, ground, (20.025, 26.31), (20.025, 27.6), pcbnew.F_Cu, 0.4)
    via(board, ground, 23.45, 30.0)
    track(board, ground, (23.45, 28.5), (23.45, 30.0), pcbnew.F_Cu, 0.4)

    # R19 is top-only SMD. Move the layer transition away from the footprint
    # instead of ending a bottom trace directly beneath its pad.
    for item in original:
        if item.GetNetname() != "SYSTEM_5V" or item.GetLayer() != pcbnew.B_Cu:
            continue
        x1, y1, x2, y2 = coords(item)
        if {(x1, y1), (x2, y2)} == {(114.0, 39.0), (114.0, 48.91)}:
            board.Remove(item)
    track(board, system, (114.0, 39.0), (116.0, 46.0), pcbnew.B_Cu, 1.0)
    via(board, system, 116.0, 46.0, diameter=1.2, drill=0.6)
    track(board, system, (116.0, 46.0), (114.0, 48.9125), pcbnew.F_Cu, 1.0)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Cleaned local power routing in {BOARD_PATH}")


if __name__ == "__main__":
    main()
