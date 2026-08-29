# Bending Unit 22 workspace guidance

Before changing hardware tests or firmware, read `CURRENT_STATUS.md` and the
applicable record under `hardware/bringup/`.

- The Git repository is the source of truth. `CIRCUITPY` is a deployment
  target, never the only copy of firmware.
- Confirm the mounted board ID in `CIRCUITPY/boot_out.txt` before copying code.
- Do not infer that a physical test passed merely because firmware was written.
  Record only results explicitly observed at the bench.
- Update the relevant bring-up record after a physical test changes what is
  known about a board.
- Preserve the Rev D GPIO map in the controller test unless the PCB itself is
  revised.
- Display Controller Rev D has a known D1/D2 polarity-silkscreen error. Read
  `hardware/display-controller-rev-d/ERRATA.md` before assembly.
