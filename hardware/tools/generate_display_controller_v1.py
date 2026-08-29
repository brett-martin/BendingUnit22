"""Generate the preliminary BU-22 universal display controller V1 PCB.

Revision A establishes the board outline, component placement, footprints, and
complete net assignment. Copper routing is intentionally a separate review
step; do not send the generated board to fabrication while PRELIMINARY appears
on the silkscreen.
"""

from pathlib import Path
import heapq
import itertools
import math
import pcbnew


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "display-controller-v1"
OUTPUT = OUT_DIR / "BU-22-Display-Controller-V1.kicad_pcb"
FP_ROOT = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")


def mm(value):
    return pcbnew.FromMM(value)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def footprint(board, library, name, ref, value, x, y, rotation=0):
    fp = pcbnew.FootprintLoad(str(FP_ROOT / f"{library}.pretty"), name)
    if fp is None:
        raise RuntimeError(f"Footprint not found: {library}:{name}")
    fp.SetReference(ref)
    fp.SetValue(value)
    fp.SetPosition(pt(x, y))
    fp.SetOrientationDegrees(rotation)
    board.Add(fp)
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    return fp


def net(board, name):
    item = pcbnew.NETINFO_ITEM(board, name)
    board.Add(item)
    return item


def connect(parts, nets, ref, pin, name):
    pads = [p for p in parts[ref].Pads() if p.GetNumber() == str(pin)]
    if not pads:
        raise RuntimeError(f"No pad {ref}.{pin}")
    for pad in pads:
        pad.SetNet(nets[name])


def text(board, value, x, y, size=1.0, rotation=0, layer=pcbnew.F_SilkS):
    item = pcbnew.PCB_TEXT(board)
    item.SetText(value)
    item.SetPosition(pt(x, y))
    item.SetLayer(layer)
    item.SetTextSize(pt(size, size))
    item.SetTextThickness(mm(max(0.15, size * 0.15)))
    item.SetTextAngle(pcbnew.EDA_ANGLE(rotation, pcbnew.DEGREES_T))
    if layer in (pcbnew.B_SilkS, pcbnew.B_Fab):
        item.SetMirrored(True)
    item.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    item.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    board.Add(item)


def silk_line(board, start, end, width=0.30):
    item = pcbnew.PCB_SHAPE(board)
    item.SetShape(pcbnew.SHAPE_T_SEGMENT)
    item.SetLayer(pcbnew.F_SilkS)
    item.SetStart(pt(*start))
    item.SetEnd(pt(*end))
    item.SetWidth(mm(width))
    board.Add(item)


def track(board, net_item, coordinates, width=0.25, layer=pcbnew.F_Cu):
    for start, end in zip(coordinates, coordinates[1:]):
        if start == end:
            continue
        item = pcbnew.PCB_TRACK(board)
        item.SetLayer(layer)
        item.SetNet(net_item)
        item.SetWidth(mm(width))
        item.SetStart(pt(*start))
        item.SetEnd(pt(*end))
        board.Add(item)


def via(board, net_item, x, y, diameter=0.70, drill=0.35):
    item = pcbnew.PCB_VIA(board)
    item.SetPosition(pt(x, y))
    item.SetWidth(mm(diameter))
    item.SetDrill(mm(drill))
    item.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    item.SetNet(net_item)
    board.Add(item)


def control_escape_stubs(board, nets):
    """Reserve short fanout paths before the general signal routing."""
    track(board, nets["RESET"], [(17.64, 41.0), (17.64, 38.0)],
          0.20, pcbnew.F_Cu)
    via(board, nets["RESET"], 17.64, 38.0)
    track(board, nets["RESET"], [(48.0, 57.0), (48.0, 60.0)],
          0.20, pcbnew.F_Cu)
    track(board, nets["RESET"], [(54.5, 57.0), (54.5, 60.0)],
          0.20, pcbnew.F_Cu)
    track(board, nets["RESET"], [(110.0, 56.0), (110.0, 60.0)],
          0.20, pcbnew.F_Cu)
    track(board, nets["ADDRESS"], [(22.72, 41.0), (22.72, 38.0)],
          0.20, pcbnew.F_Cu)
    via(board, nets["ADDRESS"], 22.72, 38.0)
    track(board, nets["ADDRESS"],
          [(93.08, 44.0), (96.0, 44.0), (96.0, 48.0)],
          0.20, pcbnew.F_Cu)
    track(board, nets["ADDRESS"], [(89.0, 56.0), (84.0, 56.0)],
          0.20, pcbnew.F_Cu)
    track(board, nets["ADDRESS"], [(89.0, 58.54), (84.0, 58.54)],
          0.20, pcbnew.F_Cu)


def copper_plane(board, net_item, layer, width=140, height=65, inset=0.6):
    zone = pcbnew.ZONE(board)
    zone.SetLayer(layer)
    zone.SetNet(net_item)
    zone.SetLocalClearance(mm(0.25))
    polygon = zone.Outline()
    polygon.NewOutline()
    for x, y in ((inset, inset), (width - inset, inset),
                 (width - inset, height - inset), (inset, height - inset)):
        polygon.Append(mm(x), mm(y))
    board.Add(zone)


def autoroute_signals(board, parts, nets, only_names=None,
                      reserve_radius_override=None,
                      root_escape=None, terminal_escapes=None):
    """Route low-speed logic, optionally restricting work to named nets."""
    step = 0.125 if only_names is not None else 0.25
    route_width = 0.20 if only_names is not None else 0.25
    reserve_radius = 7 if only_names is not None else 2
    if reserve_radius_override is not None:
        reserve_radius = reserve_radius_override
    layers = (pcbnew.F_Cu, pcbnew.B_Cu)
    grid_w = int(140 / step)
    grid_h = int(65 / step)
    blocked = {layer: {} for layer in layers}
    via_forbidden = set()

    def cell(x, y):
        return (int(round(x / step)), int(round(y / step)))

    def point_mm(item):
        return (item[0] * step, item[1] * step)

    def mark_box(target, x0, y0, x1, y1, owner, inflate):
        ix0, iy0 = cell(x0 - inflate, y0 - inflate)
        ix1, iy1 = cell(x1 + inflate, y1 + inflate)
        for ix in range(ix0, ix1 + 1):
            for iy in range(iy0, iy1 + 1):
                target[(ix, iy)] = owner

    all_pads = [pad for fp in parts.values() for pad in fp.Pads()]
    for pad in all_pads:
        box = pad.GetBoundingBox()
        x0, y0 = box.GetX() / 1e6, box.GetY() / 1e6
        x1, y1 = box.GetRight() / 1e6, box.GetBottom() / 1e6
        owner = pad.GetNetCode() if pad.GetNetCode() else -1
        for layer in layers:
            if pad.IsOnLayer(layer):
                mark_box(blocked[layer], x0, y0, x1, y1, owner, 0.35)
        ix0, iy0 = cell(x0 - 0.45, y0 - 0.45)
        ix1, iy1 = cell(x1 + 0.45, y1 + 0.45)
        for ix in range(ix0, ix1 + 1):
            for iy in range(iy0, iy1 + 1):
                via_forbidden.add((ix, iy))

    # Preserve the manually routed power and cable-edge signal copper.
    for item in board.GetTracks():
        owner = item.GetNetCode() if item.GetNetCode() else -1
        if isinstance(item, pcbnew.PCB_VIA):
            pos = item.GetPosition()
            x, y = pos.x / 1e6, pos.y / 1e6
            radius = item.GetWidth(pcbnew.F_Cu) / 2e6
            for layer in layers:
                mark_box(blocked[layer], x - radius, y - radius,
                         x + radius, y + radius, owner,
                         0.35 if only_names is not None else 0.15)
            via_forbidden.add(cell(x, y))
        else:
            start, end = item.GetStart(), item.GetEnd()
            x0, x1 = sorted((start.x / 1e6, end.x / 1e6))
            y0, y1 = sorted((start.y / 1e6, end.y / 1e6))
            half = item.GetWidth() / 2e6
            mark_box(blocked[item.GetLayer()], x0 - half, y0 - half,
                     x1 + half, y1 + half, owner,
                     0.35 if only_names is not None else 0.25)

    def allowed(route_cell, layer, net_code):
        x, y = route_cell
        if x < 4 or y < 4 or x >= grid_w - 4 or y >= grid_h - 4:
            return False
        owner = blocked[layer].get(route_cell)
        return owner is None or owner == net_code

    def reserve(route_cell, layer, net_code, radius=None):
        radius = reserve_radius if radius is None else radius
        cx, cy = route_cell
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                key = (cx + dx, cy + dy)
                owner = blocked[layer].get(key)
                if owner is None or owner == net_code:
                    blocked[layer][key] = net_code

    sequence = itertools.count()

    def find_path(starts, targets, net_code):
        targets = set(targets)
        queue, cost, parent = [], {}, {}

        def heuristic(state):
            x, y, _ = state
            return min(abs(x - tx) + abs(y - ty) for tx, ty, _ in targets)

        for state in starts:
            cost[state] = 0
            heapq.heappush(queue, (heuristic(state), next(sequence), state))
        found = None
        while queue:
            _, _, state = heapq.heappop(queue)
            if state in targets:
                found = state
                break
            x, y, layer = state
            base = cost[state]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt_cell = (x + dx, y + dy)
                nxt = (nxt_cell[0], nxt_cell[1], layer)
                if nxt not in targets and not allowed(nxt_cell, layer, net_code):
                    continue
                new_cost = base + 1
                if new_cost < cost.get(nxt, 1_000_000):
                    cost[nxt], parent[nxt] = new_cost, state
                    heapq.heappush(queue, (new_cost + heuristic(nxt),
                                           next(sequence), nxt))
            via_range = 9 if only_names is not None else 3
            via_blocked = any((x + dx, y + dy) in via_forbidden
                              for dx in range(-via_range, via_range + 1)
                              for dy in range(-via_range, via_range + 1))
            # A layer change places a full via, not a zero-width route point.
            # Keep its annulus clear of copper already reserved on either
            # outer signal layer.
            via_clearance = 3 if only_names is not None else 2
            via_blocked = via_blocked or any(
                blocked[copper_layer].get((x + dx, y + dy))
                not in (None, net_code)
                for copper_layer in layers
                for dx in range(-via_clearance, via_clearance + 1)
                for dy in range(-via_clearance, via_clearance + 1)
            )
            if not via_blocked:
                other = pcbnew.B_Cu if layer == pcbnew.F_Cu else pcbnew.F_Cu
                if allowed((x, y), other, net_code):
                    nxt = (x, y, other)
                    new_cost = base + 10
                    if new_cost < cost.get(nxt, 1_000_000):
                        cost[nxt], parent[nxt] = new_cost, state
                        heapq.heappush(queue, (new_cost + heuristic(nxt),
                                               next(sequence), nxt))
        if found is None:
            return None
        path = [found]
        while path[-1] not in starts:
            path.append(parent[path[-1]])
        path.reverse()
        return path

    def simplify(points):
        if len(points) < 3:
            return points
        result = [points[0]]
        for index in range(1, len(points) - 1):
            previous, current, following = result[-1], points[index], points[index + 1]
            if ((previous[0] == current[0] == following[0]) or
                    (previous[1] == current[1] == following[1])):
                continue
            result.append(current)
        result.append(points[-1])
        return result

    def add_via(net_item, x, y):
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pt(x, y))
        via.SetWidth(mm(0.70))
        via.SetDrill(mm(0.35))
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        via.SetNet(net_item)
        board.Add(via)

    def emit(net_item, path):
        segment = [path[0]]
        for previous, current in zip(path, path[1:]):
            if previous[2] != current[2]:
                if len(segment) > 1:
                    coords = simplify([point_mm((p[0], p[1])) for p in segment])
                    track(board, net_item, coords, route_width, segment[0][2])
                x, y = point_mm((previous[0], previous[1]))
                add_via(net_item, x, y)
                segment = [current]
            else:
                segment.append(current)
        if len(segment) > 1:
            coords = simplify([point_mm((p[0], p[1])) for p in segment])
            track(board, net_item, coords, route_width, segment[0][2])

    skip = {"+5V", "GND"}
    skip.update({f"CH{channel}_{kind}_OUT"
                 for channel in range(1, 7) for kind in ("DATA", "CLOCK")})
    manual_only = {
        "CH1_CLOCK_5V", "CH6_CLOCK_5V", "CH5_DATA_3V3",
        "CH5_CLOCK_3V3", "CH3_CLOCK_3V3", "CH2_CLOCK_3V3", "OE_N",
        "CH6_DATA_3V3", "CH3_DATA_3V3", "CH2_DATA_3V3",
        "ENABLE_GPIO", "ADDRESS", "3V3_LOCAL", "HEARTBEAT", "TEST",
    }
    if only_names is None:
        skip.update(manual_only)
    priority = []
    for channel in range(1, 7):
        priority += [f"CH{channel}_DATA_5V", f"CH{channel}_CLOCK_5V"]
    for channel in range(6, 0, -1):
        priority += [f"CH{channel}_CLOCK_3V3", f"CH{channel}_DATA_3V3"]
    priority += ["OE_N", "ENABLE_GPIO", "ENABLE_BASE", "ADDRESS",
                 "ADDR_A0", "ADDR_A1", "3V3_LOCAL", "SDA", "SCL",
                 "3V3_BRAIN", "HEARTBEAT", "TEST", "RESET",
                 "PWR_LED_A", "HEART_LED_A"]
    deferred = sorted(manual_only) if only_names is None else []

    for name in priority:
        if name in skip or (only_names is not None and name not in only_names):
            continue
        net_item = nets[name]
        net_code = net_item.GetNetCode()
        pads = [pad for pad in all_pads if pad.GetNetCode() == net_code]
        if len(pads) < 2:
            continue
        terminals = []
        for pad in pads:
            pos = pad.GetPosition()
            exact = (pos.x / 1e6, pos.y / 1e6)
            pad_layers = [layer for layer in layers if pad.IsOnLayer(layer)]
            terminals.append((cell(*exact), pad_layers, exact))

        root_cell, root_layers, root_exact = terminals[0]
        root_layer = root_layers[0]
        root = (root_cell[0], root_cell[1], root_layer)
        tree = {root}
        # Include deliberate pre-routed pad escapes in the connected tree.
        # This lets a control net begin from the far side of an escape via
        # instead of trying to rediscover a path through the MCU fanout.
        if root_escape is not None:
            escape_cell = cell(*root_escape)
            tree.add((escape_cell[0], escape_cell[1], pcbnew.F_Cu))
            tree.add((escape_cell[0], escape_cell[1], pcbnew.B_Cu))
        snapped = point_mm(root_cell)
        track(board, net_item, [root_exact, snapped], route_width, root_layer)
        reserve(root_cell, root_layer, net_code)

        remaining = list(terminals[1:])
        while remaining:
            terminal = min(
                remaining,
                key=lambda item: min(abs(item[0][0] - x) + abs(item[0][1] - y)
                                     for x, y, _ in tree),
            )
            remaining.remove(terminal)
            terminal_cell, pad_layers, exact = terminal
            starts = {(terminal_cell[0], terminal_cell[1], layer)
                      for layer in pad_layers}
            if terminal_escapes and exact in terminal_escapes:
                escape_cell = cell(*terminal_escapes[exact])
                starts.add((escape_cell[0], escape_cell[1], pcbnew.F_Cu))
            path = find_path(starts, tree, net_code)
            if path is None:
                print(f"No path for {name} to terminal {exact}; "
                      f"connected tree has {len(tree)} cells")
                deferred.append(name)
                break
            chosen_layer = path[0][2]
            track(board, net_item, [exact, point_mm(terminal_cell)],
                  route_width, chosen_layer)
            emit(net_item, path)
            for x, y, layer in path:
                reserve((x, y), layer, net_code)
                tree.add((x, y, layer))
            for previous, current in zip(path, path[1:]):
                if previous[2] != current[2]:
                    via_forbidden.add((previous[0], previous[1]))
    if deferred:
        print("Deferred manual routes: " + ", ".join(deferred))
    return deferred


def mom_heart_logo(board, center_x, center_y, scale=1.0):
    """Small one-color heart/smile factory mark for front silkscreen."""
    # Symmetric heart outline, intentionally redrawn as simple PCB geometry.
    heart = (
        (0.0, 3.4), (-3.4, 0.3), (-3.8, -1.2), (-3.3, -2.5),
        (-2.2, -3.1), (-1.0, -2.8), (0.0, -1.8),
        (1.0, -2.8), (2.2, -3.1), (3.3, -2.5), (3.8, -1.2),
        (3.4, 0.3), (0.0, 3.4),
    )
    points = [(center_x + x * scale, center_y + y * scale) for x, y in heart]
    for start, end in zip(points, points[1:]):
        silk_line(board, start, end, 0.32)

    # Upturned smile inside the lower half of the heart.
    smile = (
        (-2.0, 0.7), (-1.4, 1.2), (-0.7, 1.5),
        (0.0, 1.6), (0.7, 1.5), (1.4, 1.2), (2.0, 0.7),
    )
    points = [(center_x + x * scale, center_y + y * scale) for x, y in smile]
    for start, end in zip(points, points[1:]):
        silk_line(board, start, end, 0.32)


def outline(board, width, height, radius=3.0):
    # Rounded rectangle approximated with short segments for compatibility with
    # the KiCad Python API bundled on the development Mac.
    points = []
    corners = (
        (width - radius, radius, -90, 0),
        (width - radius, height - radius, 0, 90),
        (radius, height - radius, 90, 180),
        (radius, radius, 180, 270),
    )
    for cx, cy, start_deg, end_deg in corners:
        for step in range(7):
            angle = math.radians(start_deg + (end_deg - start_deg) * step / 6)
            points.append((cx + radius * math.cos(angle),
                           cy + radius * math.sin(angle)))
    points.append(points[0])
    for start, end in zip(points, points[1:]):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetStart(pt(*start))
        edge.SetEnd(pt(*end))
        edge.SetWidth(mm(0.1))
        board.Add(edge)


def build():
    board = pcbnew.BOARD()
    board.GetDesignSettings().SetCopperLayerCount(4)
    board.GetDesignSettings().m_MinClearance = mm(0.20)
    board.GetDesignSettings().m_MinThroughDrill = mm(0.30)
    board.GetDesignSettings().m_NetSettings.GetDefaultNetclass().SetClearance(mm(0.20))
    outline(board, 140, 65)

    parts = {}

    def add(library, name, ref, value, x, y, rotation=0):
        parts[ref] = footprint(board, library, name, ref, value, x, y, rotation)

    # Six edge-facing display channels. The S4B hole row also accepts B4B.
    output_x = (32, 51, 70, 89, 108, 127)
    for index, x in enumerate(output_x, 1):
        add("Connector_JST", "JST_XH_S4B-XH-A_1x04_P2.50mm_Horizontal",
            f"J{index}", f"CH{index} 5V GND DATA CLOCK", x, 10.5, 180)

    add("TerminalBlock_Phoenix", "TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal",
        "J7", "5V INPUT", 7.0, 13.0, 270)

    # KB2040 socket geometry: 15.24 mm row spacing, USB end at left edge.
    add("Connector_PinSocket_2.54mm", "PinSocket_1x13_P2.54mm_Vertical",
        "MCU1A", "KB2040 TOP ROW", 40.5, 41.0, 270)
    add("Connector_PinSocket_2.54mm", "PinSocket_1x13_P2.54mm_Vertical",
        "MCU1B", "KB2040 BOTTOM ROW", 10.02, 56.24, 90)

    for ref, x in (("U1", 41.5), ("U2", 79.5), ("U3", 117.5)):
        add("Package_DIP", "DIP-14_W7.62mm_Socket_LongPads", ref,
            "SN74AHCT125N", x, 34.5, 90)

    # Series resistors: vertical data/clock columns directly beneath each XH
    # connector. This gives every channel a short, visually obvious fan-out.
    for index, x in enumerate(output_x, 1):
        add("Resistor_THT", "R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal",
            f"R{index * 2 - 1}", "100R DATA", x - 5.0, 21.0, 90)
        add("Resistor_THT", "R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal",
            f"R{index * 2}", "100R CLOCK", x - 7.5, 21.0, 90)

    # Buffer support components.
    for i, x in enumerate((41.5, 79.5, 117.5), 1):
        add("Capacitor_THT", "C_Disc_D3.0mm_W1.6mm_P2.50mm", f"C{i}",
            "100nF", x, 46.0, 0)
    add("Capacitor_THT", "CP_Radial_D5.0mm_P2.00mm", "C4", "10uF", 18, 20)
    add("Capacitor_THT", "CP_Radial_D10.0mm_P5.00mm", "C5", "470uF", 10, 29)

    add("Package_TO_SOT_THT", "TO-92_Inline", "Q1", "2N3904 OE", 80, 50)
    for ref, value, x, y in (
        ("R13", "10k OE PULLUP", 68, 43),
        ("R14", "10k OE BASE", 68, 46),
        ("R15", "100k EN PULLDOWN", 68, 49),
        ("R16", "10k ADDR PULLUP", 88, 44),
        ("R17", "10k ADDR A0", 88, 47),
        ("R18", "20k ADDR A1", 88, 50),
        ("R19", "1k POWER LED", 22, 31),
        ("R20", "2k2 HEART LED", 68, 53),
    ):
        add("Resistor_THT", "R_Axial_DIN0204_L3.6mm_D1.6mm_P5.08mm_Horizontal",
            ref, value, x, y)

    add("LED_THT", "LED_D3.0mm", "D1", "GREEN POWER", 30, 31)
    add("LED_THT", "LED_D3.0mm", "D2", "RED HEARTBEAT", 76, 57)
    add("Button_Switch_THT", "SW_PUSH_6mm", "SW1", "TEST", 58, 57)
    add("Button_Switch_THT", "SW_PUSH_6mm", "SW2", "RESET", 48, 57)
    add("Connector_PinHeader_2.54mm", "PinHeader_2x02_P2.54mm_Vertical",
        "JP1", "ADDRESS A1/A0", 89, 56, 0)

    add("Connector_JST", "JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal",
        "J8", "I2C TO BRAIN", 123, 51.0, 180)
    add("Connector_JST", "JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal",
        "J9", "I2C THRU NO POWER", 123, 59.0, 180)
    add("Connector_PinHeader_2.54mm", "PinHeader_1x04_P2.54mm_Vertical",
        "J10", "I2C TEST", 123, 45.5, 90)
    add("Connector_JST", "JST_PH_B4B-PH-K_1x04_P2.00mm_Vertical",
        "J11", "SERVICE IO", 104, 56, 0)

    for i, (x, y) in enumerate(((5, 5), (135, 5), (5, 60), (135, 60)), 1):
        add("MountingHole", "MountingHole_3.2mm_M3", f"H{i}", "M3", x, y)

    names = {"+5V", "GND", "3V3_LOCAL", "3V3_BRAIN", "SDA", "SCL",
             "HEARTBEAT", "ADDRESS", "TEST", "RESET", "ENABLE_GPIO",
             "ENABLE_BASE", "OE_N", "PWR_LED_A", "HEART_LED_A",
             "ADDR_A0", "ADDR_A1"}
    for ch in range(1, 7):
        names.update({f"CH{ch}_DATA_3V3", f"CH{ch}_CLOCK_3V3",
                      f"CH{ch}_DATA_5V", f"CH{ch}_CLOCK_5V",
                      f"CH{ch}_DATA_OUT", f"CH{ch}_CLOCK_OUT"})
    nets = {name: net(board, name) for name in sorted(names)}

    # KB2040 socket pin map, matching Adafruit's physical silk.
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

    # AHCT125 gate pin groups: /OE, A, Y.
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
        for pin, name in ((1, "+5V"), (2, "GND"),
                          (3, f"CH{ch}_DATA_OUT"), (4, f"CH{ch}_CLOCK_OUT")):
            connect(parts, nets, f"J{ch}", pin, name)

    connect(parts, nets, "J7", 1, "+5V")
    connect(parts, nets, "J7", 2, "GND")
    for cap in ("C1", "C2", "C3", "C4", "C5"):
        connect(parts, nets, cap, 1, "+5V")
        connect(parts, nets, cap, 2, "GND")

    # Q1 uses the common 2N3904 TO-92 E-B-C lead order. The exact purchased
    # transistor must be checked against its datasheet before assembly.
    connect(parts, nets, "Q1", 1, "GND")
    connect(parts, nets, "Q1", 2, "ENABLE_BASE")
    connect(parts, nets, "Q1", 3, "OE_N")
    connect(parts, nets, "R13", 1, "+5V")
    connect(parts, nets, "R13", 2, "OE_N")
    connect(parts, nets, "R14", 1, "ENABLE_GPIO")
    connect(parts, nets, "R14", 2, "ENABLE_BASE")
    connect(parts, nets, "R15", 1, "ENABLE_GPIO")
    connect(parts, nets, "R15", 2, "GND")
    connect(parts, nets, "R16", 1, "3V3_LOCAL")
    connect(parts, nets, "R16", 2, "ADDRESS")
    connect(parts, nets, "R17", 1, "ADDR_A0")
    connect(parts, nets, "R17", 2, "GND")
    connect(parts, nets, "R18", 1, "ADDR_A1")
    connect(parts, nets, "R18", 2, "GND")
    connect(parts, nets, "JP1", 1, "ADDRESS")
    connect(parts, nets, "JP1", 2, "ADDR_A0")
    connect(parts, nets, "JP1", 3, "ADDRESS")
    connect(parts, nets, "JP1", 4, "ADDR_A1")

    connect(parts, nets, "R19", 1, "+5V")
    connect(parts, nets, "R19", 2, "PWR_LED_A")
    connect(parts, nets, "D1", 1, "PWR_LED_A")
    connect(parts, nets, "D1", 2, "GND")
    connect(parts, nets, "R20", 1, "HEARTBEAT")
    connect(parts, nets, "R20", 2, "HEART_LED_A")
    connect(parts, nets, "D2", 1, "HEART_LED_A")
    connect(parts, nets, "D2", 2, "GND")

    connect(parts, nets, "SW1", 1, "TEST")
    connect(parts, nets, "SW1", 2, "GND")
    connect(parts, nets, "SW2", 1, "RESET")
    connect(parts, nets, "SW2", 2, "GND")

    # JST-SH convention: 1 GND, 2 3V3, 3 SDA, 4 SCL.
    for ref in ("J8", "J9"):
        connect(parts, nets, ref, 1, "GND")
        connect(parts, nets, ref, 3, "SDA")
        connect(parts, nets, ref, 4, "SCL")
    connect(parts, nets, "J8", 2, "3V3_BRAIN")
    # J9.2 intentionally NC: unpowered I2C THRU.
    for pin, name in ((1, "GND"), (2, "3V3_BRAIN"), (3, "SDA"), (4, "SCL")):
        connect(parts, nets, "J10", pin, name)
    for pin, name in ((1, "GND"), (2, "HEARTBEAT"),
                      (3, "TEST"), (4, "RESET")):
        connect(parts, nets, "J11", pin, name)

    text(board, "BU-22 DISPLAY CONTROLLER V1 REV A", 70, 61.0, 1.0,
         layer=pcbnew.B_SilkS)
    text(board, "PRELIMINARY - DO NOT FABRICATE", 70, 4.0, 0.8,
         layer=pcbnew.F_Fab)
    text(board, "USB", 2.5, 39.5, 1.0, 90)
    text(board, "5V IN", 4.5, 27, 0.9, 90)
    text(board, "D1 POWER", 30, 34.0, 0.75)
    text(board, "D2 HEART", 76, 63.0, 0.75)
    text(board, "SW1 TEST", 58, 63.0, 0.75)
    text(board, "SW2 RESET", 48, 63.0, 0.75)
    text(board, "JP1 ADDRESS", 89, 62, 0.75)
    text(board, "A0", 86.5, 51.0, 0.8)
    text(board, "A1", 91.5, 51.0, 0.8)
    text(board, "J8 TO BRAIN", 123, 48.5, 0.7)
    text(board, "J9 I2C THRU NO POWER", 123, 62.0, 0.6)
    text(board, "J10 I2C TEST", 123, 40.5, 0.7)
    text(board, "J11 SERVICE", 104, 62.0, 0.7)
    text(board, "GND HB TEST RST", 104, 51.0, 0.60)
    text(board, "MCU1 ADAFRUIT KB2040", 25, 49.0, 0.9)
    for i, x in enumerate(output_x, 1):
        text(board, f"J{i} CH{i}", x, 16.5, 1.15)

    # Human-readable assembly values. References are also visible on F.SilkS.
    for index, x in enumerate(output_x, 1):
        text(board, f"R{index * 2 - 1}", x - 5.0, 24.2, 0.58)
        text(board, f"R{index * 2}", x - 7.5, 24.2, 0.58)
    for index, x in enumerate((41.5, 79.5, 117.5), 1):
        text(board, f"C{index} 100n", x, 48.2, 0.58)
    text(board, "C4 10u", 18, 23.5, 0.65)
    text(board, "C5 470u", 10, 35.0, 0.65)
    text(board, "Q1 2N3904", 80, 46.5, 0.65)
    for label, x, y in (
        ("R13 10k", 68, 41.2), ("R14 10k", 68, 44.2),
        ("R15 100k", 68, 47.2), ("R16 10k", 88, 42.2),
        ("R17 10k", 88, 45.2), ("R18 20k", 88, 48.2),
        ("R19 1k", 22, 29.2), ("R20 2k2", 68, 51.0),
    ):
        text(board, label, x, y, 0.58)
    for index, x in enumerate((41.5, 79.5, 117.5), 1):
        text(board, f"U{index} AHCT125", x, 36.8, 0.58)

    # Found-artifact equipment identification and capacitor-sized factory mark.
    text(board, "BENDING UNIT 22", 128, 36.5, 0.80)
    text(board, "DISPLAY CONTROL MODULE", 128, 38.5, 0.70)
    text(board, "SERIAL #2716057", 128, 40.5, 0.75)
    mom_heart_logo(board, 133, 46.0, 1.0)

    # Four-layer stack: signals on the outer layers, uninterrupted ground on
    # In1.Cu, and 5 V distribution on In2.Cu.
    power = nets["+5V"]
    ground = nets["GND"]
    copper_plane(board, ground, pcbnew.In1_Cu)
    copper_plane(board, power, pcbnew.In2_Cu)

    # Short final-stage signal runs from each source resistor to its XH port.
    # Keeping these local and on F.Cu avoids vias at the removable cable edge.
    for channel, connector_x in enumerate(output_x, 1):
        data_net = nets[f"CH{channel}_DATA_OUT"]
        clock_net = nets[f"CH{channel}_CLOCK_OUT"]
        data_pad_x = connector_x - 5.0
        clock_pad_x = connector_x - 7.5
        track(board, data_net, [(data_pad_x, 15.92), (data_pad_x, 10.5)], 0.35)
        track(board, clock_net, [(clock_pad_x, 15.92), (clock_pad_x, 10.5)], 0.35)

    # Route the shared active-low output-enable backbone before the channel
    # signals so subsequent routes treat it as a fixed constraint. Each DIP's
    # top-row OE pins escape beyond the socket ends; this avoids every PTH pad.
    oe = nets["OE_N"]
    track(board, oe, [(35.5, 39.0), (136.0, 39.0)], 0.25, pcbnew.B_Cu)
    for center_x in (41.5, 79.5, 117.5):
        track(board, oe,
              [(center_x, 34.5), (center_x, 39.0)],
              0.25, pcbnew.B_Cu)
        track(board, oe,
              [(center_x + 7.62, 34.5), (center_x + 7.62, 39.0)],
              0.25, pcbnew.B_Cu)
        track(board, oe,
              [(center_x + 2.54, 26.88), (center_x + 2.54, 24.5),
               (center_x - 6.0, 24.5), (center_x - 6.0, 39.0)],
              0.25, pcbnew.B_Cu)
        track(board, oe,
              [(center_x + 10.16, 26.88), (center_x + 10.16, 24.5),
               (center_x + 18.5, 24.5), (center_x + 18.5, 39.0)],
              0.25, pcbnew.B_Cu)
    track(board, oe, [(73.08, 43.0), (73.08, 39.0)], 0.25, pcbnew.B_Cu)
    track(board, oe,
          [(82.54, 50.0), (85.0, 50.0), (85.0, 39.0)],
          0.25, pcbnew.B_Cu)

    # Begin the new routing from a clean four-layer baseline. Remaining outer
    # layer signals are added in deliberate channel/control groups below.
    autoroute_signals(
        board,
        parts,
        nets,
        {
            f"CH{channel}_{kind}_5V"
            for channel in range(1, 7)
            for kind in ("DATA", "CLOCK")
        },
    )
    autoroute_signals(
        board,
        parts,
        nets,
        {"CH1_DATA_3V3", "CH1_CLOCK_3V3"},
    )
    autoroute_signals(
        board,
        parts,
        nets,
        {"CH5_DATA_3V3", "CH5_CLOCK_3V3"},
    )
    autoroute_signals(
        board,
        parts,
        nets,
        {
            f"CH{channel}_{kind}_3V3"
            for channel in (2, 3, 4, 6)
            for kind in ("DATA", "CLOCK")
        },
    )
    autoroute_signals(
        board,
        parts,
        nets,
        {"SDA", "SCL"},
    )
    autoroute_signals(
        board,
        parts,
        nets,
        {"ENABLE_BASE", "PWR_LED_A", "HEART_LED_A", "ADDR_A0", "ADDR_A1"},
    )
    # RESET is intentionally deferred for a short manual route after the
    # remaining control nets establish the lower-board routing channels.
    for control_net in ("TEST", "HEARTBEAT", "ENABLE_GPIO"):
        autoroute_signals(board, parts, nets, {control_net})

    # Remaining functional support wiring. The brain-side 3.3 V rail is only
    # passed between the I2C input and test header; it never powers the local
    # controller. Local 3.3 V feeds only the address-selection pull-up.
    autoroute_signals(board, parts, nets, {"3V3_BRAIN"})
    autoroute_signals(board, parts, nets, {"3V3_LOCAL"},
                      reserve_radius_override=2)

    # J8/J9 are SMD Qwiic footprints, so their ground pads need explicit vias
    # into the uninterrupted In1.Cu ground plane. PTH ground pads connect to
    # that plane directly.
    via(board, ground, 124.5, 53.0)
    via(board, ground, 124.5, 61.0)

    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pcbnew.SaveBoard(str(OUTPUT), board)
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    build()
