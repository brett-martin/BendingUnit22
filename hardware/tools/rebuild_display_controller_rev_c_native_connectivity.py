"""Rebuild Rev C native KiCad schematic connectivity at exact pin anchors.

The first native schematic was converted from legacy KiCad.  That conversion
offset global labels and inserted dangling wire stubs.  This tool preserves the
native symbols/layout, removes only those generated connectivity objects, and
adds native global labels or no-connect flags directly at every physical pin.
"""

from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
SCHEMATIC = (
    ROOT
    / "display-controller-rev-c"
    / "BU-22-Display-Controller-Rev-C.kicad_sch"
)


def remove_top_level_blocks(text: str, kinds: tuple[str, ...]) -> str:
    """Remove selected one-tab-indented s-expression blocks."""
    for kind in kinds:
        marker = f"\n\t({kind}"
        while True:
            start = text.find(marker)
            if start < 0:
                break
            pos = start + 1
            depth = 0
            in_string = False
            escaped = False
            while pos < len(text):
                char = text[pos]
                if in_string:
                    if escaped:
                        escaped = False
                    elif char == "\\":
                        escaped = True
                    elif char == '"':
                        in_string = False
                else:
                    if char == '"':
                        in_string = True
                    elif char == "(":
                        depth += 1
                    elif char == ")":
                        depth -= 1
                        if depth == 0:
                            pos += 1
                            if pos < len(text) and text[pos] == "\n":
                                pos += 1
                            # Preserve a separator between the neighboring
                            # top-level forms. Without this newline, removing
                            # one block concatenates the next form to the prior
                            # closing parenthesis and prevents later matches.
                            text = text[:start] + "\n" + text[pos:]
                            break
                pos += 1
            else:
                raise RuntimeError(f"Unterminated {kind} block")
    return text


def global_label(name: str, x_mm: float, y_mm: float) -> str:
    uid = uuid4()
    return f'''\t(global_label "{name}"
\t\t(shape bidirectional)
\t\t(at {x_mm:.4f} {y_mm:.4f} 180)
\t\t(effects
\t\t\t(font (size 1.016 1.016))
\t\t\t(justify right)
\t\t)
\t\t(uuid "{uid}")
\t\t(property "Intersheetrefs" "${{INTERSHEET_REFS}}"
\t\t\t(at {x_mm:.4f} {y_mm:.4f} 0)
\t\t\t(hide yes)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects (font (size 1.27 1.27)))
\t\t)
\t)
'''


def no_connect(x_mm: float, y_mm: float) -> str:
    return f'''\t(no_connect
\t\t(at {x_mm:.4f} {y_mm:.4f})
\t\t(uuid "{uuid4()}")
\t)
'''


def pin_entries(pins: list[str], x_mil: int, y_mil: int):
    """Yield physical pin anchors for a vertical Conn_01xNN symbol."""
    x_mm = (x_mil - 200) * 0.0254
    # Conn_01xNN symbols are vertically centered around their placement
    # origin. Pin 1 begins above the origin for N > 2.
    first_y_mil = y_mil - ((len(pins) - 1) // 2) * 100
    for index, net in enumerate(pins):
        y_mm = (first_y_mil + index * 100) * 0.0254
        yield net, x_mm, y_mm


def intended_connections():
    entries = []

    def add(pins, x, y):
        entries.extend(pin_entries(pins, x, y))

    add(["SYSTEM_5V", "GND"], 1200, 1000)  # J7
    # KiCad diode pad 1 is K (striped cathode); pad 2 is A.
    add(["LOGIC_5V", "SYSTEM_5V"], 2600, 900)  # D3
    add(["SYSTEM_5V", "GND"], 2600, 1200)  # C5
    add(["LOGIC_5V", "GND"], 4100, 1200)  # C4
    add(["SYSTEM_5V", "PWR_LED_A"], 2600, 1500)  # R19
    add(["PWR_LED_A", "GND"], 4100, 1500)  # D1

    add([
        "HEARTBEAT", "ENABLE_GPIO", "TEST", "CH5_DATA_3V3",
        "CH5_CLOCK_3V3", "CH6_DATA_3V3", "CH6_CLOCK_3V3", "ADDRESS",
        "3V3_LOCAL", "RESET", "GND", "LOGIC_5V", "NC",
    ], 6100, 1500)
    add([
        "NC", "SDA", "SCL", "GND", "GND", "CH1_DATA_3V3",
        "CH1_CLOCK_3V3", "CH2_DATA_3V3", "CH2_CLOCK_3V3",
        "CH3_DATA_3V3", "CH3_CLOCK_3V3", "CH4_DATA_3V3",
        "CH4_CLOCK_3V3",
    ], 8700, 1500)

    gates = [
        ["OE_N", "CH1_DATA_3V3", "CH1_DATA_5V", "OE_N",
         "CH1_CLOCK_3V3", "CH1_CLOCK_5V", "GND", "CH2_DATA_5V",
         "CH2_DATA_3V3", "OE_N", "CH2_CLOCK_5V", "CH2_CLOCK_3V3",
         "OE_N", "LOGIC_5V"],
        ["OE_N", "CH3_DATA_3V3", "CH3_DATA_5V", "OE_N",
         "CH3_CLOCK_3V3", "CH3_CLOCK_5V", "GND", "CH4_DATA_5V",
         "CH4_DATA_3V3", "OE_N", "CH4_CLOCK_5V", "CH4_CLOCK_3V3",
         "OE_N", "LOGIC_5V"],
        ["OE_N", "CH5_DATA_3V3", "CH5_DATA_5V", "OE_N",
         "CH5_CLOCK_3V3", "CH5_CLOCK_5V", "GND", "CH6_DATA_5V",
         "CH6_DATA_3V3", "OE_N", "CH6_CLOCK_5V", "CH6_CLOCK_3V3",
         "OE_N", "LOGIC_5V"],
    ]
    for index, pins in enumerate(gates):
        x = 2300 + index * 4300
        add(pins, x, 3500)
        add(["LOGIC_5V", "GND"], x + 1500, 3500)

    for channel in range(1, 7):
        x = 1300 + (channel - 1) * 2400
        add([f"CH{channel}_DATA_5V", f"CH{channel}_DATA_OUT"], x, 5700)
        add([f"CH{channel}_CLOCK_5V", f"CH{channel}_CLOCK_OUT"], x, 6000)
        add(["GND", f"CH{channel}_CLOCK_OUT", f"CH{channel}_DATA_OUT", "SYSTEM_5V"], x, 6600)

    controls = [
        ["LOGIC_5V", "OE_N"], ["ENABLE_GPIO", "ENABLE_BASE"],
        ["ENABLE_GPIO", "GND"], ["3V3_LOCAL", "ADDRESS"],
        ["ADDR_A0", "GND"], ["ADDR_A1", "GND"],
        ["HEARTBEAT", "HEART_LED_A"],
    ]
    for index, pins in enumerate(controls):
        add(pins, 1300 + (index % 4) * 2400, 7900 + (index // 4) * 400)

    add(["GND", "ENABLE_BASE", "OE_N"], 11200, 7900)  # Q1 E-B-C
    add(["HEART_LED_A", "GND"], 13600, 7900)  # D2
    add(["ADDRESS", "ADDR_A0", "ADDRESS", "ADDR_A1"], 11200, 8500)
    add(["TEST", "GND"], 13600, 8400)
    add(["RESET", "GND"], 14800, 8400)
    add(["GND", "NC", "SDA", "SCL"], 11200, 9300)
    add(["GND", "NC", "SDA", "SCL"], 12800, 9300)
    add(["GND", "NC", "SDA", "SCL"], 14400, 9300)
    add(["GND", "HEARTBEAT"], 11200, 10100)
    return entries


def main():
    text = SCHEMATIC.read_text()
    text = remove_top_level_blocks(text, ("wire", "global_label", "no_connect"))
    objects = []
    for net, x_mm, y_mm in intended_connections():
        if net == "NC":
            objects.append(no_connect(x_mm, y_mm))
        else:
            objects.append(global_label(net, x_mm, y_mm))

    insertion = text.find("\n\t(symbol\n", text.find("\n\t(lib_symbols"))
    if insertion < 0:
        raise RuntimeError("Could not locate native symbol-instance section")
    text = text[:insertion] + "\n" + "".join(objects) + text[insertion:]
    SCHEMATIC.write_text(text)
    print(f"Rebuilt native connectivity: {SCHEMATIC}")


if __name__ == "__main__":
    main()
