"""
Light and dark themes for the standalone GUI window.

The themes are plain Qt style sheets built from a small palette, so no theme
package is needed. :class:`~je_api_testka.gui.main_window.APITestkaUI` applies
one; an application that embeds :class:`APITestkaWidget` keeps its own style.
Widgets opt into accents through object names and dynamic properties:
``#sidebar``, ``#pageTitle``, ``[role="primary"]`` buttons, ``[role="muted"]``
labels and ``[status="success"|"redirect"|"client-error"|"server-error"]``
badges.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

THEME_SYSTEM: str = "system"
THEME_LIGHT: str = "light"
THEME_DARK: str = "dark"


@dataclass(frozen=True)
class Palette:
    """Colours one theme is built from."""

    window: str
    surface: str
    raised: str
    border: str
    text: str
    muted: str
    accent: str
    accent_text: str
    sidebar: str
    selection: str
    success: str
    redirect: str
    client_error: str
    server_error: str


THEMES: Dict[str, Palette] = {
    THEME_LIGHT: Palette(window="#f6f8fa", surface="#ffffff", raised="#eef1f5", border="#d0d7de",
                         text="#1f2328", muted="#59636e", accent="#0969da", accent_text="#ffffff",
                         sidebar="#eaeef2", selection="#ddf4ff", success="#1a7f37", redirect="#9a6700",
                         client_error="#bc4c00", server_error="#cf222e"),
    THEME_DARK: Palette(window="#0d1117", surface="#161b22", raised="#21262d", border="#30363d",
                        text="#e6edf3", muted="#9198a1", accent="#4493f8", accent_text="#0d1117",
                        sidebar="#010409", selection="#1f3a5f", success="#3fb950", redirect="#d29922",
                        client_error="#f0883e", server_error="#f85149"),
}

_STYLESHEET = """
QWidget {{ background: {window}; color: {text}; font-size: 10pt; }}
QLineEdit, QPlainTextEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QListWidget, QTableWidget {{
    background: {surface}; border: 1px solid {border}; border-radius: 6px; padding: 4px 6px;
    selection-background-color: {selection}; selection-color: {text};
}}
QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{ border: 1px solid {accent}; }}
QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {{ width: 0; border: none; }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
QScrollBar::handle {{ background: {border}; border-radius: 5px; }}
QScrollBar::handle:vertical {{ min-height: 32px; }}
QScrollBar::handle:horizontal {{ min-width: 32px; }}
QScrollBar::handle:hover {{ background: {muted}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}
QPushButton {{ background: {raised}; border: 1px solid {border}; border-radius: 6px; padding: 5px 14px; }}
QPushButton:hover {{ border-color: {accent}; }}
QPushButton:disabled {{ color: {muted}; }}
QPushButton[role="primary"] {{ background: {accent}; color: {accent_text}; border-color: {accent};
    font-weight: 600; }}
QGroupBox {{ border: 1px solid {border}; border-radius: 8px; margin-top: 14px; padding: 10px 8px 8px 8px; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; color: {muted}; }}
QTabWidget::pane {{ border: 1px solid {border}; border-radius: 6px; background: {surface}; }}
QTabBar::tab {{ background: transparent; padding: 6px 12px; border-bottom: 2px solid transparent; }}
QTabBar::tab:selected {{ border-bottom: 2px solid {accent}; color: {text}; }}
QTabBar::tab:!selected {{ color: {muted}; }}
QHeaderView::section {{ background: {raised}; border: none; border-bottom: 1px solid {border}; padding: 4px; }}
QListWidget#sidebar {{ background: {sidebar}; border: none; border-radius: 0; padding: 8px 4px; outline: 0; }}
QListWidget#sidebar::item {{ padding: 8px 12px; border-radius: 6px; margin: 1px 4px; }}
QListWidget#sidebar::item:selected {{ background: {selection}; color: {text}; }}
QLabel#pageTitle {{ font-size: 15pt; font-weight: 600; padding: 2px 0 6px 0; }}
QLabel[role="muted"] {{ color: {muted}; }}
QLabel[status="success"] {{ color: {success}; font-weight: 600; }}
QLabel[status="redirect"] {{ color: {redirect}; font-weight: 600; }}
QLabel[status="client-error"] {{ color: {client_error}; font-weight: 600; }}
QLabel[status="server-error"] {{ color: {server_error}; font-weight: 600; }}
QSplitter::handle {{ background: {border}; }}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical {{ height: 1px; }}
QPlainTextEdit#console {{ font-family: Consolas, "Cascadia Mono", Menlo, monospace; font-size: 9pt; }}
"""


def build_stylesheet(name: str) -> str:
    """Return the style sheet of theme ``name`` (``light`` or ``dark``)."""
    try:
        palette = THEMES[name]
    except KeyError as error:
        raise ValueError(f"unknown theme {name!r}; expected one of {sorted(THEMES)}") from error
    return _STYLESHEET.format(**palette.__dict__)


def system_theme() -> str:
    """Return ``dark`` when the platform reports a dark colour scheme, else ``light``."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QGuiApplication

    scheme = QGuiApplication.styleHints().colorScheme()
    return THEME_DARK if scheme == Qt.ColorScheme.Dark else THEME_LIGHT


def resolve_theme(name: str) -> str:
    """Turn ``system`` into ``light`` or ``dark``; other names pass through."""
    return system_theme() if name == THEME_SYSTEM else name
