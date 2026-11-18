# -*- coding: utf-8 -*-
# ============================================================
#  第15周 · 工程车机械臂抓取/取放（底盘 mecanum_* + 手臂 mechanical_*）
#  知识点：机械臂 7 个真方法 / 颜色识别读列表 / TOF 靠近 / 函数按钮串流程
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
#  🦾 安全线：手臂活动范围里不放手和脸；每组新参数先空跑、先改小一半试
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

目标颜色 = "红色"   # ⚠️ 先跑场景1，照 print 出来的真实值填！中文机常是「红色」，英文机才是 'red'
搬运秒数 = 2        # 夹好球后往后退几秒到放置区（放置区画在车身后的垫子上）

# ===== 机械臂六个按钮（全部是真方法；机械臂只有这 7 个真方法，名字一个字不能改）=====

def 复位():
    ug.screen_print_text("复位", 1)                 # 1 = 白
    ug.mechanical_arms_restory(); time.sleep(1.5)   # 手臂回到起始姿势；Python 不等它
def 伸手():
    ug.screen_print_text("伸手", 5)                 # 5 = 黄
    ug.mechanical_move_axis(15, 2, 0, 1000); time.sleep(1.2)   # 前方15cm、高2cm、theta=0 是弧度！
def 合爪():
    ug.screen_print_text("合爪", 3)                 # 3 = 红
    ug.mechanical_clamp_close(); time.sleep(0.5)
    print("夹爪状态（1=合上）：", ug.mechanical_get_clamp_status())
def 抬起():
    ug.screen_print_text("抬起", 6)                 # 6 = 绿
    ug.mechanical_joint_control(0, 60, 0, 900); time.sleep(1.1)    # 关节1 −90~90 / 2 −80~110 / 3 −90~90
def 放低():
    ug.screen_print_text("放低", 5)
    ug.mechanical_joint_control(0, 20, 0, 900); time.sleep(1.1)    # 关节2 放回 20 度，球离地近一点
def 松爪():
    ug.screen_print_text("松爪", 1)
    ug.mechanical_clamp_release(); time.sleep(0.5)
    print("夹爪状态（0=张开）：", ug.mechanical_get_clamp_status())

def 靠近目标():
    # 手册关1 的"眼睛+脚"：认出目标颜色就一步步开过去；够近返回 True，超时返回 False
    安全距离 = 15                                   # 离目标多近算"到啦"（TOF 最远 150cm）
    for 一轮 in range(60):                          # 有界：最多找约 40 秒
        颜色结果 = ug.get_color_total_info()        # 返回【列表】，不要再 json.loads！
        print("我看到：", 颜色结果)                  # ← 第一次跑，先照这里打印的真实值填 目标颜色
        距离 = ug.read_distance_data(1)
        if 颜色结果[0] == 目标颜色 and 距离 > 0:    # 距离 <= 0 是没读到（-1 或 0），先别乱动
            ug.screen_print_text("看到目标 " + str(距离), 3)
            ug.show_light_rgb_effect(255, 0, 0, 3)  # 红灯闪烁：找到啦
            if 距离 < 安全距离:
                ug.stop_chassis()
                ug.screen_print_text("到啦", 6)
                return True
            ug.mecanum_move_speed_times(0, 35, 1, 0)     # 前进1秒自动停（工程车底盘=麦轮写法）
            time.sleep(1 + 0.3)
        else:
            ug.stop_chassis()
            ug.screen_print_text("找目标", 1)
        time.sleep(0.2)
    return False

# ============ 课堂代码复现 ============

def 场景1_认目标开过去():
    # 跑这个你会看到：工程车认出红球、红灯闪烁，一点一点开到球前15厘米内停下
    try:
        ug.load_models(['color_recognition'])
        if 靠近目标():
            ug.play_audio_tts("到啦，准备夹取", 0)
        else:
            ug.screen_print_text("没找到目标", 5)
        time.sleep(2)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾")
    finally:
        安全收尾()
        ug.release_models(['color_recognition'])

def 场景2_机械臂空跑演练():
    # 跑这个你会看到：机械臂依次做出 复位→伸手→合爪→抬起→放低→松爪→复位（⚠️ 地上先别放球！）
    复位()
    伸手()
    合爪()
    抬起()
    放低()
    松爪()
    复位()
    print("空跑结束：六个按钮都动了吗？")
    安全收尾()
    ug.mechanical_arms_restory()

def 场景3_完整取放():
    # 跑这个你会看到：工程车认出红球→开过去→伸手夹起→后退搬运→放下→手臂复位，屏幕"完成!"
    # （先空跑一次场景2 确认动作对了再放球；想加"先对准球再伸手"，看手册进阶挑战）
    try:
        ug.load_models(['color_recognition'])
        复位()                                   # 开工前手臂先回起始姿势
        ug.mechanical_clamp_release()            # ⚠️ 一定先张开爪，别对着球硬合
        if 靠近目标():
            ug.screen_print_text("夹取中", 3)
            ug.play_audio_tts("开始夹取", 0)
            time.sleep(1.5)                      # 让它说完再做，别挤在一起
            伸手(); 合爪(); 抬起()
            print("夹爪状态（应为 1）：", ug.mechanical_get_clamp_status())
            ug.mecanum_move_speed_times(1, 30, 搬运秒数, 0)   # 后退搬运到放置区（自动停）
            time.sleep(搬运秒数 + 0.5)           # ⚠️ 自动停 ≠ Python 等，自己等够
            ug.stop_chassis()
            放低(); 松爪(); 复位()
            ug.screen_print_text("完成!", 6)
            ug.show_light_rgb_effect(0, 255, 0, 0)           # 绿灯常亮 = 成功
            ug.play_audio_tts("放好啦，任务完成", 0)
        else:
            ug.screen_print_text("没找到目标", 5)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾")
    finally:
        安全收尾()
        ug.mechanical_arms_restory()             # 手臂一定要复位，别吊在半空
        ug.release_models(['color_recognition'])

# ============ 趣味加餐 ============

def 彩蛋1_机械臂三轴联动舞():
    # 跑这个你会看到：机械臂伸出去、右举、左举、举高高再收回，像在跳舞（先空跑，别放东西）
    ug.screen_print_text("臂舞!", 2)             # 2 = 紫
    复位()
    ug.mechanical_move_axis(15, 2, 0, 1000)      # 正前方伸手（r厘米 / h厘米 / theta弧度）
    time.sleep(1.2)
    ug.mechanical_move_axis(20, 6, 0.6, 1200)    # 右前方举高（theta 0.6 弧度 ≈ 34 度）
    time.sleep(1.4)
    ug.mechanical_move_axis(20, 6, -0.6, 1200)   # 左前方举高
    time.sleep(1.4)
    ug.mechanical_move_axis(15, 2, 0, 1000)      # 收回正前方
    time.sleep(1.2)
    ug.mechanical_joint_control(0, 80, 0, 900)   # 大臂举高高（关节2 上限 110）
    time.sleep(1.1)
    复位()
    安全收尾()
    ug.mechanical_arms_restory()

def 彩蛋2_双色球分类搬运():
    # 跑这个你会看到：认出红球/绿球并夹起来，按颜色送不同仓库（红=正后方，绿=右后方）
    目标们 = ["红色", "绿色"]    # ⚠️ 照你 print 出来的真实值改！
    找到的颜色 = ""
    try:
        ug.load_models(['color_recognition'])
        复位()
        ug.mechanical_clamp_release()
        for 一轮 in range(60):                   # 有界：最多找约 40 秒
            颜色结果 = ug.get_color_total_info()      # 返回【列表】，不要再 json.loads！
            距离 = ug.read_distance_data(1)
            if 颜色结果[0] in 目标们 and 距离 > 0:    # 距离 <= 0 是没读到，先别乱动
                找到的颜色 = 颜色结果[0]
                if 距离 < 15:
                    ug.stop_chassis()
                    break
                ug.mecanum_move_speed_times(0, 35, 1, 0)
                time.sleep(1 + 0.3)
            else:
                ug.stop_chassis()
            time.sleep(0.2)
        if 找到的颜色 == "":
            ug.screen_print_text("没找到球", 5)
        else:
            伸手(); 合爪(); 抬起()
            if 找到的颜色 == "红色":
                ug.play_audio_tts("红球，送去后方仓库", 0)
                ug.mecanum_move_speed_times(1, 30, 2, 0)         # 正后方
                time.sleep(2 + 0.5)
            else:
                ug.play_audio_tts("绿球，送去右侧仓库", 0)
                ug.mecanum_turn_speed_times(3, 120, 90, 2)       # 先右转 90 度（unit 2=度）
                time.sleep(90 / 120 + 0.3)
                ug.mecanum_move_speed_times(1, 30, 2, 0)         # 再后退到右后方
                time.sleep(2 + 0.5)
            ug.stop_chassis()
            放低(); 松爪(); 复位()
            ug.screen_print_text(找到的颜色 + " 分好啦", 6)
            ug.play_audio_tts("分类完成", 0)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾")
    finally:
        安全收尾()
        ug.mechanical_arms_restory()
        ug.release_models(['color_recognition'])

# ============ 想跑哪个，就去掉哪行前面的 # ============
场景2_机械臂空跑演练()    # ← 默认激活：原地空跑手臂，最安全（地上先别放球！）
# 场景1_认目标开过去()
# 场景3_完整取放()         # ← 本周大作品：红球 + 身后垫子当放置区
# 彩蛋1_机械臂三轴联动舞()
# 彩蛋2_双色球分类搬运()
