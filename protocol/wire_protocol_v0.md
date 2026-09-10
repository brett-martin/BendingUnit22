# BU-22 display wire protocol — draft v0

This document encodes the actions in `semantic_protocol_v0.md` into a compact
I2C protocol for Eyes and Mouth. It is the first implementation draft, not a
frozen public API.

## Physical assumptions

- I2C controller: Brain
- I2C targets: display modules
- Default Eyes address: `0x30`
- Default Mouth address: `0x31`
- Bus speed: 100 kHz initially
- SDA and SCL pulled up once to the Brain's 3.3 V rail
- All modules share ground
- Modules are not powered through the Qwiic power conductor during USB testing

Configurable address pads may alter the final addresses. The defaults above
remain the development and documentation addresses.

## Encoding conventions

- Each Brain write is one complete I2C transaction.
- Byte 0 is always the command.
- Remaining bytes are command arguments.
- Multi-byte integers are unsigned and big-endian.
- Identifiers are 16-bit values unless stated otherwise.
- Brightness is `0..255`.
- RGB colors are three bytes: red, green, blue.
- Boolean values are `0` or `1`.
- Text is UTF-8, limited initially to printable ASCII for the built-in font.
- Packets are limited to 32 bytes in v0.
- No packet length field is needed because I2C preserves transaction boundaries.
- No application checksum is included in v0. I2C already provides per-byte ACK
  and the module rejects malformed transaction lengths.

## Request tag

Every visual activity command includes a one-byte `tag` selected by the Brain.
The display echoes the most recently accepted tag in status.

The Brain normally increments the tag modulo 256. The tag lets it distinguish
completion of the requested activity from stale status belonging to an older
activity. A tag is an identifier, not a queue position.

Settings, message-transfer, identify, and maintenance commands do not require a
tag because they are applied immediately and are not timed visual activities.

## Command summary

### Immediate visual control — `0x10..0x1F`

| Byte | Command | Arguments |
|---:|---|---|
| `0x10` | `SHOW_NORMAL` | `tag` |
| `0x11` | `SHOW_EXPRESSION` | `tag, expression_id:u16` |
| `0x12` | `PLAY_ANIMATION` | `tag, animation_id:u16` |
| `0x13` | `PLAY_PERFORMANCE` | `tag, performance_id:u16` |
| `0x14` | `STOP` | `tag` |
| `0x15` | `SET_OFF` | `tag` |
| `0x16` | `PLAY_VISOR_DOWN` | `tag, step_ms:u16` |
| `0x17` | `PLAY_VISOR_UP` | `tag, step_ms:u16` |
| `0x18` | `PLAY_ANIMATION_TIMED` | `tag, animation_id:u16, entry_ms:u16, hold_ms:u16, exit_ms:u16` |

Every command in this group immediately interrupts the current visual activity.
There is no display-side command queue and interrupted activities do not resume.

`SHOW_NORMAL` and `STOP` both finish at Normal. They remain separate semantic
commands so status can distinguish a requested visual state from an emergency
or mode-change cancellation.

`PLAY_ANIMATION_TIMED` uses the animation's authored entry and exit sequences,
but retimes each phase to the supplied millisecond duration. Controllers sample
no faster than the catalog's global maximum display FPS, hold or skip authored
frames deterministically, and always display each phase's final frame.

### Clock and message — `0x20..0x2F`

| Byte | Command | Arguments |
|---:|---|---|
| `0x20` | `SHOW_CLOCK` | `tag, hour, minute, flags` |
| `0x21` | `UPDATE_CLOCK` | `hour, minute` |
| `0x22` | `SHOW_MESSAGE` | `tag, flags` |
| `0x23` | `MESSAGE_BEGIN` | `total_length:u8` |
| `0x24` | `MESSAGE_CHUNK` | `offset:u8, data:0..30 bytes` |
| `0x25` | `MESSAGE_COMMIT` | `expected_length:u8` |
| `0x26` | `MESSAGE_ABORT` | none |
| `0x27` | `RESET_MESSAGE` | none |

Clock flags:

| Bit | Meaning |
|---:|---|
| 0 | Colon blinks locally when set; remains solid when clear |
| 1 | Render in 24-hour format when set; 12-hour format when clear |
| 2–7 | Reserved, send zero |

Hours use display-ready local time from the Brain. Valid ranges are hour
`0..23` and minute `0..59`. The Brain owns RTC, timezone, DST, and the user's
12/24-hour preference; Eyes performs only the requested rendering.

Message flags:

| Bit | Meaning |
|---:|---|
| 0 | Repeat scrolling |
| 1 | Hold final frame instead of returning to the beginning |
| 2–7 | Reserved, send zero |

The persisted message is at most 128 bytes. Replacement is atomic:

1. `MESSAGE_BEGIN(total_length)` creates a temporary buffer.
2. One or more `MESSAGE_CHUNK(offset, data)` writes populate it.
3. `MESSAGE_COMMIT(expected_length)` validates, persists, and activates it as
   the stored message.
4. Any validation failure retains the previous stored message.
5. `MESSAGE_ABORT` discards the temporary buffer.

`RESET_MESSAGE` restores `Please Insert Girder`.

Clock- or message-specific appearance uses `SET_TEMP_BRIGHTNESS` and
`SET_TEMP_COLOR` before entering the mode, followed by the corresponding clear
commands when the override ends. This avoids duplicating color and brightness
arguments in every visual command.

### Brightness and color — `0x30..0x3F`

| Byte | Command | Arguments | Persistence |
|---:|---|---|---|
| `0x30` | `SET_GLOBAL_BRIGHTNESS` | `level` | Persisted |
| `0x31` | `SET_TEMP_BRIGHTNESS` | `level` | Volatile |
| `0x32` | `CLEAR_TEMP_BRIGHTNESS` | none | Volatile |
| `0x33` | `SET_GLOBAL_COLOR` | `R, G, B` | Persisted |
| `0x34` | `SET_TEMP_COLOR` | `R, G, B` | Volatile |
| `0x35` | `CLEAR_TEMP_COLOR` | none | Volatile |

Global settings take effect immediately and are written only when explicitly
changed by the user. Temporary settings take effect immediately without a
persistent-memory write. Clearing a temporary override reveals the current
global value.

### Development and maintenance — `0x70..0x7F`

| Byte | Command | Arguments |
|---:|---|---|
| `0x70` | `SHOW_RAW_FRAME_CHUNK` | `tag, frame_offset:u16, data:0..28 bytes` |
| `0x71` | `SHOW_RAW_FRAME_COMMIT` | `tag, frame_length:u16` |
| `0x72` | `IDENTIFY` | none |
| `0x73` | `EXIT_LOCAL_TEST` | none |
| `0x74` | `CLEAR_ERROR` | none |
| `0x75` | `SHOW_DEV_TEXT` | `tag, ASCII text:1..29 bytes` |
| `0x7F` | `FACTORY_RESET_SETTINGS` | confirmation bytes `0x22, 0xA5` |

Raw frames are for hardware validation, simulator preview, and development.
Normal operation should request stored semantic content. The module keeps a
temporary raw-frame buffer so a hardware-sized frame may exceed one packet.

`SHOW_DEV_TEXT` is a volatile Rev D development aid for button-driven mode and
test-selection feedback. It scrolls one centered line once and then clears the
display. It does not replace or persist the normal message buffer.

Factory reset restores safe brightness/color defaults and the message
`Please Insert Girder`. The two confirmation bytes reduce accidental resets;
the Brain UI should still require explicit user confirmation.

## Status readback

The Brain reads a fixed 20-byte status record directly from the module. No
selector write is conceptually required. If a CircuitPython target
implementation needs a preparatory request, it may temporarily use an internal
`PREPARE_STATUS` command without changing the contents below.

| Offset | Field | Size | Meaning |
|---:|---|---:|---|
| 0 | `magic` | 1 | `0x22` for a BU-22 module |
| 1 | `protocol_major` | 1 | `0` for this draft |
| 2 | `protocol_minor` | 1 | Initial value `2` for named local modes |
| 3 | `module_type` | 1 | `1=Eyes`, `2=Mouth` |
| 4 | `firmware_major` | 1 | Firmware version |
| 5 | `firmware_minor` | 1 | Firmware version |
| 6 | `lifecycle_state` | 1 | Lifecycle enumeration |
| 7 | `display_state` | 1 | Visual-state enumeration |
| 8 | `activity_state` | 1 | Activity enumeration |
| 9 | `active_tag` | 1 | Tag of current/latest visual request |
| 10 | `last_command` | 1 | Most recently accepted command byte |
| 11 | `error_code` | 1 | Current error enumeration |
| 12–13 | `active_content_id` | 2 | Expression/animation/performance identifier |
| 14 | `global_brightness` | 1 | Stored level |
| 15 | `effective_brightness` | 1 | Level currently applied |
| 16 | `flags` | 1 | Status flag bits |
| 17 | `i2c_address` | 1 | Active address |
| 18–19 | `feature_flags` | 2 | Supported optional features |

Status flags:

| Bit | Meaning |
|---:|---|
| 0 | Brain communication has been observed within timeout |
| 1 | Local `TEST` mode active |
| 2 | Temporary brightness override active |
| 3 | Temporary color override active |
| 4 | Timed activity busy |
| 5 | Most recent tagged activity completed normally |
| 6 | Local `BENDER` mode active |
| 7 | Persistent settings passed integrity validation |

The completion bit describes `active_tag`. A replacement command immediately
changes `active_tag` and clears completion. This prevents the Brain from
mistaking completion of an older activity for the current one.

### Development local modes

The Rev D controller button cycles three named local modes. They are derived
from lifecycle and status flags without changing the fixed 20-byte record:

| Name | Lifecycle | Status flags | Visual commands |
|---|---|---|---|
| `TARGET` | Waiting for Brain or Brain Controlled | Bits 1 and 6 clear | Accepted |
| `TEST` | Local Test | Bit 1 set | Rejected with error 10 |
| `BENDER` | Standalone Normal | Bit 6 set | Rejected with error 10 |

Identity and status reads remain available in every mode. Software APIs expose
`0=TARGET`, `1=TEST`, and `2=BENDER`; variable-length names are not placed in
the status packet.

## Enumerations

### Module type

| Value | Meaning |
|---:|---|
| 1 | Eyes |
| 2 | Mouth |

### Lifecycle state

| Value | Meaning |
|---:|---|
| 0 | Booting |
| 1 | Waiting for Brain |
| 2 | Standalone Normal |
| 3 | Brain Controlled |
| 4 | Local Test |
| 5 | Error |

### Display state

| Value | Meaning |
|---:|---|
| 0 | Normal |
| 1 | Static Expression |
| 2 | Animation |
| 3 | Performance |
| 4 | Clock |
| 5 | Message |
| 6 | Off |
| 7 | Raw Frame |
| 8 | Local Test |
| 9 | Error Display |

### Activity state

| Value | Meaning |
|---:|---|
| 0 | Idle/static |
| 1 | Running |
| 2 | Complete |
| 3 | Interrupted |
| 4 | Waiting for data/commit |

### Error code

| Value | Meaning |
|---:|---|
| 0 | No error |
| 1 | Unknown command |
| 2 | Incorrect packet length |
| 3 | Invalid argument |
| 4 | Unknown content identifier |
| 5 | Unsupported feature |
| 6 | Transfer incomplete or invalid |
| 7 | Persistent-settings integrity failure |
| 8 | Rendering/data failure |
| 9 | Hardware initialization failure |
| 10 | Busy in local `TEST` or `BENDER` mode |

An unknown content identifier enters the visible Error Display during
development. `active_content_id` contains the requested missing ID and
`last_command` identifies whether the failed request was an expression,
animation, or performance. The next valid visual command clears the visible
error and executes normally. A later production policy may choose a quieter
Normal fallback while preserving status.

## Content catalogs and compatibility

Expressions, animations, and performances use separate zero-based 16-bit ID
spaces. Human-readable names exist in source and simulator data; only the
numeric ID crosses I2C.

Before v1, catalogs are experimental and may be reset or reorganized while the
system is developed. At the v1 release, the reviewed IDs become stable. After
v1:

- Existing IDs are not renumbered, removed, or reused.
- New entries are appended.
- An existing entry may gain improved rendering or timing if its semantic
  meaning remains the same.
- A meaningfully different behavior receives a new ID, such as `BLINK_FAST`.

This allows Brain and display implementations to improve independently while a
request such as `PLAY_ANIMATION(BLINK)` retains its meaning.

## Feature flags

Feature bits allow Brain firmware to work with different display revisions.

| Bit | Capability |
|---:|---|
| 0 | Static expressions |
| 1 | Local animations |
| 2 | Local module performances |
| 3 | Clock renderer |
| 4 | Message renderer and persistent message |
| 5 | Visor renderer |
| 6 | RGB color control |
| 7 | Per-pixel brightness/raw frame |
| 8 | Local test button |
| 9 | Persistent settings |
| 10–15 | Reserved |

Eyes and Mouth may report different feature sets while using the same core
status layout and common commands.

## Command acceptance and interruption

- A well-formed visual command is acknowledged at the I2C transport level and
  becomes visible through `last_command`, `active_tag`, and status.
- Every new visual command immediately cancels the previous visual activity.
- No queued commands are retained by the display.
- Settings commands do not interrupt visual activity unless applying the new
  value inherently changes its appearance.
- Message upload commands do not display partial text.
- A valid Brain visual command immediately exits Local Test.
- Unknown or malformed commands do not replace the current valid display.

## Animation and performance data inside the module

The wire protocol selects stored content; it does not stream its timing steps.
A locally stored performance is conceptually:

```text
performance_id: angry_reaction
steps:
  normal       300 ms
  angry_1      500 ms
  angry_2     2000 ms
  angry_1      300 ms
  normal
```

The final storage format may be CircuitPython data, generated binary data, or a
compiled lookup table. It is independent of this wire protocol.

Animations and module performances return to Normal when complete. Visor Down
and Visor Up are dedicated global renderer transitions, not entries in the
animation catalog. Visor Down blanks complete rows top-to-bottom and finishes
Off. Visor Up reveals Normal rows bottom-to-top and finishes Normal.

## Startup and recovery

1. Module boots with LEDs black.
2. Module loads and validates persistent settings.
3. Module enters Waiting for Brain for approximately five seconds.
4. If no valid Brain transaction arrives, it enters Standalone Normal.
5. It continues listening indefinitely.
6. The first valid Brain visual command enters Brain Controlled and executes.
7. If communication later disappears, timed activity is cancelled and the
   module returns to Standalone Normal after the timeout.

The Brain periodically polls status while connected. On a missing target or
I2C error, it continues running, rescans, and reinitializes the returned module
with global settings followed by the desired visual state.

## CircuitPython v0 implementation note

Breadboard validation showed that the current CircuitPython I2C target loop
needs approximately 20 ms between immediately consecutive Brain transactions
so the target can return to listening. This is an implementation pacing value,
not part of the permanent semantic contract. The Brain v0 transport helper
should apply the delay centrally and future firmware/hardware can retest and
reduce it.

At 100 kHz, the tested 25-byte frame packets sustained 10 FPS with no late
frames. Production operation is expected to use stored expressions and local
timelines rather than continuous frame streaming.
