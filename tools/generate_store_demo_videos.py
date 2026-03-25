from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "out" / "store_demos"
FRAMES_DIR = OUT_DIR / "frames"

WIDTH = 1280
HEIGHT = 720
FPS = 24
SCENE_SECONDS = 3
SCENES = ("home", "category", "product", "cart", "checkout", "offer")


@dataclass(frozen=True)
class BrandSpec:
    slug: str
    brand: str
    platform: str
    domain: str
    accent: tuple[int, int, int]
    accent_alt: tuple[int, int, int]
    page_bg: tuple[int, int, int]
    products: tuple[tuple[str, str], ...]


def load_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = []
    if bold:
        candidates.extend(
            [
                r"C:\Windows\Fonts\arialbd.ttf",
                r"C:\Windows\Fonts\segoeuib.ttf",
            ]
        )
    candidates.extend(
        [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
        ]
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


FONT_H1 = load_font(36, bold=True)
FONT_H2 = load_font(24, bold=True)
FONT_BODY = load_font(18)
FONT_SM = load_font(15)
FONT_XS = load_font(13)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def draw_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font, fill=(20, 24, 28)) -> None:
    draw.text(xy, text, font=font, fill=fill)


def draw_cursor(draw: ImageDraw.ImageDraw, x: float, y: float) -> None:
    shape = [
        (x, y),
        (x + 15, y + 36),
        (x + 21, y + 22),
        (x + 34, y + 29),
        (x + 38, y + 21),
        (x + 24, y + 14),
        (x + 35, y + 3),
    ]
    draw.polygon(shape, fill=(255, 255, 255), outline=(0, 0, 0))


def draw_product_card(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    price: str,
    accent: tuple[int, int, int],
) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=14, fill=(255, 255, 255), outline=(215, 222, 228))
    draw.rounded_rectangle((x + 12, y + 12, x + w - 12, y + 118), radius=10, fill=(236, 243, 249))
    draw.rectangle((x + 22, y + 24, x + w - 22, y + 106), fill=(226, 236, 245))
    draw_text(draw, (x + 16, y + 130), title, FONT_SM)
    draw_text(draw, (x + 16, y + 152), price, FONT_SM, fill=accent)
    draw.rounded_rectangle((x + w - 102, y + h - 35, x + w - 14, y + h - 12), radius=10, fill=accent)
    draw_text(draw, (x + w - 92, y + h - 31), "Ver", FONT_XS, fill=(255, 255, 255))


def draw_top_browser(draw: ImageDraw.ImageDraw, spec: BrandSpec) -> None:
    draw.rounded_rectangle((22, 18, WIDTH - 22, HEIGHT - 18), radius=16, fill=(245, 248, 252), outline=(188, 198, 208))
    draw.rounded_rectangle((38, 34, WIDTH - 38, 72), radius=10, fill=(230, 236, 242), outline=(200, 208, 216))
    draw.ellipse((50, 45, 60, 55), fill=(239, 82, 77))
    draw.ellipse((66, 45, 76, 55), fill=(247, 190, 69))
    draw.ellipse((82, 45, 92, 55), fill=(95, 202, 105))
    draw.rounded_rectangle((120, 42, WIDTH - 78, 64), radius=9, fill=(255, 255, 255), outline=(205, 213, 220))
    draw_text(draw, (132, 46), spec.domain, FONT_XS, fill=(77, 88, 99))

    draw.rounded_rectangle((38, 82, WIDTH - 38, 132), radius=12, fill=(255, 255, 255), outline=(212, 220, 228))
    draw.rounded_rectangle((54, 96, 250, 120), radius=9, fill=spec.accent)
    draw_text(draw, (64, 100), f"{spec.brand} · {spec.platform}", FONT_XS, fill=(255, 255, 255))
    nav = "Inicio   Tienda   Iluminacion   Mobiliario   Ofertas   Contacto"
    draw_text(draw, (282, 100), nav, FONT_XS, fill=(71, 84, 97))


def scene_cursor(scene: str) -> tuple[tuple[int, int], tuple[int, int]]:
    mapping = {
        "home": ((510, 266), (548, 266)),
        "category": ((355, 203), (355, 290)),
        "product": ((775, 452), (810, 452)),
        "cart": ((965, 405), (980, 405)),
        "checkout": ((640, 405), (640, 470)),
        "offer": ((944, 220), (944, 220)),
    }
    return mapping[scene]


def draw_scene(draw: ImageDraw.ImageDraw, spec: BrandSpec, scene: str, t: float) -> None:
    body_x0, body_y0 = 48, 146
    body_x1, body_y1 = WIDTH - 48, HEIGHT - 34
    draw.rounded_rectangle((body_x0, body_y0, body_x1, body_y1), radius=14, fill=spec.page_bg, outline=(220, 228, 236))

    if scene == "home":
        draw.rounded_rectangle((70, 170, 760, 338), radius=16, fill=(255, 255, 255), outline=(210, 218, 226))
        draw_text(draw, (96, 198), f"{spec.brand} · nueva coleccion", FONT_H2)
        draw_text(draw, (96, 236), "Luminaria y mobiliario con entrega rapida", FONT_BODY, fill=(85, 95, 105))
        draw.rounded_rectangle((96, 280, 250, 314), radius=12, fill=spec.accent)
        draw_text(draw, (114, 289), "Ver catalogo", FONT_BODY, fill=(255, 255, 255))
        draw.rounded_rectangle((778, 170, 1210, 338), radius=16, fill=(255, 255, 255), outline=(210, 218, 226))
        draw_text(draw, (806, 198), "Beneficios", FONT_H2)
        draw_text(draw, (806, 238), "Envio 48h", FONT_BODY)
        draw_text(draw, (806, 264), "Cuotas sin interes", FONT_BODY)
        draw_text(draw, (806, 290), "Soporte por WhatsApp", FONT_BODY)

        start_x = 70
        for idx in range(4):
            p = spec.products[idx]
            draw_product_card(draw, start_x + idx * 286, 356, 270, 236, p[0], p[1], spec.accent)

    elif scene == "category":
        draw.rounded_rectangle((70, 170, 308, 592), radius=14, fill=(255, 255, 255), outline=(210, 218, 226))
        draw_text(draw, (88, 194), "Filtros", FONT_H2)
        labels = ["Colgantes", "De pie", "Mesa", "Pared", "Madera", "Metal"]
        for idx, label in enumerate(labels):
            y = 240 + idx * 46
            fill = spec.accent if idx == 1 else (244, 248, 252)
            txt = (255, 255, 255) if idx == 1 else (45, 57, 68)
            draw.rounded_rectangle((88, y, 286, y + 34), radius=10, fill=fill, outline=(214, 222, 230))
            draw_text(draw, (102, y + 9), label, FONT_XS, fill=txt)

        grid = spec.products
        gx, gy = 326, 170
        k = 0
        for row in range(2):
            for col in range(3):
                draw_product_card(draw, gx + col * 294, gy + row * 214, 276, 202, grid[k][0], grid[k][1], spec.accent)
                k += 1

    elif scene == "product":
        draw.rounded_rectangle((70, 170, 650, 590), radius=14, fill=(255, 255, 255), outline=(210, 218, 226))
        draw.rounded_rectangle((96, 198, 624, 564), radius=14, fill=(229, 238, 247))
        draw.rectangle((142, 236, 580, 522), fill=(220, 232, 244))
        draw.rounded_rectangle((670, 170, 1210, 590), radius=14, fill=(255, 255, 255), outline=(210, 218, 226))
        draw_text(draw, (694, 198), spec.products[0][0], FONT_H2)
        draw_text(draw, (694, 242), spec.products[0][1], FONT_H2, fill=spec.accent)
        draw_text(draw, (694, 284), "Stock inmediato", FONT_BODY)
        draw_text(draw, (694, 312), "Envio 48h", FONT_BODY)
        draw_text(draw, (694, 340), "Cuotas sin interes", FONT_BODY)
        draw.rounded_rectangle((694, 384, 980, 426), radius=12, fill=spec.accent)
        draw_text(draw, (738, 396), "Agregar al carrito", FONT_BODY, fill=(255, 255, 255))
        draw.rounded_rectangle((996, 384, 1182, 426), radius=12, fill=spec.accent_alt)
        draw_text(draw, (1042, 396), "Comprar", FONT_BODY, fill=(255, 255, 255))

    elif scene == "cart":
        draw.rounded_rectangle((70, 170, 868, 592), radius=14, fill=(255, 255, 255), outline=(210, 218, 226))
        draw.rounded_rectangle((884, 170, 1210, 592), radius=14, fill=(255, 255, 255), outline=(210, 218, 226))
        draw_text(draw, (94, 194), "Carrito", FONT_H2)
        rows = [spec.products[0], spec.products[2], spec.products[5]]
        for idx, item in enumerate(rows):
            y = 236 + idx * 104
            draw.rounded_rectangle((94, y, 846, y + 88), radius=12, fill=(248, 251, 255), outline=(219, 226, 234))
            draw.rounded_rectangle((108, y + 14, 164, y + 74), radius=10, fill=(226, 236, 246))
            draw_text(draw, (180, y + 22), item[0], FONT_BODY)
            draw_text(draw, (180, y + 48), item[1], FONT_XS, fill=(88, 99, 111))
            draw_text(draw, (760, y + 32), "x1", FONT_BODY)

        draw_text(draw, (906, 198), "Resumen", FONT_H2)
        draw_text(draw, (906, 252), "Subtotal", FONT_BODY)
        draw_text(draw, (1120, 252), "USD 607", FONT_BODY)
        draw_text(draw, (906, 286), "Envio", FONT_BODY)
        draw_text(draw, (1120, 286), "USD 0", FONT_BODY)
        draw_text(draw, (906, 326), "Total", FONT_H2)
        draw_text(draw, (1120, 326), "USD 607", FONT_H2, fill=spec.accent)
        draw.rounded_rectangle((906, 388, 1186, 432), radius=12, fill=spec.accent)
        draw_text(draw, (962, 401), "Finalizar compra", FONT_BODY, fill=(255, 255, 255))

    elif scene == "checkout":
        draw.rounded_rectangle((70, 170, 820, 592), radius=14, fill=(255, 255, 255), outline=(210, 218, 226))
        draw.rounded_rectangle((838, 170, 1210, 592), radius=14, fill=(255, 255, 255), outline=(210, 218, 226))
        draw_text(draw, (94, 194), "Checkout", FONT_H2)
        fields = [
            "Nombre y apellido",
            "Email",
            "Telefono",
            "Direccion",
            "Ciudad",
        ]
        for idx, field in enumerate(fields):
            y = 236 + idx * 64
            draw_text(draw, (94, y), field, FONT_XS, fill=(89, 100, 111))
            draw.rounded_rectangle((94, y + 18, 790, y + 50), radius=10, fill=(248, 251, 255), outline=(218, 226, 234))
        draw.rounded_rectangle((94, 548, 300, 584), radius=12, fill=spec.accent)
        draw_text(draw, (128, 559), "Pagar ahora", FONT_BODY, fill=(255, 255, 255))

        draw_text(draw, (862, 194), "Tu compra", FONT_H2)
        for idx, item in enumerate(spec.products[:3]):
            y = 246 + idx * 54
            draw_text(draw, (862, y), item[0], FONT_XS)
            draw_text(draw, (1126, y), item[1], FONT_XS, fill=spec.accent)
        draw_text(draw, (862, 446), "Total", FONT_H2)
        draw_text(draw, (1118, 446), "USD 607", FONT_H2, fill=spec.accent)

    elif scene == "offer":
        draw.rounded_rectangle((70, 170, 1210, 592), radius=14, fill=(255, 255, 255), outline=(210, 218, 226))
        draw.rounded_rectangle((94, 196, 1186, 346), radius=16, fill=spec.accent_alt)
        draw_text(draw, (126, 232), f"{spec.brand} · Sale Week", FONT_H1, fill=(255, 255, 255))
        draw_text(draw, (126, 278), "Hasta 25% OFF en luminaria y combos de living", FONT_BODY, fill=(255, 255, 255))
        draw.rounded_rectangle((126, 306, 300, 336), radius=10, fill=(255, 255, 255))
        draw_text(draw, (152, 313), "Codigo: LUZ25", FONT_XS, fill=spec.accent_alt)

        for idx in range(3):
            px = 94 + idx * 364
            draw_product_card(draw, px, 364, 340, 210, spec.products[idx + 1][0], spec.products[idx + 1][1], spec.accent)

    start, end = scene_cursor(scene)
    cx = lerp(start[0], end[0], t)
    cy = lerp(start[1], end[1], t)
    draw_cursor(draw, cx, cy)


def render_video(spec: BrandSpec) -> Path:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("No encuentro ffmpeg en PATH.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frame_dir = FRAMES_DIR / spec.slug
    if frame_dir.exists():
        shutil.rmtree(frame_dir)
    frame_dir.mkdir(parents=True, exist_ok=True)

    frames_per_scene = FPS * SCENE_SECONDS
    frame_index = 0
    for scene in SCENES:
        for i in range(frames_per_scene):
            t = 0 if frames_per_scene <= 1 else i / (frames_per_scene - 1)
            img = Image.new("RGB", (WIDTH, HEIGHT), spec.page_bg)
            draw = ImageDraw.Draw(img)
            draw_top_browser(draw, spec)
            draw_scene(draw, spec, scene, t)
            img.save(frame_dir / f"frame_{frame_index:05d}.png")
            frame_index += 1

    output = OUT_DIR / f"{spec.slug}.mp4"
    cmd = [
        ffmpeg,
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(frame_dir / "frame_%05d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)
    return output


def main() -> None:
    specs: Iterable[BrandSpec] = (
        BrandSpec(
            slug="demo_tiendanube_aurea_luz",
            brand="Aurea Luz",
            platform="Tiendanube",
            domain="aurealuz.mitiendanube.com",
            accent=(25, 166, 103),
            accent_alt=(10, 99, 74),
            page_bg=(241, 246, 244),
            products=(
                ("Lampara Colgante Aura", "USD 129"),
                ("Lampara de Pie Nexo", "USD 189"),
                ("Mesa Ratona Oslo", "USD 249"),
                ("Consola Nara", "USD 279"),
                ("Sillon Atelier 2C", "USD 490"),
                ("Aplique Faro", "USD 94"),
            ),
        ),
        BrandSpec(
            slug="demo_empretienda_nordica_lumen",
            brand="Nordica Lumen",
            platform="Empretienda",
            domain="nordicalumen.empretienda.com",
            accent=(232, 111, 61),
            accent_alt=(52, 74, 129),
            page_bg=(247, 242, 238),
            products=(
                ("Plafon Zenit", "USD 159"),
                ("Lampara Mesa Cubo", "USD 99"),
                ("Rack TV Nova", "USD 329"),
                ("Biblioteca Vertica", "USD 279"),
                ("Escritorio Roble", "USD 299"),
                ("Set Banqueta Lena", "USD 169"),
            ),
        ),
    )

    outputs = []
    for spec in specs:
        print(f"Generando video: {spec.slug} ...")
        outputs.append(render_video(spec))

    print("\nListo. Videos generados:")
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
