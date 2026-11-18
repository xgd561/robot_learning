# -*- coding: utf-8 -*-
# ============================================================
#  第5周 · 灯光与声音（四足狗）—— 课堂代码备查 + 趣味加餐
#  知识点：列表 list、RGB 颜色、函数组合（def）
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
#  ⚠️ 空旷平整干爽的地面玩；狗怕软地面，清掉地毯边和电线
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100（写 3 几乎听不见）

def 安全收尾():
    ug.stop_chassis()          # 急停
    ug.turn_off_lights()       # 关灯（红灯一直闪很耗电）
    ug.screen_clear()          # 清屏
    ug.dog_restory()           # 让狗回到初始站姿

# 【本周速记】参数写错时 SDK 只 print 一行 TypeError，机器人不动、程序不崩——先看输出区！
# 【本周速记】屏幕颜色是整数：0黑 1白 2紫 3红 4橙 5黄 6绿 7青 8蓝（不是 "FF..." 十六进制！）
# 【本周速记】灯带编号列表只能填 0~3（0顶 1左 2右 3底）；RGB 三个数是 0~255
# 【本周速记】show_light_rgb_effect(红,绿,蓝,效果)：0 常亮 / 1 关 / 2 呼吸 / 3 闪烁（没有灯带列表参数）
# 【本周速记】狗的速度上限：前进 0~25、转弯 0~20，写超了会被悄悄压到上限（没报错不等于生效）

# ============ 课堂代码复现 ============
def 场景1_灯光小秀场():
    """跑这个你会看到：狗站好挂上笑脸，灯带红→蓝→左右黄→绿灯呼吸→红灯闪烁，最后全灭"""
    ug.dog_restory()
    time.sleep(1)
    ug.screen_display_emotion("Smile")
    ug.show_light_rgb([0,1,2,3], 255, 0, 0)   # 四条灯带一起红灯（列表 = 一排带编号的抽屉）
    time.sleep(1)
    ug.turn_off_lights()                       # 灭一下
    ug.show_light_rgb([0,1,2,3], 0, 0, 255)   # 蓝灯
    time.sleep(1)
    ug.show_light_rgb([1,2], 255, 255, 0)     # 只亮左、右两条（黄）
    time.sleep(1)
    ug.show_light_rgb_effect(0, 255, 0, 2)    # 绿灯呼吸（效果 2，机器人自己呼吸，不用写循环）
    time.sleep(3)
    ug.show_light_rgb_effect(255, 0, 0, 3)    # 红灯闪烁（效果 3，报警就靠它）
    time.sleep(3)
    安全收尾()
    print("灯光秀结束！")

def 报警():
    """把「闪灯 + 变脸 + 喊话」打包成一个按钮（函数组合：想改报警动作只改这一处）"""
    ug.show_light_rgb_effect(255, 0, 0, 3)        # ① 红灯狂闪
    ug.screen_print_text("警报!", 3)              # ② 屏幕红字（3 = 红，整数 0~8）
    ug.screen_display_emotion("Anger")            # ③ 换出生气的脸
    ug.play_audio_tts("前方有障碍，请绕行", 0)      # ④ 女声喊话（1 = 男声）
    time.sleep(3)                                 # ⑤ 留 3 秒把话说完、灯闪够

def 场景2_会报警的巡逻狗():
    """跑这个你会看到：狗绿灯呼吸笑眯眯巡逻，前方 30cm 内急停 + 红闪 + 生气脸 + 喊话"""
    安全距离 = 30
    try:
        ug.dog_restory()
        ug.screen_display_emotion("Smile")        # 开心上班
        while True:
            距离 = ug.read_distance_data(1)        # TOF 测距，单位厘米
            if 距离 == -1 or 距离 == 0:            # 没读数绝不能当成"安全"
                ug.stop_chassis()
                ug.show_light_rgb_effect(255, 165, 0, 2)   # 橙色呼吸 = 我有点看不清
                ug.screen_print_text("看不清", 4)          # 4 = 橙
                time.sleep(0.5)
                continue
            if 距离 < 安全距离:                    # -1 < 30 是 True，所以必须先挡掉 -1！
                ug.stop_chassis()                  # 先急停！安全第 1
                报警()                             # 按一下"报警按钮"
                break                              # 本次演示结束
            ug.dog_move_speed(0, 15)               # 平时前进巡逻（狗速度 0~25）
            ug.show_light_rgb_effect(0, 255, 0, 2) # 平时绿灯呼吸
            time.sleep(0.1)                        # 歇 0.1 秒，别把它累着
    except KeyboardInterrupt:
        print("你点了停止 → 手动急停")
    except Exception as 错误:                      # 不用裸 except，把真错误念出来
        print("出错了，先急停：", 错误)
    finally:                                       # 不管怎么结束，都执行收尾
        安全收尾()

# ============ 趣味加餐 ============
def 彩蛋1_狗狗动作表演秀():
    """跑这个你会看到：狗挨个表演握手→伸懒腰→爬行→蹲下→站起，屏幕换表情+语音报幕"""
    动作单 = [("handshake", "握手", "Proud"),
             ("stretch", "伸懒腰", "Breathe"),
             ("crawling", "匍匐爬", "Doubt"),
             ("squatting", "蹲下", "Sleep"),
             ("standing", "站起", "WakeUp")]
    try:
        ug.dog_restory()
        time.sleep(1)
        for 动作名, 中文名, 表情名 in 动作单:
            ug.screen_display_emotion(表情名)
            ug.play_audio_tts("看我" + 中文名 + "!", 0)
            ug.dog_perform_action(动作名)   # 动作名是字符串，要加引号
            time.sleep(3)                   # 等它把动作做完（做完再报下一个）
    except KeyboardInterrupt:
        print("你点了停止 → 手动急停")
    finally:
        安全收尾()

def 彩蛋2_彩虹呼吸灯():
    """跑这个你会看到：灯带颜色红→黄→绿→青→蓝慢慢转一圈，像彩虹在打转（狗不动）"""
    ug.screen_display_emotion("Love")
    try:
        for 色相 in range(0, 101, 10):                  # 色相 hue：0~100（不是 0~360！）
            ug.show_light_hsv([0,1,2,3], 色相, 100, 100)   # 三个参数全都是 0~100
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("你点了停止 → 手动急停")
    finally:
        安全收尾()

def 彩蛋3_音符小曲():
    """跑这个你会听到：机器人用蜂鸣器奏《小星星》开头，屏幕同步跳音符（狗不动）"""
    小星星 = [("C5", 3), ("C5", 3), ("G5", 3), ("G5", 3),
             ("A5", 3), ("A5", 3), ("G5", 4),
             ("F5", 3), ("F5", 3), ("E5", 3), ("E5", 3),
             ("D5", 3), ("D5", 3), ("C5", 4)]
    try:
        ug.screen_print_text("演奏中", 6)
        for 音符, 拍数 in 小星星:
            ug.screen_print_text("音符 " + 音符, 5)
            ug.play_tone(音符, 拍数)    # 音符 C5~B5、C6；拍：0=1/8 1=1/4 2=1/2 3=1拍 4=2拍
            time.sleep(0.7 if 拍数 == 3 else 1.1)   # 等这个音放完再放下一个
    except KeyboardInterrupt:
        print("你点了停止 → 手动急停")
    finally:
        安全收尾()

# ============ 想跑哪个，就去掉哪行前面的 # ============
场景1_灯光小秀场()        # ← 默认激活：本周最安全（狗不走路，只玩灯）
# 场景2_会报警的巡逻狗()
# 彩蛋1_狗狗动作表演秀()
# 彩蛋2_彩虹呼吸灯()
# 彩蛋3_音符小曲()
