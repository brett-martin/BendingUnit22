from pathlib import Path
import sys
import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_display_controller_rev_b_layout as rev_b

root = Path(__file__).resolve().parents[1]
path = root / "display-controller-rev-c" / "BU-22-Display-Controller-Rev-C.kicad_pcb"
board = pcbnew.LoadBoard(str(path))
parts = {}
fps = pcbnew.FOOTPRINTS(board.GetFootprints())
while not fps.empty():
    fp = pcbnew.FOOTPRINT(fps.front()); fps.pop_front()
    parts[fp.GetReference()] = fp
nets = {str(name): item for name, item in board.GetNetsByName().items()}
remaining = {"CH3_DATA_3V3", "CH4_CLOCK_3V3", "CH5_CLOCK_3V3",
             "OE_N", "CH2_CLOCK_5V"}
rev_b.autoroute_signals(board, parts, nets, remaining)
pcbnew.ZONE_FILLER(board).Fill(board.Zones())
pcbnew.SaveBoard(str(path), board)
