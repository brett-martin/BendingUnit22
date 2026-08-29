"""Finalize Rev D as a four-layer signal/plane/signal board."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"


def mm(value): return pcbnew.FromMM(value)
def point(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))


def endpoints(item):
    start, end = item.GetStart(), item.GetEnd()
    return {
        (round(pcbnew.ToMM(start.x), 3), round(pcbnew.ToMM(start.y), 3)),
        (round(pcbnew.ToMM(end.x), 3), round(pcbnew.ToMM(end.y), 3)),
    }


def add_track(board, net, start, end, layer, width=0.5):
    item = pcbnew.PCB_TRACK(board)
    item.SetNet(net); item.SetLayer(layer); item.SetWidth(mm(width))
    item.SetStart(point(*start)); item.SetEnd(point(*end)); board.Add(item)


def add_via(board, net, location, diameter=0.8, drill=0.4):
    item = pcbnew.PCB_VIA(board)
    item.SetNet(net); item.SetPosition(point(*location))
    item.SetWidth(mm(diameter)); item.SetDrill(mm(drill))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); board.Add(item)


def main():
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    board.SetCopperLayerCount(4)
    logic = board.FindNet("LOGIC_5V")
    ground = board.FindNet("GND")
    heart = board.FindNet("HEART_LED_A")
    original_zones = list(board.Zones())
    template = original_zones[0]
    ground_plane = pcbnew.ZONE.Cast(template.Duplicate(False))
    logic_plane = pcbnew.ZONE.Cast(template.Duplicate(False))

    bad_ground = [
        {(117.0, 36.0), (110.54, 36.0)},
        {(121.0, 32.0), (117.0, 36.0)},
        {(33.0, 36.0), (33.0, 46.96)},
        {(33.0, 46.96), (31.0, 47.5)},
        {(31.791, 33.65), (34.441, 31.0)},
        {(34.441, 31.0), (49.0, 31.0)},
    ]
    for item in list(board.GetTracks()):
        if item.GetNetname() in {"LOGIC_5V", "HEART_LED_A"}:
            board.Remove(item)
        elif item.GetNetname() == "GND" and endpoints(item) in bad_ground:
            board.Remove(item)

    # Each front-side SMD consumer gets a short local route to the internal
    # LOGIC_5V plane. Through-hole D3, C4 and MCU1A connect to it directly.
    local_logic = [
        ((24.975, 18.69), (26.5, 18.69)),
        ((21.55, 28.5), (19.5, 29.5)),
        ((62.975, 18.69), (64.5, 18.69)),
        ((59.55, 28.5), (57.8, 27.8)),
        ((100.975, 18.69), (103.0, 18.69)),
        ((97.55, 28.5), (97.55, 31.05)),
        ((38.0, 28.9125), (38.0, 30.25)),
    ]
    for start, end in local_logic:
        add_track(board, logic, start, end, pcbnew.F_Cu)
        add_via(board, logic, end)

    # Correct the two local ground approaches identified by the audit.
    add_track(board, ground, (121.0, 32.0), (121.0, 37.0), pcbnew.B_Cu, 0.8)
    add_track(board, ground, (33.0, 36.0), (30.5, 38.5), pcbnew.B_Cu, 0.4)
    add_track(board, ground, (30.5, 38.5), (30.5, 47.0), pcbnew.B_Cu, 0.4)
    add_track(board, ground, (30.5, 47.0), (31.0, 47.5), pcbnew.B_Cu, 0.4)

    # Route the heartbeat LED anode around R20 rather than through its input.
    add_track(board, heart, (35.0, 41.0875), (32.5, 41.0875), pcbnew.F_Cu, 0.3)
    add_track(board, heart, (32.5, 41.0875), (32.5, 46.5), pcbnew.F_Cu, 0.3)
    add_track(board, heart, (32.5, 46.5), (33.54, 47.5), pcbnew.F_Cu, 0.3)

    # Clone the existing board-outline zone for the two internal planes.
    ground_plane.SetLayer(pcbnew.In1_Cu)
    ground_plane.SetNetCode(ground.GetNetCode())
    ground_plane.UnFill()
    board.Add(ground_plane)

    logic_plane.SetLayer(pcbnew.In2_Cu)
    logic_plane.SetNetCode(logic.GetNetCode())
    logic_plane.UnFill()
    board.Add(logic_plane)

    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Converted to four layers: {BOARD_PATH}")


if __name__ == "__main__":
    main()
