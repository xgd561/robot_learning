# -*- coding: utf-8 -*-
# ============================================================
#  第8周 · 巡线跟随（变形车）—— 课堂代码备查 + 趣味加餐
#  知识点：巡线三步曲、偏移量 offset、按比例调速（P 的思路）
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
#  ⚠️ 提前贴好黑胶带（3~5cm 宽）在浅色地板/白纸上；场地够长
#  ⚠️ 偏移量的正负方向以你打印实测为准——走反了就把 3 和 2 对调
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100

def 安全收尾():
    ug.stop_chassis()                    # 不管发生什么，先停车最安全
    ug.transform_set_chassis_height(2)   # 车身降回最低（整数 2~7 厘米），重心稳
    ug.turn_off_lights()
    ug.screen_clear()

# 【本周速记】巡线三步曲：load_models(['line_recognition']) → set_track_recognition_line(0) →
#             get_single_track_total_info()（第②步最容易漏，漏了永远"看不到线"！）
# 【本周速记】返回 [偏移量, 线型, x, y]：线型 1 直线 / 2 Y字路口 / 3 十字路口 / 0 没线
# 【本周速记】0 = 没线必须单独判断，不能当成"偏移 0 直走"冲出去！
# 【本周速记】P 修正一行：min(封顶, abs(偏移量) * 系数)——偏越多打得越狠，但别打死
# 【本周速记】transform_set_chassis_height 只能整数 2~7 厘米；transform_raise_body 不存在！

# ============ 课堂代码复现 ============
def 场景1_看一眼线信息():
    """跑这个你会看到：输出区打印 [偏移, 线型, x, y] 四个数（车不动，用来确认"眼睛"装好了）"""
    ug.load_models(['line_recognition'])     # ① 装上"认黑线"模型（返回 True 才算成功）
    ug.set_track_recognition_line(0)         # ② 设线型：0 = 单轨 / 1 = 双轨（别漏这步！）
    ug.screen_print_text("巡线就绪", 5)       # 5 = 黄
    信息 = ug.get_single_track_total_info()   # ③ 读一次，返回列表
    print(信息)                              # ← 先打印，看清 [偏移, 线型, x, y]
    print("偏移量是第 0 格，线型是第 1 格（1直线 2Y字 3十字 0没线）")
    ug.screen_print_text("偏移:" + str(信息[0]), 5)
    ug.stop_chassis()

def 场景2_巡线小勇士():
    """跑这个你会看到：小车沿黑线自己走，偏哪边修哪边；线外轻转找线，找久了老实停下"""
    阈值 = 10          # 偏移比它小就算"基本正对"（按你实测的数字调！）
    系数 = 3           # P：偏越多，修正越多
    封顶 = 120         # 转向速度上限（transform_turn_speed 允许 5~280）
    前进速度 = 35      # transform_move_speed 允许 5~80
    找不到线的次数 = 0
    try:
        ug.load_models(['line_recognition'])
        ug.set_track_recognition_line(0)        # ← 别漏
        ug.transform_set_chassis_height(2)      # 车身最低，重心低、巡线最稳
        ug.screen_print_text("开始巡线", 5)
        while True:
            信息 = ug.get_single_track_total_info()
            偏移量 = 信息[0]
            线型 = 信息[1]
            if 线型 == 0:                        # ① 最优先：没线——不能当"正对"冲出去
                找不到线的次数 = 找不到线的次数 + 1
                if 找不到线的次数 > 20:          # 连续约 1 秒没线（每圈歇 0.05 秒）
                    ug.stop_chassis()
                    ug.screen_print_text("找不到线了", 3)   # 3 = 红
                    break                        # 老老实实停下，别乱转
                ug.transform_turn_speed(3, 40)   # 先轻轻右转"找一找"
                time.sleep(0.1)
                ug.stop_chassis()
                continue                         # 这圈到此为止，回去重新看线
            找不到线的次数 = 0                   # 看到线了，清零
            if 线型 == 2 or 线型 == 3:           # ② Y字/十字路口：慢点直着过，别乱打方向盘
                ug.screen_print_text("有路口", 5)
                ug.transform_move_speed(0, 20)
                time.sleep(0.3)
                ug.stop_chassis()
                continue
            修正 = min(封顶, abs(偏移量) * 系数)  # ③ P：偏越多打得越狠，但封顶
            if 偏移量 > 阈值:
                ug.transform_turn_speed(3, 修正)  # 3 = 右转（方向以你实测为准）
                time.sleep(0.1)
                ug.stop_chassis()                # 修一下就停，避免一直转圈
            elif 偏移量 < -阈值:
                ug.transform_turn_speed(2, 修正)  # 2 = 左转
                time.sleep(0.1)
                ug.stop_chassis()
            else:
                ug.transform_move_speed(0, 前进速度)   # 正对：直走
            time.sleep(0.05)                     # 每圈喘一口气
    except KeyboardInterrupt:
        print("你按了停止（KeyboardInterrupt），正在收尾…")
    except Exception as 错误:
        print("出错了，先急停：", 错误)
    finally:
        安全收尾()

def 场景3_巡线越障小勇士():
    """跑这个你会看到：巡线途中 TOF 测到 20cm 内有矮障碍→停下喊话→升到 6cm 压过去→降回 2cm"""
    阈值 = 10
    系数 = 3
    封顶 = 120
    前进速度 = 30
    try:
        ug.load_models(['line_recognition'])
        ug.set_track_recognition_line(0)
        ug.transform_set_chassis_height(2)      # 平时巡线：车身最低最稳
        ug.screen_print_text("巡线+越障", 5)
        while True:
            距离 = ug.read_distance_data(1)     # TOF 测距，单位厘米
            # ① 先防呆：-1 和 0 都表示"没测到"！-1 < 20 是"真"，不挡掉会对着空气越障
            if 距离 != -1 and 距离 > 0 and 距离 < 20:
                ug.screen_print_text("抬车身!", 3)
                ug.play_audio_tts("有障碍，我抬起来", 0)
                ug.stop_chassis()
                ug.transform_set_chassis_height(6)   # 升到 6 厘米（整数 2~7）
                time.sleep(1)                        # 等机构升到位，别急着开
                ug.transform_move_speed_times(0, 20, 2, 0)   # 慢速前进 2 秒自动停
                time.sleep(2.3)                      # _times 不阻塞 Python，等它真越过去！
                ug.transform_set_chassis_height(2)   # 越过去后降回最低
                time.sleep(0.5)
                continue                             # 回到循环开头，重新找线
            # ② 没障碍：正常按比例巡线
            信息 = ug.get_single_track_total_info()
            偏移量 = 信息[0]
            线型 = 信息[1]
            if 线型 == 0:
                ug.stop_chassis()
            else:
                修正 = min(封顶, abs(偏移量) * 系数)
                if 偏移量 > 阈值:
                    ug.transform_turn_speed(3, 修正)
                    time.sleep(0.1)
                    ug.stop_chassis()
                elif 偏移量 < -阈值:
                    ug.transform_turn_speed(2, 修正)
                    time.sleep(0.1)
                    ug.stop_chassis()
                else:
                    ug.transform_move_speed(0, 前进速度)
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()

# ============ 趣味加餐 ============
def 彩蛋1_俯卧撑升降秀():
    """跑这个你会看到：车身从 2cm 一格一格升到 7cm，再一格一格降回来，像做俯卧撑（原地不出脚）"""
    try:
        ug.screen_display_emotion("Proud")
        for 轮次 in range(2):                    # 做 2 轮俯卧撑
            for 高度 in range(2, 8):             # 2→3→4→5→6→7，逐档升高
                ug.transform_set_chassis_height(高度)   # 只能整数 2~7 厘米！
                time.sleep(1)                    # 每档歇 1 秒，看它慢慢长高
            for 高度 in range(7, 1, -1):         # 7→6→…→2，逐档降低
                ug.transform_set_chassis_height(高度)
                time.sleep(1)
    except KeyboardInterrupt:
        print("你点了停止 → 手动急停")
    finally:
        安全收尾()

def 彩蛋2_高姿态瞭望低姿态潜行():
    """跑这个你会看到：先升到 6cm 慢慢"瞭望"走一段，再降到 2cm 快速"潜行"走一段"""
    try:
        ug.screen_print_text("瞭望模式", 6)          # 6 = 绿
        ug.play_audio_tts("站得高看得远", 0)
        ug.transform_set_chassis_height(6)           # 升高（整数 2~7 厘米）
        time.sleep(1)                                # 等升到位
        ug.transform_move_speed_times(0, 25, 2, 0)   # 慢速瞭望 2 秒自动停（速度 5~80）
        time.sleep(2.3)                              # 等它真停下来
        ug.screen_print_text("潜行模式", 3)
        ug.play_audio_tts("低姿态，出发", 0)
        ug.transform_set_chassis_height(2)           # 降到最低，重心稳
        time.sleep(1)
        ug.transform_move_speed_times(0, 50, 2, 0)   # 快速潜行 2 秒自动停
        time.sleep(2.3)
        ug.screen_display_emotion("Proud")
    except KeyboardInterrupt:
        print("你点了停止 → 手动急停")
    finally:
        安全收尾()

# ============ 想跑哪个，就去掉哪行前面的 # ============
场景1_看一眼线信息()      # ← 默认激活：本周最安全（车不动，只打印线信息）
# 场景2_巡线小勇士()
# 场景3_巡线越障小勇士()
# 彩蛋1_俯卧撑升降秀()
# 彩蛋2_高姿态瞭望低姿态潜行()
