# -*- coding: utf-8 -*-
# ============================================================
#  第14周 · 变形车越障翻台阶 + 巡线（变形车形态 transform_）
#  知识点：巡线三步曲 / TOF 测距防呆 / transform_set_chassis_height(2~7整数) / 谁优先
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
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

# 巡线调参（照你 print 出来的偏移量数量级调，别死抄）
阈值 = 10        # 偏移比这更小，就算"基本正对"
系数 = 3         # P 思路：偏越多，修越多
封顶 = 120       # 转向速度上限（transform_turn_speed 允许 5~280）
前进速度 = 35    # transform_move_speed 允许 5~80

def 跟线一小步():
    # 手册关1 的"跟线脑子"单步版：读一次线 → 偏哪修哪（返回的是列表，别 json.loads！）
    信息 = ug.get_single_track_total_info()        # [偏移, 线型, x, y]
    偏移量 = 信息[0]
    线型 = 信息[1]
    if 线型 == 0:                                  # 0 = 没看到线 → 先停，别当成"偏移0"冲出去
        ug.stop_chassis()
    else:
        修正 = min(封顶, abs(偏移量) * 系数)       # 偏越多打得越狠，但封顶别转飞
        if 偏移量 > 阈值:
            ug.transform_turn_speed(3, 修正)       # 3 = 右转（正负方向以你实测为准）
            time.sleep(0.1); ug.stop_chassis()     # 修一下就停，避免一直原地转
        elif 偏移量 < -阈值:
            ug.transform_turn_speed(2, 修正)       # 2 = 左转
            time.sleep(0.1); ug.stop_chassis()
        else:
            ug.transform_move_speed(0, 前进速度)   # 基本正对：直走（0 = 前进）

# ============ 课堂代码复现 ============

def 场景1_巡线跟线():
    # 跑这个你会看到：变形车沿黑线自己走，线往哪歪就往哪修（车身降到最低2厘米最稳）
    try:
        ug.load_models(['line_recognition'])       # ① 装"认黑线"模型
        ug.set_track_recognition_line(0)           # ② 0 = 单轨；漏了它线型永远读成 0
        ug.transform_set_chassis_height(2)         # ③ 车身降到最低（整数 2~7 厘米）
        ug.screen_print_text("开始巡线", 5)        # 5 = 黄
        for 一轮 in range(120):                    # 手册里是 while True，这里跑约8秒自动停
            跟线一小步()
            time.sleep(0.05)                       # 每圈喘一口气
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        ug.stop_chassis()
        ug.turn_off_lights()
        ug.transform_set_chassis_height(2)         # 收尾把车身降回最低
        ug.release_models(['line_recognition'])    # 用完卸模型，机器人不发烫
        ug.screen_clear()

def 场景2_巡线遇障翻越():
    # 跑这个你会看到：变形车绿灯巡线；前方有障碍块就闪橙灯、喊一声、车身升到6厘米翻过去，再降回2厘米继续巡线
    安全距离 = 25                                  # 离坎还剩25厘米就停，留出抬车身反应距离
    def 抬升车身(高度=6):
        ug.transform_set_chassis_height(高度)      # 变形招牌：整数 2~7 厘米
        time.sleep(1)                              # ★ 等机构真升到位，别急着开
    def 恢复低姿态(高度=2):
        ug.transform_set_chassis_height(高度)
        time.sleep(0.5)                            # 同样等它降到位
    def 翻越():
        ug.stop_chassis()                          # ① 先停
        ug.screen_print_text("翻越中", 3)
        ug.show_light_rgb_effect(255, 170, 0, 3)   # 橙黄闪烁：正在干活
        ug.play_audio_tts("前面有障碍，我抬起来跨过去", 0)
        抬升车身(6)                                # ② 升到 6 厘米
        ug.transform_move_speed_times(0, 20, 2, 0) # ③ 慢速前进2秒自己停（走5~80；unit 0=秒）
        time.sleep(2.3)                            # ★ Python 不等机器人，陪着等完
        ug.stop_chassis()
        恢复低姿态(2)                              # ④ 降回最低，重心低才好巡线
        ug.turn_off_lights()
    try:
        ug.load_models(['line_recognition'])
        ug.set_track_recognition_line(0)
        ug.transform_set_chassis_height(2)
        for 一轮 in range(150):
            距离 = ug.read_distance_data(1)
            print("距离 =", 距离)
            if 距离 != -1 and 距离 != 0 and 距离 < 安全距离:   # 障碍判断放最前：撞坎比掉线危险！
                翻越()
                continue                           # 这一圈到此为止，回去重新看
            ug.screen_print_text("巡线中", 6)      # 6 = 绿
            跟线一小步()
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        ug.stop_chassis()                          # 不管走哪条路，先停车最安全
        ug.turn_off_lights()
        ug.transform_set_chassis_height(2)         # 一定降回最低
        ug.release_models(['line_recognition'])
        ug.screen_clear()
    ug.transform_restory()

# ============ 趣味加餐 ============

def 彩蛋1_变身秀():
    # 跑这个你会看到：车身 2→4→6→7 一档一档升上去、屏幕跟着报数，再"噌"地降回 2
    ug.screen_print_text("变身秀!", 5)
    for 高度 in [2, 4, 6, 7, 2]:                   # 逐档爬升再降回，每档停 1 秒
        ug.transform_set_chassis_height(高度)      # 整数 2~7 厘米；2.5 会报 int is required
        ug.screen_print_text("高度" + str(高度), 5)
        time.sleep(1)
    ug.play_audio_tts("变身完成", 0)
    time.sleep(1.5)
    安全收尾()
    ug.transform_restory()

def 彩蛋2_潜行与瞭望():
    # 跑这个你会看到：变形车先贴地潜行巡线约8秒，再原地升起瞭望、左右张望，最后降回低姿态
    try:
        ug.load_models(['line_recognition'])
        ug.set_track_recognition_line(0)
        ug.transform_set_chassis_height(2)
        time.sleep(0.8)
        ug.screen_print_text("潜行巡线", 6)
        for 一轮 in range(120):                    # 低姿态潜行约 8 秒
            跟线一小步()
            time.sleep(0.05)
        ug.stop_chassis()
        ug.transform_set_chassis_height(6)         # 升到瞭望高度（升高别开车，重心高容易晃）
        time.sleep(1)
        ug.screen_display_emotion("Search")
        ug.play_audio_tts("我升起来瞭望啦", 0)
        ug.transform_turn_speed_times(2, 60, 45, 2)    # 左张望 45 度（转 5~280；unit 2=度）
        time.sleep(45 / 60 + 0.3)
        ug.transform_turn_speed_times(3, 60, 90, 2)    # 右张望 90 度
        time.sleep(90 / 60 + 0.3)
        ug.transform_turn_speed_times(2, 60, 45, 2)    # 转回正面
        time.sleep(45 / 60 + 0.3)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        ug.stop_chassis()
        ug.turn_off_lights()
        ug.transform_set_chassis_height(2)
        ug.release_models(['line_recognition'])
        ug.screen_clear()
    ug.transform_restory()

# ============ 想跑哪个，就去掉哪行前面的 # ============
彩蛋1_变身秀()            # ← 默认激活：原地升降不跑车，最安全
# 场景1_巡线跟线()
# 场景2_巡线遇障翻越()     # ← 本周大作品：地上贴黑线 + 放一个1~2厘米的矮障碍块
# 彩蛋2_潜行与瞭望()
