"""Create the compact BU-22 display-controller Rev B placement study.

Rev B preserves the validated Rev A netlist while deliberately discarding its
routing.  It explores a smaller installed layout using hand-solderable SOIC
and 0805 parts, vertical channel connectors, and a right-facing KB2040 USB
access corridor.
"""

from pathlib import Path
import math
import sys

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_display_controller_v1 import (  # noqa: E402
    FP_ROOT, autoroute_signals, connect, copper_plane, footprint, mm,
    net, outline, pt, silk_line, text, track,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "display-controller-v1" / "BU-22-Display-Controller-V1.kicad_pcb"
OUT_DIR = ROOT / "display-controller-rev-b"
OUTPUT = OUT_DIR / "BU-22-Display-Controller-Rev-B.kicad_pcb"


def mom_heart_logo(board, center_x, center_y, scale=1.0):
    """Open heart-shaped hair interrupted by a circular smiley face."""
    # One continuous open path: it begins beside the left "ear", rises around
    # both hair lobes, and terminates beside the right ear. The face occupies
    # the missing bottom point of the otherwise recognizable heart silhouette.
    hair = (
        (-1.72, 0.62), (-2.28, 0.12), (-2.72, -0.62),
        (-2.88, -1.42), (-2.72, -2.18), (-2.28, -2.76),
        (-1.62, -3.08), (-0.92, -3.04), (-0.40, -2.76),
        (0.0, -2.22),
        (0.40, -2.76), (0.92, -3.04), (1.62, -3.08),
        (2.28, -2.76), (2.72, -2.18), (2.88, -1.42),
        (2.72, -0.62), (2.28, 0.12), (1.72, 0.62),
    )
    points = [(center_x + x * scale, center_y + y * scale) for x, y in hair]
    for start, end in zip(points, points[1:]):
        silk_line(board, start, end, 0.28)

    # The face overlaps the open lower portion of the heart at its sides.
    face_y = center_y + 1.45 * scale
    radius = 1.55 * scale
    circle = []
    for index in range(25):
        angle = math.tau * index / 24
        circle.append((center_x + radius * math.cos(angle),
                       face_y + radius * math.sin(angle)))
    for start, end in zip(circle, circle[1:]):
        silk_line(board, start, end, 0.28)

    # Two round eyes.
    for eye_x in (-0.55, 0.55):
        eye = []
        for index in range(13):
            angle = math.tau * index / 12
            eye.append((center_x + (eye_x + 0.16 * math.cos(angle)) * scale,
                        face_y + (-0.38 + 0.16 * math.sin(angle)) * scale))
        for start, end in zip(eye, eye[1:]):
            silk_line(board, start, end, 0.26)

    # Independent upturned mouth.
    smile = (
        (-0.85, 0.30), (-0.45, 0.65), (0.0, 0.78),
        (0.45, 0.65), (0.85, 0.30),
    )
    points = [(center_x + x * scale, face_y + y * scale) for x, y in smile]
    for start, end in zip(points, points[1:]):
        silk_line(board, start, end, 0.28)


def remove_item(board, item):
    board.Remove(item)


def pads(footprint_item):
    collection = pcbnew.PADS(footprint_item.Pads())
    result = []
    while not collection.empty():
        result.append(pcbnew.PAD(collection.front()))
        collection.pop_front()
    return result


def replace_footprint(board, ref, library, name, x, y, rotation=0,
                      value=None):
    old_raw = board.FindFootprintByReference(ref)
    old = pcbnew.FOOTPRINT(old_raw) if old_raw is not None else None
    if old is None:
        raise RuntimeError(f"Missing source footprint {ref}")
    old_value = old.GetValue()
    pad_nets = {}
    for pad in pads(old):
        if pad.GetNet() is not None:
            pad_nets.setdefault(pad.GetNumber(), pad.GetNet())
    board.Remove(old)
    new = footprint(board, library, name, ref, value or old_value,
                    x, y, rotation)
    for pad in pads(new):
        if pad.GetNumber() in pad_nets:
            pad.SetNet(pad_nets[pad.GetNumber()])
    return new


def move(board, ref, x, y, rotation=0):
    part_raw = board.FindFootprintByReference(ref)
    part = pcbnew.FOOTPRINT(part_raw) if part_raw is not None else None
    if part is None:
        raise RuntimeError(f"Missing footprint {ref}")
    part.SetPosition(pt(x, y))
    part.SetOrientationDegrees(rotation)


def build():
    print("stage: load", flush=True)
    if not SOURCE.exists():
        raise RuntimeError("Generate the Rev A board before creating Rev B")
    board = pcbnew.LoadBoard(str(SOURCE))

    # Placement study only: remove every routed item and copper zone.
    for item in list(board.GetTracks()):
        remove_item(board, item)
    for zone in list(board.Zones()):
        remove_item(board, zone)
    drawings = pcbnew.DRAWINGS(board.Drawings())
    while not drawings.empty():
        drawing = drawings.front()
        drawings.pop_front()
        remove_item(board, drawing)

    outline(board, 125, 55, 3.0)
    print("stage: stripped", flush=True)

    # Six vertical XH outputs form the fixed top datum.
    channel_x = (13, 32, 51, 70, 89, 104)
    for index, x in enumerate(channel_x, 1):
        replace_footprint(
            board, f"J{index}", "Connector_JST",
            "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
            x, 7.0, 0,
        )

    # One SOIC buffer directly serves each adjacent channel pair.
    for ref, x in (("U1", 22.5), ("U2", 60.5), ("U3", 98.5)):
        replace_footprint(
            board, ref, "Package_SO",
            "SOIC-14_3.9x8.7mm_P1.27mm", x, 22.5, 0,
            "74AHCT125D",
        )

    # Series resistors remain in obvious channel pairs, but 0805 packages save
    # the vertical space needed for direct connector-to-buffer fanout.
    for channel, x in enumerate(channel_x, 1):
        replace_footprint(board, f"R{channel * 2 - 1}", "Resistor_SMD",
                          "R_0805_2012Metric", x - 2.2, 14.0, 90)
        replace_footprint(board, f"R{channel * 2}", "Resistor_SMD",
                          "R_0805_2012Metric", x + 2.2, 14.0, 90)

    # Local bypass parts stay beside their ICs. Remaining small resistors use
    # the same readily hand-soldered 0805 package.
    for index, x in enumerate((22.5, 60.5, 98.5), 1):
        replace_footprint(board, f"C{index}", "Capacitor_SMD",
                          "C_0805_2012Metric", x, 28.5, 0)
    small_resistor_positions = {
        "R13": (36, 28), "R14": (40, 28), "R15": (44, 28),
        "R16": (36, 31), "R17": (40, 31), "R18": (44, 31),
        "R19": (112, 34), "R20": (45, 40),
    }
    for ref, (x, y) in small_resistor_positions.items():
        replace_footprint(board, ref, "Resistor_SMD",
                          "R_0805_2012Metric", x, y, 90)

    # KB2040 occupies the lower center. These opposing socket rows represent a
    # 180-degree rotation from Rev A; its USB connector faces right. The open
    # corridor from x=76 to the board edge must remain component-free.
    move(board, "MCU1A", 55.0, 48.5, 90)
    move(board, "MCU1B", 85.48, 33.26, 270)

    # Power lives at upper-right, outside the USB cable corridor.
    move(board, "J7", 119.0, 20.0, 90)
    move(board, "C5", 116.0, 29.0, 0)
    move(board, "C4", 108.0, 28.5, 0)
    move(board, "D1", 115.0, 37.5, 0)

    # Controls and communications occupy the lower-left and lower-middle.
    move(board, "SW2", 9.0, 47.5, 0)
    move(board, "SW1", 20.0, 47.5, 0)
    move(board, "D2", 31.0, 47.5, 0)
    move(board, "JP1", 43.0, 48.0, 0)
    move(board, "Q1", 49.0, 31.0, 0)
    replace_footprint(board, "J11", "Connector_JST",
                      "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
                      38.0, 36.0, 90, "GND HEARTBEAT")
    replace_footprint(board, "J10", "Connector_JST",
                      "JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical",
                      22.0, 38.5, 90, "I2C TEST")
    replace_footprint(board, "J8", "Connector_JST",
                      "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",
                      8.0, 36.0, 90, "I2C TO BRAIN")
    replace_footprint(board, "J9", "Connector_JST",
                      "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",
                      14.0, 36.0, 90, "I2C THRU")

    # Mounting holes retain a 4 mm edge inset.
    for ref, x, y in (("H1", 4, 4), ("H2", 121, 4),
                      ("H3", 4, 51), ("H4", 121, 51)):
        move(board, ref, x, y)

    # Minimal placement-review silk; detailed assembly labeling follows after
    # the mechanical arrangement is approved.
    text(board, "BU-22 DISPLAY CONTROLLER REV B", 62.5, 52.0, 0.8)
    text(board, "USB ACCESS ->", 96.0, 38.0, 0.8)
    text(board, "5V IN", 118.0, 14.0, 0.7)
    for index, x in enumerate(channel_x, 1):
        text(board, f"CH{index}", x, 11.0, 0.8)
    text(board, "TEST", 20.0, 53.0, 0.65)
    text(board, "RESET", 9.0, 53.0, 0.65)
    text(board, "HEART", 31.0, 53.0, 0.65)
    mom_heart_logo(board, 107.0, 35.5, 0.55)
    print("stage: placed", flush=True)

    # Four-layer architecture: uninterrupted ground and +5 V planes inside;
    # all logic and peripheral signals use the two outer layers.
    net_map = board.GetNetsByName()
    nets = {str(name): net_item for name, net_item in net_map.items()}
    print("stage: nets", flush=True)
    # Plane zones are added after outer-layer signal routing.

    parts = {
        fp.GetReference(): fp
        for fp in board.GetFootprints()
    }
    print("stage: parts", flush=True)

    # Route in functional groups so the time-critical display paths receive
    # the clearest channels first. The router may use either outer layer and
    # inserts vias where that prevents unnecessary detours.
    output_nets = {
        f"CH{channel}_{kind}_5V"
        for channel in range(1, 7)
        for kind in ("DATA", "CLOCK")
    }
    input_nets = {
        f"CH{channel}_{kind}_3V3"
        for channel in range(1, 7)
        for kind in ("DATA", "CLOCK")
    }
    # Routing is applied in a second pass after this netted placement is saved.

    # Leave zones unfilled here. KiCad fills them safely when the board opens;
    # doing it in the headless Python binding is unstable on this KiCad build.

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("stage: saving", flush=True)
    pcbnew.SaveBoard(str(OUTPUT), board)
    print(f"Generated {OUTPUT}")


def build_fresh():
    """Generate the compact electrically connected Rev B board from scratch."""
    board = pcbnew.BOARD()
    board.GetDesignSettings().SetCopperLayerCount(4)
    outline(board, 125, 55, 3.0)

    parts = {}

    def add(library, name, ref, value, x, y, rotation=0):
        parts[ref] = footprint(board, library, name, ref, value, x, y, rotation)
        # Use a deliberate, board-level silkscreen hierarchy below. KiCad's
        # automatic reference/value placement is useful in fabrication views,
        # but becomes visual noise on this compact hand-assembled controller.
        parts[ref].Reference().SetVisible(False)
        parts[ref].Value().SetVisible(False)
        return parts[ref]

    channel_x = (13, 32, 51, 70, 89, 104)
    for index, x in enumerate(channel_x, 1):
        add("Connector_JST", "JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical",
            f"J{index}", f"CH{index}", x, 7.0)
        add("Resistor_SMD", "R_0805_2012Metric", f"R{index * 2 - 1}",
            "100R DATA", x + 5.0, 14.0, 90)
        add("Resistor_SMD", "R_0805_2012Metric", f"R{index * 2}",
            "100R CLOCK", x + 2.5, 14.0, 90)

    for index, x in enumerate((22.5, 60.5, 98.5), 1):
        add("Package_SO", "SOIC-14_3.9x8.7mm_P1.27mm", f"U{index}",
            "74AHCT125D", x, 22.5)
        add("Capacitor_SMD", "C_0805_2012Metric", f"C{index}",
            "100nF", x, 28.5)

    # Rotated KB2040 socket: USB faces right into an unobstructed corridor.
    add("Connector_PinSocket_2.54mm", "PinSocket_1x13_P2.54mm_Vertical",
        "MCU1A", "KB2040 ROW A", 55.0, 50.5, 90)
    add("Connector_PinSocket_2.54mm", "PinSocket_1x13_P2.54mm_Vertical",
        "MCU1B", "KB2040 ROW B", 85.48, 35.26, 270)

    add("TerminalBlock_Phoenix",
        "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
        "J7", "5V INPUT", 119.0, 20.0, 90)
    add("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm", "C5", "470uF",
        116.0, 32.0)
    add("Capacitor_THT", "CP_Radial_D5.0mm_P2.00mm", "C4", "10uF",
        108.0, 28.5)

    small_resistor_positions = {
        "R13": (38, 28), "R14": (42, 28), "R15": (46, 28),
        "R16": (39, 42), "R17": (43, 42), "R18": (47, 42),
        "R19": (114, 43), "R20": (35, 42),
    }
    small_resistor_values = {
        "R13": "10k", "R14": "10k", "R15": "100k",
        "R16": "10k", "R17": "10k", "R18": "20k",
        "R19": "1k", "R20": "2k2",
    }
    for ref, (x, y) in small_resistor_positions.items():
        add("Resistor_SMD", "R_0805_2012Metric", ref,
            small_resistor_values[ref], x, y, 90)

    add("Package_TO_SOT_THT", "TO-92_Inline", "Q1", "2N3904 OE",
        49.0, 31.0)
    add("LED_THT", "LED_D3.0mm", "D1", "GREEN POWER", 108.0, 36.0)
    add("LED_THT", "LED_D3.0mm", "D2", "RED HEARTBEAT", 31.0, 47.5)
    add("Button_Switch_THT", "SW_PUSH_6mm", "SW1", "TEST", 20.0, 47.5)
    add("Button_Switch_THT", "SW_PUSH_6mm", "SW2", "RESET", 9.0, 47.5)
    add("Connector_PinHeader_2.54mm", "PinHeader_2x02_P2.54mm_Vertical",
        "JP1", "ADDRESS", 43.0, 48.0)
    add("Connector_JST", "JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical",
        "J11", "GND HEARTBEAT", 33.0, 36.0, 90)
    add("Connector_JST", "JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical",
        "J10", "I2C TEST", 22.0, 38.5, 90)
    add("Connector_JST", "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",
        "J8", "I2C TO BRAIN", 8.0, 36.0, 90)
    add("Connector_JST", "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical",
        "J9", "I2C THRU", 14.0, 36.0, 90)

    for ref, x, y in (("H1", 4, 4), ("H2", 121, 4),
                      ("H3", 4, 51), ("H4", 121, 51)):
        add("MountingHole", "MountingHole_3.2mm_M3", ref, "M3", x, y)

    for index, x in enumerate(channel_x, 1):
        text(board, f"CH{index}", x + 3.75, 2.0, 0.8)
    for index, x in enumerate((22.5, 60.5, 98.5), 1):
        text(board, f"U{index}", x, 16.8, 0.8)
    text(board, "RESET", 12.25, 43.0, 0.8)
    text(board, "TEST", 23.25, 43.0, 0.8)
    text(board, "HEART", 32.27, 53.0, 0.8)
    text(board, "EYES", 38.5, 53.0, 0.8)
    text(board, "MOUTH", 48.5, 53.0, 0.8)
    text(board, "GND -", 119.0, 11.2, 0.9)
    text(board, "+5V", 119.0, 25.0, 1.0)
    text(board, "ADAFRUIT KB2040", 70.2, 53.0, 0.8)
    text(board, "USB ->", 71.0, 42.0, 1.0)
    text(board, "CHANNEL OUTPUT", 80.0, 27.0, 0.9)
    text(board, "G C D 5V", 80.0, 29.0, 0.9)
    text(board, "I2C", 8.0, 31.5, 0.8)
    text(board, "HEARTBEAT", 33.0, 29.5, 0.8)
    text(board, "POWER", 109.27, 39.5, 0.8)
    text(board, "+", 105.8, 36.0, 1.0)
    text(board, "+", 28.8, 47.5, 1.0)
    text(board, "C4 10uF", 105.0, 31.5, 0.8)
    text(board, "C5 470uF", 116.0, 38.5, 0.8)

    # Assembly values. Each channel pair is labeled on its outside edges so
    # the reference and 101 (100-ohm) value unambiguously identify one part.
    for index, x in enumerate(channel_x[:5], 1):
        left_x, right_x = x - 0.2, x + 7.7
        text(board, f"R{index * 2}", left_x, 13.2, 0.8)
        text(board, "101", left_x, 14.7, 0.8)
        text(board, f"R{index * 2 - 1}", right_x, 13.2, 0.8)
        text(board, "101", right_x, 14.7, 0.8)

    # CH6 sits beside the power terminal, so its two label stacks go below.
    text(board, "R12", 106.5, 17.2, 0.8)
    text(board, "101", 106.5, 18.7, 0.8)
    text(board, "R11", 109.0, 17.2, 0.8)
    text(board, "101", 109.0, 18.7, 0.8)

    # Decoupling-capacitor labels flank their footprints: reference on the
    # left and the conventional 104 (100 nF) code on the right.
    for index, x in enumerate((22.5, 60.5, 98.5), 1):
        text(board, f"C{index}", x - 3.2, 28.5, 0.8)
        text(board, "104", x + 3.5, 28.5, 0.8)

    # Remaining 0805 parts use reference above and value code below.
    resistor_label_data = (
        ("R13", "103", 38.0, 28.0),
        ("R14", "103", 42.0, 28.0),
        ("R15", "104", 46.0, 28.0),
        ("R16", "103", 39.0, 42.0),
        ("R17", "103", 43.0, 42.0),
        ("R18", "203", 47.0, 42.0),
        ("R19", "102", 114.0, 43.0),
        ("R20", "222", 35.0, 42.0),
    )
    for ref, code, x, y in resistor_label_data:
        text(board, ref, x, y - 2.5, 0.8)
        text(board, code, x, y + 2.5, 0.8)
    text(board, "Q1 2N3904", 49.0, 34.0, 0.8)
    mom_heart_logo(board, 99.0, 42.5, 0.62)
    text(board, "BENDING UNIT 22", 99.0, 47.2, 0.8)
    text(board, "DISPLAY CONTROLLER", 99.0, 49.2, 0.8)
    text(board, "SERIAL# 2716057", 99.0, 51.2, 0.8)
    text(board, "REV B", 99.0, 53.0, 0.8)

    names = {"+5V", "GND", "3V3_LOCAL", "3V3_BRAIN", "SDA", "SCL",
             "HEARTBEAT", "ADDRESS", "TEST", "RESET", "ENABLE_GPIO",
             "ENABLE_BASE", "OE_N", "PWR_LED_A", "HEART_LED_A",
             "ADDR_A0", "ADDR_A1"}
    for ch in range(1, 7):
        names.update({f"CH{ch}_DATA_3V3", f"CH{ch}_CLOCK_3V3",
                      f"CH{ch}_DATA_5V", f"CH{ch}_CLOCK_5V",
                      f"CH{ch}_DATA_OUT", f"CH{ch}_CLOCK_OUT"})
    nets = {name: net(board, name) for name in sorted(names)}

    top = {1: "HEARTBEAT", 2: "ENABLE_GPIO", 3: "TEST",
           4: "CH5_DATA_3V3", 5: "CH5_CLOCK_3V3", 6: "CH6_DATA_3V3",
           7: "CH6_CLOCK_3V3", 8: "ADDRESS", 9: "3V3_LOCAL",
           10: "RESET", 11: "GND", 12: "+5V"}
    bottom = {2: "SDA", 3: "SCL", 4: "GND", 5: "GND",
              6: "CH1_DATA_3V3", 7: "CH1_CLOCK_3V3",
              8: "CH2_DATA_3V3", 9: "CH2_CLOCK_3V3",
              10: "CH3_DATA_3V3", 11: "CH3_CLOCK_3V3",
              12: "CH4_DATA_3V3", 13: "CH4_CLOCK_3V3"}
    for pin, name in top.items():
        connect(parts, nets, "MCU1A", pin, name)
    for pin, name in bottom.items():
        connect(parts, nets, "MCU1B", pin, name)

    gates = ((1, 2, 3), (4, 5, 6), (10, 9, 8), (13, 12, 11))
    signal_pairs = {
        "U1": ((1, "DATA"), (1, "CLOCK"), (2, "DATA"), (2, "CLOCK")),
        "U2": ((3, "DATA"), (3, "CLOCK"), (4, "DATA"), (4, "CLOCK")),
        "U3": ((5, "DATA"), (5, "CLOCK"), (6, "DATA"), (6, "CLOCK")),
    }
    for ref, assignments in signal_pairs.items():
        connect(parts, nets, ref, 7, "GND")
        connect(parts, nets, ref, 14, "+5V")
        for (oe, input_pin, output_pin), (ch, kind) in zip(gates, assignments):
            connect(parts, nets, ref, oe, "OE_N")
            connect(parts, nets, ref, input_pin, f"CH{ch}_{kind}_3V3")
            connect(parts, nets, ref, output_pin, f"CH{ch}_{kind}_5V")

    for ch in range(1, 7):
        data_r, clock_r = f"R{ch * 2 - 1}", f"R{ch * 2}"
        connect(parts, nets, data_r, 1, f"CH{ch}_DATA_5V")
        connect(parts, nets, data_r, 2, f"CH{ch}_DATA_OUT")
        connect(parts, nets, clock_r, 1, f"CH{ch}_CLOCK_5V")
        connect(parts, nets, clock_r, 2, f"CH{ch}_CLOCK_OUT")
        # Match the input-side wire order used by the SK9822 test strips:
        # left-to-right GND, CLOCK, DATA, +5V.
        for pin, name in ((1, "GND"),
                          (2, f"CH{ch}_CLOCK_OUT"),
                          (3, f"CH{ch}_DATA_OUT"),
                          (4, "+5V")):
            connect(parts, nets, f"J{ch}", pin, name)

    connect(parts, nets, "J7", 1, "+5V")
    connect(parts, nets, "J7", 2, "GND")
    for cap in ("C1", "C2", "C3", "C4", "C5"):
        connect(parts, nets, cap, 1, "+5V")
        connect(parts, nets, cap, 2, "GND")

    for ref, pin, name in (
        ("Q1", 1, "GND"), ("Q1", 2, "ENABLE_BASE"), ("Q1", 3, "OE_N"),
        ("R13", 1, "+5V"), ("R13", 2, "OE_N"),
        ("R14", 1, "ENABLE_GPIO"), ("R14", 2, "ENABLE_BASE"),
        ("R15", 1, "ENABLE_GPIO"), ("R15", 2, "GND"),
        ("R16", 1, "3V3_LOCAL"), ("R16", 2, "ADDRESS"),
        ("R17", 1, "ADDR_A0"), ("R17", 2, "GND"),
        ("R18", 1, "ADDR_A1"), ("R18", 2, "GND"),
        ("JP1", 1, "ADDRESS"), ("JP1", 2, "ADDR_A0"),
        ("JP1", 3, "ADDRESS"), ("JP1", 4, "ADDR_A1"),
        ("R19", 1, "+5V"), ("R19", 2, "PWR_LED_A"),
        ("D1", 1, "PWR_LED_A"), ("D1", 2, "GND"),
        ("R20", 1, "HEARTBEAT"), ("R20", 2, "HEART_LED_A"),
        ("D2", 1, "HEART_LED_A"), ("D2", 2, "GND"),
        ("SW1", 1, "TEST"), ("SW1", 2, "GND"),
        ("SW2", 1, "RESET"), ("SW2", 2, "GND"),
    ):
        connect(parts, nets, ref, pin, name)

    for ref in ("J8", "J9"):
        connect(parts, nets, ref, 1, "GND")
        connect(parts, nets, ref, 3, "SDA")
        connect(parts, nets, ref, 4, "SCL")
    connect(parts, nets, "J8", 2, "3V3_BRAIN")
    for pin, name in ((1, "GND"), (2, "3V3_BRAIN"),
                      (3, "SDA"), (4, "SCL")):
        connect(parts, nets, "J10", pin, name)
    connect(parts, nets, "J11", 1, "GND")
    connect(parts, nets, "J11", 2, "HEARTBEAT")

    copper_plane(board, nets["GND"], pcbnew.In1_Cu, width=125, height=55)
    copper_plane(board, nets["+5V"], pcbnew.In2_Cu, width=125, height=55)

    output_nets = {
        f"CH{channel}_{kind}_{stage}"
        for channel in range(1, 7)
        for kind in ("DATA", "CLOCK")
        for stage in ("5V", "OUT")
    }
    input_nets = {
        f"CH{channel}_{kind}_3V3"
        for channel in range(1, 7)
        for kind in ("DATA", "CLOCK")
    }
    for channel in range(1, 7):
        print(f"routing output channel {channel}", flush=True)
        autoroute_signals(
            board, parts, nets,
            {name for name in output_nets if name.startswith(f"CH{channel}_")},
        )
    for channel in range(1, 7):
        print(f"routing input channel {channel}", flush=True)
        autoroute_signals(
            board, parts, nets,
            {name for name in input_nets if name.startswith(f"CH{channel}_")},
        )

    # The final resistor-to-XH runs have a clear, repeated geometry and are
    # cleaner as short direct traces than as maze-router paths.
    def pad_xy(ref, number):
        for pad in pads(parts[ref]):
            if pad.GetNumber() == str(number):
                pos = pad.GetPosition()
                return pos.x / 1_000_000, pos.y / 1_000_000
        raise RuntimeError(f"Missing {ref}.{number}")

    for channel in range(1, 7):
        for kind, resistor, connector_pin in (
            ("DATA", f"R{channel * 2 - 1}", 3),
            ("CLOCK", f"R{channel * 2}", 2),
        ):
            start = pad_xy(resistor, 2)
            end = pad_xy(f"J{channel}", connector_pin)
            track(board, nets[f"CH{channel}_{kind}_OUT"],
                  [start, end], 0.30, pcbnew.F_Cu)
    # The compact service/control cluster is finished in a separate manual
    # pass; keeping it out of the maze router preserves the clean display bus.

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(OUTPUT), board)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    build_fresh()
