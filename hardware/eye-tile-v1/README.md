# BU-22 Eye Tile V1 — Locked Design Direction

This document records the component-agnostic architecture for the first
manufactured BU-22 eye tile. Exact LED, capacitor, connector, and assembly
part numbers remain open until sourcing and hardware comparison tests are
complete.

## Locked display architecture

- The complete eye display is `36 x 16` pixels.
- It is assembled from four identical `9 x 16` eye tiles arranged
  horizontally.
- Nominal pixel pitch is approximately 4 mm, subject only to final mechanical
  verification against the visor and diffuser.
- A tile is electrically self-contained as one display channel.
- Four tiles provide four independent controller channels while forming one
  continuous display surface.
- Pixel mapping and physical orientation will be normalized in display
  firmware, so the Brain remains independent of tile wiring order.

## Mechanical and optical rules

- LEDs occupy nearly the entire front surface.
- Left and right edges contain no mounting holes, connectors, or protruding
  components; identical tiles must meet with a consistent pixel pitch across
  each seam.
- Connectors and mounting features belong above or below the active LED area,
  or on the rear.
- The front remains clear for a flush egg-crate light baffle and flat diffuser.
- The board and baffle must provide repeatable mechanical registration so the
  four grids align as one `36 x 16` matrix.
- The eye motherboard provides the visor-sized mounting structure and tile
  sockets; the expensive LED tiles remain simple and replaceable.

## Electrical rules

- The tile uses a clocked, individually addressable RGB LED architecture with
  5 V, ground, clock, and data.
- APA102-2020 and SK9822-EC20 remain candidate components; the exact device is
  not locked yet.
- Use a four-layer PCB with robust 5 V and ground planes.
- Route the pixels as a compact serpentine chain.
- Size tile power entry, connector contacts, planes, and traces for one full
  `9 x 16` tile independently of the other tiles.
- Provide accessible 5 V and ground test pads at the power entry and far end.
- Provide clock/data test pads at useful chain boundaries.
- No display-controller, level-shifter, MCU, or unrelated electronics belong
  on the LED tile.

## Capacitor strategy

- Do not populate a capacitor at every LED in the initial assembly.
- Include one optional, rear-side `0603` decoupling-capacitor footprint for
  every pixel.
- Mark all per-pixel capacitor positions DNP for the initial build.
- Arrange the optional footprints so they can be hand-soldered after assembly.
- Include shared distributed-capacitance footprints, nominally 10–47 uF.
- Include an optional 220–470 uF bulk-capacitor footprint near power entry.
- The board must have adequate power integrity without relying on populated
  per-pixel capacitors; optional capacitors are a diagnostic and refinement
  mechanism, not a substitute for proper planes.

The planned validation sequence is:

1. Test with bulk/distributed capacitance only.
2. If needed, populate every fourth or eighth per-pixel footprint.
3. Populate all per-pixel footprints only if measurements or visible behavior
   justify it.

## Reference concept

The Adafruit DotStar High Density 8x8 Grid (product 3444) is the conceptual
reference for dense LED placement, edge-aware tiling, four-layer power
distribution, and operation without populated per-pixel capacitors. The BU-22
tile is a new design with different geometry, pitch, connectors, channel
partitioning, mounting, and optical requirements.

## Decisions intentionally left open

- APA102-2020 versus SK9822-EC20
- Exact LED manufacturer and assembly source
- Exact connector family and rear/top/bottom orientation
- Final bulk and distributed capacitor values
- Whether any optional per-pixel capacitors are populated in production
- Final board outline after mechanical measurements
