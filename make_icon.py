from PIL import Image, ImageDraw

BASE_SIZE = 256
ICON_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def _scale(size, value):
    return int(round(value * size / BASE_SIZE))


def draw_icon(size=256):
    s = lambda value: _scale(size, value)
    center = size // 2

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = s(16)
    draw.rounded_rectangle(
        [(margin, margin), (size - margin, size - margin)],
        radius=s(48),
        fill=(15, 23, 42, 255),
        outline=(34, 211, 238, 255),
        width=s(8),
    )

    badge_radius = s(76)
    draw.ellipse(
        [
            (center - badge_radius, center - badge_radius),
            (center + badge_radius, center + badge_radius),
        ],
        fill=(8, 145, 178, 255),
        outline=(125, 211, 252, 255),
        width=s(6),
    )

    cross_color = (248, 250, 252, 255)
    cross_thickness = s(34)
    cross_length = s(112)
    cross_radius = s(10)

    draw.rounded_rectangle(
        [
            (center - cross_thickness // 2, center - cross_length // 2),
            (center + cross_thickness // 2, center + cross_length // 2),
        ],
        radius=cross_radius,
        fill=cross_color,
    )
    draw.rounded_rectangle(
        [
            (center - cross_length // 2, center - cross_thickness // 2),
            (center + cross_length // 2, center + cross_thickness // 2),
        ],
        radius=cross_radius,
        fill=cross_color,
    )

    pulse_points = [
        (s(52), s(160)),
        (s(84), s(160)),
        (s(100), s(144)),
        (s(118), s(174)),
        (s(136), s(114)),
        (s(154), s(148)),
        (s(176), s(136)),
        (s(204), s(136)),
    ]
    draw.line(pulse_points, fill=(239, 68, 68, 255), width=s(10))

    img.save("icon.png")
    img.save("app/web/favicon.ico", format="ICO", sizes=ICON_SIZES)
    img.save("icon.ico", format="ICO", sizes=ICON_SIZES)
    print("EMS icons generated successfully!")


if __name__ == "__main__":
    draw_icon()
