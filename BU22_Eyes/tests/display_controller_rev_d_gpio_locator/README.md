# Rev D GPIO-to-output locator

This meter-friendly diagnostic empirically maps the KB2040 `D2` through `D9`
GPIO names to the physical CH1 through CH4 output pins. It makes no assumption
about the MCU1B socket pad orientation. Only one candidate GPIO is high at a
time; all other candidates remain low.

Disconnect LED arrays. Probe one connector signal pin, watch the visible serial
terminal, and record which named GPIO causes that physical pin to go high.
