# -*- coding: utf-8 -*-
"""
整帧合成拍立得相框 PNG（参考 1508435619f7d7bbaca2dbeba32a7917.jpg 的构图）：
- 程序绘制白色拍立得外框（圆角 + 窗口挖空 + 烘焙式外阴影/内边缘）
- 天使翅膀 / 海星从参考图抠出后按原始坐标贴回（与参考图构图一致）
- 输出单张 self-contained 的 about-frame.png，人物照片从窗口透出
"""
from PIL import Image, ImageDraw, ImageFilter

SRC = r'D:/xwechat_files/wxid_yb4okrtlr3u022_8201/temp/RWTemp/2026-10/1508435619f7d7bbaca2dbeba32a7917.jpg'
OUT = r'D:/personal-site/public/about-frame.png'

CW, CH = 1080, 1210  # 画布 = 参考图尺寸，装饰按源坐标直接贴

# 源图坐标系里的几何（依据网格测量）
FRAME = (315, 180, 772, 946)   # 相框外沿
WINDOW = (363, 222, 735, 785)  # 窗口（挖空区，人物透出）

# ---------- 抠装饰 ----------
def key_white(img, boost=2.6, floor=28):
    px = img.load()
    w, h = img.size
    out = Image.new('RGBA', (w, h))
    po = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            mn = min(r, g, b)
            a = int(min(255, (255 - mn) * boost))
            if a < floor:
                po[x, y] = (0, 0, 0, 0)
                continue
            af = a / 255.0
            fr = max(0, min(255, int((r - 255 * (1 - af)) / af)))
            fg = max(0, min(255, int((g - 255 * (1 - af)) / af)))
            fb = max(0, min(255, int((b - 255 * (1 - af)) / af)))
            po[x, y] = (fr, fg, fb, a)
    return out

ref = Image.open(SRC).convert('RGB')
wing = key_white(ref.crop((140, 85, 510, 268)))    # 贴回 (140, 85)
star = key_white(ref.crop((695, 818, 960, 1015)))  # 贴回 (695, 818)

# --- 贴回前清理：抹掉装饰层里烘焙的参考图框线残影 ---
def wipe(img, rect, ox, oy):
    x0, y0, x1, y1 = rect
    px = img.load()
    for y in range(max(0, y0 - oy), min(img.height, y1 - oy)):
        for x in range(max(0, x0 - ox), min(img.width, x1 - ox)):
            px[x, y] = (0, 0, 0, 0)

# 翅膀层：原参考图窗口左上角边线（源 x>352, y>200）+ 左下残点
wipe(wing, (352, 200, 510, 268), 140, 85)
wipe(wing, (310, 232, 360, 268), 140, 85)
# 海星层：原参考图相框右边缘线在星体上下的残段
wipe(star, (738, 818, 782, 852), 695, 818)
wipe(star, (738, 890, 782, 928), 695, 818)
wipe(star, (695, 986, 782, 1015), 695, 818)

# ---------- 画布 + 阴影 ----------
canvas = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))

# 外阴影：轮廓模糊（烘焙，CSS 无需 drop-shadow）
sil = Image.new('L', (CW, CH), 0)
d = ImageDraw.Draw(sil)
d.rounded_rectangle(FRAME, radius=16, fill=110)
shadow = sil.filter(ImageFilter.GaussianBlur(18))
black = Image.new('RGBA', (CW, CH), (70, 78, 66, 255))
canvas.paste(black, (6, 14), shadow)  # 轻微下移的柔和投影

# ---------- 相框主体（微渐变白） ----------
body = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
bd = ImageDraw.Draw(body)
x0, y0, x1, y1 = FRAME
top = (253, 252, 249)
bot = (246, 245, 240)
for y in range(y0, y1):
    t = (y - y0) / max(1, (y1 - y0))
    c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)) + (255,)
    bd.line([(x0, y), (x1, y)], fill=c)
mask = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(mask).rounded_rectangle(FRAME, radius=16, fill=255)
canvas.paste(body, (0, 0), mask)

# ---------- 窗口挖空 + 内边缘 ----------
hole = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(hole).rounded_rectangle(WINDOW, radius=8, fill=255)
# 挖空：alpha 减去 hole
r, g, b, a = canvas.split()
from PIL import ImageChops
a = ImageChops.subtract(a, hole)
canvas.putalpha(a)

# 窗口内边缘：细描边 + 顶部内陷阴影，增加「厚度」感
edge = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
ed = ImageDraw.Draw(edge)
ed.rounded_rectangle(WINDOW, radius=8, outline=(150, 152, 142, 120), width=2)
top_inner = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
td = ImageDraw.Draw(top_inner)
td.rounded_rectangle((WINDOW[0], WINDOW[1], WINDOW[2], WINDOW[1] + 22), radius=8,
                     fill=(120, 128, 112, 60))
top_inner = top_inner.filter(ImageFilter.GaussianBlur(6))
edge = Image.alpha_composite(edge, top_inner)
# 内边缘只画在窗口四周（不盖住挖空区外面的框体也无妨，贴着边即可）
canvas = Image.alpha_composite(canvas, edge)

# ---------- 贴装饰（原始坐标） ----------
canvas.alpha_composite(wing, (140, 85))
canvas.alpha_composite(star, (695, 818))

# ---------- 裁切 + 输出 ----------
bbox = canvas.getbbox()
pad = 20
box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
       min(CW, bbox[2] + pad), min(CH, bbox[3] + pad))
final = canvas.crop(box)
final.save(OUT)
print('frame:', final.size, 'crop box:', box)

# 窗口在成品图里的位置（供 CSS 百分比定位人物）
tx, ty = box[0], box[1]
w, h = final.size
wx0 = (WINDOW[0] - tx) / w * 100
wy0 = (WINDOW[1] - ty) / h * 100
wx1 = (WINDOW[2] - tx) / w * 100
wy1 = (WINDOW[3] - ty) / h * 100
print(f'window css: left {wx0:.2f}%  top {wy0:.2f}%  width {wx1-wx0:.2f}%  height {wy1-wy0:.2f}%')
print(f'window ratio: {(WINDOW[2]-WINDOW[0])} x {(WINDOW[3]-WINDOW[1])}')

# 预览：把人物塞进窗口看整体效果
person = Image.open(r'D:/personal-site/public/about-photo.png').convert('RGBA')
prev = canvas.copy()
ww, wh = WINDOW[2] - WINDOW[0], WINDOW[3] - WINDOW[1]
# 窗口底衬（雾白渐变）
wbg = Image.new('RGBA', (ww, wh), 0)
wd = ImageDraw.Draw(wbg)
for y in range(wh):
    t = y / wh
    c = (int(246 + 6 * t), int(250 + 3 * t), int(243 + 4 * t), 255)
    wd.line([(0, y), (ww, y)], fill=c)
pm = person.copy()
scale = max(ww / pm.width, wh / pm.height)
pm = pm.resize((int(pm.width * scale), int(pm.height * scale)), Image.LANCZOS)
px0 = (pm.width - ww) // 2
pm = pm.crop((px0, 0, px0 + ww, min(pm.height, wh)))
wbg.alpha_composite(pm, (0, 0))
hole_full = Image.new('L', (CW, CH), 0)
ImageDraw.Draw(hole_full).rounded_rectangle(WINDOW, radius=8, fill=255)
prev.paste(wbg, (WINDOW[0], WINDOW[1]), hole_full.crop((WINDOW[0], WINDOW[1], WINDOW[2], WINDOW[3])))
# 淡绿页面底
pv = Image.new('RGBA', (CW, CH), (222, 232, 219, 255))
pv.alpha_composite(prev)
pv.crop((60, 20, 1020, 1120)).resize((720, 825), Image.LANCZOS).convert('RGB').save(
    r'D:/personal-site/scripts/_preview_frame.png')
print('preview saved')
