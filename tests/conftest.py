# -*- coding: utf-8 -*-
"""pytest 配置：

``tests/test_core.py`` 和 ``tests/test_gui_flow.py`` 是独立的脚本式测试
（通过 ``python tests/test_core.py`` 直接运行），内部有 ``main()`` 入口，
其中以 ``test_`` 开头的函数并非 pytest 风格测试，不接受 pytest fixture。
为避免 pytest 误把它们当作测试来"收集"，在此集中忽略。
"""

collect_ignore = ["test_core.py", "test_gui_flow.py"]
