#!/usr/bin/env python3
"""Patch App Store + menu bar icons in app-store-02-busqueda screenshot."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]
APP_ICON = PROJECT / "ClipKee/Assets.xcassets/AppIcon.appiconset/icon-512.png"
SOURCE = ROOT / "app-store-02-busqueda.png"

# Coordinates on the 1536x1024 master image
APP_ICON_BOX = (112, 162, 348, 398)  # x1, y1, x2, y2
MENU_BAR_BOX = (1008, 6, 1056, 54)


def rounded_app_icon(size: int) -> Image.Image:
    source = Image.open(APP_ICON).convert("RGBA")
    source = source.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    radius = max(1, int(size * 0.223))
    draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=255)
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    icon.paste(source, (0, 0), mask)
    return icon


def load_menu_bar_symbol(size: int) -> Image.Image:
    symbol_path = ROOT / f"menubar-symbol-{size}.png"
    if not symbol_path.exists():
        export_symbol(size, symbol_path)
    return Image.open(symbol_path).convert("RGBA")


def export_symbol(size: int, path: Path) -> None:
    script = f'''
import AppKit
let size: CGFloat = {size}
let config = NSImage.SymbolConfiguration(pointSize: size, weight: .bold)
guard let image = NSImage(systemSymbolName: "list.clipboard.fill", accessibilityDescription: nil)?.withSymbolConfiguration(config) else {{ exit(1) }}
let dim = size
let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: Int(dim), pixelsHigh: Int(dim), bitsPerSample: 8, samplesPerPixel: 4, hasAlpha: true, isPlanar: false, colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)
NSColor.black.set()
image.draw(in: NSRect(x: 0, y: 0, width: dim, height: dim))
NSGraphicsContext.restoreGraphicsState()
try rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: "{path}"))
'''
    subprocess.run(["swift", "-"], input=script, text=True, check=True)


def average_color(image: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    x1, y1, x2, y2 = box
    crop = image.crop((x1, y1, x2, y2)).convert("RGB")
    pixels = list(crop.getdata())
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    return r, g, b


def patch_image(path: Path) -> None:
    base = Image.open(path).convert("RGBA")
    scale_x = base.width / 1536
    scale_y = base.height / 1024

    def scale_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        x1, y1, x2, y2 = box
        return (
            int(round(x1 * scale_x)),
            int(round(y1 * scale_y)),
            int(round(x2 * scale_x)),
            int(round(y2 * scale_y)),
        )

    app_box = scale_box(APP_ICON_BOX)
    menu_box = scale_box(MENU_BAR_BOX)

    app_w = app_box[2] - app_box[0]
    app_h = app_box[3] - app_box[1]
    app_icon = rounded_app_icon(min(app_w, app_h))
    if app_icon.size != (app_w, app_h):
        app_icon = app_icon.resize((app_w, app_h), Image.Resampling.LANCZOS)
    base.paste(app_icon, (app_box[0], app_box[1]), app_icon)

    menu_w = menu_box[2] - menu_box[0]
    menu_h = menu_box[3] - menu_box[1]
    bg = average_color(base, (
        menu_box[2] + 4,
        menu_box[1] + 4,
        menu_box[2] + 24,
        menu_box[3] - 4,
    ))
    draw = ImageDraw.Draw(base)
    draw.rectangle(menu_box, fill=bg + (255,))

    symbol_size = int(min(menu_w, menu_h) * 0.72)
    symbol = load_menu_bar_symbol(symbol_size)
    offset_x = menu_box[0] + (menu_w - symbol_size) // 2
    offset_y = menu_box[1] + (menu_h - symbol_size) // 2
    base.paste(symbol, (offset_x, offset_y), symbol)

    base.convert("RGB").save(path, optimize=True)


def export_sizes(master: Path) -> None:
    name = master.stem
    for w, h in [(1280, 800), (1440, 900), (2560, 1600), (2880, 1800)]:
        out = ROOT / f"{name}-{w}x{h}.png"
        subprocess.run(["sips", "-z", str(h), str(w), str(master), "--out", str(out)], check=True)


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source image: {SOURCE}")

    assets_source = ROOT.parents[2] / ".cursor/projects/Users-fmadriz-Trabajo-Repositorios-Reposfmadriz-ClipKee/assets/app-store-02-busqueda.png"
    if not APP_ICON.exists():
        raise SystemExit(f"Missing app icon: {APP_ICON}")

    patch_image(SOURCE)
    export_sizes(SOURCE)
    print("Patched app-store-02-busqueda and regenerated all sizes.")


if __name__ == "__main__":
    main()
