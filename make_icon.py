# make_icon.py
"""Генератор иконки приложения «ЧМ»."""
from PIL import Image, ImageDraw

S = 1024
BG = (37, 99, 235, 255)
BG_DARK = (29, 78, 216, 255)
FG = (255, 255, 255, 255)


def draw_icon(size=S):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    d.rounded_rectangle([0, 0, s - 1, s - 1],
                        radius=int(s * 0.22), fill=BG,
                        outline=BG_DARK, width=max(1, int(s * 0.012)))

    w = max(1, int(s * 0.062))
    y0, y1 = s * 0.27, s * 0.75
    ym = s * 0.545

    def stroke(pts, joint=None):
        d.line(pts, fill=FG, width=w, joint=joint)

    def cap(x, y):
        r = w / 2
        d.ellipse([x - r, y - r, x + r, y + r], fill=FG)

    xa, xb = s * 0.155, s * 0.435
    stroke([(xa, y0), (xa, ym)])
    stroke([(xa, ym), (xb, ym)])
    stroke([(xb, y0), (xb, y1)])
    for p in [(xa, y0), (xa, ym), (xb, ym), (xb, y0), (xb, y1)]:
        cap(*p)

    xc, xd = s * 0.565, s * 0.855
    xm = (xc + xd) / 2
    pts = [(xc, y1), (xc, y0), (xm, s * 0.635), (xd, y0), (xd, y1)]
    stroke(pts, joint="curve")
    for p in pts:
        cap(*p)

    return img


def main():
    base = draw_icon(S)

    sizes = [16, 24, 32, 48, 64, 128, 256]
    base.save("icon.ico", format="ICO", sizes=[(v, v) for v in sizes])
    print("✅ icon.ico")

    base.resize((512, 512), Image.LANCZOS).save("icon_512.png")
    base.resize((256, 256), Image.LANCZOS).save("icon.png")
    print("✅ icon.png / icon_512.png")

    try:
        base.save("icon.icns", format="ICNS")
        print("✅ icon.icns")
    except Exception:
        print("ℹ .icns не создан")


if __name__ == "__main__":
    main()