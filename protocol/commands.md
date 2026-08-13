# BU-22 display protocol — raw validation experiment

This is a deliberately temporary, minimal protocol used to verify the physical
I2C connection and CircuitPython target support.

The feature-oriented semantic draft is maintained separately in
`semantic_protocol_v0.md`. Values in this file must not be treated as final
production command assignments.

## Addresses

| Module | Address |
|---|---:|
| Eyes | `0x30` |
| Mouth (reserved) | `0x31` |

## Brain-to-Eyes commands

Every transaction contains exactly one byte.

| Value | Name | Meaning |
|---:|---|---|
| `0x00` | `CLEAR` | Immediately display black on every eye LED |
| `0x01` | `IDENTIFY` | Briefly illuminate every eye channel amber |

There are no responses, parameters, status registers, retries, or checksums in
this first experiment. Those should be designed only after this basic path is
confirmed on the real hardware.
