# BU-22 display protocol — semantic draft v0

This document defines what the Brain may ask a display module to do. It does
not assign command bytes or prescribe the final binary packet format.

The first corresponding binary encoding is documented in
`wire_protocol_v0.md`.

The raw breadboard commands in `commands.md` remain a separate hardware test
protocol.

## Ownership

- The Brain owns Bender's operating mode, orchestration, sensors, user input,
  RTC, audio timing, and coordination between Eyes, Mouth, and Antenna.
- Each display module owns its pixels, rendering, stored expressions, stored
  animations, locally accurate timing, persistent display settings, and local
  diagnostic button.
- Display modules do not autonomously schedule idle animations.
- A valid Brain display command immediately exits local test mode.

## Terms

### Display state

A persistent visual state that remains until replaced:

- Normal
- Static expression
- Clock
- Message
- Off
- Local test

### Expression

A named, static arrangement of pixels with no timing information.

Examples: `normal`, `angry_1`, `angry_2`, `bored`, `look_left`, `closed`.

### Animation

A finite, locally stored sequence of display states and durations. Animations
normally return to Normal.

Visor movement is a dedicated global display transition rather than cataloged
animation content. Visor Down interrupts all activity, turns off complete pixel
rows sequentially from top to bottom, and finishes Off. Visor Up starts black,
reveals Normal rows from bottom to top, and finishes Normal.

### Module performance

A longer, finite, locally stored timeline of expressions or display states and
durations. A module performance normally returns to Normal. It contains only
the activity for that module; the Brain coordinates the complete Bender
performance across modules and audio.

## Brain-to-display actions

### Core control

| Action | Arguments | Result |
|---|---|---|
| `SHOW_NORMAL` | none | Interrupt activity and show the module's Normal state |
| `SHOW_EXPRESSION` | expression identifier | Interrupt activity and hold the selected static expression |
| `PLAY_ANIMATION` | animation identifier | Interrupt activity and play a locally stored finite animation |
| `PLAY_PERFORMANCE` | performance identifier | Interrupt activity and play a locally stored finite module performance |
| `STOP` | none | Interrupt activity and show Normal |
| `SET_OFF` | none | Interrupt activity, render black, and remain Off |
| `PLAY_VISOR_DOWN` | optional speed | Animate the eye visor downward and finish Off |
| `PLAY_VISOR_UP` | optional speed | Animate the eye visor upward and finish Normal |

### Clock and message

| Action | Arguments | Result |
|---|---|---|
| `SHOW_CLOCK` | hour, minute, colon mode, optional color | Interrupt activity and continuously show the supplied time |
| `UPDATE_CLOCK` | hour, minute | Update an already active clock without restarting its renderer |
| `SHOW_MESSAGE` | optional temporary brightness/color | Interrupt activity and scroll the stored message repeatedly |
| `SET_MESSAGE` | UTF-8/ASCII text, maximum 128 characters | Replace and persist the module's stored message |
| `RESET_MESSAGE` | none | Restore and persist `Please Insert Girder` |

The Brain owns actual timekeeping. Eyes owns font rendering, scrolling, and
local colon blinking after receiving the current time and colon mode.

### Brightness and color

| Action | Arguments | Persistence |
|---|---|---|
| `SET_GLOBAL_BRIGHTNESS` | level | Persisted user preference |
| `SET_TEMP_BRIGHTNESS` | level | Volatile override |
| `CLEAR_TEMP_BRIGHTNESS` | none | Restore stored global brightness |
| `SET_GLOBAL_COLOR` | color | Persisted user preference |
| `SET_TEMP_COLOR` | color | Volatile override |
| `CLEAR_TEMP_COLOR` | none | Restore stored global color |

Temporary overrides exist for a mode, performance, ambient-light response, or
special effect. They never write persistent memory. Effective brightness and
color use the temporary values while present and otherwise use global values.

Persistent writes should occur only when a user explicitly changes a saved
setting, not for every ambient-light adjustment.

### Development and maintenance

| Action | Arguments | Result |
|---|---|---|
| `SHOW_RAW_FRAME` | hardware-sized frame | Render one development/simulator frame |
| `IDENTIFY` | none | Run a brief, recognizable module identification display |
| `EXIT_LOCAL_TEST` | none | Leave diagnostics and show Normal |
| `FACTORY_RESET_SETTINGS` | guarded confirmation | Restore default brightness, color, and message |

Raw frames are a development feature. Normal Brain operation should request
semantic content stored and rendered by the module.

## Display-to-Brain information

The Brain polls display modules. A module does not initiate I2C transactions.

### Identity

- Module type: Eyes or Mouth
- Hardware compatibility identifier
- Firmware version
- Supported feature flags
- Configured I2C address

### Runtime status

- Lifecycle state
- Visual/display state
- Active expression, animation, or performance identifier
- Busy or complete
- Last accepted command
- Brain communication present/lost
- Local test active
- Temporary brightness/color override active

### Error status

- No error
- Unknown action
- Invalid argument or identifier
- Unsupported feature
- Malformed or incomplete transfer
- Persistent-settings integrity failure
- Rendering/data failure
- Hardware initialization failure

Errors remain queryable until cleared by an explicit action or a successful
replacement operation, depending on error type.

## Lifecycle states

Display modules distinguish these internal lifecycle states:

1. `BOOTING`
2. `WAITING_FOR_BRAIN`
3. `STANDALONE_NORMAL`
4. `BRAIN_CONTROLLED`
5. `LOCAL_TEST`
6. `ERROR`

On power-up, outputs remain black while hardware initializes and persisted
settings load. The module waits approximately five seconds for valid Brain
communication. If none arrives, Eyes shows Normal eyes and Mouth shows its
normal resting state. Both continue listening indefinitely.

If communication is lost after connection, the module cancels local timed
activity and enters Standalone Normal after the same timeout. The first valid
Brain display command immediately restores Brain Controlled operation.

## Interruption and completion rules

- A new visual command immediately replaces the current visual activity.
- `STOP`, `SHOW_NORMAL`, and `SET_OFF` always take effect immediately.
- There is no command queue inside a display module.
- An interrupted activity does not resume automatically.
- Animations and module performances normally finish at Normal.
- Visor Down finishes Off; Visor Up finishes Normal.
- A completed module reports completion and its resulting state.
- The Brain decides the next whole-system action. For example, after an angry
  eye performance completes at Normal, the Brain may request Clock.

## Local test button

The display-controller button cycles through local diagnostics such as:

- Normal
- Stored expression/animation demonstration
- Channel test
- Pixel-order test
- Color test
- Brightness ramp
- I2C connection status
- I2C address
- Last command
- Error indication

Any valid Brain display command immediately exits Local Test and is executed.
Local Test never prevents the Brain from regaining control.

## Persistent defaults

- Stored message: `Please Insert Girder`
- Global brightness: conservative mid-level value, finalized after hardware testing
- Global color: Bender eye amber, finalized after diffuser testing
- Temporary overrides: none

Persistent data should include a format version and integrity check. Invalid
data loads safe defaults and sets a queryable settings-integrity error.

## Brain orchestration examples

### Expression followed by clock

1. Brain requests `PLAY_PERFORMANCE(angry_reaction)`.
2. Eyes plays its locally timed sequence and finishes Normal.
3. Brain observes completion or reaches the coordinated timeline point.
4. Brain requests `SHOW_CLOCK(...)`.

### Sensor/user interruption

1. Eyes is playing a performance.
2. User changes mode, presses mute, or leaves the sensor area.
3. Brain immediately requests `STOP`, `SET_OFF`, or another display state.
4. Eyes abandons the previous activity and executes the replacement.

### Ambient brightness

1. Brain reads the ambient-light sensor.
2. Brain requests `SET_TEMP_BRIGHTNESS(level)`.
3. Eyes applies it without persistent writes.
4. Brain requests `CLEAR_TEMP_BRIGHTNESS` when the override is no longer needed.
