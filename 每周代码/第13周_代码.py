# -*- coding: utf-8 -*-
# ============================================================
#  第13周 · 蜘蛛全向巡逻 + 传感器判断（蜘蛛形态 spider_）
#  知识点：函数封装 def / 方向常量 / TOF 测距防呆 / if-elif-else / try-finally
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量范围 0~100，写 3 几乎听不见

def 安全收尾():
    ug.stop_chassis()
    ug.turn_off_lights()
    ug.screen_clear()

# 蜘蛛方向常量：★ 同一个 2/3，在 move 里是"横移"、在 turn 里才是"转弯"！
前进 = 0
后退 = 1
左移 = 2          # move 里的 2 = 向左横移（螃蟹步）
右移 = 3          # move 里的 3 = 向右横移
左转 = 2          # turn 里的 2 = 原地左转
右转 = 3          # turn 里的 3 = 原地右转

# ============ 课堂代码复现 ============

def 场景1_全向移动按钮():
    # 跑这个你会看到：蜘蛛 前进→横着左移→横着右移→后退→原地右转，最后摆回标准站姿
    def 走(方向, 秒数, 速度=15):          # 蜘蛛走的上限 = 25
        ug.spider_move_speed(方向, 速度)
        time.sleep(秒数)                   # Python 不会替机器人等，得自己 sleep
        ug.stop_chassis()
    def 转(方向, 秒数, 速度=40):          # 蜘蛛转的上限 = 60
        ug.spider_turn_speed(方向, 速度)
        time.sleep(秒数)
        ug.stop_chassis()                  # 转弯必须停，否则转圈圈
    ug.spider_restory()                    # 先把四条腿摆回标准站姿
    ug.screen_print_text("蜘蛛就绪", 1)    # 屏幕颜色是整数：1 = 白
    time.sleep(1)
    ug.screen_clear()
    走(前进, 1)      # ① 往前
    走(左移, 1)      # ② 螃蟹步向左（蜘蛛看家本领）
    走(右移, 1)      # ③ 螃蟹步向右
    走(后退, 1)      # ④ 倒退
    转(右转, 1)      # ⑤ 原地右转
    安全收尾()
    ug.spider_restory()

def 场景2_巡逻遇障停():
    # 跑这个你会看到：蜘蛛绿灯巡逻前进；把纸箱推到30cm内，它红灯一闪立刻停下，不撞
    ug.spider_restory()
    安全距离 = 30
    try:
        for 一轮 in range(100):              # 手册里是 while True，这里跑约10秒自动停
            距离 = ug.read_distance_data(1)  # 单位厘米（带小数）
            print("距离 =", 距离)
            if 距离 == -1 or 距离 == 0:      # 读不到 → 先停，最保守（第4周那招）
                ug.stop_chassis()
                ug.screen_print_text("?", 5)             # 5 = 黄
            elif 距离 < 安全距离:            # 真的近了 → 停 + 闪红
                ug.stop_chassis()
                ug.screen_print_text("停!", 3)           # 3 = 红
                ug.show_light_rgb_effect(255, 0, 0, 3)   # 一行闪红灯：效果 3 = 闪烁
            else:                            # 前方安全 → 前进巡逻
                ug.spider_move_speed(0, 15)  # ★ 不是 40！蜘蛛上限 25
                ug.screen_print_text("巡逻", 6)          # 6 = 绿
                ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)
            time.sleep(0.1)                  # 一秒看 10 次够了，别省这行
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.spider_restory()

def 场景3_巡逻遇障避开():
    # 跑这个你会看到：蜘蛛绿灯巡逻；障碍进到30cm内它闪红灯、喊一声、自己右转90度绕开再继续巡逻
    ug.spider_restory()
    安全距离 = 30
    def 避开():                                      # 把"停 + 转向绕开"打包成一个按钮
        ug.stop_chassis()                            # ① 先停，安全第1
        ug.screen_print_text("避障", 3)
        ug.show_light_rgb_effect(255, 0, 0, 3)
        ug.play_audio_tts("前方有障碍，我绕一下", 0)  # 0 = 女声
        ug.spider_turn_speed_times(3, 40, 90, 2)     # ② 右转90度自己停（转≤60；unit 2=度）
        time.sleep(2.5)                              # ★ 它自己会停，但 Python 不等 → 陪着等
        ug.spider_move_speed_times(0, 12, 1, 0)      # ③ 前进1秒脱开（走≤25；unit 0=秒）
        time.sleep(1.2)
        ug.stop_chassis()                            # ④ 再确认停一次
        ug.turn_off_lights()
    try:
        for 一轮 in range(100):
            距离 = ug.read_distance_data(1)
            if 距离 != -1 and 距离 != 0 and 距离 < 安全距离:   # 三道锁：只有真读到近东西才算障碍
                避开()                               # 遇障 → 转向绕开（不再傻站）
            else:
                ug.spider_move_speed(0, 15)          # 平时前进巡逻（上限 25）
                ug.screen_print_text("巡逻中", 6)
                ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.spider_restory()

# ============ 趣味加餐 ============

def 彩蛋1_蜘蛛迪斯科():
    # 跑这个你会看到：蜘蛛原地转一整圈、左右横移蹦迪，紫→绿呼吸灯跟着节奏闪
    ug.spider_restory()
    ug.screen_display_emotion("Smile")
    ug.show_light_rgb_effect(255, 0, 255, 2)         # 紫色呼吸灯（效果 2 = 呼吸）
    ug.play_audio_tts("迪斯科时间到", 0)
    time.sleep(2)
    ug.spider_turn_speed_times(3, 60, 360, 2)        # 原地转一整圈（转 0~60，unit 2=度）
    time.sleep(360 / 60 + 0.3)                       # 360度 ÷ 60度每秒 ≈ 6 秒
    for 拍 in range(2):                              # 左右横移交替（螃蟹步蹦迪）
        ug.spider_move_speed_times(2, 15, 1, 0)      # 向左移 1 秒（走 0~25）
        time.sleep(1 + 0.3)
        ug.spider_move_speed_times(3, 15, 1, 0)      # 向右移 1 秒
        time.sleep(1 + 0.3)
    ug.show_light_rgb_effect(0, 255, 0, 2)           # 换绿色呼吸灯收尾
    time.sleep(1)
    安全收尾()
    ug.spider_restory()

def 彩蛋2_慢慢逼近报警():
    # 跑这个你会看到：你慢慢走近蜘蛛，灯从绿→黄→红，它一步步更着急地喊你后退（约10秒自动结束）
    上次状态 = ""
    ug.spider_restory()
    ug.screen_print_text("来靠近我", 5)
    try:
        for 一轮 in range(100):                      # 有界循环：跑 10 秒自动结束
            距离 = ug.read_distance_data(1)
            if 距离 == -1 or 距离 == 0:
                状态 = "没人"                        # TOF 最远 150cm，读不到 = 前方空空的
            elif 距离 > 60:
                状态 = "安全"
            elif 距离 > 30:
                状态 = "注意"
            else:
                状态 = "危险"
            if 状态 == "安全":
                ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)
                ug.screen_print_text("安全", 6)
            elif 状态 == "注意":
                ug.show_light_rgb([0, 1, 2, 3], 255, 255, 0)
                ug.screen_print_text("注意哦", 5)
            elif 状态 == "危险":
                ug.show_light_rgb([0, 1, 2, 3], 255, 0, 0)
                ug.screen_print_text("太近啦!", 3)
            else:
                ug.turn_off_lights()
                ug.screen_print_text("前方没人", 1)
            if 状态 != 上次状态:                     # 状态变了才喊，不会一直刷屏
                if 状态 == "安全":
                    ug.play_audio_tts("你好呀，欢迎参观", 0)
                elif 状态 == "注意":
                    ug.play_audio_tts("有点近了哦", 0)
                elif 状态 == "危险":
                    ug.play_audio_tts("太近啦，快后退", 0)
                上次状态 = 状态
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.spider_restory()

# ============ 想跑哪个，就去掉哪行前面的 # ============
场景1_全向移动按钮()      # ← 默认激活：最安全的一个
# 场景2_巡逻遇障停()
# 场景3_巡逻遇障避开()
# 彩蛋1_蜘蛛迪斯科()
# 彩蛋2_慢慢逼近报警()
