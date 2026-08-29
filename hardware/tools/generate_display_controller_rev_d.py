"""Generate a clean two-layer BU-22 Display Controller Rev D placement.

Rev D preserves Rev C's proven mechanics and power isolation, but discards all
inherited routing, moves the channel components onto an even grid, and assigns
the flexible KB2040 display GPIOs monotonically from left to right.
"""

from pathlib import Path
import sys

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "display-controller-rev-c" / "BU-22-Display-Controller-Rev-C.kicad_pcb"
OUT_DIR = ROOT / "display-controller-rev-d"
OUTPUT = OUT_DIR / "BU-22-Display-Controller-Rev-D.kicad_pcb"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_display_controller_rev_b_layout as helpers


def footprints(board):
    return {fp.GetReference(): fp for fp in board.GetFootprints()}


def clear_copper(board):
    for item in list(board.Tracks()):
        board.Remove(item)
    for zone in list(board.Zones()):
        board.Remove(zone)


def set_net(fp, pad_number, net):
    matches = [pad for pad in fp.Pads() if pad.GetNumber() == str(pad_number)]
    if not matches:
        raise RuntimeError(f"Missing pad {fp.GetReference()}.{pad_number}")
    for pad in matches:
        pad.SetNetCode(net.GetNetCode())


def disconnect(fp, pad_number):
    matches = [pad for pad in fp.Pads() if pad.GetNumber() == str(pad_number)]
    if not matches:
        raise RuntimeError(f"Missing pad {fp.GetReference()}.{pad_number}")
    for pad in matches:
        pad.SetNetCode(0)


def build():
    if not SOURCE.exists():
        raise RuntimeError(f"Missing Rev C source: {SOURCE}")

    board = pcbnew.LoadBoard(str(SOURCE))
    board.SetCopperLayerCount(2)
    parts = footprints(board)
    nets = {str(name): net for name, net in board.GetNetsByName().items()}
    # Update visible revision text before copper removal; querying fresh SWIG
    # board collections after mass deletion is unreliable in KiCad 10.
    revision_found = False
    for drawing in list(board.Drawings()):
        if not isinstance(drawing, pcbnew.PCB_TEXT):
            continue
        text = drawing.GetText().strip().upper().replace(" ", "")
        if text in {"REVB", "REVC"}:
            if revision_found:
                board.Remove(drawing)
            else:
                drawing.SetText("REV D")
                revision_found = True
        elif text == "REVD":
            if revision_found:
                board.Remove(drawing)
            else:
                revision_found = True
    # Enforce the Rev C power-domain split explicitly. The inherited board had
    # D3 on the new nets while several loads still retained the legacy +5V net.
    # SYSTEM_5V is the high-current display rail; LOGIC_5V is diode-isolated.
    system_pads = [("J7", 1), ("C5", 1), ("R19", 1)]
    system_pads += [(f"J{channel}", 4) for channel in range(1, 7)]
    logic_pads = [("MCU1A", 12), ("C4", 1), ("R13", 1)]
    logic_pads += [(f"C{index}", 1) for index in range(1, 4)]
    logic_pads += [(f"U{index}", 14) for index in range(1, 4)]
    for ref, pad_number in system_pads:
        set_net(parts[ref], pad_number, nets["SYSTEM_5V"])
    for ref, pad_number in logic_pads:
        set_net(parts[ref], pad_number, nets["LOGIC_5V"])
    set_net(parts["D3"], 1, nets["LOGIC_5V"])
    set_net(parts["D3"], 2, nets["SYSTEM_5V"])

    # Equal 18.2 mm channel pitch. Resistors remain directly below the
    # corresponding connector pins, with DATA on the right and CLOCK left.
    channel_x = (13.0, 31.2, 49.4, 67.6, 85.8, 104.0)
    for channel, x in enumerate(channel_x, 1):
        helpers.move(board, f"J{channel}", x, 7.0, 0)
        helpers.move(board, f"R{channel*2-1}", x + 5.0, 14.0, 90)
        helpers.move(board, f"R{channel*2}", x + 2.5, 14.0, 90)

    # Each buffer sits beneath the midpoint of its connector pair. Local
    # bypass capacitors are immediately below pin 14/pin 7 supply territory.
    pair_centers = ((13.0 + 31.2) / 2, (49.4 + 67.6) / 2, (85.8 + 104.0) / 2)
    for index, x in enumerate(pair_centers, 1):
        helpers.move(board, f"U{index}", x, 22.5, 0)
        helpers.move(board, f"C{index}", x, 28.5, 0)

    # Preserve USB access and the established lower-center KB2040 footprint.
    helpers.move(board, "MCU1A", 55.0, 50.5, 90)
    helpers.move(board, "MCU1B", 85.48, 35.26, 270)

    # Monotonic physical mapping. U1 uses the four leftmost signal pads,
    # U2 the next four, and U3 retains the four GPIOs on the opposite row.
    optimized_bottom = {
        13: "CH1_DATA_3V3",
        12: "CH1_CLOCK_3V3",
        11: "CH2_DATA_3V3",
        10: "CH2_CLOCK_3V3",
        9: "CH3_DATA_3V3",
        8: "CH3_CLOCK_3V3",
        7: "CH4_DATA_3V3",
        6: "CH4_CLOCK_3V3",
    }
    for pad_number, net_name in optimized_bottom.items():
        set_net(parts["MCU1B"], pad_number, nets[net_name])

    # All three I2C pin-2 positions remain deliberately isolated.
    for ref in ("J8", "J9", "J10"):
        disconnect(parts[ref], 2)

    # Remove inherited copper only after every footprint and pad edit. KiCad
    # 10's SWIG wrappers can become stale after mass deletion.
    clear_copper(board)

    # Two-layer strategy: bottom will become the reference plane after signal
    # routing. SYSTEM_5V will be a wide top-layer trunk along the channel edge.

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(OUTPUT), board)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    build()
