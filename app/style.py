# -*- coding: utf-8 -*-
"""全局样式表（QSS），统一蓝色主题 + 圆角 + 微软雅黑"""

# 主色调
COLOR_PRIMARY = "#2196F3"
COLOR_PRIMARY_DARK = "#1976D2"
COLOR_PRIMARY_LIGHT = "#BBDEFB"
COLOR_BG = "#F5F7FA"
COLOR_WHITE = "#FFFFFF"
COLOR_BORDER = "#D0D7DE"
COLOR_TEXT = "#222222"
COLOR_MUTED = "#666666"

# 状态色
COLOR_GREEN = "#4CAF50"
COLOR_BLUE = "#2196F3"
COLOR_GRAY = "#9E9E9E"

APP_QSS = f"""
* {{
    font-family: "Microsoft YaHei", "微软雅黑", "PingFang SC", "Segoe UI", sans-serif;
    font-size: 12px;
    color: {COLOR_TEXT};
}}

QMainWindow, QWidget {{
    background-color: {COLOR_BG};
}}

QLabel#TitleLabel {{
    font-size: 20px;
    font-weight: bold;
    color: {COLOR_PRIMARY_DARK};
    padding: 8px 0;
}}

QLabel#SubTitleLabel {{
    font-size: 14px;
    color: {COLOR_MUTED};
    padding: 2px 0;
}}

QLabel#SectionLabel {{
    font-size: 14px;
    font-weight: bold;
    color: {COLOR_PRIMARY_DARK};
    padding: 4px 0;
}}

QPushButton {{
    background-color: {COLOR_PRIMARY};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 14px;
    min-height: 24px;
}}

QPushButton:hover {{
    background-color: {COLOR_PRIMARY_DARK};
}}

QPushButton:disabled {{
    background-color: #BDBDBD;
    color: #EEEEEE;
}}

QPushButton#SecondaryButton {{
    background-color: {COLOR_WHITE};
    color: {COLOR_PRIMARY_DARK};
    border: 1px solid {COLOR_PRIMARY};
}}
QPushButton#SecondaryButton:hover {{
    background-color: {COLOR_PRIMARY_LIGHT};
}}

QPushButton#DangerButton {{
    background-color: #E53935;
}}
QPushButton#DangerButton:hover {{
    background-color: #C62828;
}}

QPushButton#BigButton {{
    font-size: 18px;
    font-weight: bold;
    padding: 30px 50px;
    border-radius: 10px;
    min-width: 200px;
    min-height: 100px;
}}

QPushButton#LinkButton {{
    background-color: transparent;
    color: {COLOR_PRIMARY_DARK};
    border: none;
    padding: 4px 8px;
    text-decoration: underline;
}}
QPushButton#LinkButton:hover {{
    color: {COLOR_PRIMARY};
}}

QLineEdit, QComboBox, QSpinBox, QTextEdit, QPlainTextEdit {{
    background-color: {COLOR_WHITE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 5px 8px;
    min-height: 22px;
    selection-background-color: {COLOR_PRIMARY_LIGHT};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTextEdit:focus {{
    border: 1px solid {COLOR_PRIMARY};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QCheckBox {{
    spacing: 6px;
}}

QTableWidget {{
    background-color: {COLOR_WHITE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    gridline-color: #E0E0E0;
    selection-background-color: {COLOR_PRIMARY_LIGHT};
    selection-color: {COLOR_TEXT};
}}
QTableWidget::item {{
    padding: 4px;
}}
QHeaderView::section {{
    background-color: #ECEFF1;
    color: {COLOR_TEXT};
    padding: 6px;
    border: none;
    border-right: 1px solid {COLOR_BORDER};
    border-bottom: 1px solid {COLOR_BORDER};
    font-weight: bold;
}}

QTreeWidget {{
    background-color: {COLOR_WHITE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 4px;
    selection-background-color: {COLOR_PRIMARY_LIGHT};
    selection-color: {COLOR_TEXT};
}}
QTreeWidget::item {{
    padding: 3px 2px;
}}

QListWidget {{
    background-color: {COLOR_WHITE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 4px;
    selection-background-color: {COLOR_PRIMARY_LIGHT};
    selection-color: {COLOR_TEXT};
}}
QListWidget::item {{
    padding: 6px 8px;
    border-radius: 4px;
}}

QGroupBox {{
    background-color: {COLOR_WHITE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    margin-top: 16px;
    padding: 16px 10px 10px 10px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px;
    color: {COLOR_PRIMARY_DARK};
    font-size: 13px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: #C0C0C0;
    border-radius: 5px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: #A0A0A0;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: #C0C0C0;
    border-radius: 5px;
    min-width: 20px;
}}

QDialog {{
    background-color: {COLOR_BG};
}}

QStatusBar {{
    background-color: {COLOR_WHITE};
    border-top: 1px solid {COLOR_BORDER};
}}
"""
