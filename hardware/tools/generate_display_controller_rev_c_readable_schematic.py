"""Generate a conventional, human-readable Rev C KiCad schematic.

This is intentionally different from the pin-audit schematic: components use
their normal electrical symbols and are arranged in functional blocks.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
uid = 0x72000001


def component(lib, ref, value, x, y, unit=1, orient="1 0 0 -1"):
    global uid
    ident = f"{uid:08X}"
    uid += 1
    return f'''$Comp
L {lib} {ref}
U {unit} 1 {ident}
P {x} {y}
F 0 "{ref}" H {x+200} {y+100} 50  0000 C CNN
F 1 "{value}" H {x+300} {y-100} 50  0000 C CNN
\t{unit}    {x} {y}
\t{orient}
$EndComp
'''


def wire(x1, y1, x2, y2):
    return f"Wire Wire Line\n\t{x1} {y1} {x2} {y2}\n"


def net_label(x, y, name, orientation=0):
    return f"Text Label {x} {y} {orientation}    40   ~ 0\n{name}\n"


def note(x, y, text, size=60):
    return f"Text Notes {x} {y} 0    {size}   ~ 12\n{text}\n"


def power_symbol(ref, name, x, y):
    return component(f"power:{name}", ref, name, x, y)


def horizontal_resistor(ref, value, x, y):
    return component("Device:R", ref, value, x, y, orient="0 -1 -1 0")


def output_channel(channel, x, y, uref, data_unit, clock_unit):
    """Two AHCT gates, two series resistors, and one G-C-D-5V connector."""
    s = note(x, y-500, f"CHANNEL {channel}", 55)

    # DATA path: input -> AHCT -> 100R -> output connector pin 3.
    s += component("74xx:74AHCT125", uref, "74AHCT125", x+900, y, data_unit)
    s += net_label(x+300, y, f"CH{channel}_DATA_3V3")
    s += wire(x+300, y, x+600, y)
    s += net_label(x+900, y+300, "OE_N", 1)
    s += horizontal_resistor(f"R{channel*2-1}", "100R", x+1700, y)
    s += wire(x+1200, y, x+1600, y)
    s += wire(x+1800, y, x+2100, y)
    s += net_label(x+2100, y, f"CH{channel}_DATA_OUT", 2)

    # CLOCK path: input -> AHCT -> 100R -> output connector pin 2.
    s += component("74xx:74AHCT125", uref, "74AHCT125", x+900, y+500, clock_unit)
    s += net_label(x+300, y+500, f"CH{channel}_CLOCK_3V3")
    s += wire(x+300, y+500, x+600, y+500)
    s += net_label(x+900, y+800, "OE_N", 1)
    s += horizontal_resistor(f"R{channel*2}", "100R", x+1700, y+500)
    s += wire(x+1200, y+500, x+1600, y+500)
    s += wire(x+1800, y+500, x+2100, y+500)
    s += net_label(x+2100, y+500, f"CH{channel}_CLOCK_OUT", 2)

    # Connector is drawn with its pins at the left, top-to-bottom G,C,D,5V.
    s += component("Connector_Generic:Conn_01x04", f"J{channel}",
                   f"CH{channel} G-C-D-5V", x+2700, y+250)
    # Conn_01x04 pin anchors are centered: y-100, y, y+100, y+200.
    s += net_label(x+2400, y+150, "GND")
    s += wire(x+2400, y+150, x+2500, y+150)
    s += net_label(x+2200, y+250, f"CH{channel}_CLOCK_OUT")
    s += wire(x+2200, y+250, x+2500, y+250)
    s += net_label(x+2200, y+350, f"CH{channel}_DATA_OUT")
    s += wire(x+2200, y+350, x+2500, y+350)
    s += net_label(x+2400, y+450, "SYSTEM_5V")
    s += wire(x+2400, y+450, x+2500, y+450)
    return s


def build(revision="C"):
    revision = revision.upper()
    if revision not in {"C", "D"}:
        raise ValueError("revision must be C or D")
    out = (ROOT / f"display-controller-rev-{revision.lower()}"
           / f"BU-22-Display-Controller-Rev-{revision}-readable.sch")
    out.parent.mkdir(parents=True, exist_ok=True)
    s = f'''EESchema Schematic File Version 4
LIBS:power
LIBS:device
LIBS:74xx
LIBS:Connector_Generic
LIBS:Transistor_BJT
EELAYER 29 0
EELAYER END
$Descr A3 16535 11693
Sheet 1 1
Title "BU-22 Display Controller Rev {revision}"
Date "2026-08-18"
Rev "{revision}"
Comp "Bending Unit 22"
Comment1 "Readable functional schematic"
Comment2 "Channel output order: GND, CLOCK, DATA, SYSTEM_5V"
$EndDescr
'''

    # ------------------------------------------------------------------
    # Power entry, isolation, filtering, and power indication.
    s += note(700, 650, "POWER ENTRY AND USB ISOLATION")
    s += component("Connector_Generic:Conn_01x02", "J7", "5V INPUT", 1200, 1200)
    s += net_label(800, 1200, "SYSTEM_5V")
    s += wire(800, 1200, 1000, 1200)
    s += net_label(800, 1300, "GND")
    s += wire(800, 1300, 1000, 1300)

    s += component("Device:D_Schottky", "D3", "1N5817", 2300, 1200,
                   orient="-1 0 0 1")
    s += net_label(1600, 1200, "SYSTEM_5V")
    s += wire(1600, 1200, 2200, 1200)
    s += wire(2400, 1200, 3000, 1200)
    s += net_label(2700, 1200, "LOGIC_5V")
    s += note(1900, 950, "A", 45)
    s += note(2500, 950, "K (stripe)", 45)

    s += component("Device:C_Polarized", "C5", "470uF", 1600, 1750)
    s += net_label(1600, 1450, "SYSTEM_5V", 1)
    s += wire(1600, 1450, 1600, 1650)
    s += net_label(1600, 2050, "GND", 1)
    s += wire(1600, 1850, 1600, 2050)

    s += component("Device:C_Polarized", "C4", "10uF", 2800, 1750)
    s += net_label(2800, 1450, "LOGIC_5V", 1)
    s += wire(2800, 1450, 2800, 1650)
    s += net_label(2800, 2050, "GND", 1)
    s += wire(2800, 1850, 2800, 2050)

    s += horizontal_resistor("R19", "1k", 3800, 1200)
    s += net_label(3400, 1200, "SYSTEM_5V")
    s += wire(3400, 1200, 3700, 1200)
    s += component("Device:LED", "D1", "GREEN POWER", 4400, 1200,
                   orient="-1 0 0 1")
    s += wire(3900, 1200, 4300, 1200)
    s += net_label(4700, 1200, "GND")
    s += wire(4500, 1200, 4700, 1200)

    # ------------------------------------------------------------------
    # KB2040 socket. Headers remain physical because there is no standard
    # KiCad symbol for the Adafruit KB2040 module.
    s += note(5600, 650, "ADAFRUIT KB2040 CONTROLLER")
    top = ["HEARTBEAT", "ENABLE_GPIO", "TEST", "CH5_DATA_3V3",
           "CH5_CLOCK_3V3", "CH6_DATA_3V3", "CH6_CLOCK_3V3", "ADDRESS",
           "3V3_LOCAL", "RESET", "GND", "LOGIC_5V", "NC"]
    if revision == "D":
        bottom = ["NC", "SDA", "SCL", "GND", "GND", "CH4_CLOCK_3V3",
                  "CH4_DATA_3V3", "CH3_CLOCK_3V3", "CH3_DATA_3V3",
                  "CH2_CLOCK_3V3", "CH2_DATA_3V3", "CH1_CLOCK_3V3",
                  "CH1_DATA_3V3"]
    else:
        bottom = ["NC", "SDA", "SCL", "GND", "GND", "CH1_DATA_3V3",
                  "CH1_CLOCK_3V3", "CH2_DATA_3V3", "CH2_CLOCK_3V3",
                  "CH3_DATA_3V3", "CH3_CLOCK_3V3", "CH4_DATA_3V3",
                  "CH4_CLOCK_3V3"]
    for ref, title, pins, x in (
        ("MCU1A", "KB2040 ROW A", top, 6500),
        ("MCU1B", "KB2040 ROW B", bottom, 9300),
    ):
        s += component("Connector_Generic:Conn_01x13", ref, title, x, 1450)
        first_y = 1450 - 600
        for index, name in enumerate(pins):
            py = first_y + index*100
            if name == "NC":
                s += f"NoConn ~ {x-200} {py}\n"
            else:
                s += net_label(x-600, py, name)
                s += wire(x-600, py, x-200, py)

    # ------------------------------------------------------------------
    # AHCT power units and local bypassing.
    s += note(11200, 650, "5V LEVEL SHIFTERS")
    for index, x in enumerate((11600, 13200, 14800), 1):
        s += component("74xx:74AHCT125", f"U{index}", "74AHCT125", x, 1200, 5)
        s += net_label(x, 800, "LOGIC_5V", 1)
        s += wire(x, 800, x, 900)
        s += net_label(x, 1600, "GND", 1)
        s += wire(x, 1500, x, 1600)
        s += component("Device:C", f"C{index}", "100nF", x+600, 1200)
        s += net_label(x+600, 900, "LOGIC_5V", 1)
        s += wire(x+600, 900, x+600, 1100)
        s += net_label(x+600, 1500, "GND", 1)
        s += wire(x+600, 1300, x+600, 1500)

    # Six output blocks, two rows of three.
    channel_units = {
        1: ("U1", 1, 2), 2: ("U1", 3, 4),
        3: ("U2", 1, 2), 4: ("U2", 3, 4),
        5: ("U3", 1, 2), 6: ("U3", 3, 4),
    }
    for channel, (x, y) in enumerate(((700, 3300), (5900, 3300), (11100, 3300),
                                      (700, 5200), (5900, 5200), (11100, 5200)), 1):
        uref, du, cu = channel_units[channel]
        s += output_channel(channel, x, y, uref, du, cu)

    # ------------------------------------------------------------------
    # Output enable and status controls.
    s += note(700, 7350, "OUTPUT ENABLE AND STATUS")
    s += horizontal_resistor("R13", "10k", 1600, 7800)
    s += net_label(1100, 7800, "LOGIC_5V")
    s += wire(1100, 7800, 1500, 7800)
    s += net_label(1900, 7800, "OE_N")
    s += wire(1700, 7800, 1900, 7800)

    s += horizontal_resistor("R14", "10k", 1600, 8300)
    s += net_label(1100, 8300, "ENABLE_GPIO")
    s += wire(1100, 8300, 1500, 8300)
    s += net_label(1900, 8300, "ENABLE_BASE")
    s += wire(1700, 8300, 1900, 8300)
    s += horizontal_resistor("R15", "100k", 1600, 8700)
    s += net_label(1100, 8700, "ENABLE_GPIO")
    s += wire(1100, 8700, 1500, 8700)
    s += net_label(1900, 8700, "GND")
    s += wire(1700, 8700, 1900, 8700)

    s += component("Transistor_BJT:Q_NPN_BCE", "Q1", "2N3904", 2800, 8300)
    s += net_label(2300, 8300, "ENABLE_BASE")
    s += wire(2300, 8300, 2600, 8300)
    s += net_label(2800, 7900, "OE_N", 1)
    s += net_label(2800, 8700, "GND", 1)

    s += horizontal_resistor("R20", "2k2", 3900, 8000)
    s += net_label(3400, 8000, "HEARTBEAT")
    s += wire(3400, 8000, 3800, 8000)
    s += component("Device:LED", "D2", "RED HEARTBEAT", 4500, 8000,
                   orient="-1 0 0 1")
    s += wire(4000, 8000, 4400, 8000)
    s += net_label(4800, 8000, "GND")
    s += wire(4600, 8000, 4800, 8000)
    s += component("Connector_Generic:Conn_01x02", "J11", "HEARTBEAT IN", 4500, 8600)
    s += net_label(4000, 8550, "GND")
    s += net_label(4000, 8650, "HEARTBEAT")
    s += wire(4000, 8550, 4300, 8550)
    s += wire(4000, 8650, 4300, 8650)

    # ------------------------------------------------------------------
    # Address selection, buttons, and I2C.
    s += note(5700, 7350, "ADDRESS, CONTROLS, AND I2C")
    s += horizontal_resistor("R16", "10k", 6500, 7800)
    s += net_label(6000, 7800, "3V3_LOCAL")
    s += wire(6000, 7800, 6400, 7800)
    s += net_label(6800, 7800, "ADDRESS")
    s += wire(6600, 7800, 6800, 7800)
    s += horizontal_resistor("R17", "10k", 6500, 8200)
    s += net_label(6000, 8200, "ADDR_A0")
    s += wire(6000, 8200, 6400, 8200)
    s += net_label(6800, 8200, "GND")
    s += wire(6600, 8200, 6800, 8200)
    s += horizontal_resistor("R18", "20k", 6500, 8600)
    s += net_label(6000, 8600, "ADDR_A1")
    s += wire(6000, 8600, 6400, 8600)
    s += net_label(6800, 8600, "GND")
    s += wire(6600, 8600, 6800, 8600)

    s += component("Connector_Generic:Conn_02x02_Odd_Even", "JP1",
                   "EYES / MOUTH ADDRESS", 8000, 8200)
    for yy, name in ((8150, "ADDRESS"), (8250, "ADDRESS")):
        s += net_label(7500, yy, name)
        s += wire(7500, yy, 7700, yy)
    s += net_label(8500, 8150, "ADDR_A0", 2)
    s += wire(8300, 8150, 8500, 8150)
    s += net_label(8500, 8250, "ADDR_A1", 2)
    s += wire(8300, 8250, 8500, 8250)

    s += component("Switch:SW_Push", "SW1", "TEST", 9400, 7900,
                   orient="0 1 1 0")
    s += net_label(9000, 7900, "TEST")
    s += net_label(9800, 7900, "GND", 2)
    s += component("Switch:SW_Push", "SW2", "RESET", 9400, 8500,
                   orient="0 1 1 0")
    s += net_label(9000, 8500, "RESET")
    s += net_label(9800, 8500, "GND", 2)

    for ref, title, x in (
        ("J8", "I2C TO BRAIN", 11200),
        ("J9", "I2C PASS-THRU", 13000),
        ("J10", "I2C TEST", 14800),
    ):
        s += component("Connector_Generic:Conn_01x04", ref, title, x, 8200)
        # Pin 2 is deliberately isolated. The Brain may provide 3.3V on a
        # standard Qwiic cable, but this controller neither receives nor
        # forwards that rail.
        nets = ["GND", "NC", "SDA", "SCL"]
        for index, name in enumerate(nets):
            py = 8100 + index*100
            if name == "NC":
                s += f"NoConn ~ {x-200} {py}\n"
            else:
                s += net_label(x-600, py, name)
                s += wire(x-600, py, x-200, py)

    s += note(700, 10300,
              "USB powers LOGIC_5V only. External 5V powers LED SYSTEM_5V and feeds LOGIC_5V through D3.", 55)
    s += note(700, 10500,
              "D3 pad 1 = K/LOGIC_5V; pad 2 = A/SYSTEM_5V. AHCT outputs are disabled while OE_N is high.", 55)
    s += "$EndSCHEMATC\n"
    out.write_text(s)
    print(out)


if __name__ == "__main__":
    build()
