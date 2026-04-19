# -*- coding: utf-8 -*-
"""文件名编辑器对话框。

用于在 TemplateEditorDialog 的 ref_files 表格中，为某一行文件名提供
一个更好用的拼装/编辑体验。提供三种改名方式：

1. 模板格式：从"常用格式"下拉框选一个，再填前缀，一键生成；
2. 占位符快捷插入：点按钮把 ``<订单号>`` 等占位符插到当前光标位置，
   自动识别扩展名并避免插到扩展名之后；
3. 自由编辑：大号 QLineEdit，支持键盘直接编辑。

此外提供实时合法性校验：文件名不允许包含 ``\\ / : * ? " < > |`` 等字符，
``<...>`` 占位符本身视为合法。
"""

import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget
)


# Windows / 通用文件名中不允许的字符（占位符 <...> 本身会被单独放行）
_ILLEGAL_CHARS = r'\/:*?"<>|'
_ILLEGAL_CHARS_DISPLAY = r'\ / : * ? " < > |'

# 扩展名判定：最后一个点之后，只由 1~6 位字母/数字组成则视作扩展名
_EXT_RE = re.compile(r"\.[A-Za-z0-9]{1,6}$")


def _find_ext_dot_index(name: str) -> int:
    """返回 ``name`` 中扩展名点号的索引；没有扩展名时返回 -1。

    扩展名规则：最后一个 ``.`` 之后是 1~6 位字母/数字。以 ``.`` 开头的
    隐藏文件（如 ``.gitignore``）不算扩展名。
    """
    if not name:
        return -1
    m = _EXT_RE.search(name)
    if not m:
        return -1
    dot_idx = m.start()
    # 忽略像 ".gitignore" 这种点号在最前面的情况
    if dot_idx == 0:
        return -1
    return dot_idx


def _strip_placeholders(text: str) -> str:
    """去除所有形如 ``<xxx>`` 的占位符，便于合法性校验。"""
    return re.sub(r"<[^<>]*>", "", text)


def is_filename_legal(name: str) -> bool:
    """校验文件名是否合法：非空且不含非法字符。占位符 ``<...>`` 视作合法。"""
    if not name or not name.strip():
        return False
    stripped = _strip_placeholders(name)
    for ch in stripped:
        if ch in _ILLEGAL_CHARS:
            return False
    return True


class FilenameEditorDialog(QDialog):
    """文件名编辑器对话框。

    使用方式::

        dlg = FilenameEditorDialog("注意事项.pdf", parent=self)
        if dlg.exec_() == QDialog.Accepted:
            new_name = dlg.result_filename()
    """

    #: 常用格式（与 TemplateEditorDialog 保持一致）
    FORMATS = [
        "前缀-<订单号>.xlsx",
        "前缀-<订单号>.xls",
        "前缀-<订单号>.pdf",
        "前缀-<订单号>.doc",
        "前缀-<订单号>-<客户名称>.xlsx",
        "前缀-<订单号>-<客户名称>.pdf",
    ]

    #: 所有占位符按钮（文本, 是否高亮主色）
    PLACEHOLDERS = [
        ("<订单号>", True),
        ("<客户名称>", False),
        ("<客户PO号>", False),
        ("<日期>", False),
        ("<业务员>", False),
        ("<SHXY>", False),
    ]

    def __init__(self, initial_name: str = "", parent=None,
                 row_info: str = ""):
        """构造对话框。

        :param initial_name: 传入的初始文件名（表格中该行的当前值）。
        :param parent: 父窗口。
        :param row_info: 顶部说明里显示的"当前行"信息，可选。
        """
        super().__init__(parent)
        self.setWindowTitle("✎ 文件名编辑器")
        self.setModal(True)
        self.resize(640, 360)

        self._initial_name = initial_name or ""
        self._row_info = row_info or ""

        self._build_ui()
        self._connect_signals()
        # 初始化预览框 & 合法性状态
        self.edit_preview.setText(self._initial_name)
        self._validate()

    # ------------------------------------------------------------------
    # UI 构建
    # ------------------------------------------------------------------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 顶部说明
        header_text = "修改该行文件名。可任选一种方式编辑，最终结果以下方"\
            "「文件名预览」为准。"
        if self._row_info:
            header_text = f"当前行：{self._row_info}\n" + header_text
        header = QLabel(header_text)
        header.setWordWrap(True)
        header.setObjectName("HintLabel")
        layout.addWidget(header)

        # ---- 方式一：模板格式 ----
        fmt_title = QLabel("方式一：套用常用格式")
        fmt_title.setObjectName("SectionLabel")
        layout.addWidget(fmt_title)

        fmt_row = QHBoxLayout()
        fmt_row.setSpacing(8)
        self.cmb_format = QComboBox()
        self.cmb_format.addItems(self.FORMATS)
        self.cmb_format.setMinimumWidth(240)
        fmt_row.addWidget(self.cmb_format, 2)

        self.edit_prefix = QLineEdit()
        self.edit_prefix.setPlaceholderText("例如 CI、PL、CG、BL")
        self.edit_prefix.setMaximumWidth(160)
        fmt_row.addWidget(self.edit_prefix, 1)

        self.btn_apply_fmt = QPushButton("应用此格式")
        self.btn_apply_fmt.setObjectName("SecondaryButton")
        self.btn_apply_fmt.setFocusPolicy(Qt.NoFocus)
        fmt_row.addWidget(self.btn_apply_fmt, 0)
        fmt_row.addStretch(1)
        layout.addLayout(fmt_row)

        # ---- 方式二：占位符快捷插入 ----
        ph_title = QLabel("方式二：点按钮插入占位符（会自动避开扩展名）")
        ph_title.setObjectName("SectionLabel")
        layout.addWidget(ph_title)

        ph_row = QHBoxLayout()
        ph_row.setSpacing(6)
        self._placeholder_buttons = []
        for text, highlight in self.PLACEHOLDERS:
            btn = QPushButton(text)
            # 关键：点击按钮不抢焦点，连续插入多个占位符
            btn.setFocusPolicy(Qt.NoFocus)
            if not highlight:
                btn.setObjectName("SecondaryButton")
            # 点击用 lambda 绑定文本
            btn.clicked.connect(
                lambda _=False, t=text: self._insert_placeholder_at_cursor(t)
            )
            ph_row.addWidget(btn)
            self._placeholder_buttons.append(btn)
        ph_row.addStretch(1)
        layout.addLayout(ph_row)

        # ---- 方式三：自由编辑 / 文件名预览 ----
        preview_title = QLabel("方式三：直接编辑（最终结果）")
        preview_title.setObjectName("SectionLabel")
        layout.addWidget(preview_title)

        self.edit_preview = QLineEdit()
        # 字号略大，便于阅读
        preview_font = QFont()
        preview_font.setPointSize(14)
        self.edit_preview.setFont(preview_font)
        self.edit_preview.setMinimumHeight(36)
        layout.addWidget(self.edit_preview)

        # 合法性提示
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("HintLabel")
        layout.addWidget(self.lbl_status)

        layout.addStretch(1)

        # ---- 底部按钮 ----
        btn_row = QHBoxLayout()
        self.btn_reset = QPushButton("↺ 重置")
        self.btn_reset.setObjectName("SecondaryButton")
        btn_row.addWidget(self.btn_reset)
        btn_row.addStretch(1)

        self.btns = QDialogButtonBox()
        self.btn_ok = self.btns.addButton("✔ 确认", QDialogButtonBox.AcceptRole)
        self.btn_cancel = self.btns.addButton("取消", QDialogButtonBox.RejectRole)
        # 次要样式给取消按钮
        self.btn_cancel.setObjectName("SecondaryButton")
        btn_row.addWidget(self.btns)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    # 信号连接
    # ------------------------------------------------------------------
    def _connect_signals(self):
        self.edit_preview.textChanged.connect(self._validate)
        self.btn_apply_fmt.clicked.connect(self._apply_format)
        self.btn_reset.clicked.connect(self._on_reset)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)
        # 回车：若合法则 accept
        self.edit_preview.returnPressed.connect(self._on_enter)

    # ------------------------------------------------------------------
    # 业务逻辑
    # ------------------------------------------------------------------
    def _insert_placeholder_at_cursor(self, placeholder: str):
        """把占位符插入预览框当前光标位置；若光标在扩展名之内/之后，
        则自动挪到扩展名点号之前。"""
        text = self.edit_preview.text()
        pos = self.edit_preview.cursorPosition()

        dot_idx = _find_ext_dot_index(text)
        # 如果存在扩展名，且光标在点号或其之后：挪到点号前
        if dot_idx >= 0 and pos > dot_idx:
            pos = dot_idx

        new_text = text[:pos] + placeholder + text[pos:]
        # 设置后把光标定位到占位符之后，便于连续插入
        self.edit_preview.setText(new_text)
        self.edit_preview.setCursorPosition(pos + len(placeholder))
        # 手动给预览框保留焦点，以免下一次误点表格
        self.edit_preview.setFocus(Qt.OtherFocusReason)

    def _apply_format(self):
        """用前缀替换掉下拉格式中的"前缀"二字，写入预览框。"""
        fmt = self.cmb_format.currentText()
        prefix = self.edit_prefix.text().strip()
        if not prefix:
            # 前缀为空时也允许应用，但会保留字样"前缀"，用户可手动改
            new_name = fmt
        else:
            new_name = fmt.replace("前缀", prefix)
        self.edit_preview.setText(new_name)
        # 把光标放到扩展名点号之前，用户可立即继续插入占位符
        dot_idx = _find_ext_dot_index(new_name)
        if dot_idx >= 0:
            self.edit_preview.setCursorPosition(dot_idx)
        else:
            self.edit_preview.setCursorPosition(len(new_name))
        self.edit_preview.setFocus(Qt.OtherFocusReason)

    def _on_reset(self):
        """将预览框恢复为初始文件名。"""
        self.edit_preview.setText(self._initial_name)
        self.edit_preview.setCursorPosition(len(self._initial_name))
        self.edit_preview.setFocus(Qt.OtherFocusReason)

    def _on_enter(self):
        if self.btn_ok.isEnabled():
            self.accept()

    def _validate(self):
        """实时校验：更新状态标签 + 启用/禁用"确认"按钮。"""
        text = self.edit_preview.text()
        if not text or not text.strip():
            self.lbl_status.setText("✗ 文件名不能为空")
            self.lbl_status.setStyleSheet("color:#DC2626;")
            self.btn_ok.setEnabled(False)
            return
        legal = is_filename_legal(text)
        if legal:
            self.lbl_status.setText("✓ 文件名合法")
            self.lbl_status.setStyleSheet("color:#6B7280;")
            self.btn_ok.setEnabled(True)
        else:
            self.lbl_status.setText(
                f"✗ 文件名包含不允许的字符： {_ILLEGAL_CHARS_DISPLAY}"
            )
            self.lbl_status.setStyleSheet("color:#DC2626;")
            self.btn_ok.setEnabled(False)

    # ------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------
    def result_filename(self) -> str:
        """返回用户确认的文件名（已 strip）。"""
        return self.edit_preview.text().strip()

    # 便于测试：显式的占位符插入接口
    def insert_placeholder(self, placeholder: str):
        """测试/外部调用入口：按当前光标位置插入占位符。"""
        self._insert_placeholder_at_cursor(placeholder)

    def apply_format(self, prefix: str, fmt: str = None):
        """测试/外部调用入口：应用指定前缀到当前（或给定）格式。"""
        if fmt is not None:
            idx = self.cmb_format.findText(fmt)
            if idx >= 0:
                self.cmb_format.setCurrentIndex(idx)
            else:
                # 不在默认列表里也允许直接使用
                self.cmb_format.addItem(fmt)
                self.cmb_format.setCurrentIndex(self.cmb_format.count() - 1)
        self.edit_prefix.setText(prefix)
        self._apply_format()
