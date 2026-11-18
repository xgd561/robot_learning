# -*- coding: utf-8 -*-
# ============================================================
#  第12周 · 四足狗仿生步态 + 语音播报（dog_）—— 课堂代码备查 + 趣味加餐
#  知识点：def 函数按钮（参数/默认值）+ 语音播报 + 表情 + 狗的 6 个真动作
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100（不是 1~5！填 3 几乎听不见）

def 安全收尾():
    ug.stop_chassis()
    ug.turn_off_lights()
    ug.screen_clear()

# ============ 课堂代码复现 ============

# —— 场景1（关1）：狗动起来（先看清狗的速度脾气）——
def 场景1_狗动起来():
    # 跑这个你会看到：狗迈着狗步前进 2 秒、停下站好，屏幕红字"站稳"（⚠️ 动手前先清空周围 1.5 米！）
    ug.dog_restory()               # 先让四条腿复位站好，别带着歪腿下令
    time.sleep(1)
    try:
        ug.dog_move_speed(0, 12)   # 0=前进(1=后退)，速度 0~25 —— 12 就是散步（填 70 不报错，会被悄悄压到 25）
        time.sleep(2)              # 走 2 秒
        ug.stop_chassis()          # 停！不然它会一直走到撞墙
        ug.dog_restory()           # 站好，别瘫在地上
        ug.screen_print_text("站稳", 3)   # 屏幕颜色是整数 0~8：3 = 红
        time.sleep(2)
    except KeyboardInterrupt:
        print("你按了停止，程序中断")
    finally:
        安全收尾()
        ug.dog_restory()

# —— 场景2（关2）：走 / 跑 / 转身 三个步态按钮（先不喊话）——
def 场景2_三步态按钮():
    # 跑这个你会看到：狗先散步 2 秒 → 撒欢跑 2 秒 → 原地左转 1 秒，动作之间停顿清楚，最后绿字"表演完毕"
    def walk(秒数, 速度=12):        # "走"按钮：散步速度
        ug.dog_move_speed_times(0, 速度, 秒数, 0)   # 0=前进，末尾 0=秒：走够它自己停（move_* 单位只认 0秒/1厘米）
        time.sleep(秒数)                            # 它自己停，但 Python 不等——这行不能省
    def run(秒数, 速度=25):         # "跑"按钮：25 就是狗的上限，"跑"其实是顶格走
        ug.dog_move_speed_times(0, 速度, 秒数, 0)
        time.sleep(秒数)
    def turn(秒数, 速度=10):        # "转身"按钮：转向上限只有 20！
        ug.dog_turn_speed_times(2, 速度, 秒数, 0)   # 2=左转，想右转填 3（turn_* 单位只认 0秒/2度）
        time.sleep(秒数)
    ug.dog_restory()
    time.sleep(1)
    try:
        walk(2)        # 慢慢走 2 秒
        run(2)         # 飞快跑 2 秒
        turn(1)        # 原地左转 1 秒
        ug.screen_print_text("表演完毕", 6)   # 6 = 绿
        time.sleep(2)                          # 不等一下，下面 finally 一清屏就看不见字了
    except KeyboardInterrupt:
        print("你按了停止，程序中断")
    finally:
        安全收尾()
        ug.dog_restory()

# —— 场景3（关3 · 终极版）：每个按钮加"播报 + 心情脸"，再补两个真动作（本周大作品）——
def 场景3_步态播报表演():
    # 跑这个你会看到（验收）：狗说完"狗狗表演开始啦"才动，然后走→跑→转身→握手→趴下，
    #   每切换一个动作女声就播报一句、表情跟着换，最后"表演完毕"
    def walk(秒数, 速度=12):                              # 按钮①：散步
        ug.dog_move_speed_times(0, 速度, 秒数, 0)         # 前进 0~25，末尾 0=秒（自己停）
        ug.play_audio_tts("我在走", 0)                    # 一迈步就播报（0 女声 / 1 男声）
        ug.screen_display_emotion("Smile")                # 心情：开心
        ug.show_light_rgb_effect(0, 255, 0, 2)            # 绿灯呼吸（effect 2=呼吸，没有灯带列表）
        time.sleep(秒数)                                  # 狗自己停，Python 要陪着等
    def run(秒数, 速度=25):                               # 按钮②：撒欢（25 就是狗的上限）
        ug.dog_move_speed_times(0, 速度, 秒数, 0)
        ug.play_audio_tts("我在跑", 0)
        ug.screen_display_emotion("Proud")                # 心情：得意
        ug.show_light_rgb_effect(255, 165, 0, 3)          # 橙灯闪烁（effect 3=闪烁）
        time.sleep(秒数)
    def turn(秒数, 速度=10):                              # 按钮③：转身（转向上限只有 20）
        ug.dog_turn_speed_times(2, 速度, 秒数, 0)         # 2=左转，想右转填 3
        ug.play_audio_tts("我在转身", 0)
        ug.screen_display_emotion("Search")               # 心情：找找看
        time.sleep(秒数)
    def 握手(秒数=3):                                     # 按钮④：真动作，不看速度
        ug.dog_perform_action("handshake")                # ← 动作名是字符串，引号不能丢
        ug.play_audio_tts("给你握个手", 0)
        ug.screen_display_emotion("Love")
        time.sleep(秒数)                                  # 动作要几秒做完，Python 不等它
    def 趴下(秒数=3):                                     # 按钮⑤：真动作
        ug.dog_perform_action("squatting")                # 狗动作表里的"蹲/趴"
        ug.play_audio_tts("我休息一下", 0)
        ug.screen_display_emotion("Sleep")
        time.sleep(秒数)
    ug.dog_restory()
    time.sleep(1)
    try:
        ug.play_audio_tts("狗狗表演开始啦", 0, True)       # 第三个参数 True = 说完再动
        walk(2)          # 播报"我在走" + 走 2 秒
        run(2)           # 播报"我在跑" + 跑 2 秒
        turn(1)          # 播报"我在转身" + 转 1 秒
        握手()           # 播报"给你握个手" + 握手约 3 秒
        趴下()           # 播报"我休息一下" + 趴下约 3 秒
        ug.screen_print_text("表演完毕", 6)
        time.sleep(2)
    except KeyboardInterrupt:
        print("你按了停止，程序中断")
    except Exception as 错误:
        print("出问题了，红字是：", 错误)
    finally:
        安全收尾()
        ug.dog_restory()

# ============ 趣味加餐 ============

# —— 彩蛋1：狗狗才艺串烧（6 个真动作挨个演）——
def 彩蛋1_才艺串烧():
    # 跑这个你会看到：狗挨个表演 站好→伸懒腰→握手→爬行→蹲下→抬腿，每个动作前女声报幕，演完自动收工
    节目单 = [("standing", "站好"), ("stretch", "伸个懒腰"), ("handshake", "握个手"),
              ("crawling", "匍匐前进"), ("squatting", "蹲下"), ("urination", "抬腿……嗯你懂的")]
    ug.dog_restory()
    time.sleep(1)
    try:
        ug.play_audio_tts("才艺表演开始", 0, True)
        for 动作, 报幕 in 节目单:              # 有界 for：演完 6 个自动收工
            ug.play_audio_tts(报幕, 0, True)   # 说完再动
            ug.dog_perform_action(动作)        # 动作名是字符串，狗只有这 6 个（别塞 Smile 那套表情名）
            ug.screen_print_text(报幕, 6)
            time.sleep(4)                      # 每个动作约 3~4 秒做完，Python 要陪着等
    except KeyboardInterrupt:
        print("你按了停止，程序中断")
    finally:
        安全收尾()
        ug.dog_restory()

# —— 彩蛋2：握手互动 ——
def 彩蛋2_握手互动():
    # 跑这个你会看到：狗说"我们来握个手吧"→伸手握手→屏幕冒爱心、夸你"你真棒"，来回 3 次
    ug.dog_restory()
    time.sleep(1)
    try:
        for 轮数 in range(3):                       # 有界循环：握 3 次就收工
            ug.play_audio_tts("我们来握个手吧", 0, True)
            ug.dog_perform_action("handshake")
            ug.screen_display_emotion("Love")
            time.sleep(3)
            ug.play_audio_tts("你真棒", 0)
            ug.dog_perform_action("standing")       # 演完站好，准备下一次
            time.sleep(2)
    except KeyboardInterrupt:
        print("你按了停止，程序中断")
    finally:
        安全收尾()
        ug.dog_restory()

# ============ 想跑哪个，就去掉哪行前面的 # ============
彩蛋2_握手互动()       # ← 默认激活：本周最安全（原地握手 + 夸奖，不跑动）
# 场景1_狗动起来()     # 关1：先看清狗的速度脾气（70 会被悄悄压到 25）
# 场景2_三步态按钮()   # 关2：走 → 跑 → 转身（先不喊话）
# 场景3_步态播报表演() # 关3 · 本周大作品：每个动作都有语音播报 + 表情
# 彩蛋1_才艺串烧()
