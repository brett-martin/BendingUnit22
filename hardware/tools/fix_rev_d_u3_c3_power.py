"""Complete U3/C3 local power routing and rebuild the ground pour."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"


def mm(value):
    return pcbnew.FromMM(value)


def point(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def add_track(board, net, start, end, layer, width):
    item = pcbnew.PCB_TRACK(board)
    item.SetNet(net)
    item.SetLayer(layer)
    item.SetWidth(mm(width))
    item.SetStart(point(*start))
    item.SetEnd(point(*end))
    board.Add(item)


def add_via(board, net, x, y, diameter=0.8, drill=0.4):
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
    ground = board.FindNet("GND")

    # U3 pin 14 -> top via -> bottom-layer path -> top via -> C3 pad 1.
    # The right-side descent avoids the manually adjusted CH6 bottom traces.
    add_track(board, logic, (100.975, 18.69), (103.0, 18.69), pcbnew.F_Cu, 0.5)
    add_via(board, logic, 103.0, 18.69)
    add_track(board, logic, (103.0, 18.69), (103.0, 30.5), pcbnew.B_Cu, 0.5)
    add_track(board, logic, (103.0, 30.5), (97.55, 31.05), pcbnew.B_Cu, 0.5)
    add_via(board, logic, 97.55, 31.05)

    # C3 pad 2's existing top trace ends here; stitch that endpoint directly
    # into the B.Cu ground plane.
    add_via(board, ground, 105.142, 27.358)

    # Close the sub-grid gap between the earlier U1 bottom-layer via and the
    # autorouted main LOGIC_5V endpoint. They visually overlap in KiCad but
    # differ by a few microns and otherwise remain separate copper islands.
    add_track(board, logic, (42.19, 32.45), (42.1915, 32.4534), pcbnew.F_Cu, 0.5)
    # Restore the local pull-up feed removed during the manual trace cleanup.
    add_track(board, logic, (38.0, 28.9125), (42.19, 32.45), pcbnew.F_Cu, 0.5)

    # Force a complete repour after the user's bottom-layer route changes.
    for zone in board.Zones():
        zone.UnFill()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Completed U3/C3 power and repoured ground in {BOARD_PATH}")


if __name__ == "__main__":
    main()
