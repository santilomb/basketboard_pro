import re

_HEX_RE = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$")


def is_hex_color(s: str) -> bool:
    """Devuelve True si s es un color hex válido (#rgb o #rrggbb)."""
    if not isinstance(s, str):
        return False
    return bool(_HEX_RE.match(s.strip()))


def normalize_hex(s: str) -> str:
    """
    Normaliza un color hex a formato #rrggbb en minúsculas.
    Acepta #rgb o #rrggbb. Lanza ValueError si es inválido.
    """
    s = (s or "").strip()
    if not is_hex_color(s):
        raise ValueError(f"Color hex inválido: {s!r}")
    s = s.lower()
    if len(s) == 4:  # #rgb -> #rrggbb
        r, g, b = s[1], s[2], s[3]
        return f"#{r}{r}{g}{g}{b}{b}"
    return s


def hex_to_rgb(s: str) -> tuple[int, int, int]:
    """Convierte '#rrggbb' (o '#rgb') a (r, g, b)."""
    h = normalize_hex(s)[1:]
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convierte (r, g, b) a '#rrggbb' validando rango 0..255."""
    for v in (r, g, b):
        if not (0 <= int(v) <= 255):
            raise ValueError(f"Componente RGB fuera de rango: {v}")
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


def contrast_color(bg_hex: str) -> str:
    """
    Retorna '#000000' o '#ffffff' según contraste con el fondo.
    Usa luminancia relativa aproximada (percepción sRGB).
    """
    r, g, b = hex_to_rgb(bg_hex)
    # convertir a luminancia aproximada
    lum = (0.2126 * (r / 255) + 0.7152 * (g / 255) + 0.0722 * (b / 255))
    return "#000000" if lum > 0.5 else "#ffffff"

