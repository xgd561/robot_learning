# -*- coding: utf-8 -*-
# ============================================================
#  第16周 · 自由综合周 · 收官大作品（形态自选！）
#  知识点：自己出题 / 三关叠加 / 真方法名清单 / 收尾清单
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
#  🎓 ⚠️ 自选形态后，把代码里的运动前缀一换（速度也要照限速表重调！）：
#     麦轮/工程车底盘 mecanum_（走5~80 转5~280，工程车没有 engineer_）
#     变形车 transform_（5~80 / 5~280）   轮足 wheelleg_（5~60 / 5~180）
#     蜘蛛 spider_（0~25 / 0~60，先 spider_restory()）
#     四足狗 dog_（0~25 / 0~20，动作是字符串 dog_perform_action("standing")）
#     平衡车 balance_（5~80 / 5~360，动之前先 balance_start_balancing()）
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量范围 0~100

def 安全收尾():
    ug.stop_chassis()
    ug.turn_off_lights()
    ug.screen_clear()

# ============ 课堂代码复现（手册里的项目骨架） ============

def 场景1_收官项目骨架():
    # 跑这个你会看到：现在只是"空转的骨架"——照 TODO 一格格填空，填完它就是你的毕业作品！
    # ① 先填计划书：形态？主题？至少用哪 2 样本领？（手册步骤①那张表）
    我的速度 = 40            # TODO: 按你的形态限速改（蜘蛛/狗最多 25！轮足最多 60！）
    def 我的动作():
        # TODO 关1：只写"核心动作"，先让它动起来，例如：
        # ug.mecanum_move_speed_times(0, 我的速度, 2, 0)   # 走 2 秒自己停
        # time.sleep(2 + 0.3)                              # 自动停 ≠ Python 等
        pass
    try:
        # TODO 开机动作（按你的形态打开）：蜘蛛 ug.spider_restory() / 狗 ug.dog_perform_action("standing")
        # TODO 需要视觉就加载模型（名字照事实表）：ug.load_models(['gesture'])
        ug.screen_print_text("开工!", 6)
        ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)
        for 一轮 in range(100):                    # 有界循环：先跑 10 秒试试
            # TODO 关2 感知：距离 = ug.read_distance_data(1)   # -1 和 0 = 没读到！
            # TODO 关2 判断：if 距离 != -1 and 距离 != 0 and 距离 < 30:（先保命再干活）
            # TODO 关2 加料：ug.show_light_rgb_effect(255, 0, 0, 3) / ug.play_audio_tts("话", 0)
            # TODO 关3：把"感知→判断→动作"串成你的完整流程
            我的动作()
            time.sleep(0.1)                        # while/for 循环里一定要有 sleep
    except KeyboardInterrupt:
        print("你按了停止，正在收尾")
    finally:
        # ↓ 计划书⑦的收尾清单，一行都别省（用了哪样就打开哪行）
        ug.stop_chassis()
        ug.turn_off_lights()
        ug.screen_clear()
        # ug.release_models(['你加载过的模型名'])
        # ug.mechanical_arms_restory()               # 用了工程车手臂才打开
        # ug.stop_all_servos()                       # 用了舵机/结构件才打开
        # ug.spider_restory()  /  ug.dog_restory()  /  ug.transform_restory()

# ============ 趣味加餐（彩蛋自助餐，跨形态随便挑） ============

def 彩蛋1_狗狗握手会():
    # 跑这个你会看到：四足狗先站稳、屏幕笑眯眯打招呼，然后跟你握个手（四足狗形态专用）
    ug.dog_perform_action("standing")       # 先站稳（动作名是字符串，别写成数字）
    time.sleep(2.5)
    ug.screen_display_emotion("Smile")
    ug.play_audio_tts("你好呀，我们握个手吧", 0)
    time.sleep(2.5)
    ug.dog_perform_action("handshake")      # 握手！
    time.sleep(3.5)
    ug.screen_display_emotion("Love")
    ug.dog_perform_action("standing")       # 站回来
    time.sleep(2)
    安全收尾()
    ug.dog_restory()

def 彩蛋2_谢幕秀():
    # 跑这个你会看到：屏幕表情和身体动作一幕一幕配合演出，最后放一段小音乐谢幕（任何形态都能演）
    幕布 = [("WakeUp", "WakeUp"), ("Smile", "Smile"), ("Doubt", "Doubt"),
            ("Love", "Love"), ("Proud", "Proud")]     # (表情名, 通用动作名) 两套都是字符串
    for 表情, 动作 in 幕布:
        ug.screen_display_emotion(表情)
        ug.perform_action(动作)
        time.sleep(2.5)
    ug.screen_display_emotion("Smile")
    for 音符 in ["C5", "E5", "G5", "C6"]:     # beat 3 = 1 拍（音名 C5~B5、C6）
        ug.play_tone(音符, 3)
        time.sleep(0.5)
    ug.play_audio_tts("谢谢大家，毕业快乐！", 0)
    time.sleep(3)
    安全收尾()

def 彩蛋3_麦轮方块走位():
    # 跑这个你会看到：麦轮车走出一个正方形，每条边换一种灯色（麦轮车形态专用）
    灯色们 = [[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 0]]
    for 边 in range(4):
        ug.screen_print_text("第" + str(边 + 1) + "边", 5)
        灯 = 灯色们[边]
        ug.show_light_rgb([0, 1, 2, 3], 灯[0], 灯[1], 灯[2])
        ug.mecanum_move_speed_times(0, 40, 2, 0)      # 前进 2 秒自动停（走 5~80）
        time.sleep(2 + 0.3)
        ug.mecanum_turn_speed_times(3, 120, 90, 2)    # 右转 90 度自动停（转 5~280）
        time.sleep(90 / 120 + 0.3)
    ug.play_audio_tts("正方形走完啦", 0)
    安全收尾()

def 彩蛋4_空白项目模板():
    # 跑这个你会看到：机器人亮绿灯说"开工"——五个 TODO 填完，它就变成你自己的作品！
    # 填空口诀：初始化 → 循环感知 → 判断 → 动作 → 收尾
    # ① 初始化：TODO 换形态前缀 + 开机动作 + 加载模型（例：ug.load_models(['color_recognition'])）
    try:
        ug.screen_print_text("开工!", 6)
        ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)
        # ② 循环感知 → ③ 判断 → ④ 动作（循环体里别忘了 time.sleep(0.1)）
        for 一轮 in range(100):
            # TODO 感知：读传感器或视觉，例如
            # 距离 = ug.read_distance_data(1)
            # TODO 判断：先挡住"没读到"（-1 和 0）再比大小，例如
            # if 距离 != -1 and 距离 != 0 and 距离 < 30:
            # TODO 动作：让轮子/手臂/灯/声音响应（前缀换成你的形态！），例如
            # ug.stop_chassis(); ug.show_light_rgb_effect(255, 0, 0, 3)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾")
    finally:
        # ⑤ 收尾：一行都别省（用了哪样就打开哪行）
        ug.stop_chassis()
        ug.turn_off_lights()
        ug.screen_clear()
        # ug.release_models(['你加载过的模型名'])
        # ug.mechanical_arms_restory()    # 用了工程车手臂

# ============ 想跑哪个，就去掉哪行前面的 # ============
彩蛋2_谢幕秀()            # ← 默认激活：不跑车、任何形态都能演的最安全谢幕
# 场景1_收官项目骨架()     # ← 你的毕业作品从这里的 TODO 开始填
# 彩蛋1_狗狗握手会()       # 四足狗形态专用
# 彩蛋3_麦轮方块走位()     # 麦轮车形态专用
# 彩蛋4_空白项目模板()
