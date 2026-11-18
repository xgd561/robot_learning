# -*- coding: utf-8 -*-
# ============================================================
#  第2周 · 屏幕与循环（麦轮车）—— 课堂代码备查 + 趣味加餐
#  知识点：变量、str() 数字变文字、for 循环、time.sleep、TTS 语音
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100，太小基本听不见

def 安全收尾():
    # 每个场景跑完都叫它一声：停车 + 关灯 + 擦屏幕
    ug.stop_chassis()
    ug.turn_off_lights()
    ug.screen_clear()

# 💡 本周最容易翻车的点：循环里忘了 time.sleep —— 电脑发命令快如闪电，
#    5 个数 0.1 秒内全发完，屏幕只留下最后一个 1、声音糊成一团。

# ============ 课堂代码复现 ============

def 场景1_变量初体验_显示一个数字():
    # 跑这个你会看到：屏幕跳出红色数字 3，女声同时念「三」——变量就是这么用的
    n = 3                                # 建一个叫 n 的盒子，里面装数字 3
    ug.screen_print_text(str(n), 3)      # str() 把数字 3 变成文字 "3"，屏幕才认
    ug.play_audio_tts(str(n), 0)         # 女声念出来（0 女声 / 1 男声）
    time.sleep(2)
    安全收尾()

def 场景2_倒计时_只数数不走路():
    # 跑这个你会看到：屏幕 5→1 红字跳动、女声跟着念，最后绿字 GO + 喊「出发」
    for n in range(5, 0, -1):                # 从 5 数到 1，每次 -1
        ug.screen_print_text(str(n), 3)      # str() 把数字变文字，屏幕才认；3 = 红
        ug.play_audio_tts(str(n), 0)         # 0 = 女声，1 = 男声
        time.sleep(1)                        # ★ 等它数完一个再数下一个
    ug.screen_print_text("GO!", 6)           # 6 = 绿
    ug.play_audio_tts("出发", 0, True)       # True = 等它说完再往下走，比死等 1 秒准
    time.sleep(1)
    安全收尾()

def 场景3_课堂项目_倒计时火箭():
    # 跑这个你会看到：每数一个数往前走 1 秒，数完绿字 GO + 喊「出发」，稳稳停下
    # ⚠️ 运动！要清出一条 2 米的直路，前面别放鞋和充电线
    for n in range(5, 0, -1):
        ug.screen_print_text(str(n), 3)                 # ① 屏幕显示数字（红）
        ug.play_audio_tts(str(n), 0)                    # ② 女声报数
        ug.mecanum_move_speed_times(0, 30, 1, 0)        # ③ 前进 1 秒自动停（想纯数数就删这行）
        time.sleep(1)                                   # ④ 陪它走完这 1 秒
    ug.screen_print_text("GO!", 6)
    ug.play_audio_tts("出发", 0, True)
    time.sleep(1)                            # 让最后一次「前进 1 秒」走完
    ug.stop_chassis()                        # 停！安全第一
    安全收尾()

# ============ 趣味加餐 ============

def 彩蛋1_音阶歌():
    # 跑这个你会看到：机器人从低音 do 一路弹到高音 do，屏幕跟着显示音符名
    音阶 = ["C5", "D5", "E5", "F5", "G5", "A5", "B5", "C6"]   # 一排音符（列表，第5周细讲）
    for 音符 in 音阶:
        ug.play_tone(音符, 3)                # 弹这个音符，3 = 弹 1 拍
        ug.screen_print_text(音符, 5)        # 5 = 黄
        time.sleep(0.5)                      # 等半秒再弹下一个，不然糊成一团
    time.sleep(1)
    安全收尾()

def 彩蛋2_跑马灯():
    # 跑这个你会看到：四条灯带像流水一样 0→1→2→3 依次亮绿光，跑两轮
    for 轮数 in range(2):                    # 整套动作来两遍
        for 灯 in [0, 1, 2, 3]:              # 0 顶 / 1 左 / 2 右 / 3 底
            ug.turn_off_lights()             # 先全灭，才像「流水」往前跑
            ug.show_light_rgb([灯], 0, 255, 0)   # 只点亮这一条，绿色
            time.sleep(0.3)
    安全收尾()                               # 收尾里的 turn_off_lights() 把灯全关

def 彩蛋3_变量当油门():
    # 跑这个你会看到：小车从慢到快分 4 档加速，屏幕报出每档速度，最后急停
    for 速度 in range(10, 50, 10):           # 速度依次是 10, 20, 30, 40
        ug.screen_print_text("速度" + str(速度), 8)     # 8 = 蓝
        ug.mecanum_move_speed_times(0, 速度, 1, 0)      # 这一档走 1 秒自动停
        time.sleep(1)                        # 陪它走完这一档
    ug.stop_chassis()                        # 最后一下急停
    安全收尾()

# 📌 翻车速查（记住：机器人没反应 = 先查参数，不是机器人坏了）
#   · 屏幕只停在最后一个数、声音糊成一团 → 循环里忘了 time.sleep(1)（或缩进跑错了行）；
#   · 看到 invalid value of color → 颜色写成了 "FFFF0000"，要 0~8 的整数（红3 绿6 蓝8 黄5）；
#   · 看到 invalid value of voice_type, expected 0 or 1 → 声音那格只能 0 女声 / 1 男声；
#   · 数字参数带引号（如速度 "40"）会真的抛红字中断程序——去掉引号就好；
#   · 💡 进阶：把 screen_print_text 换成 screen_print_text_newline，5 个数会一行一行
#     留在屏幕上（最后用 screen_clear() 擦掉）。
#
# 🃏 本周速记卡（截图保存）
#   变量：n = 5（贴标签的盒子）        数字变文字：str(n)
#   倒计时循环：for n in range(5, 0, -1):    # 5,4,3,2,1，每次 -1
#   屏幕红字：ug.screen_print_text(str(n), 3)   # 颜色 0~8 整数
#   女声/男声：ug.play_audio_tts("文字", 0) / ("文字", 1)
#   等它说完再继续：ug.play_audio_tts("出发", 0, True)
#   调音量：ug.set_volume(60)          # 0~100
#   弹音符：ug.play_tone("C5", 3)      # 音符 C5~B5、C6；3 = 1 拍
#   前进 N 秒：ug.mecanum_move_speed_times(0, 30, N, 0)   # 单位 0=秒
#   急停：ug.stop_chassis()
# 🔁 range 三参数：range(开始, 停在哪之前, 步长) —— range(1, 6) 是 1→5 正数（闹钟模式！）
#
# 🧪 改造灵感（调试思维：改一改、跑一跑、看变化）
#   · range(5, 0, -1) 改成 range(10, 0, -1)：数到 10（记得场地要更长）
#   · 颜色 3 全改成 8（蓝）或 1（白）；女声 0 改成男声 1
#   · time.sleep(1) 改成 0.5：节奏变快；删掉前进那行：变成"只数数不走路"
#   · 表情版：加一行 ug.screen_display_emotion("WakeUp")，带着表情数数
#   · 偶数蓝奇数红：循环里加 if n % 2 == 0: 分一下（% 是取余数，第4周细讲）
#
# ============ 想跑哪个，就去掉哪行前面的 # ============
场景1_变量初体验_显示一个数字()  # ← 默认激活：只亮屏+说一句话，最安全
# 场景2_倒计时_只数数不走路()
# 场景3_课堂项目_倒计时火箭()     # 运动！清出直路再跑
# 彩蛋1_音阶歌()
# 彩蛋2_跑马灯()
# 彩蛋3_变量当油门()            # 运动！
