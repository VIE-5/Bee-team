# -*- coding: utf-8 -*-
"""土蚝小院素材定量分析：测量 Logo 实际色值 + 三张 Moodboard 主色分布
输出：analyze_result.txt（同目录）
"""
from collections import Counter
from PIL import Image

PATHS = {
    "LOGO": r"E:\唐V-work\土蚝小院\土蚝\LOGO定\task-mu6sp8rv3w83z.png",
    "MOODBOARD-01-色彩": r"C:\Users\27612\.workbuddy\clipboard-images\clipboard-2026-09-19T01-29-59-052Z-4e615174.jpg",
    "MOODBOARD-05-图形": r"C:\Users\27612\.workbuddy\clipboard-images\clipboard-2026-09-19T01-29-59-055Z-40e1e57e.jpg",
}

OUT = []
def w(s=""):
    OUT.append(str(s))

def hexs(c):
    return "#%02X%02X%02X" % c

for key, p in PATHS.items():
    im = Image.open(p)
    w("=" * 52)
    w(f"[{key}] {im.size} mode={im.mode}")
    rgb = im.convert("RGB")
    q = rgb.quantize(colors=16, method=Image.MEDIANCUT).convert("RGB")
    cnt = Counter(q.getdata())
    total = sum(cnt.values())
    for col, n in cnt.most_common(16):
        w(f"   {hexs(col)}  {col}  {n * 100.0 / total:6.2f}%")
    if key == "LOGO":
        # 深色像素（笔触/图形）平均色
        dk = [px for px in rgb.getdata() if 0.299*px[0]+0.587*px[1]+0.114*px[2] < 70]
        if dk:
            avg = tuple(sum(c[i] for c in dk)//len(dk) for i in range(3))
            w(f"   >> 深色笔触平均色 {hexs(avg)}  {avg}  占比 {len(dk)*100.0/total:.2f}%")
        # 红色印章像素
        rd = [px for px in rgb.getdata() if px[0] > 110 and px[0]-px[1] > 45 and px[0]-px[2] > 45]
        if rd:
            avg = tuple(sum(c[i] for c in rd)//len(rd) for i in range(3))
            w(f"   >> 朱砂印章平均色 {hexs(avg)}  {avg}  占比 {len(rd)*100.0/total:.2f}%")
        # 最饱和的红色单像素
        rd.sort(key=lambda c: c[0]-(c[1]+c[2])/2, reverse=True)
        w(f"   >> 最饱和红像素 {hexs(rd[0])} {rd[0]}")
        # 背景色（四角取样）
        W, H = rgb.size
        corners = [rgb.getpixel(p2) for p2 in [(2,2),(W-3,2),(2,H-3),(W-3,H-3)]]
        w(f"   >> 四角背景 {[hexs(c) for c in corners]}")

with open(r"D:\WORK——Vie\沃克巴蒂\蜂群\蜂王\03-任务档案\20260919-土蚝小院品牌视觉系统\01-素材分析\analyze_result.txt",
          "w", encoding="utf-8") as f:
    f.write("\n".join(OUT))
print("OK")
