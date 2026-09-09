# Rev D half-scale static Eyes I2C test

Protocol-capable static test for two `9 x 16` serpentine eye tiles. The physical
left eye is on CH6 and the physical right eye is on CH5. On startup it displays
Normal; Brain commands select Normal, Angry, or Off. It uses the existing
`SHOW_NORMAL`, `SHOW_EXPRESSION`, and `SET_OFF` protocol operations and returns
the proven 20-byte status structure.

The Rev D A3 jumper network still selects the target address at startup. This
board should be jumpered as Eyes and report `0x30`.
