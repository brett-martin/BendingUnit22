"""Generate the authoritative KiCad schematic for BU-22 Display Controller Rev C.

The schematic uses physical-pin connector symbols for the socketed KB2040 and
AHCT packages. This keeps every PCB pad/net mapping explicit and reviewable.
KiCad opens this legacy schematic directly and offers conversion to kicad_sch.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "display-controller-rev-c" / "BU-22-Display-Controller-Rev-C.sch"


_component_id = 0x61000001


def comp(lib, ref, value, x, y, orient="1 0 0 -1"):
    global _component_id
    uid = f"{_component_id:08X}"
    _component_id += 1
    return f'''$Comp\nL {lib} {ref}\nU 1 1 {uid}\nP {x} {y}\nF 0 "{ref}" H {x+200} {y+100} 50  0000 C CNN\nF 1 "{value}" H {x+300} {y-100} 50  0000 C CNN\n\t1    {x} {y}\n\t{orient}\n$EndComp\n'''


def label(x, y, name):
    # Legacy KiCad direction 2 puts the electrical anchor at the supplied
    # coordinate and draws the label body to the left.  Direction 0 places
    # the anchor at the far end of the rendered label, which left every net
    # dangling after conversion to the native .kicad_sch format.
    return f"Text GLabel {x} {y} 2    40   BiDi ~ 0\n{name}\n"


def wire(x1, y1, x2, y2):
    return f"Wire Wire Line\n\t{x1} {y1} {x2} {y2}\n"


def connector(ref, value, pins, x, y):
    out = comp(f"Connector_Generic:Conn_01x{len(pins):02d}", ref, value, x, y)
    # Default vertical connector: pins are on the left at x-200 and begin at
    # the symbol origin, stepping downward by 100 mil per physical pin.
    y0 = y
    for i, netname in enumerate(pins):
        py = y0 + i*100
        if netname and netname != "NC":
            out += label(x-200, py, netname)
        else:
            out += f"NoConn ~ {x-200} {py}\n"
    return out


def two_pin(ref, lib, value, left_net, right_net, x, y):
    # Physical two-pin representation avoids library-dependent symbol
    # orientation while preserving exact pad 1/pad 2 connectivity.
    return connector(ref, value, [left_net, right_net], x, y)


def build():
    s = '''EESchema Schematic File Version 4\nLIBS:power\nLIBS:device\nLIBS:74xx\nLIBS:Connector_Generic\nEELAYER 29 0\nEELAYER END\n$Descr A3 16535 11693\nSheet 1 1\nTitle "BU-22 Display Controller Rev C"\nDate "2026-08-17"\nRev "C"\nComp "Bending Unit 22"\nComment1 "SYSTEM_5V display rail; diode-isolated LOGIC_5V for KB2040 and AHCT"\nComment2 "Channel pin order: GND, CLOCK, DATA, SYSTEM_5V"\n$EndDescr\n'''

    # Power entry and automatic USB/external isolation.
    s += connector("J7", "5V INPUT", ["SYSTEM_5V", "GND"], 1200, 1000)
    s += two_pin("D3", "Device:D_Schottky", "1N5817", "LOGIC_5V", "SYSTEM_5V", 2600, 900)
    s += two_pin("C5", "Device:C_Polarized", "470uF", "SYSTEM_5V", "GND", 2600, 1200)
    s += two_pin("C4", "Device:C_Polarized", "10uF", "LOGIC_5V", "GND", 4100, 1200)
    s += two_pin("R19", "Device:R", "1k", "SYSTEM_5V", "PWR_LED_A", 2600, 1500)
    s += two_pin("D1", "Device:LED", "GREEN POWER", "PWR_LED_A", "GND", 4100, 1500)

    # Socketed KB2040, matching the PCB's two 1x13 physical rows.
    top = ["HEARTBEAT", "ENABLE_GPIO", "TEST", "CH5_DATA_3V3",
           "CH5_CLOCK_3V3", "CH6_DATA_3V3", "CH6_CLOCK_3V3", "ADDRESS",
           "3V3_LOCAL", "RESET", "GND", "LOGIC_5V", "NC"]
    bottom = ["NC", "SDA", "SCL", "GND", "GND", "CH1_DATA_3V3",
              "CH1_CLOCK_3V3", "CH2_DATA_3V3", "CH2_CLOCK_3V3",
              "CH3_DATA_3V3", "CH3_CLOCK_3V3", "CH4_DATA_3V3",
              "CH4_CLOCK_3V3"]
    s += connector("MCU1A", "ADAFRUIT KB2040 ROW A", top, 6100, 1500)
    s += connector("MCU1B", "ADAFRUIT KB2040 ROW B", bottom, 8700, 1500)

    # Three physical SOIC-14 packages. Pin lists are literal package order.
    gates = {
        "U1": ["OE_N", "CH1_DATA_3V3", "CH1_DATA_5V", "OE_N",
               "CH1_CLOCK_3V3", "CH1_CLOCK_5V", "GND", "CH2_DATA_5V",
               "CH2_DATA_3V3", "OE_N", "CH2_CLOCK_5V", "CH2_CLOCK_3V3",
               "OE_N", "LOGIC_5V"],
        "U2": ["OE_N", "CH3_DATA_3V3", "CH3_DATA_5V", "OE_N",
               "CH3_CLOCK_3V3", "CH3_CLOCK_5V", "GND", "CH4_DATA_5V",
               "CH4_DATA_3V3", "OE_N", "CH4_CLOCK_5V", "CH4_CLOCK_3V3",
               "OE_N", "LOGIC_5V"],
        "U3": ["OE_N", "CH5_DATA_3V3", "CH5_DATA_5V", "OE_N",
               "CH5_CLOCK_3V3", "CH5_CLOCK_5V", "GND", "CH6_DATA_5V",
               "CH6_DATA_3V3", "OE_N", "CH6_CLOCK_5V", "CH6_CLOCK_3V3",
               "OE_N", "LOGIC_5V"],
    }
    for idx, (ref, pinlist) in enumerate(gates.items()):
        x = 2300 + idx*4300
        s += connector(ref, "74AHCT125 SOIC-14", pinlist, x, 3500)
        s += two_pin(f"C{idx+1}", "Device:C", "100nF", "LOGIC_5V", "GND", x+1500, 3500)

    # Six output channels and their 100-ohm data/clock series resistors.
    for ch in range(1, 7):
        x = 1300 + (ch-1)*2400
        s += two_pin(f"R{ch*2-1}", "Device:R", "100R",
                     f"CH{ch}_DATA_5V", f"CH{ch}_DATA_OUT", x, 5700)
        s += two_pin(f"R{ch*2}", "Device:R", "100R",
                     f"CH{ch}_CLOCK_5V", f"CH{ch}_CLOCK_OUT", x, 6000)
        s += connector(f"J{ch}", f"CH{ch} G-C-D-5V",
                       ["GND", f"CH{ch}_CLOCK_OUT", f"CH{ch}_DATA_OUT", "SYSTEM_5V"],
                       x, 6600)

    # Enable, address, heartbeat, buttons and communications.
    controls = (
        ("R13", "10k", "LOGIC_5V", "OE_N"),
        ("R14", "10k", "ENABLE_GPIO", "ENABLE_BASE"),
        ("R15", "100k", "ENABLE_GPIO", "GND"),
        ("R16", "10k", "3V3_LOCAL", "ADDRESS"),
        ("R17", "10k", "ADDR_A0", "GND"),
        ("R18", "20k", "ADDR_A1", "GND"),
        ("R20", "2k2", "HEARTBEAT", "HEART_LED_A"),
    )
    for i, (ref, value, a, b) in enumerate(controls):
        s += two_pin(ref, "Device:R", value, a, b, 1300+(i%4)*2400, 7900+(i//4)*400)
    s += connector("Q1", "2N3904 E-B-C", ["GND", "ENABLE_BASE", "OE_N"], 11200, 7900)
    s += two_pin("D2", "Device:LED", "RED HEARTBEAT", "HEART_LED_A", "GND", 13600, 7900)
    s += connector("JP1", "ADDRESS EYES/MOUTH", ["ADDRESS", "ADDR_A0", "ADDRESS", "ADDR_A1"], 11200, 8500)
    s += connector("SW1", "TEST", ["TEST", "GND"], 13600, 8400)
    s += connector("SW2", "RESET", ["RESET", "GND"], 14800, 8400)
    s += connector("J8", "I2C TO BRAIN", ["GND", "NC", "SDA", "SCL"], 11200, 9300)
    s += connector("J9", "I2C PASS-THRU UNPOWERED", ["GND", "NC", "SDA", "SCL"], 12800, 9300)
    s += connector("J10", "I2C TEST", ["GND", "NC", "SDA", "SCL"], 14400, 9300)
    s += connector("J11", "HEARTBEAT", ["GND", "HEARTBEAT"], 11200, 10100)

    s += '''Text Notes 900 10600 0    60   ~ 12\nPOWER BEHAVIOR: USB powers LOGIC_5V only. External 5V powers SYSTEM_5V and, through D3, LOGIC_5V.\nText Notes 900 10800 0    60   ~ 0\nD3 striped cathode (K) faces LOGIC_5V. AHCT devices operate at 4.5-5.5V and accept 3.3V TTL-level inputs.\n$EndSCHEMATC\n'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(s)
    print(OUT)


if __name__ == "__main__":
    build()
