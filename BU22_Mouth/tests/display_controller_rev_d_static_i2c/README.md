# Rev D half-scale static Mouth I2C test

Protocol-capable static test treating three `5 x 11` serpentine mouth tiles as
one `15 x 11` display. The installed order is CH6, CH5, and CH4 from physical
left to right. On startup it displays Normal; Brain commands
select Normal, Open, or Off. Normal uses a dark horizontal tooth separator and
vertical tile separators. Open bows two dark boundaries away from each other
near the center.

The Rev D A3 jumper network selects the target address at startup. This board
should be jumpered as Mouth and report `0x31`.
