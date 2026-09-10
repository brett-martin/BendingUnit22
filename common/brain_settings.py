"""Persistent BU-22 clock settings and UTC/local time conversion."""

MAGIC = b"BU22"
VERSION = 1
SIZE = 10

ZONE_LABELS = ("EST", "CST", "MST", "PST")
STANDARD_UTC_OFFSETS = (-5, -6, -7, -8)

COLON_SOLID = 0
COLON_FLASH = 1


def local_hour(utc_value, timezone, dst):
    return (utc_value + STANDARD_UTC_OFFSETS[timezone]
            + int(bool(dst))) % 24


def utc_hour(local_value, timezone, dst):
    return (local_value - STANDARD_UTC_OFFSETS[timezone]
            - int(bool(dst))) % 24


class ClockSettings:
    def __init__(self):
        self.timezone = 0
        self.dst = False
        self.use_24_hour = False
        self.colon_mode = COLON_FLASH

    def encode(self):
        data = bytearray(SIZE)
        data[:4] = MAGIC
        data[4] = VERSION
        data[5] = self.timezone
        data[6] = int(self.dst)
        data[7] = int(self.use_24_hour)
        data[8] = self.colon_mode
        data[9] = sum(data[:9]) & 0xFF
        return data

    def save(self, storage):
        storage[:SIZE] = self.encode()

    def load(self, storage):
        if len(storage) < SIZE:
            return False
        data = bytes(storage[:SIZE])
        valid = (
            data[:4] == MAGIC
            and data[4] == VERSION
            and data[9] == (sum(data[:9]) & 0xFF)
            and data[5] <= 3
            and data[6] <= 1
            and data[7] <= 1
            and data[8] <= 1
        )
        if not valid:
            self.save(storage)
            return False
        self.timezone = data[5]
        self.dst = bool(data[6])
        self.use_24_hour = bool(data[7])
        self.colon_mode = data[8]
        return True
