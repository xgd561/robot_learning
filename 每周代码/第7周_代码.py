# -*- coding: utf-8 -*-
# ============================================================
#  第7周 · 颜色与人物识别（工程车）—— 课堂代码备查 + 趣味加餐
#  知识点：列表取值 [0]、if/elif 分类反应、机械臂 7 个真方法
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
#  ⚠️ 工程车的轮子就是麦轮那套（mecanum_*），没有 engineer_ 前缀！
#  ⚠️ 机械臂动作范围内别放手和脸；第一次试角度先改小一半
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100

def 安全收尾():
    ug.stop_chassis()               # 急停
    ug.mechanical_arms_restory()    # 机械臂复位（工程车专属收尾）
    ug.turn_off_lights()
    ug.screen_clear()

# 【本周速记】get_color_total_info() 返回列表 [颜色,形状,x,y,高,宽,面积]，直接 [0] 取值，别 json.loads！
# 【本周速记】颜色名跟机器人语言走：中文机给'红色'，英文机给'red'——先 print 看真实值再写 ==
# 【本周速记】没认到颜色时第 0 格是空字符串 ''；人脸没认到时是空列表 []（len==0）
# 【本周速记】机械臂关节范围：关节1 −90~90、关节2 −80~110、关节3 −90~90、时长 20~5000 毫秒
# 【本周速记】mechanical_move / mechanical_turn 不存在！机械臂只有 7 个真方法（见本文件用到的）

# ============ 课堂代码复现 ============
def 场景1_认红绿球分类():
    """跑这个你会看到：红球入镜→红灯红字"红色!"+女声；换绿球→全变绿（车不动，只认色）"""
    ug.load_models(['color_recognition'])    # 装"颜色眼睛"（先装再读，顺序别反！）
    ug.mechanical_clamp_release()            # 夹爪先张开，等着夹球
    ug.screen_print_text("我在看颜色啦", 5)    # 5 = 黄
    上一次 = ""                               # 记住上次看到的颜色，避免一直重复念
    try:
        while True:
            颜色结果 = ug.get_color_total_info()   # 返回列表，直接下标取值
            颜色 = 颜色结果[0]                      # 第 0 格 = 颜色名
            if 颜色 == '':                          # 空字符串 = 这一下没认到任何颜色
                ug.screen_print_text("没看到颜色", 1)   # 1 = 白
                ug.turn_off_lights()
                上一次 = ""
            elif 颜色 != 上一次:                    # 只有颜色变了才反应
                上一次 = 颜色
                if 颜色 == '红色' or 颜色 == 'red':    # ← 以你 print 出来的真实值为准！
                    ug.screen_print_text("红色!", 3)   # 3 = 红
                    ug.show_light_rgb([0,1,2,3], 255, 0, 0)   # 红灯
                    ug.play_audio_tts("这是红色", 0)
                elif 颜色 == '绿色' or 颜色 == 'green':
                    ug.screen_print_text("绿色!", 6)   # 6 = 绿
                    ug.show_light_rgb([0,1,2,3], 0, 255, 0)   # 绿灯
                    ug.play_audio_tts("这是绿色", 0)
                else:
                    ug.screen_print_text("看到:" + str(颜色), 5)
                    ug.turn_off_lights()
            time.sleep(0.1)                         # 歇一下再看，别把机器人累坏
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()

def 场景2_认出红球夹起来():
    """跑这个你会看到：认出红球→屏幕红字+语音→机械臂伸过去→咔哒合爪→打印夹爪状态 1"""
    ug.load_models(['color_recognition'])
    ug.mechanical_arms_restory()        # 手臂先回到起始姿势（每次开工前必做）
    time.sleep(1)
    ug.mechanical_clamp_release()       # 夹爪张开
    ug.screen_print_text("给我红球", 5)
    try:
        while True:
            颜色 = ug.get_color_total_info()[0]     # 只取第 0 格：颜色名
            if 颜色 == '红色' or 颜色 == 'red':      # ← 照步骤①打印的真实值改！
                ug.screen_print_text("夹起来!", 3)
                ug.play_audio_tts("我夹到红色了", 0)
                # 三个关节一起动：30/20/-40 都是手册核实的范围内的值，800 毫秒到位
                ug.mechanical_joint_control(30, 20, -40, 800)
                time.sleep(1)                        # 等手臂到位再合爪
                ug.mechanical_clamp_close()          # 合上夹爪
                time.sleep(0.5)
                print("夹爪状态：", ug.mechanical_get_clamp_status())   # 1 = 已合上
                break                                # 夹到了就退出循环
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()

# ============ 趣味加餐 ============
def 彩蛋1_夹娃娃机演示():
    """跑这个你会看到：张开→合爪夹住→手臂抬起→车前进一段→松爪放下→手臂归位，一气呵成"""
    ug.mechanical_arms_restory()        # 开工先复位
    time.sleep(1)
    try:
        ug.screen_print_text("夹娃娃开始", 5)
        ug.play_audio_tts("看我的", 0)
        ug.mechanical_clamp_release()                  # ① 夹爪张开
        time.sleep(0.5)
        ug.mechanical_clamp_close()                    # ② 合爪"夹住"娃娃
        time.sleep(0.5)
        print("夹爪状态：", ug.mechanical_get_clamp_status())
        ug.mechanical_joint_control(0, 60, -40, 1000)  # ③ 三关节一起把娃娃抬起来
        time.sleep(1.3)                                # 等 1000 毫秒到位
        ug.screen_print_text("搬运中", 6)
        ug.mecanum_move_speed_times(0, 30, 1, 0)       # ④ 底盘前进 1 秒自动停（工程车底盘=麦轮）
        time.sleep(1.3)                                # _times 不阻塞 Python，必须等它真停稳！
        ug.screen_print_text("放下啦", 3)
        ug.mechanical_clamp_release()                  # ⑤ 松爪放下
        time.sleep(0.5)
        ug.play_audio_tts("送货成功", 0)
    except KeyboardInterrupt:
        print("你点了停止，正在收尾…")
    finally:
        安全收尾()                                     # ⑥ 收尾里就有机械臂归位

def 彩蛋2_人脸录入喊名():
    """跑这个你会看到：屏幕倒数 3 秒拍你的脸存成"爸爸"，之后认出你就喊"你好 爸爸"（约 30 秒）"""
    ug.face_recognition_add_name("爸爸")   # 它自己会：装模型→开摄像头→倒数 3 秒→拍照上传
    time.sleep(1)                          # 等它把这张脸存好
    print("已录入的脸：", ug.face_recognition_get_all_names())
    ug.load_models(['face_recognition'])   # 装"人脸眼睛"再开始认人
    ug.screen_print_text("谁来了?", 5)
    上一次 = ""
    try:
        for 第几眼 in range(300):          # 有界循环：约 30 秒后自动结束
            人脸结果 = ug.get_face_recognition_total_info()   # 二维列表 [[名字,x,y,高,宽,面积],...]
            if len(人脸结果) == 0:         # 一张脸都没有 → 空列表 []
                ug.screen_print_text("没看到脸", 1)
                ug.turn_off_lights()
                上一次 = ""
            else:
                名字 = 人脸结果[0][0]      # 第 1 张脸的第 0 格 = 名字
                if 名字 != 上一次:         # 只有"换人"了才打招呼
                    上一次 = 名字
                    if 名字 == '陌生人' or 名字 == 'Unknown':   # 有脸但没录入过 = 翻译值
                        ug.screen_print_text("脸熟但没名字", 4)   # 4 = 橙
                        ug.play_audio_tts("你是谁呀", 0)
                    else:
                        ug.screen_print_text("你好 " + 名字, 6)
                        ug.show_light_rgb([0,1,2,3], 0, 255, 0)   # 绿灯欢迎
                        ug.play_audio_tts("你好 " + 名字, 0)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你点了停止，正在收尾…")
    finally:
        安全收尾()

def 彩蛋3_底盘蟹行舞():
    """跑这个你会看到：工程车像螃蟹一样右移→左移→右移→左移，纯横移不转身，最后回到原地"""
    try:
        ug.screen_print_text("螃蟹舞", 7)     # 7 = 青
        ug.play_audio_tts("螃蟹跳舞", 0)
        for 角度, 方向名 in [(90, "右"), (-90, "左"), (90, "右"), (-90, "左")]:
            ug.screen_print_text("横移" + 方向名, 5)
            # 角度 -180~180（90=右横移，-90=左横移）；速度 5~80；走 1 秒自动停
            ug.mecanum_translate_speed_times(角度, 30, 1, 0)
            time.sleep(1.3)                    # 等它真停稳再下一个动作
    except KeyboardInterrupt:
        print("你点了停止，正在收尾…")
    finally:
        安全收尾()

# ============ 想跑哪个，就去掉哪行前面的 # ============
场景1_认红绿球分类()      # ← 默认激活：本周最安全（车不移动，只认颜色）
# 场景2_认出红球夹起来()
# 彩蛋1_夹娃娃机演示()
# 彩蛋2_人脸录入喊名()
# 彩蛋3_底盘蟹行舞()
