"""Correct standard KiCad LED pad polarity and reroute both indicators."""

from pathlib import Path
import pcbnew

ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"


def mm(value): return pcbnew.FromMM(value)
def point(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))


def add_track(board, net, a, b, layer, width):
    item = pcbnew.PCB_TRACK(board)
    item.SetNet(net); item.SetLayer(layer); item.SetWidth(mm(width))
    item.SetStart(point(*a)); item.SetEnd(point(*b)); board.Add(item)


def pads(fp):
    return {pad.GetNumber(): pad for pad in fp.Pads()}


def xy(item):
    a, b = item.GetStart(), item.GetEnd()
    return tuple(round(pcbnew.ToMM(v), 3) for v in (a.x, a.y, b.x, b.y))


def main():
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    ground = board.FindNet("GND")
    power_led = board.FindNet("PWR_LED_A")
    heart_led = board.FindNet("HEART_LED_A")

    # LED_THT:LED_D3.0mm uses pad 1 = K and pad 2 = A.
    for ref, driven in (("D1", power_led), ("D2", heart_led)):
        led_pads = pads(board.FindFootprintByReference(ref))
        led_pads["1"].SetNetCode(ground.GetNetCode())
        led_pads["2"].SetNetCode(driven.GetNetCode())

    original = list(board.GetTracks())
    for item in original:
        if item.GetNetname() in {"PWR_LED_A", "HEART_LED_A"}:
            board.Remove(item)
            continue
        if item.GetNetname() == "GND" and item.GetLayer() == pcbnew.B_Cu:
            ends = {(xy(item)[0], xy(item)[1]), (xy(item)[2], xy(item)[3])}
            if (33.54, 47.5) in ends:
                board.Remove(item)

    # R19 pad 2 to D1 anode (pad 2); D1 cathode joins the ground pour.
    add_track(board, power_led, (114.0, 47.0875), (112.0, 45.0875), pcbnew.F_Cu, 0.3)
    add_track(board, power_led, (112.0, 45.0875), (110.54, 43.0), pcbnew.F_Cu, 0.3)

    # R20 pad 2 to D2 anode (pad 2); retain the existing local ground spine,
    # but terminate it at the newly assigned cathode pad 1.
    add_track(board, heart_led, (35.0, 41.0875), (35.0, 46.0), pcbnew.F_Cu, 0.3)
    add_track(board, heart_led, (35.0, 46.0), (33.54, 47.5), pcbnew.F_Cu, 0.3)
    add_track(board, ground, (33.0, 46.96), (31.0, 47.5), pcbnew.B_Cu, 0.4)
    add_track(board, ground, (29.04, 52.0), (31.0, 47.5), pcbnew.B_Cu, 0.4)

    for zone in board.Zones(): zone.UnFill()
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Corrected LED polarity in {BOARD_PATH}")


if __name__ == "__main__": main()
