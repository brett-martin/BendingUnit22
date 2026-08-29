"""Clear the final native KiCad DRC warnings on Rev D."""

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


board = pcbnew.LoadBoard(str(BOARD_PATH))
drawings = list(board.GetDrawings())

# These were leftover ground stubs. The internal ground plane now provides the
# connection at the original via, so neither front-layer segment is needed.
for item in list(board.GetTracks()):
    if (item.GetNetname() == "GND" and item.GetLayer() == pcbnew.F_Cu and
            endpoints(item) in (
                {(107.0, 25.5), (110.0, 25.5)},
                {(105.142, 27.358), (107.0, 25.5)},
            )):
        board.Remove(item)

for item in drawings:
    if not hasattr(item, "GetText"):
        continue
    if item.GetText() == "R19":
        item.SetPosition(point(111.0, 45.5))
    elif item.GetText() == "C5 470uF":
        item.SetPosition(point(120.0, 44.0))

pcbnew.SaveBoard(str(BOARD_PATH), board)
print("Cleared final Rev D DRC warnings")
