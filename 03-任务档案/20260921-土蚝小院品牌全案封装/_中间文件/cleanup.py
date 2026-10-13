# -*- coding: utf-8 -*-
"""清理渲染临时页目录 _pages/。"""
import os
import shutil

d = r'D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260921-土蚝小院品牌全案封装\01-工蜂产出\_pages'
if os.path.isdir(d):
    try:
        shutil.rmtree(d)
        print('removed _pages')
    except OSError as e:
        print('failed:', e)
else:
    print('_pages not present')
