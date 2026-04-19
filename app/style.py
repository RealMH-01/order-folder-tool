# -*- coding: utf-8 -*-
"""全局样式表（QSS）。

采用 Fluent / Material 融合简化版设计语言：
- 柔和浅灰底 + 白色卡片 + 主蓝色按钮
- 统一圆角 6px（对话框 10px）
- 标准化按钮 / 输入框 / 表格 / 树 / 滚动条样式

对外导出常量：
    - 颜色 token：COLOR_BG / COLOR_PRIMARY / ...
    - ``APP_QSS``：可直接 ``app.setStyleSheet(APP_QSS)``
"""

# --------------------------------------------------------------------
# 颜色 Token（便于后续换主题）
# --------------------------------------------------------------------
COLOR_BG = "#F7F8FA"            # 主背景
COLOR_SURFACE = "#FFFFFF"       # 卡片 / 对话框背景
COLOR_BORDER = "#E5E7EB"        # 浅边框
COLOR_BORDER_HOVER = "#CBD5E1"  # hover 边框
COLOR_TEXT = "#111827"          # 主文字
COLOR_TEXT_SUB = "#6B7280"      # 次级文字
COLOR_PRIMARY = "#2563EB"       # 主色（按钮、选中）
COLOR_PRIMARY_HOVER = "#1D4ED8"
COLOR_PRIMARY_PRESSED = "#1E40AF"
COLOR_PRIMARY_LIGHT = "#EFF6FF"  # 选中行背景
COLOR_ACCENT = "#F59E0B"        # 橙色强调（自定义节点）
COLOR_DANGER = "#DC2626"        # 红色（删除、错误）
COLOR_DANGER_BG = "#FEF2F2"     # 红色 hover 背景
COLOR_SUCCESS = "#16A34A"       # 绿色（成功）

# --- 向后兼容：保留老代码里使用的名字 ------------------------------
COLOR_PRIMARY_DARK = COLOR_PRIMARY_HOVER
COLOR_WHITE = COLOR_SURFACE
COLOR_MUTED = COLOR_TEXT_SUB
COLOR_BLUE = COLOR_PRIMARY
COLOR_GREEN = COLOR_SUCCESS
COLOR_GRAY = COLOR_TEXT_SUB

# --------------------------------------------------------------------
# 字体（同时覆盖中英文）
# --------------------------------------------------------------------
FONT_FAMILY = ('"Microsoft YaHei UI", "Microsoft YaHei", "微软雅黑", '
               '"PingFang SC", "Segoe UI", sans-serif')
FONT_BODY_SIZE = "13px"
FONT_TITLE_SIZE = "15px"
FONT_BUTTON_SIZE = "13px"
FONT_HINT_SIZE = "12px"


APP_QSS = f"""
/* ==================== 全局 ==================== */
* {{
    font-family: {FONT_FAMILY};
    font-size: {FONT_BODY_SIZE};
    color: {COLOR_TEXT};
}}

QMainWindow, QWidget {{
    background-color: {COLOR_BG};
}}

QDialog {{
    background-color: {COLOR_BG};
    border-radius: 10px;
}}

/* ==================== Labels ==================== */
QLabel {{
    background: transparent;
    color: {COLOR_TEXT};
}}

QLabel#TitleLabel {{
    font-size: 20px;
    font-weight: bold;
    color: {COLOR_TEXT};
    padding: 8px 0;
}}

QLabel#SubTitleLabel {{
    font-size: 14px;
    color: {COLOR_TEXT_SUB};
    padding: 2px 0;
}}

QLabel#SectionLabel {{
    font-size: {FONT_TITLE_SIZE};
    font-weight: bold;
    color: {COLOR_TEXT};
    padding: 2px 0;
}}

QLabel#HintLabel {{
    font-size: {FONT_HINT_SIZE};
    color: {COLOR_TEXT_SUB};
}}

/* ==================== 按钮 ==================== */
QPushButton {{
    background-color: {COLOR_PRIMARY};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 18px;
    min-height: 24px;
    font-size: {FONT_BUTTON_SIZE};
}}
QPushButton:hover {{
    background-color: {COLOR_PRIMARY_HOVER};
}}
QPushButton:pressed {{
    background-color: {COLOR_PRIMARY_PRESSED};
}}
QPushButton:disabled {{
    background-color: #D1D5DB;
    color: #F3F4F6;
}}

/* 次要按钮：白底 + 边框 */
QPushButton#SecondaryButton {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
}}
QPushButton#SecondaryButton:hover {{
    background-color: #F3F4F6;
    border: 1px solid {COLOR_BORDER_HOVER};
}}
QPushButton#SecondaryButton:pressed {{
    background-color: #E5E7EB;
}}
QPushButton#SecondaryButton:disabled {{
    background-color: {COLOR_SURFACE};
    color: #9CA3AF;
    border: 1px solid {COLOR_BORDER};
}}

/* 危险操作按钮：文字红，悬停淡红底 */
QPushButton#DangerButton {{
    background-color: {COLOR_SURFACE};
    color: {COLOR_DANGER};
    border: 1px solid {COLOR_BORDER};
}}
QPushButton#DangerButton:hover {{
    background-color: {COLOR_DANGER_BG};
    border: 1px solid {COLOR_DANGER};
}}
QPushButton#DangerButton:pressed {{
    background-color: #FEE2E2;
}}

/* 大按钮（首页用） */
QPushButton#BigButton {{
    font-size: 18px;
    font-weight: bold;
    padding: 30px 50px;
    border-radius: 10px;
    min-width: 200px;
    min-height: 100px;
}}

/* 链接按钮 */
QPushButton#LinkButton {{
    background-color: transparent;
    color: {COLOR_PRIMARY};
    border: none;
    padding: 4px 8px;
    text-decoration: underline;
}}
QPushButton#LinkButton:hover {{
    color: {COLOR_PRIMARY_HOVER};
}}

/* ==================== 输入框 ==================== */
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 22px;
    selection-background-color: {COLOR_PRIMARY_LIGHT};
    selection-color: {COLOR_PRIMARY};
}}
QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover,
QComboBox:hover, QSpinBox:hover {{
    border: 1px solid {COLOR_BORDER_HOVER};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
QComboBox:focus, QSpinBox:focus {{
    border: 2px solid {COLOR_PRIMARY};
    padding: 5px 9px;
}}
QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled {{
    background-color: #F3F4F6;
    color: #9CA3AF;
}}

QComboBox::drop-down {{
    border: none;
    width: 22px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    selection-background-color: {COLOR_PRIMARY_LIGHT};
    selection-color: {COLOR_PRIMARY};
    padding: 4px;
    outline: 0;
}}

/* ==================== CheckBox / RadioButton ==================== */
QCheckBox, QRadioButton {{
    spacing: 6px;
    background: transparent;
}}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px;
    height: 16px;
}}

/* ==================== 表格 ==================== */
QTableWidget, QTableView {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    gridline-color: {COLOR_BORDER};
    selection-background-color: {COLOR_PRIMARY_LIGHT};
    selection-color: {COLOR_PRIMARY};
    alternate-background-color: #FAFBFC;
}}
QTableWidget::item, QTableView::item {{
    padding: 6px 4px;
}}
QTableWidget::item:selected, QTableView::item:selected {{
    background-color: {COLOR_PRIMARY_LIGHT};
    color: {COLOR_PRIMARY};
}}

QHeaderView::section {{
    background-color: #F9FAFB;
    color: {COLOR_TEXT_SUB};
    padding: 8px 6px;
    border: none;
    border-right: 1px solid {COLOR_BORDER};
    border-bottom: 1px solid {COLOR_BORDER};
    font-weight: bold;
}}
QHeaderView::section:last {{
    border-right: none;
}}

/* ==================== 树 ==================== */
QTreeWidget, QTreeView {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 4px;
    selection-background-color: {COLOR_PRIMARY_LIGHT};
    selection-color: {COLOR_TEXT};
    outline: 0;
}}
QTreeWidget::item, QTreeView::item {{
    padding: 4px 2px;
    border-radius: 4px;
}}
QTreeWidget::item:hover, QTreeView::item:hover {{
    background-color: #F3F4F6;
}}
QTreeWidget::item:selected, QTreeView::item:selected {{
    background-color: {COLOR_PRIMARY_LIGHT};
    color: {COLOR_TEXT};
}}

/* ==================== 列表 ==================== */
QListWidget, QListView {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 4px;
    selection-background-color: {COLOR_PRIMARY_LIGHT};
    selection-color: {COLOR_PRIMARY};
    outline: 0;
}}
QListWidget::item, QListView::item {{
    padding: 6px 10px;
    border-radius: 4px;
}}
QListWidget::item:hover, QListView::item:hover {{
    background-color: #F3F4F6;
}}

/* ==================== GroupBox ==================== */
QGroupBox {{
    background-color: {COLOR_SURFACE};
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
    color: {COLOR_TEXT};
    font-size: 13px;
}}

/* ==================== TabWidget ==================== */
QTabWidget::pane {{
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    background-color: {COLOR_SURFACE};
    top: -1px;
}}
QTabBar::tab {{
    background: #F3F4F6;
    color: {COLOR_TEXT_SUB};
    padding: 8px 18px;
    border: 1px solid transparent;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {COLOR_SURFACE};
    color: {COLOR_PRIMARY};
    border: 1px solid {COLOR_BORDER};
    border-bottom: 2px solid {COLOR_PRIMARY};
}}
QTabBar::tab:hover:!selected {{
    background: #E5E7EB;
}}

/* ==================== Menu ==================== */
QMenu {{
    background-color: {COLOR_SURFACE};
    border: 1px solid {COLOR_BORDER};
    border-radius: 6px;
    padding: 6px;
}}
QMenu::item {{
    padding: 6px 18px;
    border-radius: 4px;
}}
QMenu::item:selected {{
    background-color: #F3F4F6;
    color: {COLOR_TEXT};
}}
QMenu::separator {{
    height: 1px;
    background: {COLOR_BORDER};
    margin: 4px 8px;
}}

QMenuBar {{
    background-color: {COLOR_SURFACE};
    border-bottom: 1px solid {COLOR_BORDER};
}}
QMenuBar::item {{
    padding: 6px 12px;
    background: transparent;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background-color: #F3F4F6;
}}

/* ==================== ToolTip ==================== */
QToolTip {{
    background-color: #111827;
    color: #FFFFFF;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: {FONT_HINT_SIZE};
}}

/* ==================== ScrollBar ==================== */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: #D1D5DB;
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: #9CA3AF;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
    background: transparent;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: #D1D5DB;
    border-radius: 4px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background: #9CA3AF;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
    background: transparent;
}}

/* ==================== StatusBar ==================== */
QStatusBar {{
    background-color: {COLOR_SURFACE};
    border-top: 1px solid {COLOR_BORDER};
    color: {COLOR_TEXT_SUB};
}}

/* ==================== Dialog Button Box ==================== */
QDialogButtonBox QPushButton {{
    min-width: 72px;
}}
"""
