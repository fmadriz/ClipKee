#!/usr/bin/env python3
"""Render App Store preview videos with cursor interaction and real app UI copy."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FFMPEG = shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg"
MENU_BAR_ICON = (ROOT / "menubar-icons/clipkee.png").as_uri()
WALLPAPER = (
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=3840&q=80"
)
LANDSCAPE = (
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=800&q=80"
)

WIDTH = 1920
HEIGHT = 1080
RENDER_FPS = 20
OUTPUT_FPS = 30
DURATION_SECONDS = 20
APP_VERSION = "1.0.2"

# Panel placement (matches MenuBarExtra window: 360×560)
PANEL_RIGHT = 280
PANEL_TOP = 32
PANEL_WIDTH = 360
PANEL_HEIGHT = 560
PANEL_LEFT = WIDTH - PANEL_RIGHT - PANEL_WIDTH

# Interaction targets (screen coordinates)
POINTS = {
    "start": (1500, 820),
    "menubar_icon": (PANEL_LEFT + PANEL_WIDTH - 18, 16),
    "search_btn": (PANEL_LEFT + 268, PANEL_TOP + 24),
    "search_field": (PANEL_LEFT + 150, PANEL_TOP + 58),
    "card_0": (PANEL_LEFT + 180, PANEL_TOP + 118),
    "card_1": (PANEL_LEFT + 180, PANEL_TOP + 210),
    "gear_btn": (PANEL_LEFT + 298, PANEL_TOP + 24),
    "settings_checkbox": (PANEL_LEFT + 52, PANEL_TOP + 168),
    "settings_done": (PANEL_LEFT + 180, PANEL_TOP + 248),
}

LOCALES = {
    "es": {
        "output": "app-preview-es",
        "datetime": "Mar 9 de jun  9:41",
        "menubar": ["Finder", "Archivo", "Edición", "Visualización", "Ir", "Ventana", "Ayuda"],
        "subtitle": "Historial del portapapeles",
        "settings": "Ajustes",
        "launch_at_login": "Abrir ClipKee al iniciar sesión en este Mac",
        "done": "Listo",
        "search_placeholder": "Buscar en textos copiados...",
        "clear": "Limpiar",
        "footer_all": "34 elementos",
        "footer_filtered": "2 de 34 elementos",
        "text": "Texto",
        "image": "Imagen",
        "file": "Archivo",
        "click_copy": "Clic para copiar",
        "click_copy_image": "Clic para copiar imagen",
        "click_copy_file": "Clic para copiar archivo",
        "text_copied": "Texto copiado",
        "search_term": "proyecto",
        "cards_history": [
            ("text", "09:42", "Reunión seguimiento proyecto", "click_copy"),
            ("text", "09:38", "Informe trimestral Q1 — borrador final", "click_copy"),
            ("file", "09:35", "Propuesta-Cliente.pdf", "click_copy_file"),
        ],
        "cards_filtered": [
            ("text", "09:42", "Reunión seguimiento proyecto", "click_copy"),
            ("text", "09:38", "Informe trimestral Q1 — borrador final", "click_copy"),
        ],
        "cards_mixed": [
            ("text", "09:42", "Reunión seguimiento proyecto", "click_copy"),
            ("image", "09:35", "", "click_copy_image"),
            ("file", "09:31", "Propuesta-Cliente.pdf", "click_copy_file"),
        ],
    },
    "en": {
        "output": "app-preview-en",
        "datetime": "Tue Jun  9  9:41 AM",
        "menubar": ["Finder", "File", "Edit", "View", "Go", "Window", "Help"],
        "subtitle": "Clipboard history",
        "settings": "Settings",
        "launch_at_login": "Open ClipKee when I log in to this Mac",
        "done": "Done",
        "search_placeholder": "Search copied text...",
        "clear": "Clear",
        "footer_all": "34 items",
        "footer_filtered": "2 of 34 items",
        "text": "Text",
        "image": "Image",
        "file": "File",
        "click_copy": "Click to copy",
        "click_copy_image": "Click to copy image",
        "click_copy_file": "Click to copy file",
        "text_copied": "Text copied",
        "search_term": "project",
        "cards_history": [
            ("text", "09:42", "Project follow-up meeting notes", "click_copy"),
            ("text", "09:38", "Q1 quarterly report — final draft", "click_copy"),
            ("file", "09:35", "Client-Proposal.pdf", "click_copy_file"),
        ],
        "cards_filtered": [
            ("text", "09:42", "Project follow-up meeting notes", "click_copy"),
            ("text", "09:38", "Q1 quarterly report — final draft", "click_copy"),
        ],
        "cards_mixed": [
            ("text", "09:42", "Project follow-up meeting notes", "click_copy"),
            ("image", "09:35", "", "click_copy_image"),
            ("file", "09:31", "Client-Proposal.pdf", "click_copy_file"),
        ],
    },
}


@dataclass
class FrameState:
    cursor: tuple[float, float]
    clicking: bool
    panel_open: bool
    search_visible: bool
    search_text: str
    search_active: bool
    cards: list[tuple]
    copied_index: int | None
    settings_visible: bool
    footer: str


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_point(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))


def move_cursor(
    frame: int,
    start_f: int,
    end_f: int,
    start_pt: tuple[float, float],
    end_pt: tuple[float, float],
) -> tuple[float, float]:
    if frame < start_f:
        return start_pt
    if frame >= end_f:
        return end_pt
    t = smoothstep((frame - start_f) / max(1, end_f - start_f))
    return lerp_point(start_pt, end_pt, t)


def clicking(frame: int, click_frame: int, duration: int = 8) -> bool:
    return click_frame <= frame < click_frame + duration


def build_timeline(locale: dict) -> list[FrameState]:
    term = locale["search_term"]
    total = int(DURATION_SECONDS * RENDER_FPS)
    states: list[FrameState] = []

    def sec(s: float) -> int:
        return int(s * RENDER_FPS)

    for f in range(total):
        panel_open = f >= sec(1.2)
        search_visible = f >= sec(4.2)
        settings_visible = sec(15.7) <= f < sec(18.7)
        copied_index = 0 if sec(11.8) <= f < sec(13.5) else None
        cards = locale["cards_history"]
        footer = locale["footer_all"]
        search_text = ""

        if f >= sec(13.5):
            cards = locale["cards_mixed"]
        elif f >= sec(4.8):
            cards = locale["cards_filtered"]
            footer = locale["footer_filtered"]
            chars = min(len(term), max(0, (f - sec(5.2)) // 2))
            search_text = term[:chars]

        cursor = POINTS["start"]
        click = False

        if f < sec(1.2):
            cursor = move_cursor(f, 0, sec(1.1), POINTS["start"], POINTS["menubar_icon"])
            click = clicking(f, sec(1.0))
        elif f < sec(4.2):
            cursor = move_cursor(f, sec(1.3), sec(2.5), POINTS["menubar_icon"], POINTS["card_0"])
            if f >= sec(3.0):
                cursor = move_cursor(f, sec(3.0), sec(4.1), POINTS["card_0"], POINTS["search_btn"])
            click = clicking(f, sec(4.0))
        elif f < sec(7.0):
            cursor = move_cursor(f, sec(4.2), sec(5.0), POINTS["search_btn"], POINTS["search_field"])
            if f >= sec(5.0):
                cursor = POINTS["search_field"]
            click = clicking(f, sec(4.3))
        elif f < sec(11.8):
            cursor = move_cursor(f, sec(7.0), sec(8.3), POINTS["search_field"], POINTS["card_0"])
            if f >= sec(8.3):
                cursor = POINTS["card_0"]
            click = clicking(f, sec(11.5))
        elif f < sec(15.7):
            cursor = move_cursor(f, sec(13.5), sec(14.8), POINTS["card_0"], POINTS["gear_btn"])
            if f >= sec(14.8):
                cursor = POINTS["gear_btn"]
            click = clicking(f, sec(15.5))
        elif f < sec(18.7):
            cursor = move_cursor(f, sec(15.7), sec(17.0), POINTS["gear_btn"], POINTS["settings_done"])
            if f >= sec(17.0):
                cursor = POINTS["settings_done"]
            click = clicking(f, sec(18.2))
        else:
            cursor = move_cursor(f, sec(18.7), sec(19.7), POINTS["settings_done"], POINTS["card_0"])
            settings_visible = False

        states.append(
            FrameState(
                cursor=cursor,
                clicking=click,
                panel_open=panel_open,
                search_visible=search_visible,
                search_text=search_text,
                search_active=f >= sec(4.8),
                cards=cards,
                copied_index=copied_index,
                settings_visible=settings_visible,
                footer=footer,
            )
        )

    return states


TRASH_ICON = """
<svg viewBox="0 0 16 18" width="12" height="13" fill="currentColor" aria-hidden="true">
  <path d="M3 4.5h10l-.8 10.2a1.5 1.5 0 0 1-1.5 1.3H5.3a1.5 1.5 0 0 1-1.5-1.3L3 4.5Zm2.1-.5L5 2.8A1 1 0 0 1 6 2h4a1 1 0 0 1 1 .8l-.1.2h2.1a.75.75 0 0 1 0 1.5H5.1a.75.75 0 0 1 0-1.5H5.1Z"/>
</svg>
"""

KIND_ICONS = {
    "text": "text.alignleft",
    "image": "photo",
    "file": "doc",
}


def card_html(locale: dict, kind: str, time: str, body: str, hint_key: str, copied: bool) -> str:
    label = locale[kind]
    hint = locale[hint_key]
    if kind == "image":
        body_html = f'<div class="image-preview"><img src="{LANDSCAPE}" alt=""></div>'
    elif kind == "file":
        body_html = f"""
        <div class="file-row">
          <svg viewBox="0 0 16 18" width="13" height="14" fill="currentColor" opacity="0.55"><path d="M3 1.5h6.5L14 6v10.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 16.5v-14A1.5 1.5 0 0 1 3.5 1H3Zm6 0V6h4.5L9 1.5Z"/></svg>
          <span>{body}</span>
        </div>
        """
    else:
        body_html = f'<div class="card-body">{body}</div>'

    overlay = ""
    if copied:
        overlay = f"""
        <div class="copied-overlay">
          <svg viewBox="0 0 20 20" width="24" height="24" fill="currentColor"><path d="M10 1.5a8.5 8.5 0 1 1 0 17 8.5 8.5 0 0 1 0-17Zm3.53 5.47-4.6 4.6-1.77-1.77a.75.75 0 1 0-1.06 1.06l2.3 2.3a.75.75 0 0 0 1.06 0l5.13-5.13a.75.75 0 1 0-1.06-1.06Z"/></svg>
          <span>{locale["text_copied"]}</span>
        </div>
        """

    return f"""
    <div class="card">
      {overlay}
      <div class="card-top">
        <div class="card-label">
          <svg viewBox="0 0 20 20" width="11" height="11" fill="currentColor" opacity="0.55"><circle cx="10" cy="10" r="8"/></svg>
          <span>{label}</span>
        </div>
        <span>{time}</span>
      </div>
      {body_html}
      <div class="card-bottom"><span>{hint}</span><span class="trash">{TRASH_ICON}</span></div>
    </div>
    """


def panel_html(locale: dict, state: FrameState) -> str:
    if not state.panel_open:
        return ""

    cards = "".join(
        card_html(locale, kind, time, body, hint_key, copied=(index == state.copied_index))
        for index, (kind, time, body, hint_key) in enumerate(state.cards)
    )

    search_html = ""
    if state.search_visible:
        clear_btn = (
            '<button class="icon-btn" aria-label="clear">×</button>' if state.search_text else ""
        )
        search_html = f"""
        <div class="searchbar">
          <svg viewBox="0 0 20 20" width="14" height="14" fill="currentColor" opacity="0.45"><path d="M8.5 2a6.5 6.5 0 1 1 0 13 6.5 6.5 0 0 1 0-13Zm0 1.5a5 5 0 1 0 0 10 5 5 0 0 0 0-10Zm7.03 11.47a.75.75 0 1 1 1.06 1.06l-2.7 2.7a.75.75 0 1 1-1.06-1.06l2.7-2.7Z"/></svg>
          <span class="search-text {'filled' if state.search_text else 'placeholder'}">{state.search_text or locale["search_placeholder"]}</span>
          {clear_btn}
          <button class="icon-btn" aria-label="hide">×</button>
        </div>
        """

    settings_html = ""
    if state.settings_visible:
        settings_html = f"""
        <div class="modal-backdrop">
          <div class="settings-card">
            <div class="settings-header">{locale["settings"]}</div>
            <div class="settings-divider"></div>
            <label class="settings-toggle">
              <input type="checkbox" checked>
              <span>{locale["launch_at_login"]}</span>
            </label>
            <button class="done-btn">{locale["done"]}</button>
            <div class="settings-version">ClipKee {APP_VERSION}</div>
          </div>
        </div>
        """

    search_icon_class = "header-btn active" if state.search_visible else "header-btn"
    gear_class = "header-btn active" if state.settings_visible else "header-btn"

    return f"""
    <div class="panel" style="left:{PANEL_LEFT}px;top:{PANEL_TOP}px">
      <div class="header">
        <div class="header-left">
          <h1>ClipKee</h1>
          <p>{locale["subtitle"]}</p>
        </div>
        <div class="header-actions">
          <div class="{search_icon_class}">
            <svg viewBox="0 0 20 20" width="18" height="18" fill="currentColor"><path d="M8.5 2a6.5 6.5 0 1 1 0 13 6.5 6.5 0 0 1 0-13Zm0 1.5a5 5 0 1 0 0 10 5 5 0 0 0 0-10Zm7.03 11.47a.75.75 0 1 1 1.06 1.06l-2.7 2.7a.75.75 0 1 1-1.06-1.06l2.7-2.7Z"/></svg>
          </div>
          <div class="{gear_class}">
            <svg viewBox="0 0 20 20" width="18" height="18" fill="currentColor"><path d="M8.59 1.5h2.82l.28 1.64a5.6 5.6 0 0 1 1.47.85l1.57-.6 1.99 1.99-.6 1.57c.36.46.64.96.85 1.47l1.64.28v2.82l-1.64.28a5.6 5.6 0 0 1-.85 1.47l.6 1.57-1.99 1.99-1.57-.6a5.6 5.6 0 0 1-1.47.85l-.28 1.64H8.59l-.28-1.64a5.6 5.6 0 0 1-1.47-.85l-1.57.6-1.99-1.99.6-1.57a5.6 5.6 0 0 1-.85-1.47L1.5 11.41V8.59l1.64-.28c.21-.51.49-1.01.85-1.47l-.6-1.57 1.99-1.99 1.57.6c.46-.36.96-.64 1.47-.85l.28-1.64ZM10 7.2A2.8 2.8 0 1 0 12.8 10 2.8 2.8 0 0 0 10 7.2Z"/></svg>
          </div>
          <div class="header-btn">
            <svg viewBox="0 0 20 20" width="18" height="18" fill="currentColor"><path d="M10 1.5a8.5 8.5 0 1 1 0 17 8.5 8.5 0 0 1 0-17Zm3.53 5.47a.75.75 0 1 0-1.06-1.06L10 8.94 7.53 6.47A.75.75 0 0 0 6.47 7.53L8.94 10l-2.47 2.47a.75.75 0 1 0 1.06 1.06L10 11.06l2.47 2.47a.75.75 0 0 0 1.06-1.06L11.06 10l2.47-2.47Z"/></svg>
          </div>
        </div>
      </div>
      {search_html}
      <div class="divider"></div>
      <div class="cards">{cards}</div>
      <div class="divider"></div>
      <div class="footer"><span>{state.footer}</span><button>{locale["clear"]}</button></div>
      {settings_html}
    </div>
    """


def cursor_html(state: FrameState) -> str:
    x, y = state.cursor
    scale = 0.92 if state.clicking else 1.0
    return f"""
    <div class="cursor {"clicking" if state.clicking else ""}" style="left:{x}px;top:{y}px;transform:scale({scale})">
      <svg viewBox="0 0 24 28" width="22" height="26" aria-hidden="true">
        <path d="M4 2l2 18 4-4 5 8 3-1-5-8h6L4 2z" fill="#111" stroke="#fff" stroke-width="1.2" stroke-linejoin="round"/>
      </svg>
    </div>
    """


def frame_html(locale: dict, state: FrameState, *, include_cursor: bool = True) -> str:
    menu_items = "".join(f"<span>{item}</span>" for item in locale["menubar"][1:])
    menubar_icon = ""
    if state.panel_open:
        menubar_icon = f"""
        <div class="status-app-icon" style="left:{PANEL_LEFT + PANEL_WIDTH - 22}px">
          <img src="{MENU_BAR_ICON}" alt="">
        </div>
        """

    return f"""<!DOCTYPE html>
<html><head><meta charset='utf-8'>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: {WIDTH}px; height: {HEIGHT}px; overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", sans-serif;
}}
.desktop {{ width: {WIDTH}px; height: {HEIGHT}px; position: relative; overflow: hidden; }}
.wallpaper {{ position: absolute; inset: 0; background: url('{WALLPAPER}') center/cover no-repeat; }}
.overlay {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.08)); }}
.menubar {{
  height: 28px; background: rgba(255,255,255,0.22); backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255,255,255,0.28);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 14px; color: rgba(0,0,0,0.84); font-size: 12px; font-weight: 500; z-index: 10;
}}
.menubar-left, .menubar-right {{ display: flex; align-items: center; gap: 14px; }}
.menubar-left span:first-child {{ font-weight: 600; }}
.menubar-right {{ font-size: 11px; opacity: 0.88; }}
.status-app-icon {{
  position: absolute; top: 5px; width: 18px; height: 18px; z-index: 20;
  display: flex; align-items: center; justify-content: center;
}}
.status-app-icon img {{ width: 14px; height: 14px; display: block; }}
.panel {{
  position: absolute; width: {PANEL_WIDTH}px; height: {PANEL_HEIGHT}px;
  border-radius: 12px; overflow: hidden; z-index: 15;
  background: rgba(246,246,246,0.82); backdrop-filter: blur(28px) saturate(160%);
  border: 1px solid rgba(255,255,255,0.55); box-shadow: 0 22px 60px rgba(0,0,0,0.22);
  display: flex; flex-direction: column;
}}
.header {{ padding: 14px; display: flex; align-items: center; justify-content: space-between; }}
.header-left h1 {{ font-size: 15px; font-weight: 600; letter-spacing: -0.2px; color: rgba(0,0,0,0.88); }}
.header-left p {{ font-size: 11px; color: rgba(0,0,0,0.45); margin-top: 2px; }}
.header-actions {{ display: flex; gap: 8px; align-items: center; color: rgba(0,0,0,0.45); }}
.header-btn {{ opacity: 0.55; display: flex; }}
.header-btn.active {{ opacity: 0.95; color: rgba(0,0,0,0.85); }}
.searchbar {{
  display: flex; align-items: center; gap: 8px; padding: 10px 14px;
  background: rgba(0,0,0,0.04); font-size: 13px; color: rgba(0,0,0,0.55);
}}
.search-text.placeholder {{ color: rgba(0,0,0,0.45); }}
.search-text.filled {{ color: rgba(0,0,0,0.82); }}
.icon-btn {{
  border: none; background: transparent; color: rgba(0,0,0,0.45);
  font-size: 14px; width: 18px; height: 18px; line-height: 1;
}}
.divider {{ height: 1px; background: rgba(0,0,0,0.08); flex-shrink: 0; }}
.cards {{ padding: 12px; display: flex; flex-direction: column; gap: 10px; overflow: hidden; flex: 1; }}
.card {{
  position: relative; border-radius: 16px; padding: 12px;
  background: rgba(255,255,255,0.96); border: 1px solid rgba(0,0,0,0.08);
}}
.card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; color: rgba(0,0,0,0.45); font-size: 11px; }}
.card-label {{ display: flex; align-items: center; gap: 5px; }}
.card-body {{ font-size: 13px; line-height: 1.45; color: rgba(0,0,0,0.86); margin-bottom: 10px; }}
.file-row {{ display: flex; align-items: center; gap: 8px; font-size: 13px; color: rgba(0,0,0,0.86); margin-bottom: 10px; }}
.card-bottom {{ display: flex; justify-content: space-between; align-items: center; font-size: 10px; color: rgba(0,0,0,0.45); }}
.trash {{ color: rgba(0,0,0,0.38); display: flex; }}
.image-preview {{ height: 118px; border-radius: 12px; overflow: hidden; margin-bottom: 10px; background: rgba(0,0,0,0.04); }}
.image-preview img {{ width: 100%; height: 100%; object-fit: cover; }}
.copied-overlay {{
  position: absolute; inset: 0; border-radius: 16px; z-index: 2;
  background: rgba(0,0,0,0.45); display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 8px; color: white;
}}
.copied-overlay span {{ font-size: 12px; font-weight: 600; }}
.footer {{ padding: 10px 14px; display: flex; justify-content: space-between; font-size: 11px; color: rgba(0,0,0,0.45); }}
.footer button {{ border: none; background: transparent; font: inherit; color: inherit; }}
.modal-backdrop {{
  position: absolute; inset: 0; background: rgba(0,0,0,0.45); z-index: 5;
  display: flex; align-items: center; justify-content: center;
}}
.settings-card {{
  width: 300px; background: rgba(246,246,246,0.92); backdrop-filter: blur(24px);
  border-radius: 16px; border: 1px solid rgba(0,0,0,0.08);
  box-shadow: 0 24px 60px rgba(0,0,0,0.25); padding-bottom: 16px;
  display: flex; flex-direction: column;
}}
.settings-header {{ padding: 14px; font-size: 15px; font-weight: 600; }}
.settings-divider {{ height: 1px; background: rgba(0,0,0,0.08); }}
.settings-toggle {{
  display: flex; align-items: flex-start; gap: 10px; padding: 20px 20px 0;
  font-size: 13px; line-height: 1.4; color: rgba(0,0,0,0.88);
}}
.settings-toggle input {{ width: 14px; height: 14px; margin-top: 2px; accent-color: #007aff; }}
.done-btn {{
  margin: 28px 20px 0; border: none; border-radius: 8px; padding: 10px 16px;
  background: #007aff; color: white; font-size: 14px; font-weight: 500;
}}
.settings-version {{
  margin-top: auto; padding-top: 24px; text-align: center;
  font-size: 11px; color: rgba(0,0,0,0.35);
}}
.cursor {{
  position: absolute; z-index: 100; pointer-events: none;
  transform-origin: 0 0; filter: drop-shadow(0 1px 2px rgba(0,0,0,0.35));
}}
.cursor.clicking {{ filter: drop-shadow(0 1px 1px rgba(0,0,0,0.25)); }}
</style></head>
<body>
  <div class="desktop">
    <div class="wallpaper"></div>
    <div class="overlay"></div>
    <div class="menubar">
      <div class="menubar-left">
        <span>{locale["menubar"][0]}</span>
        {menu_items}
      </div>
      <div class="menubar-right"><span>{locale["datetime"]}</span></div>
    </div>
    {menubar_icon}
    {panel_html(locale, state)}
    {cursor_html(state) if include_cursor else ""}
  </div>
</body></html>
"""


def state_cache_key(state: FrameState) -> tuple:
    return (
        state.panel_open,
        state.search_visible,
        state.search_text,
        state.search_active,
        tuple(state.cards),
        state.copied_index,
        state.settings_visible,
        state.footer,
    )


def draw_cursor(image: Image.Image, state: FrameState) -> Image.Image:
    frame = image.copy()
    draw = ImageDraw.Draw(frame)
    x, y = state.cursor
    scale = 0.92 if state.clicking else 1.0
    # macOS pointer simplified polygon
    points = [
        (x, y),
        (x + 3 * scale, y + 16 * scale),
        (x + 7 * scale, y + 12 * scale),
        (x + 11 * scale, y + 20 * scale),
        (x + 14 * scale, y + 19 * scale),
        (x + 10 * scale, y + 11 * scale),
        (x + 16 * scale, y + 11 * scale),
    ]
    draw.polygon(points, fill=(20, 20, 20), outline=(255, 255, 255))
    return frame


def render_png(html: str, path: Path) -> None:
    html_path = path.with_suffix(".html")
    html_path.write_text(html, encoding="utf-8")
    subprocess.run(
        [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            f"--window-size={WIDTH},{HEIGHT}",
            f"--screenshot={path}",
            html_path.as_uri(),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def base_image(locale: dict, state: FrameState, cache: dict[tuple, Image.Image]) -> Image.Image:
    key = state_cache_key(state)
    if key not in cache:
        digest = hashlib.sha1(repr(key).encode()).hexdigest()[:12]
        tmp = ROOT / ".preview-cache" / f"{digest}.png"
        tmp.parent.mkdir(exist_ok=True)
        render_png(frame_html(locale, state, include_cursor=False), tmp)
        cache[key] = Image.open(tmp).convert("RGBA")
    return cache[key]


def render_locale(locale: dict) -> None:
    frames_dir = ROOT / f"{locale['output']}-frames"
    frames_dir.mkdir(exist_ok=True)

    timeline = build_timeline(locale)
    cache: dict[tuple, Image.Image] = {}
    total = len(timeline)
    print(f"  rendering {total} frames...")

    for index, state in enumerate(timeline):
        if index % 20 == 0:
            print(f"    frame {index + 1}/{total} (cached bases: {len(cache)})")
        base = base_image(locale, state, cache)
        frame = draw_cursor(base, state)
        frame.convert("RGB").save(frames_dir / f"frame-{index + 1:05d}.png", optimize=True)

    output = ROOT / f"{locale['output']}.mp4"
    print(f"  encoding {output.name}...")
    encode_video(frames_dir, output)
    print(f"  created {output}")


def encode_video(frames_dir: Path, output: Path) -> None:
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-framerate",
            str(RENDER_FPS),
            "-i",
            str(frames_dir / "frame-%05d.png"),
            "-c:v",
            "libx264",
            "-profile:v",
            "high",
            "-level",
            "4.0",
            "-b:v",
            "10M",
            "-maxrate",
            "12M",
            "-bufsize",
            "16M",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(OUTPUT_FPS),
            "-movflags",
            "+faststart",
            str(output),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> None:
    icon_path = ROOT / "menubar-icons/clipkee.png"
    if not icon_path.exists():
        subprocess.run(["python3", str(ROOT / "render-promo-store.py")], check=True)

    for locale in LOCALES.values():
        print(f"Rendering {locale['output']}...")
        render_locale(locale)

    print("Done.")


if __name__ == "__main__":
    main()
