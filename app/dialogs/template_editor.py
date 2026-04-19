# -*- coding: utf-8 -*-
"""模板编辑对话框（可勾选的树 + 右键菜单 + ref_files 编辑）"""

import copy

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont
from PyQt5.QtWidgets import (
    QAction, QComboBox, QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout,
    QHeaderView, QInputDialog, QLabel, QLineEdit, QMenu, QMessageBox,
    QPushButton, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget
)


ROLE_IS_STANDARD = Qt.UserRole + 1  # 是否来自标准模板（不可删除）
ROLE_REF_FILES = Qt.UserRole + 2    # 该节点的 ref_files（list）
ROLE_OPTIONAL = Qt.UserRole + 3
ROLE_CONDITION = Qt.UserRole + 4


class TemplateEditorDialog(QDialog):
    """
    template：dict（会被拷贝后编辑）
    base_template：标准模板，用于标注哪些节点是"标准节点"（不可删除）
    """

    def __init__(self, template, base_template=None, title="编辑模板", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(980, 640)
        self._template = copy.deepcopy(template)
        self._base_template = base_template or template
        self._standard_paths = self._collect_paths(self._base_template)
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
        self.tbl = QTableWidget(0, 3)
        self.tbl.setHorizontalHeaderLabels(["文件名 (filename)", "来源 (source)",
                                             "模板文件 (file_template)"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right.addWidget(self.tbl, 1)

        row_ops = QHBoxLayout()
        b_add = QPushButton("+ 新增")
        b_add.setObjectName("SecondaryButton")
        b_add.clicked.connect(self._add_ref)
        b_del = QPushButton("- 删除选中")
        b_del.setObjectName("SecondaryButton")
        b_del.clicked.connect(self._del_ref)
        b_apply = QPushButton("✔ 应用修改到当前文件夹")
        b_apply.clicked.connect(self._apply_refs_to_node)
        row_ops.addWidget(b_add)
        row_ops.addWidget(b_del)
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
            self.tbl.setItem(r, 0, QTableWidgetItem(rf.get("filename", "")))
            self.tbl.setItem(r, 1, QTableWidgetItem(rf.get("source", "")))
            self.tbl.setItem(r, 2, QTableWidgetItem(rf.get("file_template") or ""))

    def _add_ref(self):
        r = self.tbl.rowCount()
        self.tbl.insertRow(r)
        self.tbl.setItem(r, 0, QTableWidgetItem("新文件-<订单号>.xlsx"))
        self.tbl.setItem(r, 1, QTableWidgetItem("自制"))
        self.tbl.setItem(r, 2, QTableWidgetItem(""))

    def _del_ref(self):
        rows = sorted({i.row() for i in self.tbl.selectedIndexes()}, reverse=True)
        for r in rows:
            self.tbl.removeRow(r)

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
