# -*- coding: utf-8 -*-
# ============================================================
#  第10周 · 平衡车直立过障 + 灯光报警（balance_）—— 课堂代码备查 + 趣味加餐
#  知识点：if/elif/else 三档判断（危险的写最前）、开关变量防复读机、报警函数、加速度对比
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100，写 3 约等于静音

def 安全收尾():
    ug.stop_chassis()
    ug.turn_off_lights()
    ug.screen_clear()

def 站起来():
    """平衡车的"起床仪式"：开机是趴着的，不叫它站起来什么命令都不理（而且不报错）"""
    ug.balance_start_balancing()   # 平衡车专属：进入自平衡、把自己立起来
    time.sleep(2)                  # 等 2 秒站稳（晃两下很正常），别急着推它走

# ============ 课堂代码复现 ============

# —— 场景1（关1）：先站起来，再直立前行 ——
def 场景1_站起来走一走():
    # 跑这个你会看到：它自己立起来晃两下定住，亮着绿灯慢慢往前走（按停止收尾时它会向后倒，伸手扶！）
    站起来()
    ug.screen_print_text("站稳了", 6)            # 屏幕颜色是整数：6 = 绿
    正常速度 = 35   # balance_move_speed 允许 5~80（先别拉满）
    try:
        while True:
            ug.balance_move_speed(0, 正常速度)           # 0=前进，1=后退
            ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)   # 绿灯 = 我在前进（RGB 各 0~255）
            time.sleep(0.1)                              # 每圈喘口气，必写
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.balance_stop_balancing()  # 退出自平衡：它会缓缓往后倒，伸手扶一下再放平！

# —— 场景2（关2）：测距三档（红停 / 黄减速 / 绿前进）——
def 场景2_测距三档():
    # 跑这个你会看到：绿灯正常走 → 纸箱推近到 50cm 内变黄灯减速 → 20cm 内红灯停下；挪开又走
    # 注意：本周"读不到（-1、0）"= 前方空旷 → 继续走（和第4周蜘蛛找墙正好相反）
    站起来()
    停止距离 = 20   # 厘米：小于它就停
    减速距离 = 50   # 一定比停止距离大
    正常速度 = 35   # 5~80
    慢速 = 15
    try:
        while True:
            距离 = ug.read_distance_data(1)   # TOF 厘米（浮点），没读到 -1（也可能 0）
            print("距离 =", 距离)             # 卡住时的救命一行：先看真实读数
            if 距离 != -1 and 距离 != 0 and 距离 < 停止距离:      # 🥇最危险写最前：真读到+很近
                ug.stop_chassis()
                ug.screen_print_text("停!", 3)                    # 3 = 红
                ug.show_light_rgb([0, 1, 2, 3], 255, 0, 0)
            elif 距离 != -1 and 距离 != 0 and 距离 < 减速距离:    # 🥈有点近：减速慢走
                ug.balance_move_speed(0, 慢速)
                ug.screen_print_text("减速", 5)                   # 5 = 黄
                ug.show_light_rgb([0, 1, 2, 3], 255, 255, 0)
            else:                             # 🥉远 / 读不到 = 前方空旷：正常前进
                ug.balance_move_speed(0, 正常速度)
                ug.screen_print_text("前进", 6)
                ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.balance_stop_balancing()

def 报警():
    """把'闪红 + 喊话'打包成一个按钮（第5周那招），两行都不阻塞循环"""
    ug.show_light_rgb_effect(255, 0, 0, 3)   # 红灯闪烁：effect 3（0常亮/1关/2呼吸/3闪烁），没有 lights 参数
    ug.play_audio_tts("注意障碍", 0)          # 0 = 女声（默认不等说完就往下跑）

# —— 场景3（关3 · 终极版）：直立过障 + 灯光报警（本周大作品）——
def 场景3_直立过障报警():
    # 跑这个你会看到（验收五步）：绿灯前进 → 黄灯减速 → 红灯闪 + 喊一遍"注意障碍" → 挪开箱子又自己走
    站起来()
    停止距离 = 20
    减速距离 = 50
    正常速度 = 35
    慢速 = 15
    报警中 = False   # 开关变量：True = 这一遍障碍已经喊过了
    try:
        while True:
            距离 = ug.read_distance_data(1)
            有障碍 = 距离 != -1 and 距离 != 0 and 距离 < 停止距离   # 真读到 + 真很近
            有点近 = 距离 != -1 and 距离 != 0 and 距离 < 减速距离
            if 有障碍:                        # 🔴 危险档：停 + 闪红 + 只喊一遍
                ug.stop_chassis()
                ug.screen_print_text("警报!", 3)
                if not 报警中:                # 只有"刚从安全变危险"这一圈才喊
                    报警中 = True
                    报警()
            elif 有点近:                      # 🟡 减速档 + 黄灯常亮（effect 0）
                报警中 = False                # 警报解除，下次再近还能重新喊
                ug.balance_move_speed(0, 慢速)
                ug.screen_print_text("减速", 5)
                ug.show_light_rgb_effect(255, 255, 0, 0)
            else:                             # 🟢 安全档（含读不到 = 空旷）
                报警中 = False
                ug.balance_move_speed(0, 正常速度)
                ug.screen_print_text("前进", 6)
                ug.show_light_rgb_effect(0, 255, 0, 0)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.balance_stop_balancing()

# ============ 趣味加餐 ============

# —— 彩蛋1：红绿灯游戏 ——
def 彩蛋1_红绿灯游戏():
    # 跑这个你会看到：它像考驾照一样跑 3 轮——绿=正常走、黄=减速、红=闪灯停下，每轮都有语音口令
    站起来()
    try:
        for 轮数 in range(3):                       # 有界循环：跑 3 轮自动收工
            ug.play_audio_tts("绿灯行", 0, True)    # True = 说完再动
            ug.show_light_rgb_effect(0, 255, 0, 0)
            ug.screen_print_text("绿灯行", 6)
            ug.balance_move_speed(0, 30)
            time.sleep(3)
            ug.play_audio_tts("黄灯减速", 0, True)
            ug.show_light_rgb_effect(255, 255, 0, 0)
            ug.screen_print_text("黄灯慢", 5)
            ug.balance_move_speed(0, 12)
            time.sleep(2)
            ug.play_audio_tts("红灯停", 0, True)
            ug.stop_chassis()
            ug.show_light_rgb_effect(255, 0, 0, 3)  # 红灯闪烁
            ug.screen_print_text("红灯停", 3)
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.balance_stop_balancing()

# —— 彩蛋2：慢加速 vs 急加速对比（balance_set_acceleration）——
def 彩蛋2_加速对比():
    # 跑这个你会看到：同样是"前进"，慢加速像老爷爷起步，急加速一脚油门蹿出去（acceleration 必须填正数）
    站起来()
    try:
        ug.play_audio_tts("先看慢加速", 0, True)
        ug.balance_set_acceleration(10)      # 加速度调小：起步肉肉的
        ug.balance_move_speed(0, 30)
        time.sleep(3)
        ug.stop_chassis()
        time.sleep(1)
        ug.balance_reset_acceleration()      # 恢复默认加速度
        time.sleep(0.5)
        ug.play_audio_tts("再看急加速", 0, True)
        ug.balance_set_acceleration(60)      # 加速度调大：起步猛
        ug.balance_move_speed(0, 30)
        time.sleep(3)
        ug.stop_chassis()
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        ug.balance_reset_acceleration()
        安全收尾()
        ug.balance_stop_balancing()

# ============ 想跑哪个，就去掉哪行前面的 # ============
彩蛋1_红绿灯游戏()     # ← 默认激活：本周最安全（速度压在 30 以下、有界 3 轮、每轮都停）
# 场景1_站起来走一走() # 关1：一直往前走直到你按停止（要长场地！）
# 场景2_测距三档()     # 关2：准备一个纸箱，从远处慢慢推近它
# 场景3_直立过障报警() # 关3 · 本周大作品：完整"过障 + 报警"流水线
# 彩蛋2_加速对比()
