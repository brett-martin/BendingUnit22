"""Remove known Rev D copper conflicts found by the geometry audit."""

from pathlib import Path
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"


def mm(v): return pcbnew.FromMM(v)
def point(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))


def coords(item):
    a, b = item.GetStart(), item.GetEnd()
    return tuple(round(pcbnew.ToMM(v), 4) for v in (a.x, a.y, b.x, b.y))


def endpoints(item):
    x1, y1, x2, y2 = coords(item)
    return {(x1, y1), (x2, y2)}


def add_track(board, net, a, b, layer, width):
    item = pcbnew.PCB_TRACK(board)
    item.SetNet(net); item.SetLayer(layer); item.SetWidth(mm(width))
    item.SetStart(point(*a)); item.SetEnd(point(*b)); board.Add(item)


def add_via(board, net, x, y, diameter=0.8, drill=0.4):
    item = pcbnew.PCB_VIA(board)
    item.SetNet(net); item.SetPosition(point(x, y))
    item.SetWidth(mm(diameter)); item.SetDrill(mm(drill))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); board.Add(item)


def main():
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    logic = board.FindNet("LOGIC_5V")
    ground = board.FindNet("GND")
    heart = board.FindNet("HEART_LED_A")
    original = list(board.GetTracks())

    remove_logic = [
        {(100.975, 18.69), (96.3583, 14.0733)},
        {(96.3583, 14.0733), (67.5917, 14.0733)},
        {(67.5917, 14.0733), (62.975, 18.69)},
        {(55.5966, 32.4534), (42.1915, 32.4534)},
        {(38.0, 28.9125), (42.19, 32.45)},
        {(42.19, 32.45), (43.0, 32.4534)},
        {(42.19, 32.45), (42.1915, 32.4534)},
    ]
    remove_ground = [
        {(117.0, 36.0), (110.54, 36.0)},
        {(121.0, 32.0), (117.0, 36.0)},
        {(33.0, 36.0), (33.0, 46.96)},
        {(33.0, 46.96), (31.0, 47.5)},
        {(31.791, 33.65), (34.441, 31.0)},
        {(34.441, 31.0), (49.0, 31.0)},
    ]

    for item in original:
        ep = endpoints(item)
        if item.GetNetname() == "LOGIC_5V" and ep in remove_logic:
            board.Remove(item)
        elif item.GetNetname() == "GND" and ep in remove_ground:
            board.Remove(item)
        elif item.GetNetname() == "HEART_LED_A":
            board.Remove(item)

    # Heartbeat anode exits R20 to the left, avoiding its heartbeat-side pad.
    add_track(board, heart, (35.0, 41.0875), (32.5, 41.0875), pcbnew.F_Cu, 0.3)
    add_track(board, heart, (32.5, 41.0875), (32.5, 46.5), pcbnew.F_Cu, 0.3)
    add_track(board, heart, (32.5, 46.5), (33.54, 47.5), pcbnew.F_Cu, 0.3)

    # Replace the congested top-layer logic rail with a bottom-layer backbone.
    add_via(board, logic, 55.5966, 32.4534)
    add_track(board, logic, (42.19, 32.45), (42.19, 34.5), pcbnew.B_Cu, 0.5)
    add_track(board, logic, (42.19, 34.5), (55.5966, 34.5), pcbnew.B_Cu, 0.5)
    add_track(board, logic, (55.5966, 34.5), (55.5966, 32.4534), pcbnew.B_Cu, 0.5)

    # R13 joins the same supply through its own local via.
    add_via(board, logic, 38.0, 30.0)
    add_track(board, logic, (38.0, 28.9125), (38.0, 30.0), pcbnew.F_Cu, 0.5)
    add_track(board, logic, (38.0, 30.0), (42.19, 32.45), pcbnew.B_Cu, 0.5)

    # U2/C2 to U3/C3 continuation, entirely below the resistor field.
    add_track(board, logic, (57.794, 27.7814), (61.0, 30.5), pcbnew.B_Cu, 0.5)
    add_track(board, logic, (61.0, 30.5), (94.5, 30.5), pcbnew.B_Cu, 0.5)
    add_track(board, logic, (94.5, 30.5), (97.55, 31.05), pcbnew.B_Cu, 0.5)

    # Ground branches now approach the relevant cathode/pad from clear sides.
    add_track(board, ground, (121.0, 32.0), (121.0, 37.0), pcbnew.B_Cu, 0.8)
    add_track(board, ground, (33.0, 36.0), (30.5, 38.5), pcbnew.B_Cu, 0.4)
    add_track(board, ground, (30.5, 38.5), (30.5, 47.0), pcbnew.B_Cu, 0.4)
    add_track(board, ground, (30.5, 47.0), (31.0, 47.5), pcbnew.B_Cu, 0.4)

    for zone in board.Zones(): zone.UnFill()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Cleared known copper conflicts in {BOARD_PATH}")


if __name__ == "__main__": main()
