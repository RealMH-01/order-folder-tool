# -*- coding: utf-8 -*-
"""使用帮助页（完全傻瓜式教程）

- 使用 QTextBrowser 展示富文本（HTML）
- 顶部有返回首页按钮 + 章节快速跳转按钮栏
- 内容面向从未接触过程序的普通办公人员
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QTextBrowser, QVBoxLayout, QWidget
)


# 章节锚点 ID（稳定的英文 id，避免中文 fragment 问题）
SECTIONS = [
    ("sec-quick", "快速开始"),
    ("sec-single", "创建订单"),
    ("sec-batch", "批量导入"),
    ("sec-templates", "模板管理"),
    ("sec-history", "历史记录"),
    ("sec-naming", "命名变量"),
    ("sec-faq", "常见问题"),
]


def _build_help_html() -> str:
    """构造帮助页 HTML 内容。"""
    css = """
    <style>
      body { font-family: "Microsoft YaHei", "微软雅黑", sans-serif;
             font-size: 14px; color:#222; line-height:1.7; }
      h1   { color:#0D47A1; font-size:24px; border-bottom:3px solid #1976D2;
             padding-bottom:6px; margin-top:28px; }
      h2   { color:#1565C0; font-size:18px; margin-top:22px; }
      h3   { color:#1976D2; font-size:16px; margin-top:16px; }
      ol li, ul li { margin:6px 0; }
      .note { background:#FFF3E0; border-left:4px solid #FB8C00;
              padding:10px 14px; margin:12px 0; border-radius:4px; }
      .tip  { background:#E3F2FD; border-left:4px solid #1976D2;
              padding:10px 14px; margin:12px 0; border-radius:4px; }
      .warn { background:#FFEBEE; border-left:4px solid #E53935;
              padding:10px 14px; margin:12px 0; border-radius:4px; }
      code { background:#ECEFF1; padding:2px 6px; border-radius:3px;
             font-family: Consolas, "Courier New", monospace; }
      .k { color:#C62828; font-weight:bold; }
      .btn { background:#1976D2; color:white; padding:2px 8px;
             border-radius:4px; font-weight:bold; }
      table { border-collapse:collapse; margin:10px 0; }
      th, td { border:1px solid #B0BEC5; padding:6px 12px; }
      th { background:#E3F2FD; color:#0D47A1; }
      pre { background:#263238; color:#ECEFF1; padding:12px;
            border-radius:6px; font-size:13px; overflow-x:auto; }
    </style>
    """

    quick = """
    <h1 id="sec-quick">第一章 · 快速开始（首次使用）</h1>

    <h2>第一步：设置根目录</h2>
    <ol>
      <li>打开程序后，会看到一个输入框，旁边写着<b>"公司资料根目录"</b>。</li>
      <li>点右边的 <span class="btn">浏览…</span> 按钮，会弹出一个文件夹选择窗口。</li>
      <li>找到「<b>华为云盘下载（金泓公司云盘）</b>」这个文件夹，点一下选中它。</li>
      <li>点 <span class="btn">选择文件夹</span>，回到程序后点 <span class="btn">保存</span>。</li>
      <li>看到弹窗提示"<b>根目录已保存</b>"，就说明设置成功了。</li>
    </ol>
    <div class="note"><b>提示：</b>根目录是所有订单文件夹的"总仓库"。
    程序会自动在根目录下找 <code>1订单/</code> 文件夹，所有订单都会创建在那里。</div>

    <h2>第二步：设置模板文件目录（可选）</h2>
    <ol>
      <li>点击<b>"模板文件目录"</b>旁边的 <span class="btn">浏览…</span> 按钮。</li>
      <li>选择存放模板文件（CI、PL、托书、采购合同等）的文件夹。</li>
      <li>点 <span class="btn">保存</span> 即可。</li>
    </ol>
    <div class="tip">如果你没有模板文件，这一步可以跳过，程序照样能用，
    只是不会自动复制模板文件而已。</div>

    <h2>第三步：导入业务员和客户</h2>
    <ol>
      <li>点首页的 <span class="btn">🔍 扫描导入业务员</span> 按钮。</li>
      <li>程序会自动读取 <code>1订单/</code> 文件夹里的所有子文件夹，
          并弹出一个勾选窗口。</li>
      <li>把<b>属于业务员</b>的文件夹打勾 ✓（例如 张莹莹、解小康、冷斌捷）。</li>
      <li>不是业务员的<b>不要勾</b>（例如"船级证-金山IBC"这种资料文件夹）。</li>
      <li>如果有像「湖北」这样的<b>分公司</b>文件夹，点开它，把里面的
          业务员（文天堂、张子航）打勾。</li>
      <li>勾选完成后点 <span class="btn">确认导入</span>。</li>
    </ol>
    <div class="tip">导入成功后，以后创建订单时就可以直接从下拉框里选业务员和客户了，
    不用再手动输入。</div>
    """

    single = """
    <h1 id="sec-single">第二章 · 创建订单文件夹（最常用）</h1>

    <ol>
      <li>点首页的 <span class="btn">📝 单笔创建</span> 按钮。</li>
      <li>在<b>上方身份与模板选择</b>区依次选：
        <ul>
          <li><b>业务员</b>（下拉框）</li>
          <li><b>客户</b>（会根据业务员自动列出对应客户）</li>
          <li><b>订单类型</b>：外贸 / 内贸</li>
          <li>这时<b>模板</b>下拉框会自动匹配好，一般不用改</li>
          <li><b>产品类别</b>：戊二醛 / 其他产品</li>
        </ul>
      </li>
      <li>在<b>下方订单信息</b>区填写：
        <ul>
          <li><b>订单号</b>：必填（例如 <code>XS-GAP2604018NH</code>）</li>
          <li><b>客户名称</b>：会根据上方选择自动填好</li>
          <li><b>产品信息</b>、<b>客户PO号</b>：选填</li>
        </ul>
      </li>
      <li>如果这个订单<b>需要商检</b>，勾选"需要商检资料"；不需要就不用管。
          （只有外贸订单才显示这个选项）</li>
      <li>点右下角蓝色的 <span class="btn">下一步：扫描并预览 →</span>。</li>
      <li>程序会弹出预览窗口，用三种颜色告诉你接下来的操作：
        <table>
          <tr><th>颜色</th><th>含义</th></tr>
          <tr><td style="color:#4CAF50;"><b>■ 绿色</b></td><td>文件夹已经存在，<b>不会重复创建</b></td></tr>
          <tr><td style="color:#2196F3;"><b>■ 蓝色</b></td><td>文件夹还没有，程序会<b>帮你新建</b></td></tr>
          <tr><td style="color:#9E9E9E;"><b>■ 灰色</b></td><td>你自己建的、不在模板里的文件夹，<b>程序不会碰</b></td></tr>
        </table>
      </li>
      <li>确认无误后，点 <span class="btn">确认创建</span>。</li>
      <li>完成！会弹窗告诉你创建了多少个文件夹、复制了多少个模板文件。
          可以点 <span class="btn">打开订单文件夹</span> 直接跳转过去。</li>
    </ol>

    <div class="note"><b>重要提示：</b>
    如果你之前已经手动创建过这个订单的部分文件夹，程序<b>只会补建缺少的部分</b>，
    不会覆盖或删除已有内容。请放心使用。</div>

    <h3>目标路径是如何构造的？</h3>
    <p>程序会按以下规则拼出订单文件夹的完整路径：</p>
    <pre>&lt;根目录&gt;/1订单/&lt;业务员&gt;/[&lt;中间层&gt;/]&lt;客户名&gt;/&lt;订单号&gt;/</pre>
    <p>举例：</p>
    <ul>
      <li>张莹莹 + LLC KEMIKLKRAFT + XS-001
          → <code>根目录/1订单/张莹莹/LLC KEMIKLKRAFT/XS-001/</code></li>
      <li>文天堂（湖北分公司）+ 客户A + XS-002
          → <code>根目录/1订单/湖北/文天堂/客户A/XS-002/</code></li>
      <li>解小康（中间层"进行中订单"）+ BASF + XS-003
          → <code>根目录/1订单/解小康/进行中订单/BASF/XS-003/</code></li>
    </ul>
    """

    batch = """
    <h1 id="sec-batch">第三章 · 批量导入（一次创建多个订单）</h1>

    <ol>
      <li>点首页的 <span class="btn">📦 批量导入</span> 按钮。</li>
      <li>点 <span class="btn">下载 Excel 模板</span>，保存一个 Excel 文件到电脑上。</li>
      <li>用 Excel 打开这个模板文件，按表头填写每一行（<b>一行就是一笔订单</b>）：
        <table>
          <tr><th>列名</th><th>说明</th></tr>
          <tr><td>订单类型</td><td>外贸 / 内贸</td></tr>
          <tr><td>订单号</td><td>例如 XS-GAP2604018NH</td></tr>
          <tr><td>客户名称</td><td>客户全称</td></tr>
          <tr><td>产品信息</td><td>选填</td></tr>
          <tr><td>产品类别</td><td>戊二醛 / 其他产品</td></tr>
          <tr><td>是否需要商检</td><td>是 / 否</td></tr>
          <tr><td>业务员</td><td>可选。不填时将使用页面顶部的业务员</td></tr>
        </table>
      </li>
      <li>保存 Excel，回到程序点 <span class="btn">导入 Excel</span>，选择刚保存的文件。</li>
      <li>程序会把所有订单显示在列表里，<b>检查一遍</b>有没有填错的。</li>
      <li>确认无误后，点 <span class="btn">确认批量创建</span>，程序一次性帮你
          创建所有订单的文件夹。</li>
    </ol>

    <div class="tip">批量创建时，每一笔订单的路径仍然按"业务员 / 客户 / 订单号"
    来拼接，保证与单笔创建完全一致。</div>
    """

    templates = """
    <h1 id="sec-templates">第四章 · 模板管理</h1>

    <p>这个功能用来查看和管理文件夹模板。程序内置了
       <b>外贸</b> 和 <b>内贸</b> 两套标准模板。</p>

    <h3>查看模板</h3>
    <ol>
      <li>点首页 <span class="btn">🗂 模板管理</span> 按钮。</li>
      <li>左边列出所有模板，点任意一个，右边显示该模板的文件夹结构树。</li>
    </ol>

    <h3>另存为个人模板</h3>
    <p>如果你想在标准模板基础上做些修改（例如加一个子文件夹），可以编辑后点
      <span class="btn">另存为业务员个人模板</span>。</p>

    <h3>另存为客户专属模板</h3>
    <p>如果某个客户的订单结构比较特殊，可以编辑后点
      <span class="btn">另存为客户专属模板</span>。下次选到这个客户时，
      程序会<b>自动</b>使用这个专属模板。</p>

    <div class="warn"><b>注意：</b>公司标准模板<b>不能删除</b>，只能在其基础上另存新模板。</div>
    """

    history = """
    <h1 id="sec-history">第五章 · 历史记录</h1>

    <ol>
      <li>点首页 <span class="btn">🕘 历史记录</span> 按钮。</li>
      <li>会显示你之前所有的操作记录，包括：
        <ul>
          <li>创建时间</li>
          <li>业务员、客户、订单号、订单类型</li>
          <li>创建结果（新建几个、跳过几个、复制了几个模板文件）</li>
          <li>订单文件夹的完整路径</li>
        </ul>
      </li>
      <li>可以在搜索框里输入订单号或客户名，快速找到某条记录。</li>
    </ol>
    """

    naming = """
    <h1 id="sec-naming">第六章 · 命名变量说明</h1>

    <p>在「模板管理」中编辑文件名时，可以使用以下<b>占位符</b>，
    程序在创建时会自动替换成实际内容：</p>

    <table>
      <tr><th>占位符</th><th>含义</th><th>示例</th></tr>
      <tr><td><code>&lt;订单号&gt;</code></td><td>你填写的订单号</td><td>XS-GAP2604018NH</td></tr>
      <tr><td><code>&lt;客户名称&gt;</code></td><td>你选择的客户名称</td><td>LLC KEMIKLKRAFT</td></tr>
      <tr><td><code>&lt;客户PO号&gt;</code></td><td>客户的采购单号（如有填）</td><td>PO-2026-001</td></tr>
      <tr><td><code>&lt;产品信息&gt;</code></td><td>产品信息（如有填）</td><td>戊二醛 200KG</td></tr>
      <tr><td><code>&lt;业务员&gt;</code></td><td>当前选择的业务员姓名</td><td>张莹莹</td></tr>
      <tr><td><code>&lt;日期&gt;</code></td><td>创建当天的日期（YYYYMMDD）</td><td>20260419</td></tr>
    </table>

    <p>例如模板写 <code>CI-&lt;订单号&gt;.xlsx</code>，实际创建时会变成
    <code>CI-XS-GAP2604018NH.xlsx</code>。</p>

    <div class="tip">模板中还有一个特殊的 <code>[产地]</code> 标记，会根据
    "产品类别"自动替换：<br/>
    &nbsp;&nbsp;• 戊二醛 &rarr; 宁夏<br/>
    &nbsp;&nbsp;• 其他产品 &rarr; 湖北天鹅</div>
    """

    faq = """
    <h1 id="sec-faq">第七章 · 常见问题</h1>

    <h3>Q：模板下拉框是空的怎么办？</h3>
    <p>A：检查左边的"订单类型"是不是选对了。外贸和内贸用的是不同的模板，
       切换订单类型后模板会自动更新。</p>

    <h3>Q：为什么业务员下拉框里没有人？</h3>
    <p>A：首次使用需要先导入业务员。回到首页点
       <span class="btn">扫描导入业务员</span>，按提示操作即可。
       也可以在创建订单页面点业务员旁边的小蓝色 <span class="btn">+</span>
       按钮手动添加。</p>

    <h3>Q：创建出来的文件夹位置不对怎么办？</h3>
    <p>A：在预览界面底部有"目标路径"的显示，可以点
       <span class="btn">修改…</span> 按钮手动调整。</p>

    <h3>Q：程序打不开怎么办？</h3>
    <p>A：确保电脑上已经安装了 Python。如果没有，请联系 IT 同事安装。
       一键打包版本（<code>一键打包.bat</code>）可以直接双击运行无需 Python。</p>

    <h3>Q：想给同事用这个程序，要怎么做？</h3>
    <p>A：把整个程序文件夹发给同事就行。同事打开后第一次需要设置自己的
       根目录和导入业务员，之后就可以正常使用了。</p>

    <h3>Q：已经创建过的订单，再跑一遍会怎样？</h3>
    <p>A：程序会自动识别已存在的文件夹（显示为绿色），<b>只补建缺失的</b>，
       不会覆盖或删除已有内容。非常安全。</p>

    <h3>Q：手动在订单文件夹下建了其它文件夹会被删除吗？</h3>
    <p>A：<b>绝对不会。</b>不在模板里的文件夹（灰色显示）程序完全不会碰它。</p>
    """

    parts = [css, quick, single, batch, templates, history, naming, faq]
    return "<html><body>" + "\n".join(parts) + "</body></html>"


class HelpPage(QWidget):
    """使用帮助页"""

    request_back = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 14, 20, 14)
        root.setSpacing(10)

        # 顶部栏
        top = QHBoxLayout()
        btn_back = QPushButton("← 返回首页")
        btn_back.setObjectName("SecondaryButton")
        btn_back.clicked.connect(self.request_back.emit)
        top.addWidget(btn_back)
        title = QLabel("使用帮助")
        title.setObjectName("TitleLabel")
        top.addWidget(title)
        top.addStretch(1)
        root.addLayout(top)

        # 章节导航
        nav = QHBoxLayout()
        nav.setSpacing(6)
        nav.addWidget(QLabel("快速跳转："))
        for anchor, label in SECTIONS:
            b = QPushButton(label)
            b.setObjectName("SecondaryButton")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _=False, a=anchor: self._goto_anchor(a))
            nav.addWidget(b)
        nav.addStretch(1)
        root.addLayout(nav)

        # 帮助内容
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.setHtml(_build_help_html())
        root.addWidget(self.browser, 1)

    def refresh(self):
        """由主窗口统一调用；本页无状态无需特殊刷新。"""
        self.browser.verticalScrollBar().setValue(0)

    def _goto_anchor(self, anchor: str):
        """跳到锚点（QTextBrowser 支持 scrollToAnchor）"""
        self.browser.scrollToAnchor(anchor)
