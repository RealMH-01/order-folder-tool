# -*- coding: utf-8 -*-
"""
扫描导入业务员对话框。

用户点击首页「扫描导入业务员」按钮后：
1. 程序在 <根目录>/1订单/ 下列出所有第一层文件夹
2. 以树形勾选列表展示，每个文件夹旁边有复选框
3. 对每个文件夹，如果其下还有子文件夹（可能是分公司 → 业务员的情况），
   可以展开它，勾选真正的"业务员"所在层级
4. 用户勾选后点"确认导入"，对话框返回被勾选项的列表：
      [{"name": "张莹莹", "rel_path": "张莹莹"},
       {"name": "文天堂", "rel_path": "湖北/文天堂"}, ...]
   调用方再调用 Storage.import_scanned_salespersons(rel_paths) 完成导入。
"""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout
)


class ScanImportDialog(QDialog):
    """扫描导入业务员对话框"""

    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.setWindowTitle("扫描导入业务员")
        self.resize(720, 640)
        self._order_root = ""
        self._selected_rel_paths = []  # 确认后的结果
        self._build_ui()
        self._populate()

    # ------------------------------ UI ------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)

        # 顶部说明
        intro = QLabel(
            "程序会扫描「<b>1订单/</b>」文件夹下的所有子文件夹。<br/>"
            "请勾选其中<b>属于业务员</b>的文件夹；不属于业务员的（如"
            "资料文件夹、Excel 文件）不要勾选。<br/>"
            "若某个文件夹是<b>分公司</b>（例如「湖北」），请点开它，勾选里面的"
            "业务员子文件夹。<br/>"
            "勾选完成后点「确认导入」。"
        )
        intro.setWordWrap(True)
        intro.setStyleSheet("background:#FFF3E0;padding:10px;border-radius:6px;"
                            "border:1px solid #FFCC80;")
        root.addWidget(intro)

        # 订单文件夹路径显示
        path_row = QHBoxLayout()
        path_row.addWidget(QLabel("订单根文件夹："))
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        path_row.addWidget(self.path_edit, 1)
        self.btn_browse = QPushButton("手动指定…")
        self.btn_browse.setObjectName("SecondaryButton")
        self.btn_browse.clicked.connect(self._browse_custom_order_root)
        path_row.addWidget(self.btn_browse)
        self.btn_rescan = QPushButton("重新扫描")
        self.btn_rescan.setObjectName("SecondaryButton")
        self.btn_rescan.clicked.connect(self._populate)
        path_row.addWidget(self.btn_rescan)
        root.addLayout(path_row)

        # 工具栏：全选、全不选、展开全部
        tools = QHBoxLayout()
        btn_check_all = QPushButton("全部勾选")
        btn_check_all.setObjectName("SecondaryButton")
        btn_check_all.clicked.connect(lambda: self._set_all_checked(True))
        btn_uncheck_all = QPushButton("全部取消")
        btn_uncheck_all.setObjectName("SecondaryButton")
        btn_uncheck_all.clicked.connect(lambda: self._set_all_checked(False))
        btn_expand = QPushButton("展开全部")
        btn_expand.setObjectName("SecondaryButton")
        btn_expand.clicked.connect(lambda: self.tree.expandAll())
        btn_collapse = QPushButton("折叠全部")
        btn_collapse.setObjectName("SecondaryButton")
        btn_collapse.clicked.connect(lambda: self.tree.collapseAll())
        tools.addWidget(btn_check_all)
        tools.addWidget(btn_uncheck_all)
        tools.addSpacing(20)
        tools.addWidget(btn_expand)
        tools.addWidget(btn_collapse)
        tools.addStretch(1)
        root.addLayout(tools)

        # 树
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["文件夹名", "预览：下面的客户（若勾选将作为业务员导入）"])
        self.tree.setColumnWidth(0, 260)
        self.tree.itemChanged.connect(self._on_item_changed)
        root.addWidget(self.tree, 1)

        # 提示：识别规则
        rule_tip = QLabel(
            "客户识别规则：若业务员文件夹下有<b>同时包含「进行」和「订单」</b>"
            "关键词的子文件夹（如「进行中订单」、「1.进行订单」），"
            "将进入该文件夹抓取客户；否则把业务员下的子文件夹直接作为客户。"
        )
        rule_tip.setWordWrap(True)
        rule_tip.setStyleSheet("color:#555;font-size:12px;")
        root.addWidget(rule_tip)

        # 按钮
        btns = QDialogButtonBox()
        self.btn_ok = btns.addButton("确认导入", QDialogButtonBox.AcceptRole)
        self.btn_cancel = btns.addButton("取消", QDialogButtonBox.RejectRole)
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        root.addWidget(btns)

    # --------------------- 数据填充 ---------------------
    def _populate(self):
        """扫描 1订单 并构建树"""
        self.tree.blockSignals(True)
        self.tree.clear()
        self._order_root = ""

        if not self.storage.root_dir:
            QMessageBox.warning(self, "提示", "请先在首页设置并保存"
                                "「公司资料根目录」。")
            self.tree.blockSignals(False)
            return

        default_order_root = os.path.join(
            self.storage.root_dir, self.storage.ORDER_ROOT_FOLDER
        )
        if not os.path.isdir(default_order_root):
            # 提示用户手动选择
            ret = QMessageBox.question(
                self, "未找到「1订单」文件夹",
                f"在根目录下没有找到「{self.storage.ORDER_ROOT_FOLDER}」文件夹：\n"
                f"{default_order_root}\n\n是否手动指定订单根文件夹？",
                QMessageBox.Yes | QMessageBox.No,
            )
            if ret == QMessageBox.Yes:
                self._browse_custom_order_root()
                return
            self.tree.blockSignals(False)
            return

        self._order_root = default_order_root
        self.path_edit.setText(self._order_root)
        self._fill_tree_from_order_root()
        self.tree.blockSignals(False)

    def _browse_custom_order_root(self):
        d = QFileDialog.getExistingDirectory(
            self, "请选择订单根文件夹（通常名为 1订单）",
            self.storage.root_dir or ""
        )
        if not d:
            return
        self._order_root = d
        self.path_edit.setText(d)
        self.tree.blockSignals(True)
        self.tree.clear()
        self._fill_tree_from_order_root()
        self.tree.blockSignals(False)

    def _fill_tree_from_order_root(self):
        """按 self._order_root 扫描并填充树。支持两层：
           第 1 层 = 1订单 下的文件夹（可能是业务员，也可能是分公司）
           第 2 层 = 第 1 层文件夹的子文件夹（用于分公司内的业务员）
        """
        if not self._order_root or not os.path.isdir(self._order_root):
            return
        try:
            entries = sorted(os.listdir(self._order_root))
        except OSError as e:
            QMessageBox.warning(self, "错误", f"无法读取目录：{e}")
            return

        for name in entries:
            full = os.path.join(self._order_root, name)
            if not os.path.isdir(full) or name.startswith("."):
                continue
            lvl1 = QTreeWidgetItem([name, ""])
            # 注意：不要使用 ItemIsAutoTristate，否则勾选父节点会自动勾选所有子节点，
            # 破坏"父作为业务员 vs 子作为业务员"的互斥语义。
            lvl1.setFlags(lvl1.flags() | Qt.ItemIsUserCheckable)
            lvl1.setCheckState(0, Qt.Unchecked)
            lvl1.setData(0, Qt.UserRole, {"rel_path": name, "abs": full})
            # 第 1 层客户预览
            lvl1.setText(1, self._customer_preview(name))
            self.tree.addTopLevelItem(lvl1)

            # 第 2 层：分公司内的业务员（若当前层还有子文件夹）
            try:
                for sub in sorted(os.listdir(full)):
                    sub_full = os.path.join(full, sub)
                    if not os.path.isdir(sub_full) or sub.startswith("."):
                        continue
                    rel_sub = f"{name}/{sub}"
                    lvl2 = QTreeWidgetItem([sub, ""])
                    lvl2.setFlags(lvl2.flags() | Qt.ItemIsUserCheckable)
                    lvl2.setCheckState(0, Qt.Unchecked)
                    lvl2.setData(0, Qt.UserRole,
                                 {"rel_path": rel_sub, "abs": sub_full})
                    lvl2.setText(1, self._customer_preview(rel_sub))
                    lvl1.addChild(lvl2)
            except OSError:
                pass

        self.tree.expandToDepth(0)

    def _customer_preview(self, rel_under_order_root: str) -> str:
        """根据扫描规则，预览将作为客户导入的数量及前几项（仅展示，不改数据）"""
        try:
            mid, customers = self.storage.scan_customers_for(rel_under_order_root)
        except Exception:
            return ""
        if not customers:
            return "（无客户子文件夹）"
        sample = "、".join(customers[:3])
        more = f" …共 {len(customers)} 个" if len(customers) > 3 else ""
        mid_str = f"【中间层：{mid}】 " if mid else ""
        return f"{mid_str}{sample}{more}"

    # --------------------- 交互 ---------------------
    def _on_item_changed(self, item, column):
        """互斥逻辑：
           - 勾选父节点 → 自动取消所有子节点（把父本身作为业务员导入）
           - 勾选任一子节点 → 自动取消父节点（把子作为业务员导入，父作为分公司）
        """
        if column != 0:
            return
        self.tree.blockSignals(True)
        try:
            # 判断是父还是子
            if item.parent() is None:
                # 父节点被勾选
                if item.checkState(0) == Qt.Checked:
                    # 清掉所有子节点
                    for j in range(item.childCount()):
                        item.child(j).setCheckState(0, Qt.Unchecked)
            else:
                # 子节点被勾选
                if item.checkState(0) == Qt.Checked:
                    parent = item.parent()
                    if parent.checkState(0) == Qt.Checked:
                        parent.setCheckState(0, Qt.Unchecked)
        finally:
            self.tree.blockSignals(False)

    def _set_all_checked(self, checked: bool):
        self.tree.blockSignals(True)
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            if not checked:
                # 取消：全部取消
                top.setCheckState(0, Qt.Unchecked)
                for j in range(top.childCount()):
                    top.child(j).setCheckState(0, Qt.Unchecked)
            else:
                # 勾选：有子节点时只勾子节点不勾父节点，无子节点时勾自身
                if top.childCount() > 0:
                    top.setCheckState(0, Qt.Unchecked)
                    for j in range(top.childCount()):
                        top.child(j).setCheckState(0, Qt.Checked)
                else:
                    top.setCheckState(0, Qt.Checked)
        self.tree.blockSignals(False)

    def _on_accept(self):
        """收集勾选结果。规则：
           - 若第 1 层已勾选且它没有勾选的子节点，就按 rel_path=第1层名字 导入
           - 若第 1 层已勾选但有被勾选的子节点，说明它是"分公司"，此时只导入子节点
           - 若第 1 层未勾选但其子节点被勾选，只导入被勾选的子节点
        """
        selected = []
        for i in range(self.tree.topLevelItemCount()):
            top = self.tree.topLevelItem(i)
            top_checked = (top.checkState(0) == Qt.Checked)
            top_partial = (top.checkState(0) == Qt.PartiallyChecked)
            child_checked_items = []
            for j in range(top.childCount()):
                c = top.child(j)
                if c.checkState(0) == Qt.Checked:
                    child_checked_items.append(c)
            # 情况 1：只有父被勾选，没有子被勾选 → 父作为业务员
            if top_checked and not child_checked_items:
                info = top.data(0, Qt.UserRole) or {}
                selected.append({
                    "name": top.text(0),
                    "rel_path": info.get("rel_path", top.text(0)),
                })
            else:
                # 情况 2/3：有子被勾选 → 只导入被勾选的子节点（父不作为业务员）
                for c in child_checked_items:
                    info = c.data(0, Qt.UserRole) or {}
                    selected.append({
                        "name": c.text(0),
                        "rel_path": info.get("rel_path", c.text(0)),
                    })

        if not selected:
            QMessageBox.information(self, "提示", "还没有勾选任何业务员文件夹。")
            return

        self._selected_rel_paths = [s["rel_path"] for s in selected]
        self._selected_items = selected
        self.accept()

    # --------------------- 对外 ---------------------
    def get_selected_rel_paths(self):
        return list(self._selected_rel_paths)

    def get_selected_items(self):
        return list(getattr(self, "_selected_items", []))
