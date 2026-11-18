# -*- coding: utf-8 -*-
# ============================================================
#  第11周 · 轮足高低地形适应 + AI 跟随（wheelleg_）—— 课堂代码备查 + 趣味加餐
#  知识点：姿态感知（read_gyro_data / get_attitude）+ 摇晃保护 + 颜色跟随 + 底盘高度切换
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100，写 3 你几乎听不见

def 安全收尾():
    ug.stop_chassis()
    ug.turn_off_lights()
    ug.screen_clear()

def 站起来():
    """轮足的"起床仪式"：不先进自平衡，发什么运动命令它都装听不懂"""
    ug.wheelleg_start_balancing()   # 轮足专属：站起来、进入自平衡
    time.sleep(2)                   # 站稳（手册写等 1 秒也行，多等 1 秒更稳）

# ============ 课堂代码复现 ============

# —— 场景1（关1）：站稳行走 + 读出"姿态" ——
def 场景1_站稳行走读姿态():
    # 跑这个你会看到：它先立起来慢慢走、绿灯亮，输出区一直刷"俯仰:xx 摇晃:False"；抱上小坡俯仰会变
    站起来()
    try:
        print("陀螺仪一共 9 个数：", ug.read_gyro_data())   # [俯仰,横滚,偏航, 角速度×3, 加速度×3]
        while True:
            ug.wheelleg_move_speed(0, 30)               # 0=前进；轮足速度范围 5~60（不是麦轮的 80）
            ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)  # 绿灯 = 平稳前进（灯带只能填 0~3）
            姿态 = ug.get_attitude()                    # 7 个布尔：前倾/后倾/左倾/右倾/屏朝上/屏朝下/摇晃
            陀螺 = ug.read_gyro_data()                  # 9 个数，[0] = 俯仰（爬坡时最直观）
            print("俯仰:", 陀螺[0], "摇晃:", 姿态[6])    # ★ 本周先看 print，别只盯屏幕
            ug.screen_print_text("俯仰:" + str(陀螺[0]), 6)   # 屏幕颜色是整数：6 = 绿
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止 → 手动急停")
    except Exception as 错误:                           # 不用裸 except，把真错误念出来
        print("出问题了，先急停：", 错误)
    finally:
        安全收尾()
        ug.wheelleg_restory()          # 轮足回到初始姿势（中等高度）
        ug.wheelleg_stop_balancing()   # 退出自平衡：它会松腿降低，伸手护一下别摔倒

# —— 场景2（关2）：蹲低 + 摇晃保护，过起伏不摔 ——
def 场景2_蹲低摇晃保护():
    # 跑这个你会看到：它蹲得低低的、绿灯走着；你轻推它一下 → 立刻红灯狂闪 + 停下；扶稳又继续走
    站起来()
    ug.wheelleg_set_chassis_height(3)   # 3=低（1高/2中/3低，只能整数）：过起伏先蹲低，重心越低越稳
    time.sleep(1)                       # 等它把腿伸到位
    正常速度 = 30    # 轮足前进 5~60，重心高宁慢勿快
    try:
        while True:
            姿态 = ug.get_attitude()
            if 姿态[6]:                     # 第 7 个（下标 6）= 摇晃 → 快保不住平衡
                ug.stop_chassis()           # 先停，最安全
                ug.screen_print_text("晃!", 3)                # 3 = 红
                ug.show_light_rgb_effect(255, 0, 0, 3)        # 红灯狂闪：一行搞定（没有灯带列表）
            else:                           # 平稳
                ug.wheelleg_move_speed(0, 正常速度)
                ug.show_light_rgb_effect(0, 255, 0, 0)        # 绿灯常亮：我在稳稳走
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止 → 手动急停")
    except Exception as 错误:
        print("出问题了，先急停：", 错误)
    finally:
        安全收尾()
        ug.wheelleg_restory()
        ug.wheelleg_stop_balancing()

# —— 场景3（关3 · 终极版）：蹲低保护 + 颜色块跟随（本周大作品）——
def 场景3_颜色跟随():
    # 跑这个你会看到（验收两步）：过起伏不摔（摇晃自动保护）+ 红球偏左它左转、偏右右转、正前方就追上来
    # ⚠️ 先做一次"标定"（手册步骤③关3）：球放机器人正前方中间，print 出的 x 填进 中线；
    #     颜色名抄真实的（中文机 '红色' / 英文机 'red'），填错它就死活"等目标"
    站起来()
    ug.wheelleg_set_chassis_height(3)   # 蹲低：追目标也要稳
    time.sleep(1)
    正常速度 = 30    # 轮足前进 5~60（不是麦轮的 80）
    转向速度 = 60    # 轮足转向 5~180（不是麦轮的 280）
    中线 = 200       # ← 抄你标定出来的数，别照抄这里
    半宽 = 40        # 中线 ±40 以内都算"正前方"
    目标颜色 = '红色' # ← 抄 print 出来的真实值（英文机填 'red'）
    try:
        print("眼睛装好了吗：", ug.load_models(['color_recognition']))   # True 才算叫醒
        time.sleep(2)                       # 模型加载要一两秒，冲太快就读到空值
        while True:
            姿态 = ug.get_attitude()
            if 姿态[6]:                     # —— 摇晃保护（过起伏不摔），优先级最高 ——
                ug.stop_chassis()
                ug.screen_print_text("晃!", 3)
                ug.show_light_rgb_effect(255, 0, 0, 3)
                time.sleep(0.3)
                continue                    # 跳过下面，等稳了再追
            结果 = ug.get_color_total_info()   # 【列表】[颜色,形状,x,y,高,宽,面积]，不要 json.loads！
            颜色, x = 结果[0], 结果[2]         # [0]=颜色名，[2]=左右位置（越大越靠右）
            print("看到：", 颜色, " x =", x)   # ★ 卡住时的救命一行
            if 颜色 == '' or x == -1:          # 什么都没认到 → 先停，别乱冲
                ug.stop_chassis()
                ug.screen_print_text("找目标", 1)     # 1 = 白
            elif 颜色 == 目标颜色:
                ug.show_light_rgb_effect(0, 255, 0, 0)   # 绿灯常亮 = 锁定
                if x < 中线 - 半宽:                       # 偏左 → 左转对准
                    ug.wheelleg_turn_speed(2, 转向速度)
                    ug.screen_print_text("左转追", 5)     # 5 = 黄
                elif x > 中线 + 半宽:                     # 偏右 → 右转对准
                    ug.wheelleg_turn_speed(3, 转向速度)
                    ug.screen_print_text("右转追", 5)
                else:                                     # 中间 → 前进追上
                    ug.wheelleg_move_speed(0, 正常速度)
                    ug.screen_print_text("前进追", 6)     # 6 = 绿
            else:                              # 看到的是别的颜色 → 等着，不乱动
                ug.stop_chassis()
                ug.screen_print_text("等目标", 1)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止 → 手动急停")
    except Exception as 错误:
        print("出问题了，先急停：", 错误)
    finally:
        安全收尾()
        ug.wheelleg_restory()
        ug.wheelleg_stop_balancing()
        ug.release_models(['color_recognition'])   # 请"颜色专家"去睡觉

# ============ 趣味加餐 ============

# —— 彩蛋1：姿态仪表灯（7 个布尔 → 灯色 + 表情）——
def 彩蛋1_姿态仪表灯():
    # 跑这个你会看到：它原地站桩当"仪表盘"——前/后倾亮黄灯冒问号脸，侧歪亮紫灯，摇晃红灯闪+生气脸，平稳绿灯+笑脸
    站起来()
    try:
        for 轮数 in range(10):              # 有界循环：看 10 轮（约 7 秒）自动收工
            姿态 = ug.get_attitude()
            print("7 个布尔：", 姿态)       # 先看清每个位置是什么，再玩灯
            if 姿态[6]:                     # 摇晃（下标 6）
                ug.show_light_rgb_effect(255, 0, 0, 3)
                ug.screen_display_emotion("Anger")
                ug.screen_print_text("晃!", 3)
            elif 姿态[0] or 姿态[1]:        # 前倾 / 后倾
                ug.show_light_rgb([0, 1, 2, 3], 255, 255, 0)   # 黄灯
                ug.screen_display_emotion("Doubt")
                ug.screen_print_text("歪了", 5)
            elif 姿态[2] or 姿态[3]:        # 左倾 / 右倾
                ug.show_light_rgb([0, 1, 2, 3], 255, 0, 255)   # 紫灯
                ug.screen_display_emotion("Doubt")
                ug.screen_print_text("侧歪", 5)
            else:                           # 稳如泰山
                ug.show_light_rgb_effect(0, 255, 0, 0)
                ug.screen_display_emotion("Smile")
                ug.screen_print_text("稳!", 6)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("你按了停止 → 手动急停")
    finally:
        安全收尾()
        ug.wheelleg_restory()
        ug.wheelleg_stop_balancing()

# —— 彩蛋2：地形切换表演（wheelleg_set_chassis_height）——
def 彩蛋2_地形切换():
    # 跑这个你会看到：它原地站桩换三档身高——1 最高像长颈鹿、3 最低最稳，最后复位回中等
    站起来()
    try:
        ug.play_audio_tts("我要变身啦", 0, True)   # True = 说完再动
        ug.wheelleg_set_chassis_height(1)   # 1 = 最高（只能填整数 1/2/3）
        time.sleep(2)
        ug.screen_print_text("最高", 6)
        ug.wheelleg_set_chassis_height(2)   # 2 = 中
        time.sleep(2)
        ug.screen_print_text("中等", 5)
        ug.wheelleg_set_chassis_height(3)   # 3 = 最低：过起伏地面最稳
        time.sleep(2)
        ug.screen_print_text("最低", 3)
        ug.wheelleg_restory()               # 复位回中等高度
        ug.play_audio_tts("变身完毕", 0, True)
        time.sleep(1)
    except KeyboardInterrupt:
        print("你按了停止 → 手动急停")
    finally:
        安全收尾()
        ug.wheelleg_restory()
        ug.wheelleg_stop_balancing()

# ============ 想跑哪个，就去掉哪行前面的 # ============
彩蛋1_姿态仪表灯()    # ← 默认激活：本周最安全（原地站桩读姿态，不走一步）
# 场景1_站稳行走读姿态()   # 关1：往前走并观察俯仰/摇晃（要小坡场地）
# 场景2_蹲低摇晃保护()     # 关2：蹲低 + 摇晃就红灯保护（轻推它试试）
# 场景3_颜色跟随()         # 关3 · 本周大作品：先标定中线，再追红球
# 彩蛋2_地形切换()
