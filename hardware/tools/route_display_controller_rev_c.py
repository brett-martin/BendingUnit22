from pathlib import Path
import pcbnew

root = Path(__file__).resolve().parents[1]
board_path = root / "display-controller-rev-c" / "BU-22-Display-Controller-Rev-C.kicad_pcb"
dsn_path = Path("/tmp/BU-22-Display-Controller-Rev-C.dsn")
board = pcbnew.LoadBoard(str(board_path))
ses_path = Path("/tmp/BU-22-Display-Controller-Rev-C.ses")
if ses_path.exists():
    pcbnew.ImportSpecctraSES(board, str(ses_path))
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(str(board_path), board)
    print(f"Imported {ses_path}")
else:
    pcbnew.ExportSpecctraDSN(board, str(dsn_path))
    print(dsn_path)
