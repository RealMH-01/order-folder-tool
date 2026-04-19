# -*- coding: utf-8 -*-
"""FilenameEditorDialog 的单元测试（使用 pytest-qt）。

覆盖：
- 初始化（预览框、合法性提示）
- 占位符智能插入（扩展名之前、光标位置、多次连续插入）
- 模板格式套用
- 合法性校验（非法字符 / 空值 → 禁用确认按钮）
- 重置按钮
- 占位符按钮焦点策略（不抢焦点）
- 无扩展名 / 点号开头文件的处理
"""

import os
import sys

# 让测试可以 import app.*
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialogButtonBox

from app.dialogs.filename_editor import (
    FilenameEditorDialog,
    _find_ext_dot_index,
    is_filename_legal,
)


# ---------------------------------------------------------------
# Pure-function 测试（无需 qtbot）
# ---------------------------------------------------------------

def test_find_ext_dot_index_basic():
    assert _find_ext_dot_index("abc.pdf") == 3
    assert _find_ext_dot_index("abc.xlsx") == 3
    assert _find_ext_dot_index("abc.jpeg") == 3


def test_find_ext_dot_index_no_ext():
    assert _find_ext_dot_index("README") == -1
    assert _find_ext_dot_index("") == -1


def test_find_ext_dot_index_hidden_file():
    # .gitignore 不应被当作扩展名
    assert _find_ext_dot_index(".gitignore") == -1


def test_find_ext_dot_index_multi_dot():
    # 多个点：应取最后一个
    assert _find_ext_dot_index("foo.bar.pdf") == 7


def test_is_filename_legal():
    assert is_filename_legal("abc.pdf")
    assert is_filename_legal("注意事项-<订单号>-<客户PO号>.pdf")
    assert not is_filename_legal("a/b.pdf")
    assert not is_filename_legal('ab?.pdf')
    assert not is_filename_legal("")
    assert not is_filename_legal("   ")


# ---------------------------------------------------------------
# pytest-qt fixture
# ---------------------------------------------------------------

@pytest.fixture
def dlg(qtbot):
    """创建一个默认初始值的对话框。"""
    d = FilenameEditorDialog("注意事项.pdf")
    qtbot.addWidget(d)
    return d


# ---------------------------------------------------------------
# Dialog 测试
# ---------------------------------------------------------------

def test_init_with_name(qtbot):
    """a) 传入初值后预览框显示正确。"""
    d = FilenameEditorDialog("注意事项.pdf")
    qtbot.addWidget(d)
    assert d.edit_preview.text() == "注意事项.pdf"
    assert d.result_filename() == "注意事项.pdf"
    # 确认按钮应启用（合法初值）
    assert d.btn_ok.isEnabled()


def test_insert_placeholder_before_extension(dlg):
    """b) 初值 '注意事项.pdf'，插入 <订单号>，应得到 '注意事项<订单号>.pdf'。"""
    # 将光标放到末尾（模拟用户刚打开对话框）
    dlg.edit_preview.setCursorPosition(len(dlg.edit_preview.text()))
    dlg.insert_placeholder("<订单号>")
    assert dlg.edit_preview.text() == "注意事项<订单号>.pdf"


def test_insert_at_cursor(qtbot):
    """c) 初值 'ABC.pdf'，光标在位置 1，插入 <订单号>，应得到 'A<订单号>BC.pdf'。"""
    d = FilenameEditorDialog("ABC.pdf")
    qtbot.addWidget(d)
    d.edit_preview.setCursorPosition(1)
    d.insert_placeholder("<订单号>")
    assert d.edit_preview.text() == "A<订单号>BC.pdf"


def test_multi_placeholder(dlg):
    """d) 连续插入多个占位符，都应在扩展名之前且顺序正确。"""
    dlg.edit_preview.setCursorPosition(len(dlg.edit_preview.text()))
    dlg.insert_placeholder("<订单号>")
    dlg.insert_placeholder("<客户PO号>")
    assert dlg.edit_preview.text() == "注意事项<订单号><客户PO号>.pdf"


def test_apply_format(qtbot):
    """e) 套用 '前缀-<订单号>-<客户名称>.xlsx'，前缀 'CI'。"""
    d = FilenameEditorDialog("原始.xlsx")
    qtbot.addWidget(d)
    d.apply_format("CI", "前缀-<订单号>-<客户名称>.xlsx")
    assert d.edit_preview.text() == "CI-<订单号>-<客户名称>.xlsx"


def test_illegal_chars_disable_ok(dlg):
    """f) 输入含 '/' → 确认按钮禁用 + 状态提示为非法。"""
    dlg.edit_preview.setText("a/b.pdf")
    assert not dlg.btn_ok.isEnabled()
    assert "不允许" in dlg.lbl_status.text()


def test_empty_disable_ok(dlg):
    """g) 清空内容 → 确认按钮禁用。"""
    dlg.edit_preview.setText("")
    assert not dlg.btn_ok.isEnabled()


def test_reset_button(qtbot, dlg):
    """h) 任意编辑后点重置 → 预览框恢复初值。"""
    dlg.edit_preview.setText("完全不同的内容.pdf")
    qtbot.mouseClick(dlg.btn_reset, Qt.LeftButton)
    assert dlg.edit_preview.text() == "注意事项.pdf"
    assert dlg.btn_ok.isEnabled()


def test_placeholder_buttons_no_focus(dlg):
    """i) 占位符按钮的 focusPolicy 必须为 Qt.NoFocus。"""
    assert len(dlg._placeholder_buttons) >= 5
    for btn in dlg._placeholder_buttons:
        assert btn.focusPolicy() == Qt.NoFocus


def test_no_extension_append_to_end(qtbot):
    """j) 初值 'README'（无扩展名），插入 <订单号> → 'README<订单号>'。"""
    d = FilenameEditorDialog("README")
    qtbot.addWidget(d)
    d.edit_preview.setCursorPosition(len(d.edit_preview.text()))
    d.insert_placeholder("<订单号>")
    assert d.edit_preview.text() == "README<订单号>"


def test_short_name_with_dot(qtbot):
    """k) '.gitignore'（点号开头的隐藏文件）插入 <订单号> 应该附加到末尾。"""
    d = FilenameEditorDialog(".gitignore")
    qtbot.addWidget(d)
    d.edit_preview.setCursorPosition(len(d.edit_preview.text()))
    d.insert_placeholder("<订单号>")
    assert d.edit_preview.text() == ".gitignore<订单号>"


def test_click_placeholder_button_inserts(qtbot, dlg):
    """l) 实际点击第一个占位符按钮，应触发插入。"""
    dlg.edit_preview.setCursorPosition(len(dlg.edit_preview.text()))
    first_btn = dlg._placeholder_buttons[0]  # <订单号>
    qtbot.mouseClick(first_btn, Qt.LeftButton)
    assert dlg.edit_preview.text() == "注意事项<订单号>.pdf"


def test_click_another_placeholder_then_another(qtbot, dlg):
    """m) 连续点击两个不同按钮，模拟"单击即插"而不中断编辑。"""
    dlg.edit_preview.setCursorPosition(len(dlg.edit_preview.text()))
    # <订单号>
    qtbot.mouseClick(dlg._placeholder_buttons[0], Qt.LeftButton)
    # <客户PO号>（位置 2）
    qtbot.mouseClick(dlg._placeholder_buttons[2], Qt.LeftButton)
    assert dlg.edit_preview.text() == "注意事项<订单号><客户PO号>.pdf"


def test_legal_state_for_placeholders_only(qtbot):
    """n) 纯占位符（被视作合法字符）应通过校验。"""
    d = FilenameEditorDialog("")
    qtbot.addWidget(d)
    d.edit_preview.setText("<订单号>-<客户PO号>.pdf")
    assert d.btn_ok.isEnabled()
    assert "合法" in d.lbl_status.text()


def test_cursor_after_apply_format_before_ext(qtbot):
    """o) 应用格式后，光标应自动停在扩展名点号之前，便于继续插入占位符。"""
    d = FilenameEditorDialog("原始.xlsx")
    qtbot.addWidget(d)
    d.apply_format("CI", "前缀-<订单号>.xlsx")
    # 应用后文本： "CI-<订单号>.xlsx"，点号在 "CI-<订单号>".length
    expected = "CI-<订单号>.xlsx"
    assert d.edit_preview.text() == expected
    dot_idx = expected.rfind(".")
    assert d.edit_preview.cursorPosition() == dot_idx


def test_result_filename_strips(qtbot):
    """p) result_filename() 去掉首尾空白。"""
    d = FilenameEditorDialog("  abc.pdf  ")
    qtbot.addWidget(d)
    # text 原样保留，但 result_filename 应 strip
    assert d.result_filename() == "abc.pdf"
