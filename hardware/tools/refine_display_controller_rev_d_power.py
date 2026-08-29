"""Refine the Rev D power placement and routing without disturbing signals."""

from pathlib import Path
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
BOARD_PATH = ROOT / "display-controller-rev-d" / "BU-22-Display-Controller-Rev-D.kicad_pcb"


def mm(value):
    return pcbnew.FromMM(value)


def point(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def move(board, ref, x, y):
    board.FindFootprintByReference(ref).SetPosition(point(x, y))


def add_track(board, net, start, end, layer, width):
    track = pcbnew.PCB_TRACK(board)
    track.SetNet(net)
    track.SetLayer(layer)
    track.SetWidth(mm(width))
    track.SetStart(point(*start))
    track.SetEnd(point(*end))
    board.Add(track)


def add_path(board, net, coords, layer, width):
    for start, end in zip(coords, coords[1:]):
        add_track(board, net, start, end, layer, width)


def add_via(board, net, x, y, diameter=0.8, drill=0.4):
    via = pcbnew.PCB_VIA(board)
    via.SetNet(net)
    via.SetPosition(point(x, y))
    via.SetWidth(mm(diameter))
    via.SetDrill(mm(drill))
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    board.Add(via)


def xy(item, which):
    pos = item.GetStart() if which == "start" else item.GetEnd()
    return pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)


def main():
    board = pcbnew.LoadBoard(str(BOARD_PATH))
    system = board.FindNet("SYSTEM_5V")
    logic = board.FindNet("LOGIC_5V")
    led = board.FindNet("PWR_LED_A")
    original_tracks = list(board.GetTracks())

    # Give the external-power area breathing room while leaving J7 fixed.
    move(board, "D3", 108.0, 29.0)
    move(board, "C4", 108.0, 35.5)
    move(board, "C5", 116.0, 37.0)
    move(board, "D1", 108.0, 43.0)
    move(board, "R19", 114.0, 48.0)

    # Replace the entire high-current rail and the short LED branch.
    for item in original_tracks:
        if item.GetNetname() in {"SYSTEM_5V", "PWR_LED_A"}:
            board.Remove(item)

    # Straight horizontal display rail with perpendicular drops to pin 4.
    channel_5v_x = (20.5, 39.5, 58.5, 77.5, 96.5, 111.5)
    add_track(board, system, (channel_5v_x[0], 4.5), (channel_5v_x[-1], 4.5), pcbnew.F_Cu, 1.0)
    for x in channel_5v_x:
        add_track(board, system, (x, 4.5), (x, 7.0), pcbnew.F_Cu, 1.0)

    # J7 feeds the top bus and the local power components on the bottom layer.
    add_path(board, system, [(119.0, 20.0), (115.0, 16.0), (111.5, 12.5), (111.5, 7.0)], pcbnew.B_Cu, 1.0)
    add_path(board, system, [(119.0, 20.0), (118.16, 24.0), (118.16, 29.0)], pcbnew.B_Cu, 1.0)
    add_path(board, system, [(118.16, 29.0), (116.0, 31.16), (116.0, 37.0)], pcbnew.B_Cu, 1.0)
    add_path(board, system, [(116.0, 37.0), (114.0, 39.0), (114.0, 46.0)], pcbnew.B_Cu, 1.0)
    add_via(board, system, 114.0, 46.0, diameter=1.2, drill=0.6)
    add_track(board, system, (114.0, 46.0), (114.0, 48.9125), pcbnew.F_Cu, 1.0)

    # Power LED resistor-to-anode branch after the placement change.
    add_path(board, led, [(114.0, 47.09), (112.0, 45.09), (108.0, 43.0)], pcbnew.F_Cu, 0.3)

    # Remove only the unruly U1 and moved right-side portions of LOGIC_5V.
    # The central U2/U3/MCU routing remains untouched.
    for item in original_tracks:
        if item.GetNetname() != "LOGIC_5V":
            continue
        sx, sy = xy(item, "start")
        ex, ey = xy(item, "end")
        if min(sx, ex) < 42.0 or max(sx, ex) > 103.0:
            board.Remove(item)

    # U1 supply: top pad -> via -> bottom crossover -> via -> local capacitor.
    add_track(board, logic, (24.98, 18.69), (26.5, 18.69), pcbnew.F_Cu, 0.5)
    add_via(board, logic, 26.5, 18.69)
    add_path(board, logic, [(26.5, 18.69), (26.5, 27.0), (24.0, 29.5)], pcbnew.B_Cu, 0.5)
    add_via(board, logic, 24.0, 29.5)
    add_track(board, logic, (24.0, 29.5), (21.55, 28.5), pcbnew.F_Cu, 0.5)
    # Rejoin U1/C1 to the preserved central logic rail from below.
    add_via(board, logic, 42.19, 32.45)
    add_path(board, logic, [(24.0, 29.5), (28.0, 32.45), (42.19, 32.45)], pcbnew.B_Cu, 0.5)
    add_track(board, logic, (42.19, 32.45), (42.191, 32.453), pcbnew.F_Cu, 0.5)
    # R13 was part of the inherited left-side branch removed above.
    add_track(board, logic, (38.0, 28.9125), (42.191, 32.453), pcbnew.F_Cu, 0.5)

    # Moved diode and logic reservoir capacitor, rejoined at C3 and MCU RAW.
    add_track(board, logic, (108.0, 29.0), (108.0, 35.5), pcbnew.F_Cu, 0.5)
    add_path(board, logic, [(108.0, 35.5), (104.0, 31.5), (97.55, 28.5)], pcbnew.F_Cu, 0.5)
    add_via(board, logic, 108.0, 35.5)
    add_path(board, logic, [(108.0, 35.5), (104.0, 39.5), (82.94, 50.5)], pcbnew.B_Cu, 0.5)

    # Explicit ground spine for the relocated through-hole power parts. The
    # filled plane remains the broad return path; these tracks make the local
    # connections deterministic even before the plane is refilled.
    ground = board.FindNet("GND")
    add_path(
        board,
        ground,
        [(119.0, 14.92), (122.5, 18.42), (122.5, 35.5), (121.0, 37.0),
         (114.5, 43.0), (110.54, 43.0), (110.0, 35.5)],
        pcbnew.B_Cu,
        0.8,
    )

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD_PATH), board)
    print(f"Refined power routing in {BOARD_PATH}")


if __name__ == "__main__":
    main()
