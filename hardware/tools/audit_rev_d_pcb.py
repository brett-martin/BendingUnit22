"""Run repeatable electrical and copper-clearance checks on Rev D."""

from itertools import combinations
from pathlib import Path
import sys

import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"
CLEARANCE_MM = 0.20


def mm(value):
    return pcbnew.FromMM(value)


def point_text(item):
    if item.GetClass() == "PAD":
        pos = item.GetPosition()
        return f"{item.GetParentFootprint().GetReference()}.{item.GetNumber()} @ " \
               f"({pcbnew.ToMM(pos.x):.3f},{pcbnew.ToMM(pos.y):.3f})"
    if isinstance(item, pcbnew.PCB_VIA):
        pos = item.GetPosition()
        return f"via @ ({pcbnew.ToMM(pos.x):.3f},{pcbnew.ToMM(pos.y):.3f})"
    start, end = item.GetStart(), item.GetEnd()
    return (f"track ({pcbnew.ToMM(start.x):.3f},{pcbnew.ToMM(start.y):.3f}) -> "
            f"({pcbnew.ToMM(end.x):.3f},{pcbnew.ToMM(end.y):.3f})")


def copper_items(board, layer):
    result = []
    for footprint in board.GetFootprints():
        for pad in footprint.Pads():
            if pad.IsOnLayer(layer) and pad.GetNetCode():
                result.append(pad)
    for item in board.GetTracks():
        if item.GetNetCode() and (item.GetLayer() == layer or isinstance(item, pcbnew.PCB_VIA)):
            result.append(item)
    return result


def clearance_hits(board, layer):
    hits = []
    items = copper_items(board, layer)
    for first, second in combinations(items, 2):
        if first.GetNetCode() == second.GetNetCode():
            continue
        if first.GetEffectiveShape(layer).Collide(
                second.GetEffectiveShape(layer), mm(CLEARANCE_MM)):
            hits.append((first, second))
    return hits


def main():
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    board.BuildConnectivity()
    ratsnest = board.GetConnectivity().GetUnconnectedCount(False)
    print(f"Board: {BOARD_PATH}")
    print(f"Unconnected items: {ratsnest}")

    total_hits = 0
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        name = board.GetLayerName(layer)
        hits = clearance_hits(board, layer)
        total_hits += len(hits)
        print(f"{name} clearance hits at {CLEARANCE_MM:.2f} mm: {len(hits)}")
        for first, second in hits:
            print(f"  {first.GetNetname()} {point_text(first)}")
            print(f"    vs {second.GetNetname()} {point_text(second)}")

    if ratsnest or total_hits:
        print(f"AUDIT FAILED: {ratsnest} unconnected, {total_hits} clearance hits")
        return 1
    print("AUDIT PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
