"""Refill all Rev D copper zones in a fresh pcbnew process."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"

board = pcbnew.LoadBoard(str(BOARD_PATH))
zones = list(board.Zones())
for zone in zones:
    zone.UnFill()
pcbnew.ZONE_FILLER(board).Fill(zones)
pcbnew.SaveBoard(str(BOARD_PATH), board)
print(f"Refilled {len(zones)} Rev D zones")
