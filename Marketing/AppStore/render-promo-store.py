#!/usr/bin/env python3
"""Render App Store promo hero images (Spanish + English) with current ClipKee UI."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
APP_ICON = (REPO / "ClipKee/Assets.xcassets/AppIcon.appiconset/icon-1024.png").as_uri()
DOCK_ICON = (REPO / "ClipKee/Assets.xcassets/AppIcon.appiconset/icon-128.png").as_uri()
DOCK_ICONS_DIR = ROOT / "dock-icons"
MENUBAR_ICONS_DIR = ROOT / "menubar-icons"
MENU_BAR_ICON = (MENUBAR_ICONS_DIR / "clipkee.png").as_uri()
EXPORT_MENUBAR_ICONS = ROOT / "export-menubar-icons.swift"
WALLPAPER = (
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=3840&q=80"
)
LANDSCAPE = (
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=800&q=80"
)

WIDTH = 2560
HEIGHT = 1600
PANEL_WIDTH = 360
PANEL_RIGHT = 620

TRASH = """
<svg viewBox="0 0 16 18" width="13" height="14" fill="currentColor" aria-hidden="true">
  <path d="M3 4.5h10l-.8 10.2a1.5 1.5 0 0 1-1.5 1.3H5.3a1.5 1.5 0 0 1-1.5-1.3L3 4.5Zm2.1-.5L5 2.8A1 1 0 0 1 6 2h4a1 1 0 0 1 1 .8l-.1.2h2.1a.75.75 0 0 1 0 1.5H5.1a.75.75 0 0 1 0-1.5H5.1Z"/>
</svg>
"""

TEXT_ICON = """
<svg viewBox="0 0 20 16" width="12" height="10" fill="currentColor" aria-hidden="true">
  <path d="M2 2.5A1.5 1.5 0 0 1 3.5 1h13A1.5 1.5 0 0 1 18 2.5v1A1.5 1.5 0 0 1 16.5 5h-13A1.5 1.5 0 0 1 2 3.5v-1ZM3.5 7h13a.75.75 0 0 1 0 1.5h-13A.75.75 0 0 1 3.5 7Zm0 3.5h9a.75.75 0 0 1 0 1.5h-9a.75.75 0 0 1 0-1.5Zm0 3.5h11a.75.75 0 0 1 0 1.5h-11a.75.75 0 0 1 0-1.5Z"/>
</svg>
"""

PHOTO_ICON = """
<svg viewBox="0 0 20 16" width="12" height="10" fill="currentColor" aria-hidden="true">
  <path d="M2 2.5A1.5 1.5 0 0 1 3.5 1h13A1.5 1.5 0 0 1 18 2.5v11A1.5 1.5 0 0 1 16.5 15h-13A1.5 1.5 0 0 1 2 13.5v-11ZM4 12.5l3.2-3.4a1 1 0 0 1 1.45 0L11.5 12l2-2.1a1 1 0 0 1 1.4 0L16 12.5V4H4v8.5Zm2.5-5a1.75 1.75 0 1 1 0 3.5 1.75 1.75 0 0 1 0-3.5Z"/>
</svg>
"""

DOC_ICON = """
<svg viewBox="0 0 16 18" width="12" height="13" fill="currentColor" aria-hidden="true">
  <path d="M3 1.5h6.5L14 6v10.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 16.5v-14A1.5 1.5 0 0 1 3.5 1H3Zm6 0V6h4.5L9 1.5ZM5 9.5h6v1.5H5V9.5Zm0 3h4v1.5H5v-1.5Z"/>
</svg>
"""

SEARCH_ICON = """
<svg viewBox="0 0 20 20" width="18" height="18" fill="currentColor">
  <path d="M8.5 2a6.5 6.5 0 1 1 0 13 6.5 6.5 0 0 1 0-13Zm0 1.5a5 5 0 1 0 0 10 5 5 0 0 0 0-10Zm7.03 11.47a.75.75 0 1 1 1.06 1.06l-2.7 2.7a.75.75 0 1 1-1.06-1.06l2.7-2.7Z"/>
</svg>
"""

GEAR_ICON = """
<svg viewBox="0 0 20 20" width="18" height="18" fill="currentColor">
  <path d="M8.59 1.5h2.82l.28 1.64a5.6 5.6 0 0 1 1.47.85l1.57-.6 1.99 1.99-.6 1.57c.36.46.64.96.85 1.47l1.64.28v2.82l-1.64.28a5.6 5.6 0 0 1-.85 1.47l.6 1.57-1.99 1.99-1.57-.6a5.6 5.6 0 0 1-1.47.85l-.28 1.64H8.59l-.28-1.64a5.6 5.6 0 0 1-1.47-.85l-1.57.6-1.99-1.99.6-1.57a5.6 5.6 0 0 1-.85-1.47L1.5 11.41V8.59l1.64-.28c.21-.51.49-1.01.85-1.47l-.6-1.57 1.99-1.99 1.57.6c.46-.36.96-.64 1.47-.85l.28-1.64ZM10 7.2A2.8 2.8 0 1 0 12.8 10 2.8 2.8 0 0 0 10 7.2Z"/>
</svg>
"""

QUIT_ICON = """
<svg viewBox="0 0 20 20" width="18" height="18" fill="currentColor">
  <path d="M10 1.5a8.5 8.5 0 1 1 0 17 8.5 8.5 0 0 1 0-17Zm3.53 5.47a.75.75 0 1 0-1.06-1.06L10 8.94 7.53 6.47A.75.75 0 0 0 6.47 7.53L8.94 10l-2.47 2.47a.75.75 0 1 0 1.06 1.06L10 11.06l2.47 2.47a.75.75 0 0 0 1.06-1.06L11.06 10l2.47-2.47Z"/>
</svg>
"""

LOCALES = {
    "es": {
        "filename": "promo-store-es",
        "menubar": ["Finder", "Archivo", "Edición", "Visualización", "Ir", "Ventana", "Ayuda"],
        "datetime": "Mar 9 de jun  9:41",
        "tagline": "Tu historial del portapapeles. Siempre disponible.",
        "features": [
            ("Historial", "Accede a todo lo que copiaste, cuando lo necesites.", "clipboard"),
            (
                "Todo tipo de contenido",
                "Texto, imágenes, archivos y más. En un solo lugar.",
                "content",
            ),
            ("Privado y seguro", "Tus datos se mantienen en tu Mac.", "lock"),
        ],
        "subtitle": "Historial del portapapeles",
        "cards": [
            ("text", "06:38", "Reunión seguimiento proyecto", "Clic para copiar", None),
            ("text", "06:38", "Informe trimestral Q1 — borrador final", "Clic para copiar", None),
            ("file", "06:38", "Propuesta-Cliente.pdf", "Clic para copiar archivo", None),
            ("image", "06:38", "", "Clic para copiar imagen", LANDSCAPE),
        ],
        "footer_count": "34 elementos",
        "clear": "Limpiar",
        "labels": {"text": "Texto", "image": "Imagen", "file": "Archivo"},
    },
    "en": {
        "filename": "promo-store-en",
        "menubar": ["Finder", "File", "Edit", "View", "Go", "Window", "Help"],
        "datetime": "Tue Jun  9  9:41 AM",
        "tagline": "Your clipboard history. Always available.",
        "features": [
            ("History", "Access everything you copied, whenever you need it.", "clipboard"),
            (
                "All kinds of content",
                "Text, images, files and more. All in one place.",
                "content",
            ),
            ("Private and secure", "Your data stays on your Mac.", "lock"),
        ],
        "subtitle": "Clipboard history",
        "cards": [
            ("text", "06:38", "Project follow-up meeting notes", "Click to copy", None),
            ("text", "06:38", "Q1 quarterly report — final draft", "Click to copy", None),
            ("file", "06:38", "Client-Proposal.pdf", "Click to copy file", None),
            ("image", "06:38", "", "Click to copy image", LANDSCAPE),
        ],
        "footer_count": "34 items",
        "clear": "Clear",
        "labels": {"text": "Text", "image": "Image", "file": "File"},
    },
}


def ensure_menubar_icons() -> None:
    required = ["apple", "control-center", "wifi", "battery", "spotlight", "clipkee"]
    if all((MENUBAR_ICONS_DIR / f"{name}.png").exists() for name in required):
        return
    subprocess.run(
        ["swift", str(EXPORT_MENUBAR_ICONS), str(MENUBAR_ICONS_DIR)],
        check=True,
    )


def menubar_icon(name: str, width: int, height: int | None = None) -> str:
    path = MENUBAR_ICONS_DIR / f"{name}.png"
    h = height or width
    return f'<span class="menubar-icon"><img src="{path.as_uri()}" width="{width}" height="{h}" alt=""></span>'


def menubar_html(locale: dict) -> str:
    menu_items = "".join(
        f'<span class="menubar-item">{item}</span>' for item in locale["menubar"][1:]
    )
    # System status icons stay on the far right; ClipKee icon sits above the panel.
    status_icons = "".join(
        [
            menubar_icon("control-center", 14, 14),
            menubar_icon("wifi", 15, 11),
            menubar_icon("battery", 24, 11),
            menubar_icon("spotlight", 13, 13),
        ]
    )
    return f"""
    <div class="menubar">
      <div class="menubar-left">
        {menubar_icon("apple", 13, 16)}
        <span class="menubar-app">{locale["menubar"][0]}</span>
        {menu_items}
      </div>
      <div class="menubar-right">
        {status_icons}
        <span class="menubar-datetime">{locale["datetime"]}</span>
      </div>
    </div>
    """


def app_status_html() -> str:
    return f"""
    <div class="app-status-wrap">
      <div class="status-app-icon"><img src="{MENU_BAR_ICON}" alt="ClipKee"></div>
    </div>
    """


def dock_html() -> str:
    apps = [
        "finder",
        "safari",
        "mail",
        "maps",
        "photos",
        "calendar",
        "notes",
        "reminders",
        "tv",
        "music",
        "podcasts",
        "appstore",
        "settings",
    ]
    icons = []
    for name in apps:
        path = DOCK_ICONS_DIR / f"{name}.png"
        if path.exists():
            icons.append(f'<div class="dock-icon"><img src="{path.as_uri()}" alt="{name}"></div>')
    icons.append(f'<div class="dock-icon app"><img src="{DOCK_ICON}" alt="ClipKee"></div>')
    return "".join(icons)


def feature_icon(kind: str) -> str:
    if kind == "clipboard":
        return """
        <svg viewBox="0 0 24 24" width="32" height="32" fill="#178f86" aria-hidden="true">
          <path d="M8 2.5h8A2.5 2.5 0 0 1 18.5 5v1.2h1A2.5 2.5 0 0 1 22 8.7v11.8A2.5 2.5 0 0 1 19.5 23h-15A2.5 2.5 0 0 1 2 20.5V8.7A2.5 2.5 0 0 1 4.5 6.2h1V5A2.5 2.5 0 0 1 8 2.5Zm8 3.2H8V5a.8.8 0 0 1 .8-.8h6.4a.8.8 0 0 1 .8.8v.7ZM5.2 8.2a.8.8 0 0 0-.8.8v11.5c0 .44.36.8.8.8h13.6a.8.8 0 0 0 .8-.8V9a.8.8 0 0 0-.8-.8H5.2Zm4.3 3.8h5a1 1 0 1 1 0 2h-5a1 1 0 1 1 0-2Zm0 4h7.5a1 1 0 1 1 0 2H9.5a1 1 0 1 1 0-2Z"/>
        </svg>
        """
    if kind == "content":
        return """
        <svg viewBox="0 0 24 24" width="32" height="32" fill="#178f86" aria-hidden="true">
          <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v13A2.5 2.5 0 0 1 17.5 21h-11A2.5 2.5 0 0 1 4 18.5v-13ZM6.5 5a.5.5 0 0 0-.5.5v13c0 .28.22.5.5.5h11a.5.5 0 0 0 .5-.5v-13a.5.5 0 0 0-.5-.5h-11Zm2 2.5h9v1.8h-9V7.5Zm0 4h6v1.8h-6v-1.8Z"/>
        </svg>
        """
    return """
    <svg viewBox="0 0 24 24" width="32" height="32" fill="#178f86" aria-hidden="true">
      <path d="M12 2a5 5 0 0 1 5 5v2h1.2A2.8 2.8 0 0 1 21 11.8v8.4A2.8 2.8 0 0 1 18.2 23H5.8A2.8 2.8 0 0 1 3 20.2v-8.4A2.8 2.8 0 0 1 5.8 9H7V7a5 5 0 0 1 5-5Zm0 2.8A2.2 2.2 0 0 0 9.8 7v2h4.4V7A2.2 2.2 0 0 0 12 4.8ZM5.8 10.8a1.3 1.3 0 0 0-1.3 1.3v8.1c0 .72.58 1.3 1.3 1.3h12.4c.72 0 1.3-.58 1.3-1.3v-8.1a1.3 1.3 0 0 0-1.3-1.3H5.8Z"/>
    </svg>
    """


def card_html(locale: dict, kind: str, time: str, body: str, hint: str, image_url: str | None) -> str:
    if kind == "text":
        icon = TEXT_ICON
    elif kind == "image":
        icon = PHOTO_ICON
    else:
        icon = DOC_ICON

    label = locale["labels"][kind]
    body_html = f'<div class="card-body">{body}</div>'
    if kind == "image" and image_url:
        body_html = f'<div class="image-preview"><img src="{image_url}" alt=""></div>'
    elif kind == "file":
        body_html = f"""
        <div class="file-row">{DOC_ICON}<span>{body}</span></div>
        """

    return f"""
    <div class="card">
      <div class="card-top">
        <div class="card-label">{icon}<span>{label}</span></div>
        <span>{time}</span>
      </div>
      {body_html}
      <div class="card-bottom">
        <span>{hint}</span>
        <span class="trash">{TRASH}</span>
      </div>
    </div>
    """


def panel_html(locale: dict) -> str:
    cards = "".join(
        card_html(locale, kind, time, body, hint, image)
        for kind, time, body, hint, image in locale["cards"]
    )
    return f"""
    <div class="panel">
      <div class="header">
        <div class="header-left"><h1>ClipKee</h1><p>{locale["subtitle"]}</p></div>
        <div class="header-actions">
          {SEARCH_ICON}
          {GEAR_ICON}
          {QUIT_ICON}
        </div>
      </div>
      <div class="divider"></div>
      <div class="cards">{cards}</div>
      <div class="divider"></div>
      <div class="footer"><span>{locale["footer_count"]}</span><button>{locale["clear"]}</button></div>
    </div>
    """


def features_html(locale: dict) -> str:
    rows = []
    for title, desc, icon_kind in locale["features"]:
        rows.append(
            f"""
            <div class="feature">
              <div class="feature-icon">{feature_icon(icon_kind)}</div>
              <div class="feature-copy">
                <h3>{title}</h3>
                <p>{desc}</p>
              </div>
            </div>
            """
        )
    return "".join(rows)


def page_html(locale: dict) -> str:
    return f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: {WIDTH}px; height: {HEIGHT}px; overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif;
}}
.desktop {{
  width: {WIDTH}px; height: {HEIGHT}px; position: relative; overflow: hidden;
}}
.wallpaper {{
  position: absolute; inset: 0;
  background: url('{WALLPAPER}') center/cover no-repeat;
}}
.overlay {{
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.10) 100%);
}}
.menubar {{
  height: 44px; background: rgba(255,255,255,0.22); backdrop-filter: blur(24px) saturate(180%);
  border-bottom: 1px solid rgba(255,255,255,0.28);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 18px; color: rgba(0,0,0,0.84); font-size: 13px; font-weight: 500;
  position: relative; z-index: 30;
}}
.menubar-left, .menubar-right {{ display: flex; align-items: center; gap: 14px; }}
.menubar-left {{ gap: 16px; }}
.menubar-app {{ font-weight: 600; }}
.menubar-item {{ opacity: 0.88; white-space: nowrap; }}
.menubar-icon {{
  display: flex; align-items: center; justify-content: center; opacity: 0.84;
}}
.menubar-icon img {{ display: block; }}
.menubar-datetime {{
  font-size: 12.5px; font-weight: 500; letter-spacing: -0.1px;
  opacity: 0.88; white-space: nowrap; margin-left: 2px;
}}
.menu-icon {{
  width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;
  margin-left: 4px;
}}
.menu-icon img {{ width: 18px; height: 18px; display: block; filter: contrast(1.15); }}
.app-status-wrap {{
  position: absolute; top: 0; right: {PANEL_RIGHT}px; z-index: 31;
  width: {PANEL_WIDTH}px; height: 44px;
  display: flex; align-items: center; justify-content: flex-end;
  padding-right: 6px;
}}
.status-app-icon {{
  width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;
}}
.status-app-icon img {{ width: 18px; height: 18px; display: block; }}
.marketing-card {{
  position: absolute; left: 96px; top: 50%; transform: translateY(-46%);
  width: 980px; padding: 44px 48px 40px;
  background: rgba(255,255,255,0.82); backdrop-filter: blur(28px) saturate(160%);
  border: 1px solid rgba(255,255,255,0.72); border-radius: 28px;
  box-shadow: 0 24px 70px rgba(0,0,0,0.18);
  z-index: 12;
}}
.app-icon {{ width: 118px; height: 118px; border-radius: 26px; display: block; margin-bottom: 28px; box-shadow: 0 18px 40px rgba(0,0,0,0.18); }}
.marketing-card h1 {{ font-size: 108px; line-height: 0.98; letter-spacing: -2px; color: rgba(0,0,0,0.88); margin-bottom: 20px; }}
.tagline {{ font-size: 40px; line-height: 1.25; color: #178f86; font-weight: 600; margin-bottom: 44px; max-width: 820px; }}
.feature {{ display: flex; gap: 20px; align-items: flex-start; margin-bottom: 30px; }}
.feature-icon {{ width: 46px; flex: 0 0 46px; display: flex; align-items: center; justify-content: center; padding-top: 2px; }}
.feature-copy h3 {{ font-size: 32px; line-height: 1.15; color: rgba(0,0,0,0.86); margin-bottom: 8px; font-weight: 700; }}
.feature-copy p {{ font-size: 28px; line-height: 1.35; color: rgba(0,0,0,0.56); max-width: 740px; }}
.panel-wrap {{
  position: absolute; top: 48px; right: {PANEL_RIGHT}px; z-index: 25;
}}
.panel {{
  width: {PANEL_WIDTH}px; min-height: 560px; border-radius: 12px; overflow: hidden;
  background: rgba(255,255,255,0.74); backdrop-filter: blur(28px) saturate(160%);
  border: 1px solid rgba(255,255,255,0.55); box-shadow: 0 22px 60px rgba(0,0,0,0.22);
  display: flex; flex-direction: column;
}}
.header {{ padding: 14px; display: flex; align-items: center; justify-content: space-between; }}
.header-left h1 {{ font-size: 15px; font-weight: 600; letter-spacing: -0.2px; color: rgba(0,0,0,0.88); }}
.header-left p {{ font-size: 11px; color: rgba(0,0,0,0.45); margin-top: 2px; }}
.header-actions {{ display: flex; gap: 10px; align-items: center; color: rgba(0,0,0,0.45); }}
.divider {{ height: 1px; background: rgba(0,0,0,0.08); }}
.cards {{ padding: 12px; display: flex; flex-direction: column; gap: 10px; }}
.card {{
  border-radius: 16px; padding: 12px; background: rgba(255,255,255,0.96);
  border: 1px solid rgba(0,0,0,0.08);
}}
.card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; color: rgba(0,0,0,0.45); font-size: 11px; }}
.card-label {{ display: flex; align-items: center; gap: 5px; }}
.card-body {{ font-size: 13px; line-height: 1.45; color: rgba(0,0,0,0.86); margin-bottom: 10px; }}
.file-row {{ display: flex; align-items: center; gap: 8px; font-size: 13px; color: rgba(0,0,0,0.86); margin-bottom: 10px; }}
.card-bottom {{ display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: rgba(0,0,0,0.45); }}
.trash {{ color: rgba(0,0,0,0.38); display: flex; align-items: center; }}
.image-preview {{
  height: 118px; border-radius: 12px; background: rgba(0,0,0,0.05);
  overflow: hidden; margin-bottom: 10px;
}}
.image-preview img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 10px; }}
.footer {{ padding: 10px 14px; display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: rgba(0,0,0,0.45); }}
.footer button {{ border: none; background: transparent; font: inherit; color: inherit; }}
.dock-wrap {{
  position: absolute; left: 50%; bottom: 18px; transform: translateX(-50%); z-index: 20;
}}
.dock {{
  display: flex; align-items: end; gap: 12px; padding: 10px 16px 8px;
  background: rgba(255,255,255,0.34); backdrop-filter: blur(28px) saturate(180%);
  border: 1px solid rgba(255,255,255,0.42); border-radius: 22px;
  box-shadow: 0 16px 40px rgba(0,0,0,0.16);
}}
.dock-icon {{
  width: 52px; height: 52px; border-radius: 12px; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
}}
.dock-icon img {{ width: 52px; height: 52px; border-radius: 12px; display: block; }}
.dock-icon.app {{ width: 58px; height: 58px; }}
.dock-icon.app img {{ width: 58px; height: 58px; border-radius: 14px; }}
</style></head>
<body>
  <div class="desktop">
    <div class="wallpaper"></div>
    <div class="overlay"></div>
    {menubar_html(locale)}
    {app_status_html()}
    <div class="marketing-card">
      <img class="app-icon" src="{APP_ICON}" alt="ClipKee">
      <h1>ClipKee</h1>
      <p class="tagline">{locale["tagline"]}</p>
      {features_html(locale)}
    </div>
    <div class="panel-wrap">{panel_html(locale)}</div>
    <div class="dock-wrap">
      <div class="dock">
        {dock_html()}
      </div>
    </div>
  </div>
</body></html>
"""


def render(name: str, html: str) -> None:
    html_path = ROOT / f"{name}.html"
    png_path = ROOT / f"{name}.png"
    html_path.write_text(html, encoding="utf-8")
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={WIDTH},{HEIGHT}",
            f"--screenshot={png_path}",
            html_path.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for w, h in [(1280, 800), (1440, 900), (2560, 1600), (2880, 1800)]:
        out = ROOT / f"{name}-{w}x{h}.png"
        subprocess.run(
            ["sips", "-z", str(h), str(w), str(png_path), "--out", str(out)],
            check=True,
            stdout=subprocess.DEVNULL,
        )


def main() -> None:
    ensure_menubar_icons()
    for locale in LOCALES.values():
        name = locale["filename"]
        print(f"Rendering {name}...")
        render(name, page_html(locale))
    print("Done.")


if __name__ == "__main__":
    main()
