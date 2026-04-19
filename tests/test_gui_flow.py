# -*- coding: utf-8 -*-
"""
GUI 完整流程测试（用 offscreen 平台）
- 启动首页 → 设置根目录 + 模板目录
- 切换到单笔创建 → 填表 → 扫描（不弹对话框，直接跑 execute_build）
- 切换到批量导入
- 切换到模板管理、历史记录
"""

import os
import sys
import tempfile
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication

from app.main_window import MainWindow
from app.style import APP_QSS


def setup_workspace():
    tmp = Path(tempfile.mkdtemp(prefix="gui_test_"))
    root = tmp / "公司资料"
    root.mkdir()
    tpl_dir = tmp / "模板"
    (tpl_dir / "通用").mkdir(parents=True)
    (tpl_dir / "外贸通用").mkdir(parents=True)
    (tpl_dir / "宁夏").mkdir(parents=True)
    (tpl_dir / "湖北天鹅").mkdir(parents=True)
    files = [
        "通用/CG.xlsx", "外贸通用/CI.xlsx", "外贸通用/PL.xls",
        "外贸通用/托书.doc", "宁夏/宁夏外贸生产.doc",
        "宁夏/宁夏外贸发货.docx", "宁夏/宁夏内贸生产.xlsx",
        "宁夏/宁夏内贸发货.xlsx", "湖北天鹅/湖北天鹅外贸生产.xlsx",
        "湖北天鹅/湖北天鹅外贸发货.xlsx",
    ]
    for f in files:
        (tpl_dir / f).write_text("X", encoding="utf-8")
    return str(root), str(tpl_dir)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)
    win = MainWindow()
    win.show()

    root, tpl_dir = setup_workspace()

    # 在首页设置根目录和模板目录
    hp = win.page_home
    hp.root_edit.setText(root)
    hp._save_root()  # 会弹框 → 但 offscreen 下阻塞？用 QTimer 关掉
    hp.tpl_edit.setText(tpl_dir)
    # 直接操作 storage 避免 messagebox 阻塞
    win.storage.update_config(template_files_dir=tpl_dir)

    print("根目录已设置：", win.storage.root_dir)
    print("模板目录：", tpl_dir)

    # 新增业务员+客户
    win.storage.add_salesperson("张三")
    win.storage.add_customer("张三", "ACME")

    # 切到单笔创建
    win.stack.setCurrentIndex(1)
    sp = win.page_single
    sp.refresh()
    assert sp.cmb_sales.count() > 0, "业务员下拉框应加载"
    assert "张三" in [sp.cmb_sales.itemText(i) for i in range(sp.cmb_sales.count())]
    sp.cmb_sales.setCurrentText("张三")
    sp.cmb_customer.setCurrentText("ACME")
    sp.cmb_order_type.setCurrentText("外贸")
    sp.cmb_category.setCurrentText("戊二醛")
    sp.edit_order_no.setText("XS-TEST-001")
    sp.edit_customer.setText("ACME")
    # 收集
    order = sp._collect_order()
    assert order is not None
    assert order["order_no"] == "XS-TEST-001"
    print("单笔表单采集：", order)

    # 模板已自动匹配
    assert sp._current_template is not None
    print("匹配模板：", sp._current_template_name)

    # 切到批量导入
    win.stack.setCurrentIndex(2)
    bp = win.page_batch
    bp.refresh()
    bp._add_row({
        "order_type": "外贸", "order_no": "XS-B001", "customer": "ACME",
        "product_info": "", "product_category": "戊二醛",
        "needs_inspection": True,
    })
    bp._add_row({
        "order_type": "内贸", "order_no": "NS-B002", "customer": "某某公司",
        "product_info": "戊二醛1T", "product_category": "戊二醛",
        "needs_inspection": False,
    })
    bp.cmb_sales.setCurrentText("张三")
    rows = bp._collect_rows()
    print(f"批量采集行数：{len(rows)}")
    assert len(rows) == 2

    # 预览（不会弹框）
    bp._preview_all()
    # 状态列：加入「客户PO号」列后，状态列从 7 移到 8
    status1 = bp.table.item(0, 8).text()
    status2 = bp.table.item(1, 8).text()
    print(f"预览状态：行1={status1}  行2={status2}")
    assert "待创建" in status1

    # 切到模板管理
    win.stack.setCurrentIndex(3)
    tp = win.page_templates
    tp.refresh()
    count = tp.list.count()
    print(f"模板列表项数：{count}")
    assert count >= 5  # 3 个 header + 2 个 standard + 可能的业务员模板

    # 切到历史记录
    win.stack.setCurrentIndex(4)
    hp2 = win.page_history
    hp2.refresh()
    # 目前还没记录
    assert hp2.table.rowCount() == 0

    # 写一条历史再看
    win.storage.append_history({
        "time": "2025-01-01 10:00:00", "operator": "test",
        "salesperson": "张三", "customer": "ACME",
        "order_no": "XS-TEST-001", "order_type": "外贸",
        "product_category": "戊二醛", "template_name": "standard_export.json",
        "path": "/tmp/xxx", "result": "成功",
        "created_count": 8, "skipped_count": 0, "copied_count": 6,
    })
    hp2.refresh()
    assert hp2.table.rowCount() == 1
    # 搜索
    hp2.edit_search.setText("XS-TEST")
    assert hp2.table.rowCount() == 1
    hp2.edit_search.setText("XS-NOTEXIST")
    assert hp2.table.rowCount() == 0
    hp2.edit_search.setText("")

    print("\n🎉 GUI 完整流程测试通过")

    # 退出
    QTimer.singleShot(0, app.quit)
    app.exec_()


if __name__ == "__main__":
    # 屏蔽弹框：把 QMessageBox 方法 patch 成空
    from PyQt5.QtWidgets import QMessageBox
    for m in ("information", "warning", "critical", "question"):
        setattr(QMessageBox, m, staticmethod(lambda *a, **k: QMessageBox.Ok))
    main()
