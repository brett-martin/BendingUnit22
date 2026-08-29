"""Create a temporary Rev D board with only LOGIC_5V unrouted."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"
OUTPUT = Path("/tmp/revd-logic-only.kicad_pcb")


def main():
    board = pcbnew.LoadBoard(str(SOURCE))
    tracks = list(board.GetTracks())
    for item in tracks:
        if item.GetNetname() == "LOGIC_5V":
            board.Remove(item)
    for zone in board.Zones():
        zone.UnFill()
    pcbnew.SaveBoard(str(OUTPUT), board)
    print(OUTPUT)


if __name__ == "__main__":
    main()
