"""Fail-dark, scan-only I2C target test for Display Controller Rev D."""

import time
import analogio
import digitalio
import i2ctarget

import config


VERSION = "0.2"


def read_address_adc(pin, samples=16):
    total = 0
    for _ in range(samples):
        total += pin.value
        time.sleep(0.005)
    return total // samples


def decode_address(value):
    if value < config.BOTH_A0_THRESHOLD:
        return config.SPARE_ADDRESS, "Spare display (both shunts)"
    if value < config.A0_A1_THRESHOLD:
        return config.MOUTH_ADDRESS, "Mouth (A0 shunt)"
    if value < config.A1_OPEN_THRESHOLD:
        return config.EYES_ADDRESS, "Eyes (A1 shunt)"
    return config.DEVELOPMENT_ADDRESS, "Development (open/open)"


print("\nBU-22 DISPLAY CONTROLLER REV D I2C TARGET", VERSION)

# Never initialize display clock/data pins in this scan-only test.
output_enable = digitalio.DigitalInOut(config.BUFFER_ENABLE)
output_enable.switch_to_output(value=False)
print("AHCT outputs: DISABLED")

address_pin = analogio.AnalogIn(config.ADDRESS)
address_raw = read_address_adc(address_pin)
address, role = decode_address(address_raw)
address_pin.deinit()

print("Address ADC raw:", address_raw)
print("Selected role:", role)
print("I2C target address: 0x%02X" % address)
print("Waiting for Brain scan on Rev D RX=SCL, TX=SDA")

target = i2ctarget.I2CTarget(config.I2C_SCL, config.I2C_SDA, (address,))

while True:
    try:
        request = target.request(timeout=0.1)
    except OSError as error:
        if error.args and error.args[0] == 116:
            request = None
        else:
            print("I2C ERROR:", repr(error))
            request = None

    if request is None:
        continue

    with request:
        if request.is_read:
            request.write(bytes((0x22, address, address_raw >> 8,
                                 address_raw & 0xFF)))
            print("I2C read from Brain")
        else:
            payload = bytes(request.read())
            print("I2C write from Brain:", payload)
