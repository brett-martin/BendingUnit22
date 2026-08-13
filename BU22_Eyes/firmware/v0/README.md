# BU-22 Eyes firmware v0 slice

This is the first clean implementation of the draft wire protocol on the 6×4
breadboard display. It supports:

- `SHOW_NORMAL`
- `SHOW_EXPRESSION`
- `PLAY_ANIMATION`
- `STOP`
- `SET_OFF`
- Dedicated global `PLAY_VISOR_DOWN` and `PLAY_VISOR_UP` row transitions
- Immediate command interruption
- Locally timed animations returning to Normal
- Visor Down interrupts activity, blanks full rows top-to-bottom, and ends Off
- Visor Up reveals Normal rows bottom-to-top and ends Normal
- Proven 20-byte status; on an unknown-content error, `active_content_id` is
  the missing ID and `last_command` identifies its category
- Visible red error pattern for unknown expressions/animations
- Five-second standalone Normal fallback

It intentionally omits performances, Clock, Message, settings persistence, raw
frames, and the local test button until this vertical slice is validated.

## Display orientation

Expressions are authored in logical top-left orientation. The current
breadboard is physically rotated 180 degrees, so `config.ROTATE_DISPLAY_180`
maps logical column `x` to physical channel `5-x` and logical row `y` to
physical pixel `3-y`. Future hardware can disable the transform without
changing expression or animation data.

Facial symmetry is handled separately from hardware orientation. Angry eyelid
patterns use a right-eye source shape and mirror it only for the left eye so
both lids slope inward. Gaze expressions are not mirrored because both pupils
must move in the same physical direction. At extreme left/right gaze, the full
outside pupil-side column is black, including its top and bottom LEDs.

## Serial action log

`config.ACTION_LOGGING` defaults to `True` for development. Eyes prints only
semantic commands and meaningful state changes: expressions, animation start
and completion, STOP, Off, visor transitions, missing-content errors, and
communication fallback. It does not print individual frames, rows, or pixels.
Set the option to `False` when quiet serial output is preferred.
