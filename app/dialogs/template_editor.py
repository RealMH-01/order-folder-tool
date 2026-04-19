# -*- coding: utf-8 -*-
"""模板编辑对话框（可勾选的树 + 右键菜单 + ref_files 编辑）"""

import copy
import os
import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QAbstractItemView, QAction, QComboBox, QDialog, QDialogButtonBox,
    QFileDialog, QGridLayout, QHBoxLayout, QHeaderView, QInputDialog, QLabel,
    QLineEdit, QMenu, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
)

from app.dialogs.filename_editor import FilenameEditorDialog

# 扩展名判定：最后一个 `.` 之后是 1~6 位字母/数字（与 filename_editor 保持一致）
_EXT_RE = re.compile(r"\.[A-Za-z0-9]{1,6}$")


def _ext_dot_index(name: str) -> int:
    """返回 ``name`` 中扩展名点号的索引；没有扩展名时返回 -1。"""
    if not name:
        return -1
    m = _EXT_RE.search(name)
    if not m:
        return -1
    dot_idx = m.start()
    if dot_idx == 0:
        return -1
    return dot_idx


ROLE_IS_STANDARD = Qt.UserRole + 1  # 是否来自标准模板（不可删除）
ROLE_REF_FILES = Qt.UserRole + 2    # 该节点的 ref_files（list）
ROLE_OPTIONAL = Qt.UserRole + 3
ROLE_CONDITION = Qt.UserRole + 4


class TemplateEditorDialog(QDialog):
    """
    template：dict（会被拷贝后编辑）
    base_template：标准模板，用于标注哪些节点是"标准节点"（不可删除）
    """

    def __init__(self, template, base_template=None, title="编辑模板",
                 parent=None, template_files_dir: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1020, 680)
        self._template = copy.deepcopy(template)
        self._base_template = base_template or template
        self._standard_paths = self._collect_paths(self._base_template)
        self._template_files_dir = template_files_dir or ""
        self._build_ui()
        self._populate()

    # ============== 工具 ==============
    @staticmethod
    def _collect_paths(tpl, parent_path=""):
        """收集标准模板里所有文件夹的相对路径集合"""
        s = set()
        name = tpl.get("name", "")
        cur = name if not parent_path else parent_path + "/" + name
        s.add(cur)
        for ch in tpl.get("children", []) or []:
            s.update(TemplateEditorDialog._collect_paths(ch, cur))
        return s

    # ============== UI ==============
    def _build_ui(self):
        layout = QVBoxLayout(self)

        tip = QLabel("✓ 勾选要创建的文件夹。右键可添加/删除自定义节点。选中节点后可在右侧编辑该文件夹下的参考文件。")
        tip.setStyleSheet("color:#555;")
        layout.addWidget(tip)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("模板名称："))
        self.edit_display_name = QLineEdit()
        self.edit_display_name.setText(self._template.get("display_name", ""))
        self.edit_display_name.setPlaceholderText("输入模板的显示名称")
        name_row.addWidget(self.edit_display_name)
        layout.addLayout(name_row)

        body = QHBoxLayout()
        # 左：树
        left = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["文件夹"])
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._tree_menu)
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.itemSelectionChanged.connect(self._on_selection)
        left.addWidget(self.tree, 1)
        body.addLayout(left, 1)

        # 右：ref_files 编辑
        right = QVBoxLayout()
        right.addWidget(QLabel("该文件夹下的参考文件（ref_files）"))

        # 功能 A：提示文字
        hint_label = QLabel(
            "💡 如需一次性修改多个占位符，建议点击下方「✎ 改名...」按钮获得更好体验；"
            "也可以使用下方快捷按钮或「常用格式」下拉框。"
        )
        hint_label.setObjectName("HintLabel")
        hint_label.setWordWrap(True)
        right.addWidget(hint_label)

        # 功能 B：占位符快捷按钮 + 常用格式下拉框
        quick_row = QHBoxLayout()
        quick_row.setSpacing(4)
        # 占位符按钮
        placeholder_defs = [
            ("<订单号>", True),   # 醒目高亮
            ("<客户名称>", False),
            ("<客户PO号>", False),
            ("<日期>", False),
            ("<业务员>", False),
        ]
        for text, highlight in placeholder_defs:
            btn = QPushButton(text)
            # 非高亮按钮使用次要样式；高亮按钮使用默认主按钮样式
            if not highlight:
                btn.setObjectName("SecondaryButton")
            # 关键修复：点击按钮不再抢走单元格焦点，支持连续插入
            btn.setFocusPolicy(Qt.NoFocus)
            btn.clicked.connect(
                lambda _=False, t=text: self._insert_placeholder(t))
            quick_row.addWidget(btn)

        quick_row.addSpacing(12)
        quick_row.addWidget(QLabel("常用格式："))
        self.cmb_format = QComboBox()
        self.cmb_format.addItems([
            "前缀-<订单号>.xlsx",
            "前缀-<订单号>.xls",
            "前缀-<订单号>.pdf",
            "前缀-<订单号>.doc",
            "前缀-<订单号>-<客户名称>.xlsx",
            "前缀-<订单号>-<客户名称>.pdf",
        ])
        self.cmb_format.setMinimumWidth(220)
        quick_row.addWidget(self.cmb_format)
        btn_apply_fmt = QPushButton("应用格式")
        btn_apply_fmt.setObjectName("SecondaryButton")
        btn_apply_fmt.clicked.connect(self._apply_format)
        quick_row.addWidget(btn_apply_fmt)
        quick_row.addStretch(1)
        right.addLayout(quick_row)

        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels(["文件名 (filename)", "来源 (source)",
                                             "模板文件 (file_template)"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # 整行选中，便于"改名"按钮识别目标行
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        # 保留默认编辑触发（双击/F2/敲字母）——"文件名"列的 item
        # 我们会在填充时去掉 ItemIsEditable 标记，改用 FilenameEditorDialog
        self.tbl.cellDoubleClicked.connect(self._on_cell_double_clicked)
        right.addWidget(self.tbl, 1)

        row_ops = QHBoxLayout()
        b_add = QPushButton("+ 新增")
        b_add.setObjectName("SecondaryButton")
        b_add.clicked.connect(self._add_ref)
        b_del = QPushButton("- 删除选中")
        b_del.setObjectName("DangerButton")
        b_del.clicked.connect(self._del_ref)
        # ✎ 改名...：弹出 FilenameEditorDialog
        b_rename = QPushButton("✎ 改名...")
        b_rename.setObjectName("SecondaryButton")
        b_rename.setToolTip("打开文件名编辑器，可套用常用格式、插入占位符或自由编辑")
        b_rename.clicked.connect(self._open_filename_editor)
        # 功能 E：浏览选择模板文件
        b_browse_tpl = QPushButton("📂 选择模板文件")
        b_browse_tpl.setObjectName("SecondaryButton")
        b_browse_tpl.clicked.connect(self._browse_template_file)
        b_apply = QPushButton("✔ 应用修改到当前文件夹")
        b_apply.clicked.connect(self._apply_refs_to_node)
        row_ops.addWidget(b_add)
        row_ops.addWidget(b_del)
        row_ops.addWidget(b_rename)
        row_ops.addWidget(b_browse_tpl)
        row_ops.addStretch(1)
        row_ops.addWidget(b_apply)
        right.addLayout(row_ops)

        body.addLayout(right, 1)
        layout.addLayout(body, 1)

        btns = QDialogButtonBox()
        b_ok = btns.addButton("保存", QDialogButtonBox.AcceptRole)
        b_cancel = btns.addButton("取消", QDialogButtonBox.RejectRole)
        btns.accepted.connect(self._save_and_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    # ============== 填充 ==============
    def _populate(self):
        self.tree.clear()
        root = self._add_item(None, self._template, "")
        self.tree.expandAll()
        if root:
            self.tree.setCurrentItem(root)

    def _add_item(self, parent, node, parent_path):
        name = node.get("name", "")
        path = name if not parent_path else parent_path + "/" + name
        item = QTreeWidgetItem([name])
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(0, Qt.Checked if node.get("_enabled", True) else Qt.Unchecked)
        is_std = path in self._standard_paths
        item.setData(0, ROLE_IS_STANDARD, is_std)
        item.setData(0, ROLE_REF_FILES, copy.deepcopy(node.get("ref_files", []) or []))
        item.setData(0, ROLE_OPTIONAL, bool(node.get("optional")))
        item.setData(0, ROLE_CONDITION, node.get("condition", ""))
        if is_std:
            item.setForeground(0, QBrush(QColor("#1976D2")))
        else:
            item.setForeground(0, QBrush(QColor("#EF6C00")))  # 自定义：橙色
        if node.get("optional"):
            item.setText(0, f"{name}  [可选]")
        if parent is None:
            self.tree.addTopLevelItem(item)
        else:
            parent.addChild(item)
        for child in node.get("children", []) or []:
            self._add_item(item, child, path)
        return item

    # ============== 交互 ==============
    def _on_item_changed(self, item, col):
        # 勾选状态改变时：勾选/取消勾选子节点
        if col != 0:
            return
        state = item.checkState(0)
        self.tree.blockSignals(True)
        for i in range(item.childCount()):
            item.child(i).setCheckState(0, state)
        self.tree.blockSignals(False)

    def _on_selection(self):
        items = self.tree.selectedItems()
        if not items:
            self._load_refs_table([])
            return
        refs = items[0].data(0, ROLE_REF_FILES) or []
        self._load_refs_table(refs)

    def _load_refs_table(self, refs):
        self.tbl.setRowCount(0)
        for rf in refs:
            r = self.tbl.rowCount()
            self.tbl.insertRow(r)
            fn_item = QTableWidgetItem(rf.get("filename", ""))
            # 文件名列禁用内联编辑——改用 FilenameEditorDialog
            fn_item.setFlags(fn_item.flags() & ~Qt.ItemIsEditable)
            self.tbl.setItem(r, 0, fn_item)
            self.tbl.setItem(r, 1, QTableWidgetItem(rf.get("source", "")))
            self.tbl.setItem(r, 2, QTableWidgetItem(rf.get("file_template") or ""))

    def _add_ref(self):
        r = self.tbl.rowCount()
        self.tbl.insertRow(r)
        fn_item = QTableWidgetItem("新文件-<订单号>.xlsx")
        fn_item.setFlags(fn_item.flags() & ~Qt.ItemIsEditable)
        self.tbl.setItem(r, 0, fn_item)
        self.tbl.setItem(r, 1, QTableWidgetItem("自制"))
        self.tbl.setItem(r, 2, QTableWidgetItem(""))
        self.tbl.selectRow(r)

    def _del_ref(self):
        rows = sorted({i.row() for i in self.tbl.selectedIndexes()}, reverse=True)
        for r in rows:
            self.tbl.removeRow(r)

    # 功能 B：占位符快捷插入（已修复：自动识别扩展名，插到点号之前）
    def _insert_placeholder(self, placeholder: str):
        r = self._current_ref_row()
        if r < 0:
            QMessageBox.information(self, "提示", "请先选中一行（在文件名表格中点击一行）")
            return
        item = self.tbl.item(r, 0)
        if item is None:
            item = QTableWidgetItem("")
            self.tbl.setItem(r, 0, item)
        old_text = item.text() or ""
        dot_idx = _ext_dot_index(old_text)
        if dot_idx >= 0:
            new_text = old_text[:dot_idx] + placeholder + old_text[dot_idx:]
        else:
            new_text = old_text + placeholder
        item.setText(new_text)

    def _current_ref_row(self) -> int:
        """返回 ref_files 表格中当前选中行（没有返回 -1）。"""
        sm = self.tbl.selectionModel()
        rows = sm.selectedRows() if sm else []
        if rows:
            return rows[0].row()
        return self.tbl.currentRow()

    # 功能 B：常用格式一键应用
    def _apply_format(self):
        r = self._current_ref_row()
        if r < 0:
            QMessageBox.information(self, "提示", "请先选中一行（在文件名表格中点击一行）")
            return
        fmt = self.cmb_format.currentText()
        prefix, ok = QInputDialog.getText(
            self, "请输入前缀",
            "例如 CI、PL、CG、BL：")
        if not ok:
            return
        prefix = prefix.strip()
        if not prefix:
            QMessageBox.information(self, "提示", "前缀不能为空")
            return
        new_name = fmt.replace("前缀", prefix)
        item = self.tbl.item(r, 0)
        if item is None:
            item = QTableWidgetItem(new_name)
            self.tbl.setItem(r, 0, item)
        else:
            item.setText(new_name)

    # ✎ 改名...：弹出 FilenameEditorDialog
    def _open_filename_editor(self, row: int = -1):
        """打开文件名编辑器。``row=-1`` 表示取当前选中行。"""
        if row is None or row < 0:
            row = self._current_ref_row()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选中一行")
            return
        item = self.tbl.item(row, 0)
        current_name = item.text() if item else ""
        # 读取"来源"作为行信息提示
        src_item = self.tbl.item(row, 1)
        row_info = src_item.text() if src_item else ""
        dlg = FilenameEditorDialog(
            current_name, parent=self, row_info=row_info
        )
        if dlg.exec_() == QDialog.Accepted:
            new_name = dlg.result_filename()
            if item is None:
                self.tbl.setItem(row, 0, QTableWidgetItem(new_name))
            else:
                item.setText(new_name)

    def _on_cell_double_clicked(self, row: int, col: int):
        """双击"文件名"列：弹出 FilenameEditorDialog 取代默认内联编辑。
        双击其他列保持默认内联编辑体验。"""
        if col != 0:
            return
        # 阻止默认的编辑状态
        self.tbl.closePersistentEditor(self.tbl.item(row, col))
        self._open_filename_editor(row)

    # 功能 E：浏览并选择模板文件
    def _browse_template_file(self):
        r = self._current_ref_row()
        if r < 0:
            QMessageBox.information(self, "提示", "请先选中一行（在文件名表格中点击一行）")
            return
        if not self._template_files_dir or not os.path.isdir(self._template_files_dir):
            QMessageBox.information(
                self, "提示",
                "请先在首页设置模板文件目录。\n"
                "（首页 → 「模板文件目录」 → 浏览并保存）"
            )
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "选择模板文件",
            self._template_files_dir,
            "所有文件 (*.*)"
        )
        if not path:
            return
        try:
            rel = os.path.relpath(path, self._template_files_dir)
        except ValueError:
            QMessageBox.warning(
                self, "提示",
                "所选文件不在模板文件目录内，请选择该目录下的文件。"
            )
            return
        # 防止用户跑到目录外 (../xxx)
        if rel.startswith(".."):
            QMessageBox.warning(
                self, "提示",
                "所选文件不在模板文件目录内，请选择该目录下的文件。"
            )
            return
        # 统一用正斜杠，与 default_templates 中的写法保持一致
        rel = rel.replace("\\", "/")
        it = self.tbl.item(r, 2)
        if it is None:
            it = QTableWidgetItem(rel)
            self.tbl.setItem(r, 2, it)
        else:
            it.setText(rel)

    def _apply_refs_to_node(self):
        items = self.tree.selectedItems()
        if not items:
            QMessageBox.information(self, "提示", "请先选中一个文件夹节点")
            return
        refs = []
        for r in range(self.tbl.rowCount()):
            fn_it = self.tbl.item(r, 0)
            src_it = self.tbl.item(r, 1)
            tpl_it = self.tbl.item(r, 2)
            filename = (fn_it.text() if fn_it else "").strip()
            if not filename:
                continue
            refs.append({
                "filename": filename,
                "source": (src_it.text() if src_it else "").strip(),
                "file_template": (tpl_it.text() if tpl_it else "").strip() or None,
            })
        items[0].setData(0, ROLE_REF_FILES, refs)
        QMessageBox.information(self, "已应用", "该文件夹的参考文件列表已更新。")

    def _tree_menu(self, pos):
        item = self.tree.itemAt(pos)
        menu = QMenu(self)
        act_add = QAction("➕ 添加子文件夹", self)
        act_add.triggered.connect(lambda: self._add_subfolder(item))
        menu.addAction(act_add)

        act_add_sibling = QAction("➕ 添加同级文件夹", self)
        act_add_sibling.triggered.connect(lambda: self._add_sibling(item))
        menu.addAction(act_add_sibling)

        if item is not None:
            if item.parent() is not None:
                is_std = item.data(0, ROLE_IS_STANDARD)
                if is_std:
                    act_del = QAction("🗑 删除此节点", self)

                    def _confirm_del(checked=False, i=item):
                        name = i.text(0).split("  [")[0]
                        r = QMessageBox.question(
                            self, "确认删除",
                            f"「{name}」是标准模板节点，删除后可通过重置模板恢复。确定删除吗？",
                            QMessageBox.Yes | QMessageBox.No)
                        if r == QMessageBox.Yes:
                            i.parent().removeChild(i)
                    act_del.triggered.connect(_confirm_del)
                else:
                    act_del = QAction("🗑 删除此自定义节点", self)
                    act_del.triggered.connect(lambda: self._delete_node(item))
                menu.addAction(act_del)
            act_rename = QAction("✎ 重命名", self)
            act_rename.triggered.connect(lambda: self._rename_node(item))
            menu.addAction(act_rename)
        menu.exec_(self.tree.viewport().mapToGlobal(pos))

    def _add_subfolder(self, parent_item):
        name, ok = QInputDialog.getText(self, "新文件夹", "名称：")
        if not (ok and name.strip()):
            return
        new_item = QTreeWidgetItem([name.strip()])
        new_item.setFlags(new_item.flags() | Qt.ItemIsUserCheckable)
        new_item.setCheckState(0, Qt.Checked)
        new_item.setData(0, ROLE_IS_STANDARD, False)
        new_item.setData(0, ROLE_REF_FILES, [])
        new_item.setForeground(0, QBrush(QColor("#EF6C00")))
        if parent_item is None:
            self.tree.addTopLevelItem(new_item)
        else:
            parent_item.addChild(new_item)
            parent_item.setExpanded(True)

    def _add_sibling(self, item):
        if item is None or item.parent() is None:
            # 顶层不允许添加兄弟（订单号只有一个）
            QMessageBox.information(self, "提示", "根节点不能添加兄弟")
            return
        self._add_subfolder(item.parent())

    def _delete_node(self, item):
        if item.parent() is None:
            return
        item.parent().removeChild(item)

    def _rename_node(self, item):
        old = item.text(0).split("  [")[0]
        name, ok = QInputDialog.getText(self, "重命名", "名称：", text=old)
        if ok and name.strip():
            opt = item.data(0, ROLE_OPTIONAL)
            item.setText(0, f"{name.strip()}  [可选]" if opt else name.strip())

    # ============== 保存 ==============
    def _save_and_accept(self):
        # 先把当前选中节点的 ref 应用一下
        if self.tree.selectedItems():
            self._apply_refs_to_node_silent()
        self._template = self._build_template_from_tree()
        dn = self.edit_display_name.text().strip()
        if dn:
            self._template["display_name"] = dn
        self.accept()

    def _apply_refs_to_node_silent(self):
        items = self.tree.selectedItems()
        if not items:
            return
        refs = []
        for r in range(self.tbl.rowCount()):
            fn_it = self.tbl.item(r, 0)
            src_it = self.tbl.item(r, 1)
            tpl_it = self.tbl.item(r, 2)
            filename = (fn_it.text() if fn_it else "").strip()
            if not filename:
                continue
            refs.append({
                "filename": filename,
                "source": (src_it.text() if src_it else "").strip(),
                "file_template": (tpl_it.text() if tpl_it else "").strip() or None,
            })
        items[0].setData(0, ROLE_REF_FILES, refs)

    def _build_template_from_tree(self):
        root_item = self.tree.topLevelItem(0)
        root_dict = self._item_to_dict(root_item)
        # 保留原 type / display_name
        root_dict["type"] = self._template.get("type", "")
        if self._template.get("display_name"):
            root_dict["display_name"] = self._template["display_name"]
        return root_dict

    def _item_to_dict(self, item):
        name_raw = item.text(0).split("  [")[0]
        enabled = item.checkState(0) == Qt.Checked
        d = {
            "name": name_raw,
            "children": [],
            "ref_files": item.data(0, ROLE_REF_FILES) or [],
            "_enabled": enabled,
        }
        if item.data(0, ROLE_OPTIONAL):
            d["optional"] = True
            d["condition"] = item.data(0, ROLE_CONDITION) or ""
        # 如果该节点未被勾选，且是可选节点，直接不输出（其结构被丢弃）
        # 对于常规节点，保留 _enabled 标记；flatten 时根据它过滤
        for i in range(item.childCount()):
            child = item.child(i)
            if child.checkState(0) == Qt.Unchecked:
                # 未勾选的节点不输出到最终模板
                continue
            d["children"].append(self._item_to_dict(child))
        return d

    def result_template(self):
        return self._template
