"""Generate BU-22 Display Controller Rev C.

Rev C adds explicit USB/external-power isolation and evenly spaces the six
display-channel connectors.  SYSTEM_5V powers only the external display rail;
LOGIC_5V powers the KB2040 and AHCT buffers through a 1N5817 Schottky diode.
"""

from pathlib import Path
import sys

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_display_controller_rev_b_layout as rev_b


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "display-controller-rev-c"
OUTPUT = OUT_DIR / "BU-22-Display-Controller-Rev-C.kicad_pcb"


def build():
    # Generate Rev B as the stable baseline, then transform its fully routed
    # board. Moving channel footprints requires a fresh route, so tracks/zones
    # are intentionally removed and recreated below.
    source = ROOT / "display-controller-rev-b" / "BU-22-Display-Controller-Rev-B.kicad_pcb"
    if not source.exists():
        raise RuntimeError("Rev B baseline board is missing")
    board = pcbnew.LoadBoard(str(source))

    # Retain the validated Rev B routing as a starting point. Connector moves
    # and the split power net are repaired in the subsequent routing pass.
    for zone in list(board.Zones()):
        board.Remove(zone)

    parts = {}
    fps = pcbnew.FOOTPRINTS(board.GetFootprints())
    while not fps.empty():
        fp = pcbnew.FOOTPRINT(fps.front())
        fps.pop_front()
        parts[fp.GetReference()] = fp
    channel_x = (13.0, 31.2, 49.4, 67.6, 85.8, 104.0)
    for index, x in enumerate(channel_x, 1):
        rev_b.move(board, f"J{index}", x, 7.0)
        rev_b.move(board, f"R{index * 2 - 1}", x + 5.0, 14.0, 90)
        rev_b.move(board, f"R{index * 2}", x + 2.5, 14.0, 90)

    # Add the DO-15 Schottky between the external/system rail and the isolated
    # logic rail. KiCad diode pad 1 is K (striped cathode), pad 2 is A.
    parts["D3"] = rev_b.footprint(
        board, "Diode_THT", "D_DO-15_P10.16mm_Horizontal",
        "D3", "1N5817 LOGIC ISOLATION", 108.0, 23.0, 0,
    )
    parts["D3"].Reference().SetVisible(False)
    parts["D3"].Value().SetVisible(False)

    nets = {str(name): item for name, item in board.GetNetsByName().items()}
    nets["SYSTEM_5V"] = rev_b.net(board, "SYSTEM_5V")
    nets["LOGIC_5V"] = rev_b.net(board, "LOGIC_5V")

    # Reassign every former +5V pad according to its load domain.
    system_refs = {"J7", "C5", "R19"} | {f"J{i}" for i in range(1, 7)}
    logic_refs = {"MCU1A", "C1", "C2", "C3", "C4", "R13"} | {f"U{i}" for i in range(1, 4)}
    for ref in system_refs | logic_refs:
        for pad in rev_b.pads(parts[ref]):
            if pad.GetNetname() == "+5V":
                pad.SetNet(nets["SYSTEM_5V"] if ref in system_refs else nets["LOGIC_5V"])
    rev_b.connect(parts, nets, "D3", 1, "LOGIC_5V")
    rev_b.connect(parts, nets, "D3", 2, "SYSTEM_5V")

    # All I2C headers intentionally omit the Qwiic 3.3V rail. The Brain may
    # present 3.3V on pin 2, but the display controller must not receive or
    # forward it. Only GND, SDA, and SCL are used.
    for ref in ("J8", "J9", "J10"):
        parts[ref].FindPadByNumber("2").SetNetCode(0)

    rev_b.copper_plane(board, nets["GND"], pcbnew.In1_Cu, width=125, height=55)
    rev_b.copper_plane(board, nets["SYSTEM_5V"], pcbnew.In2_Cu, width=125, height=55)

    # Route all non-plane nets afresh after connector movement and rail split.
    route_names = {name for name in nets if name not in {"", "GND", "SYSTEM_5V", "+5V"}}
    # Save the clean, netted placement first. Routing is performed as a
    # separate FreeRouting pass; the in-process maze router is not stable for
    # this full-board 4-layer reroute.

    # Rev C identification and diode assembly marking.
    rev_b.text(board, "D3 1N5817", 108.0, 20.0, 0.8)
    rev_b.text(board, "A", 102.8, 23.0, 0.8)
    rev_b.text(board, "K", 113.2, 23.0, 0.8)
    rev_b.text(board, "REV C", 99.0, 54.0, 0.8)

    # Clear inherited Rev B copper only after all net/placement edits. Using
    # KiCad's typed collection avoids dangling SWIG wrappers.
    tracks = pcbnew.TRACKS(board.GetTracks())
    while not tracks.empty():
        item = pcbnew.PCB_TRACK(tracks.front())
        tracks.pop_front()
        board.Remove(item)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(OUTPUT), board)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    build()
