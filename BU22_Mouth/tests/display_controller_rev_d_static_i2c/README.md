# Rev D half-scale static Mouth I2C test

Protocol-capable static test treating three `5 x 11` serpentine mouth tiles as
one `15 x 11` display. CH6 renders the left tile and CH5 the center tile. For
diagnosis, the rightmost tile pattern is duplicated on CH1 through CH4 so the
same physical tile can test any of those connectors. On startup it displays
Normal; Brain commands select Normal,
Open, or Off. The logical grid repeats three lit rows or columns followed by
one dark separator across the complete display; physical tile boundaries do
not define the grid. Open bows the two dark horizontal lines away from each
other near the center.

The Rev D A3 jumper network selects the target address at startup. This board
should be jumpered as Mouth and report `0x31`.
