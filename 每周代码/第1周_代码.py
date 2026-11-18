# -*- coding: utf-8 -*-
# ============================================================
#  第1周 · 环境搭建与连接（麦轮车）—— 课堂代码备查 + 趣味加餐
#  知识点：连接机器人（IP=门牌号）、屏幕显示（颜色0~8）、time.sleep、急停习惯
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100，60 听得清

def 安全收尾():
    # 每个场景跑完都叫它一声：停车 + 关灯 + 擦屏幕
    ug.stop_chassis()
    ug.turn_off_lights()
    ug.screen_clear()

# 🔢 数字暗号速查（机器人只认数字，先记这三行）
#   ① 方向：前进=0  后退=1  左转=2  右转=3
#   ② 屏幕颜色（必须是 0~8 的整数）：0黑 1白 2紫 3红 4橙 5黄 6绿 7青 8蓝
#   ③ _times 的单位：走 move_* 只认 0=秒 / 1=厘米；转 turn_* 只认 0=秒 / 2=度
#     例：ug.mecanum_move_speed_times(0, 40, 2, 0) = 前进 / 速度40 / 2 秒 / 按秒算
# ⚡ 速度上限（超了会被悄悄压上限，不报错）：麦轮车走 5~80、转 5~280
# ⏱️ 铁律：带 _times 的方法机器人会自己停，但 Python 发完命令就跑下一行——
#     后面必须补 time.sleep，陪它把动作做完！
# 🛑 急停万能：ug.stop_chassis()（不分形态，慌了就跑它）
# 📢 排错顺序：先看编辑器下面有没有 TypeError 提示行 → 再查连接三件套 → 最后才怀疑机器人
# 📚 配套材料：IP 是什么 →《第1周_教案.md》第五节；原版代码 →《第1周_实践手册.md》步骤⑤
# 🔌 开课三件套：uCode Link 托盘常驻 + Chrome/Firefox 开 py.ubtrobot.com + 机器人同 WiFi

# ============ 课堂代码复现 ============

def 场景1_我连上啦_亮屏测试():
    # 跑这个你会看到：机器人屏幕亮出红红的「我连上啦」，2 秒后擦掉（不运动）
    ug.screen_print_text("我连上啦", 3)   # 3 = 红；颜色必须是 0~8 的整数
    time.sleep(2)                         # 留 2 秒让你看清楚
    安全收尾()

def 场景2_屏幕颜色试衣间():
    # 跑这个你会看到：屏幕像换衣服一样轮着显示 红→绿→蓝→黄 四种字
    ug.screen_print_text("我是红色", 3)   # 3 = 红
    time.sleep(2)
    ug.screen_print_text("我是绿色", 6)   # 6 = 绿
    time.sleep(2)
    ug.screen_print_text("我是蓝色", 8)   # 8 = 蓝
    time.sleep(2)
    ug.screen_print_text("我是黄色", 5)   # 5 = 黄
    time.sleep(2)
    安全收尾()

def 场景3_课堂项目_前进2秒():
    # 跑这个你会看到：红字「我连上啦」→ 机器人前进 2 秒自己停下 → 急停保险
    # ⚠️ 运动！先清出一块空地（麦轮车最怕地毯边和桌脚）
    ug.screen_print_text("我连上啦", 3)          # 屏幕红字（颜色 3 = 红）
    ug.mecanum_move_speed_times(0, 40, 2, 0)     # 方向0=前进 / 速度40(5~80) / 2 / 单位0=秒
    time.sleep(2)                                # _times 会自己停，但 Python 不等，要陪它走完
    ug.stop_chassis()                            # 刹车习惯：任何时候慌了就喊它
    安全收尾()

# ============ 趣味加餐 ============

def 彩蛋1_表情动作自我介绍秀():
    # 跑这个你会看到：屏幕换表情、身体做动作，还开口自我介绍，一套连招五连拍
    ug.play_audio_tts("大家好，我是UGOT", 0)     # 0 = 女声
    ug.screen_display_emotion("WakeUp")          # 表情名是字符串（共15个）
    ug.perform_action("WakeUp")                  # 动作名也是字符串
    time.sleep(3)                                # 每个动作之间要等它做完
    ug.screen_display_emotion("Smile")
    ug.perform_action("Love")
    time.sleep(3)
    ug.screen_display_emotion("Proud")
    ug.perform_action("Proud")
    time.sleep(3)
    ug.screen_display_emotion("Ticklish")
    ug.perform_action("Ticklish")
    time.sleep(3)
    ug.screen_display_emotion("Sleep")           # 最后拍：装睡收场
    ug.perform_action("Sleep")
    time.sleep(3)
    安全收尾()

def 彩蛋2_灯带彩虹():
    # 跑这个你会看到：四条灯带各亮一种颜色拼成彩虹，几秒后一起变紫，最后全灭
    # 灯带编号：0 顶 / 1 左 / 2 右 / 3 底；RGB 各 0~255（和屏幕的 0~8 不是一套！）
    ug.show_light_rgb([0], 255, 0, 0)            # 顶灯带 红
    ug.show_light_rgb([1], 0, 255, 0)            # 左灯带 绿
    ug.show_light_rgb([2], 0, 0, 255)            # 右灯带 蓝
    ug.show_light_rgb([3], 255, 255, 0)          # 底灯带 黄
    time.sleep(3)
    ug.show_light_rgb([0, 1, 2, 3], 255, 0, 255) # 四条一起变紫
    time.sleep(3)
    安全收尾()                                   # 里面的 turn_off_lights() 负责关灯

def 彩蛋3_扫描找IP():
    # 跑这个你会看到：编辑器下方打印出同一 WiFi 里所有 UGOT 的名字和 IP
    print("正在扫描同一 WiFi 里的 UGOT，稍等……")
    print(ug.scan_device())                      # 返回 {"机器人名字": "IP"}，忘了 IP 就靠它
    ug.screen_print_text("看电脑屏幕", 5)        # 5 = 黄
    time.sleep(2)
    安全收尾()

# 📌 翻车速查（记住：机器人没反应 = 先查参数，不是机器人坏了）
#   · 看到 print 出 TypeError: 方法名(): invalid value of ...  → 参数取值写错，
#     程序没崩，机器人只是拒绝执行那一条命令；
#   · 屏幕不显示字 → 颜色写成了字符串 "FFFF0000"，要改成 0~8 的整数（红3 绿6 蓝8）；
#   · 只 print 了 invalid value of unit → move_speed_times 第 4 格只能填 0=秒 / 1=厘米；
#   · 一直走不停 → 用了不带 _times 的方法，后面要补 time.sleep + stop_chassis()；
#   · 第一行就报错连不上 → IP 抄错 / 不同 WiFi / uCode Link 没开（右下角托盘看图标）。
#
# ============ 想跑哪个，就去掉哪行前面的 # ============
场景1_我连上啦_亮屏测试()      # ← 默认激活：最安全的亮屏测试（不运动）
# 场景2_屏幕颜色试衣间()
# 场景3_课堂项目_前进2秒()      # 运动！清出空地再跑
# 彩蛋1_表情动作自我介绍秀()
# 彩蛋2_灯带彩虹()
# 彩蛋3_扫描找IP()
