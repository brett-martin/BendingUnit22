"""Compact variable-width 3x5 font for the temporary half-size displays."""

# Rows are encoded left-to-right, most-significant used bit first.
GLYPHS = {
    " ": (0, 0, 0, 0, 0),
    ";": (0, 0, 0, 0, 0),  # One-column blank used for a hidden clock colon.
    "-": (0, 0, 7, 0, 0),
    ":": (0, 1, 0, 1, 0),
    "0": (7, 5, 5, 5, 7), "1": (2, 6, 2, 2, 7),
    "2": (7, 1, 7, 4, 7), "3": (7, 1, 7, 1, 7),
    "4": (5, 5, 7, 1, 1), "5": (7, 4, 7, 1, 7),
    "6": (7, 4, 7, 5, 7), "7": (7, 1, 1, 1, 1),
    "8": (7, 5, 7, 5, 7), "9": (7, 5, 7, 1, 7),
    "A": (2, 5, 7, 5, 5), "B": (6, 5, 6, 5, 6),
    "C": (3, 4, 4, 4, 3), "D": (6, 5, 5, 5, 6),
    "E": (7, 4, 6, 4, 7), "F": (7, 4, 6, 4, 4),
    "G": (3, 4, 5, 5, 3), "H": (5, 5, 7, 5, 5),
    "I": (7, 2, 2, 2, 7), "J": (1, 1, 1, 5, 2),
    "K": (5, 5, 6, 5, 5), "L": (4, 4, 4, 4, 7),
    "M": (5, 7, 7, 5, 5), "N": (5, 7, 7, 7, 5),
    "O": (2, 5, 5, 5, 2), "P": (6, 5, 6, 4, 4),
    "Q": (2, 5, 5, 3, 1), "R": (6, 5, 6, 5, 5),
    "S": (3, 4, 2, 1, 6), "T": (7, 2, 2, 2, 2),
    "U": (5, 5, 5, 5, 7), "V": (5, 5, 5, 5, 2),
    "W": (5, 5, 7, 7, 5), "X": (5, 5, 2, 5, 5),
    "Y": (5, 5, 2, 2, 2), "Z": (7, 1, 2, 4, 7),
}


def glyph_width(character):
    return 1 if character in (":", ";") else 3


def text_width(text, spacing=1):
    text = text.upper()
    if not text:
        return 0
    return sum(glyph_width(character) for character in text) + spacing * (len(text) - 1)


def draw_text(buffer, width, height, text, x, y, value=1, spacing=1):
    cursor = x
    for character in text.upper():
        rows = GLYPHS.get(character, GLYPHS[" "])
        glyph_w = glyph_width(character)
        for row, bits in enumerate(rows):
            py = y + row
            if not 0 <= py < height:
                continue
            for column in range(glyph_w):
                px = cursor + column
                source_bit = 0 if character in (":", ";") else 2 - column
                if 0 <= px < width and bits & (1 << source_bit):
                    buffer[py * width + px] = value
        cursor += glyph_w + spacing
    return cursor - spacing


def centered_text(buffer, width, height, text, value=1):
    x = (width - text_width(text)) // 2
    y = (height - 5) // 2
    draw_text(buffer, width, height, text, x, y, value)


def scroll_positions(text, viewport_width):
    return range(viewport_width, -text_width(text) - 1, -1)
