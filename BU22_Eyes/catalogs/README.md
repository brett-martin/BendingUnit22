# BU-22 Eyes content catalogs

These catalogs are experimental before v1. They may be reorganized or reset
while the first firmware and simulator export are still being developed.

At v1, the reviewed numeric IDs become stable. After that:

- Existing IDs are not renumbered, removed, or reused.
- New content is appended.
- Rendering and timing may improve without changing an ID when the semantic
  meaning remains the same.
- A meaningfully different variation receives a new ID, such as `BLINK_FAST`.

The Brain transmits numeric IDs. Human-readable names are used by source code,
the simulator, documentation, and generated tools.
