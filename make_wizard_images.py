# يولّد صور معالج التثبيت (BMP) بتصميم عصري. يُستدعى تلقائيًا من build.py
import os
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
TOP, BOTTOM = (15, 118, 110), (8, 30, 38)


def gradient(w, h):
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3)))
    return img


def pattern(img):
    # دوائر هندسية خفيفة (طابع إسلامي هادئ)
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = w // 2
    for cx, cy in ((0, int(h * .12)), (w, int(h * .45)), (0, int(h * .78))):
        for k in range(1, 5):
            rr = int(r * (0.35 + 0.22 * k))
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(255, 255, 255, 18), width=max(1, w // 120))
    return Image.alpha_composite(img.convert("RGBA"), layer)


def large(w=246, h=470):
    img = pattern(gradient(w, h))
    icon = Image.open(os.path.join(HERE, "icon.png")).convert("RGBA")
    size = int(w * 0.62)
    icon = icon.resize((size, size), Image.LANCZOS)
    shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", (size, size), (0, 0, 0, 120))
    shadow.paste(sh, ((w - size) // 2, int(h * .30)), icon)
    shadow = shadow.filter(ImageFilter.GaussianBlur(w // 25))
    img = Image.alpha_composite(img, shadow)
    img.alpha_composite(icon, ((w - size) // 2, int(h * .28)))
    # شريط ذهبي رفيع أسفل الصورة
    d = ImageDraw.Draw(img)
    d.rectangle([0, h - max(3, w // 60), w, h], fill=(245, 166, 35, 255))
    return img.convert("RGB")


def small(s=110):
    img = Image.new("RGB", (s, s), (255, 255, 255))
    icon = Image.open(os.path.join(HERE, "icon.png")).convert("RGBA").resize((int(s * .86), int(s * .86)), Image.LANCZOS)
    img = img.convert("RGBA")
    img.alpha_composite(icon, ((s - icon.width) // 2, (s - icon.height) // 2))
    return img.convert("RGB")


def main():
    large().save(os.path.join(HERE, "wizard_large.bmp"), "BMP")
    small().save(os.path.join(HERE, "wizard_small.bmp"), "BMP")
    print("wizard images created")


if __name__ == "__main__":
    main()
