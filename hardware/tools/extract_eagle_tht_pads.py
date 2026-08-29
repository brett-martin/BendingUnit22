#!/usr/bin/env python3
"""Print transformed through-hole pad coordinates from an Eagle .brd file."""

import math
import sys
import xml.etree.ElementTree as ET


def transform(px, py, ex, ey, rotation):
    rotation = rotation or "R0"
    mirrored = rotation.startswith("M")
    angle_text = rotation[1:] if mirrored else rotation[1:]
    angle = float(angle_text or 0)
    if mirrored:
        px = -px
    radians = math.radians(angle)
    x = px * math.cos(radians) - py * math.sin(radians) + ex
    y = px * math.sin(radians) + py * math.cos(radians) + ey
    return round(x, 4), round(y, 4)


def main(path):
    root = ET.parse(path).getroot()
    board = root.find("./drawing/board")
    packages = {}
    for library in board.findall("./libraries/library"):
        library_name = library.attrib["name"]
        for package in library.findall("./packages/package"):
            pads = []
            for pad in package.findall("pad"):
                pads.append((pad.attrib["name"], float(pad.attrib["x"]), float(pad.attrib["y"])))
            packages[(library_name, package.attrib["name"])] = pads

    pad_nets = {}
    for signal in board.findall("./signals/signal"):
        for contact in signal.findall("contactref"):
            pad_nets[(contact.attrib["element"], contact.attrib["pad"])] = signal.attrib["name"]

    for element in board.findall("./elements/element"):
        key = (element.attrib["library"], element.attrib["package"])
        pads = packages.get(key, [])
        if not pads:
            continue
        ex, ey = float(element.attrib["x"]), float(element.attrib["y"])
        transformed = [
            (name, *transform(x, y, ex, ey, element.attrib.get("rot", "R0")))
            for name, x, y in pads
        ]
        print(f"{element.attrib['name']} {key[1]} {element.attrib.get('rot', 'R0')}")
        print(
            "  "
            + " ".join(
                f"{name}:{pad_nets.get((element.attrib['name'], name), '?')}@({x:g},{y:g})"
                for name, x, y in transformed
            )
        )


if __name__ == "__main__":
    main(sys.argv[1])
