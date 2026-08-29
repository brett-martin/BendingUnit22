"""Apply power and reference-plane cleanup to the routed Rev D board."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"


def mm(value):
    return pcbnew.FromMM(value)


def main():
    board = pcbnew.LoadBoard(str(BOARD_PATH))

    # Keep exactly one current revision marking. Rev D inherits Rev B/C
    # silkscreen from the mechanical source board before it is rerouted.
    revision_found = False
    for drawing in list(board.Drawings()):
        if not isinstance(drawing, pcbnew.PCB_TEXT):
            continue
        text = drawing.GetText().strip().upper().replace(" ", "")
        if text in {"REVB", "REVC", "REVD"}:
            if revision_found:
                board.Remove(drawing)
            else:
                drawing.SetText("REV D")
                revision_found = True

    # The autorouter intentionally used a conservative uniform width. Increase
    # the two supply domains after routing, while leaving logic at 0.20 mm.
    for item in list(board.Tracks()):
        if isinstance(item, pcbnew.PCB_VIA):
            continue
        if item.GetNetname() == "SYSTEM_5V":
            item.SetWidth(mm(1.00))
        elif item.GetNetname() == "LOGIC_5V":
            item.SetWidth(mm(0.50))

    # Full-board bottom reference plane, inset from the routed outline. Routed
    # GND traces remain as deterministic connections if the pour is locally
    # split by signal traces.
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(board.FindNet("GND"))
    zone.SetLocalClearance(mm(0.25))
    polygon = zone.Outline()
    polygon.NewOutline()
    for x, y in ((0.6, 0.6), (124.4, 0.6), (124.4, 54.4), (0.6, 54.4)):
        polygon.Append(mm(x), mm(y))
    board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Finished {BOARD_PATH}")


if __name__ == "__main__":
    main()
