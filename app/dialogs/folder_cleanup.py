# -*- coding: utf-8 -*-
"""
功能 D：文件夹一键整理

用户实际工作流程：
  1. 程序创建订单文件夹（空白模板文件带 `_对照` 后缀）。
  2. 用户从上一票订单文件夹手动复制文件过来。
  3. 对照着 `_对照` 文件修改这些旧文件的内容。
  4. 点「整理文件夹」：
     - 删除所有带 `_对照` 的空白模板文件
     - 按当前模板命名规则，给剩下的文件重命名
       （不是简单字符串替换，而是基于模板定义的期望命名）
"""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QHeaderView, QLabel,
    QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget
)

from ..core import folder_builder


# 操作常量
OP_DELETE = "删除"
OP_RENAME = "重命名"
OP_SKIP = "跳过"


# 颜色标识
COLOR_RED = "#E53935"       # 删除（_对照 文件）
COLOR_BLUE = "#1976D2"      # 高置信度匹配
COLOR_ORANGE = "#FB8C00"    # 低置信度匹配（需确认）
COLOR_GRAY = "#9E9E9E"      # 未匹配


def _extract_keyword_prefix(filled_name: str) -> str:
    """
    从"已占位符替换"的期望文件名中提取关键字前缀。

    规则：取文件名（不含扩展名）的第一个 "-" 之前的部分。
    例如：
      - "CI-XS-NEW001NH.xlsx"         → "CI"
      - "发货通知单-XS-NEW001NH.doc"  → "发货通知单"
      - "发票-XS-NEW001NH-BAKER.xlsx" → "发票"
      - "BL-XS-NEW001NH.pdf"          → "BL"
      - "贴唛图.jpg"（无订单号占位符） → "贴唛图"
    """
    stem = os.path.splitext(os.path.basename(filled_name))[0]
    if not stem:
        return ""
    if "-" in stem:
        return stem.split("-", 1)[0]
    return stem


def _build_expected_file_list(template: Dict[str, Any],
                              ctx: Dict[str, str],
                              product_category: str,
                              needs_inspection: bool) -> List[Dict[str, Any]]:
    """
    从模板展开得到期望文件清单（每项描述该文件应该在哪、叫什么）。

    返回列表，每项包含：
      - folder_rel: str，相对「订单号文件夹」的子目录（如 "SD"、"货代资料/唛头"、""=根目录）
      - filled_name: str，占位符替换后的期望文件名（不带 _对照）
      - ext: str，文件后缀（带点）
      - prefix: str，关键字前缀（如 "CI"）
    """
    # flatten_template_folders 返回的 rel_path 是相对"客户目录"，根节点为订单号。
    tpl_folders = folder_builder.flatten_template_folders(
        template, "", ctx, needs_inspection, parent_path=None
    )
    if not tpl_folders:
        return []
    # 根节点 rel_path = 订单号；子节点 rel_path = 订单号/xxx
    order_root_rel = ""
    for it in tpl_folders:
        if it.get("is_root"):
            order_root_rel = it["rel_path"]
            break

    expected = []
    for it in tpl_folders:
        rel = it["rel_path"]
        # 子目录相对于"订单号文件夹"
        if it.get("is_root"):
            folder_rel = ""
        else:
            if order_root_rel and rel.startswith(order_root_rel):
                folder_rel = rel[len(order_root_rel):].lstrip("/\\")
            else:
                folder_rel = rel
            # 统一用正斜杠
            folder_rel = folder_rel.replace("\\", "/")

        for rf in it.get("ref_files", []) or []:
            raw = rf.get("filename", "")
            if not raw:
                continue
            filled = folder_builder.replace_placeholders(raw, ctx)
            # 补全扩展名
            if "." not in os.path.basename(filled):
                resolved_tpl = folder_builder.resolve_file_template(
                    rf.get("file_template"), product_category)
                if resolved_tpl:
                    filled += os.path.splitext(resolved_tpl)[1]
                else:
                    # 没有可推断的扩展名，跳过（无法可靠匹配）
                    continue
            ext = os.path.splitext(filled)[1].lower()
            prefix = _extract_keyword_prefix(filled)
            expected.append({
                "folder_rel": folder_rel,
                "filled_name": filled,
                "ext": ext,
                "prefix": prefix,
            })
    return expected


def _scan_actual_files(order_folder: str) -> List[Dict[str, Any]]:
    """扫描订单文件夹下所有文件（递归）。

    返回每项：
      - folder_rel: 相对订单文件夹的子目录（"" 表示在根）
      - name: 文件名
      - abs_path: 绝对路径
      - ext: 后缀（小写，带点）
      - is_reference: 是否是 _对照 模板文件
    """
    results = []
    root = Path(order_folder)
    if not root.is_dir():
        return results
    for dirpath, _, filenames in os.walk(str(root)):
        for fname in filenames:
            # 跳过程序自己生成的清单
            if fname.startswith("文件清单-") and fname.endswith(".xlsx"):
                continue
            # 跳过 Excel 临时文件
            if fname.startswith("~$"):
                continue
            abs_path = os.path.join(dirpath, fname)
            rel = os.path.relpath(dirpath, str(root)).replace("\\", "/")
            if rel == ".":
                rel = ""
            ext = os.path.splitext(fname)[1].lower()
            is_ref = "_对照" in fname
            results.append({
                "folder_rel": rel,
                "name": fname,
                "abs_path": abs_path,
                "ext": ext,
                "is_reference": is_ref,
            })
    return results


def _plan_cleanup(actual_files: List[Dict[str, Any]],
                  expected: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    把实际文件与模板期望文件配对，生成操作计划。

    返回每项：
      - folder_rel / old_name / abs_path
      - op: OP_DELETE / OP_RENAME / OP_SKIP
      - new_name: 重命名目标文件名（仅 OP_RENAME）
      - confidence: "high" / "low" / "none"
      - note: 说明文字
    """
    plans = []
    # expected 可能被"消耗"（同一个期望条目只应被一个文件匹配一次），
    # 但为了简单保留不消耗，让用户自己选择。
    # 按 folder_rel 索引 expected 方便查找
    exp_by_folder: Dict[str, List[Dict[str, Any]]] = {}
    for e in expected:
        exp_by_folder.setdefault(e["folder_rel"], []).append(e)

    for af in actual_files:
        if af["is_reference"]:
            plans.append({
                "folder_rel": af["folder_rel"],
                "old_name": af["name"],
                "abs_path": af["abs_path"],
                "op": OP_DELETE,
                "new_name": "",
                "confidence": "ref",
                "note": "空白模板对照文件，建议删除",
            })
            continue

        # 尝试匹配
        cand_same_folder_ext = [
            e for e in exp_by_folder.get(af["folder_rel"], [])
            if e["ext"] == af["ext"]
        ]
        # 高置信度：同目录、同扩展、文件名含关键字前缀
        high = None
        for e in cand_same_folder_ext:
            prefix = e["prefix"]
            if prefix and prefix in af["name"]:
                high = e
                break
        if high is not None:
            plans.append({
                "folder_rel": af["folder_rel"],
                "old_name": af["name"],
                "abs_path": af["abs_path"],
                "op": OP_RENAME if af["name"] != high["filled_name"] else OP_SKIP,
                "new_name": high["filled_name"],
                "confidence": "high",
                "note": f"匹配到模板条目「{high['filled_name']}」"
                         + ("（已是目标名）" if af["name"] == high["filled_name"] else ""),
            })
            continue

        # 低置信度：同目录、同扩展，但关键字不匹配 → 让用户决定
        if cand_same_folder_ext:
            e = cand_same_folder_ext[0]
            plans.append({
                "folder_rel": af["folder_rel"],
                "old_name": af["name"],
                "abs_path": af["abs_path"],
                "op": OP_RENAME if af["name"] != e["filled_name"] else OP_SKIP,
                "new_name": e["filled_name"],
                "confidence": "low",
                "note": f"同目录同后缀，候选「{e['filled_name']}」（需确认）",
            })
            continue

        # 未匹配
        plans.append({
            "folder_rel": af["folder_rel"],
            "old_name": af["name"],
            "abs_path": af["abs_path"],
            "op": OP_SKIP,
            "new_name": "",
            "confidence": "none",
            "note": "未找到匹配的模板条目，保持原样",
        })
    return plans


class FolderCleanupDialog(QDialog):
    """文件夹整理对话框"""

    HEADERS = ["所在子文件夹", "当前文件名", "操作", "新文件名", "说明"]

    def __init__(self, order_folder_path: str, order_no: str,
                 template: Dict[str, Any], ctx: Dict[str, str],
                 parent=None,
                 product_category: str = "戊二醛",
                 needs_inspection: bool = False):
        super().__init__(parent)
        self.setWindowTitle(f"整理订单文件夹 - {order_no}")
        self.resize(960, 600)
        self._order_folder = order_folder_path
        self._order_no = order_no
        self._template = template
        self._ctx = ctx or {}
        self._product_category = product_category
        self._needs_inspection = needs_inspection

        self._expected = _build_expected_file_list(
            template, self._ctx, product_category, needs_inspection
        )
        self._actual = _scan_actual_files(order_folder_path)
        self._plans = _plan_cleanup(self._actual, self._expected)

        self._build_ui()
        self._fill_table()

    # -------- UI --------
    def _build_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel(
            f"<b>订单号：</b>{self._order_no}<br>"
            f"<b>文件夹：</b>{self._order_folder}"
        )
        header.setStyleSheet("margin-bottom:6px;")
        layout.addWidget(header)

        legend = QLabel(
            f'<span style="color:{COLOR_RED};font-weight:bold;">■</span> 对照文件（删除） &nbsp;&nbsp;'
            f'<span style="color:{COLOR_BLUE};font-weight:bold;">■</span> 高置信度匹配（自动重命名） &nbsp;&nbsp;'
            f'<span style="color:{COLOR_ORANGE};font-weight:bold;">■</span> 低置信度（需确认） &nbsp;&nbsp;'
            f'<span style="color:{COLOR_GRAY};font-weight:bold;">■</span> 未匹配（跳过）'
        )
        layout.addWidget(legend)

        self.table = QTableWidget(0, len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setColumnWidth(0, 160)
        self.table.setColumnWidth(1, 260)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 240)
        self.table.setColumnWidth(4, 200)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table, 1)

        btns = QDialogButtonBox()
        self.btn_exec = btns.addButton("执行整理", QDialogButtonBox.AcceptRole)
        self.btn_exec.setStyleSheet("font-weight:bold;")
        self.btn_cancel = btns.addButton("取消", QDialogButtonBox.RejectRole)
        btns.accepted.connect(self._execute)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _fill_table(self):
        self.table.setRowCount(0)
        for plan in self._plans:
            r = self.table.rowCount()
            self.table.insertRow(r)

            folder_text = plan["folder_rel"] or "（根目录）"
            it_folder = QTableWidgetItem(folder_text)
            it_folder.setFlags(it_folder.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(r, 0, it_folder)

            it_old = QTableWidgetItem(plan["old_name"])
            it_old.setFlags(it_old.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(r, 1, it_old)

            cmb = QComboBox()
            cmb.addItems([OP_DELETE, OP_RENAME, OP_SKIP])
            cmb.setCurrentText(plan["op"])
            self.table.setCellWidget(r, 2, cmb)

            it_new = QTableWidgetItem(plan["new_name"])
            self.table.setItem(r, 3, it_new)

            it_note = QTableWidgetItem(plan["note"])
            it_note.setFlags(it_note.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(r, 4, it_note)

            # 设置颜色
            color = self._row_color(plan["confidence"])
            for c in range(self.table.columnCount()):
                cell = self.table.item(r, c)
                if cell is not None:
                    cell.setForeground(QBrush(QColor(color)))

    def _row_color(self, confidence: str) -> str:
        return {
            "ref": COLOR_RED,
            "high": COLOR_BLUE,
            "low": COLOR_ORANGE,
            "none": COLOR_GRAY,
        }.get(confidence, "#333333")

    # -------- 执行 --------
    def _collect_final_plans(self) -> List[Dict[str, Any]]:
        """从表格中回读最终的操作计划。"""
        out = []
        for r in range(self.table.rowCount()):
            base = self._plans[r]
            cmb = self.table.cellWidget(r, 2)
            op = cmb.currentText() if cmb else base["op"]
            new_name_item = self.table.item(r, 3)
            new_name = new_name_item.text().strip() if new_name_item else ""
            out.append({
                "abs_path": base["abs_path"],
                "folder_rel": base["folder_rel"],
                "old_name": base["old_name"],
                "op": op,
                "new_name": new_name,
            })
        return out

    def _execute(self):
        plans = self._collect_final_plans()
        total = len(plans)
        del_cnt = sum(1 for p in plans if p["op"] == OP_DELETE)
        ren_cnt = sum(1 for p in plans if p["op"] == OP_RENAME)
        skip_cnt = sum(1 for p in plans if p["op"] == OP_SKIP)

        reply = QMessageBox.question(
            self, "确认执行",
            f"即将执行：\n"
            f"  · 删除 {del_cnt} 个文件\n"
            f"  · 重命名 {ren_cnt} 个文件\n"
            f"  · 跳过 {skip_cnt} 个文件\n\n"
            f"是否继续？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        errors = []
        deleted = 0
        renamed = 0
        # 优先执行删除，避免改名后命名冲突
        for p in plans:
            if p["op"] != OP_DELETE:
                continue
            try:
                os.remove(p["abs_path"])
                deleted += 1
            except Exception as e:
                errors.append(f"删除失败 {p['abs_path']}：{e}")

        # 再执行重命名
        for p in plans:
            if p["op"] != OP_RENAME:
                continue
            new_name = p["new_name"].strip()
            if not new_name:
                errors.append(f"跳过空新名：{p['abs_path']}")
                continue
            src = p["abs_path"]
            if not os.path.exists(src):
                errors.append(f"源文件不存在：{src}")
                continue
            dst_dir = os.path.dirname(src)
            dst = os.path.join(dst_dir, new_name)
            if os.path.abspath(src) == os.path.abspath(dst):
                continue  # 已经是目标名
            if os.path.exists(dst):
                errors.append(f"目标已存在，跳过：{dst}")
                continue
            try:
                os.rename(src, dst)
                renamed += 1
            except Exception as e:
                errors.append(f"重命名失败 {src} → {new_name}：{e}")

        # 汇总
        msg = (f"整理完成：\n"
               f"  · 删除 {deleted} 个\n"
               f"  · 重命名 {renamed} 个\n"
               f"  · 跳过 {skip_cnt} 个\n")
        if errors:
            msg += "\n出现以下问题：\n" + "\n".join(errors[:20])
            if len(errors) > 20:
                msg += f"\n... 还有 {len(errors) - 20} 条"
            QMessageBox.warning(self, "整理完成（有错误）", msg)
        else:
            QMessageBox.information(self, "整理完成", msg)
        self.accept()
