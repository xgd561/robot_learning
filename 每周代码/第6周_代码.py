# -*- coding: utf-8 -*-
# ============================================================
#  第6周 · 真AI手势遥控（轮足）—— 课堂代码备查 + 趣味加餐
#  知识点：加载 AI 模型 load_models、读 JSON、字符串比较 ==
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
#  ⚠️ 轮足靠自平衡站着走：动它之前必须 wheelleg_start_balancing()！
#  ⚠️ 认手势靠摄像头：正面对手、光线亮一点、手离镜头 30~60cm 最准
#  ⚠️ 点编辑器"停止"不会让机器人停——先比"点赞"让它停，或用带 finally 的场景
# ============================================================
from ugot import ugot
import json                     # 拆"原始 JSON 纸条"才用它（路 B 专用）
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100

def 安全收尾():
    ug.stop_chassis()              # 第 1 件事永远是停车
    ug.wheelleg_stop_balancing()   # 停自平衡
    ug.wheelleg_restory()          # 回到中等高度的初始姿势
    ug.turn_off_lights()
    ug.screen_clear()
    ug.release_models(['gesture']) # 请 AI 专家去睡觉（没加载过也不碍事）

def 看手势():
    """读手势·稳定版：拿到返回英文暗号 stone/scissor/palm/ok/good，拿不到返回 ''"""
    raw = ug.VISION.gesture_inference()   # 原始 JSON 纸条（还是一串文字）
    if not raw:
        return ''                          # 什么都没返回（模型没加载 / 摄像头忙）
    data = json.loads(raw) or {}           # json.loads 把纸条拆成字典（抽屉柜）
    return data.get('gesture') or ''       # 拉开 'gesture' 抽屉取暗号；认不出是 ''

# 【本周速记】模型没 load_models 就读结果 → 永远拿到空值 / None，程序不报错（头号大坑！）
# 【本周速记】判断用路 B（恒英文 stone/scissor/palm/ok/good）；只是念出来可用路 A get_gesture_result()
# 【本周速记】路 A 的值跟机器人语言走：中文机给"石头/剪刀/布/OK/点赞"，永远不给 'palm'！
# 【本周速记】轮足限速：前进 5~60、转弯 5~180，写超了被悄悄压到上限（没报错不等于生效）

# ============ 课堂代码复现 ============
def 场景1_手势遥控器():
    """跑这个你会看到：轮足站好后，比手掌前进、点赞停、剪刀左转、OK右转、石头后退"""
    try:
        print("加载模型：", ug.load_models(['gesture']))   # 每次 Run 都要重新叫醒专家！
        ug.wheelleg_start_balancing()   # ① 先站起来保持平衡（不站好它就不理你）
        time.sleep(2)                   # ② 留 2 秒站稳
        ug.screen_display_emotion("Search")   # 屏幕"找找看"：正在等你的手势
        while True:
            手势 = 看手势()
            print("看到：", 手势)                  # ★ 调试用：暗号对不对，一眼看穿
            if 手势 == 'palm':                     # 手掌 → 前进（轮足走 5~60）
                ug.wheelleg_move_speed(0, 40)
                ug.screen_print_text("前进", 6)     # 6 = 绿
            elif 手势 == 'good':                   # 点赞 → 停
                ug.stop_chassis()
                ug.screen_print_text("停", 3)      # 3 = 红
            elif 手势 == 'scissor':                # 剪刀 → 左转（轮足转 5~180）
                ug.wheelleg_turn_speed(2, 120)
                ug.screen_print_text("左转", 5)    # 5 = 黄
            elif 手势 == 'ok':                     # OK → 右转
                ug.wheelleg_turn_speed(3, 120)
                ug.screen_print_text("右转", 8)    # 8 = 蓝
            elif 手势 == 'stone':                  # 石头 → 后退
                ug.wheelleg_move_speed(1, 40)
                ug.screen_print_text("后退", 2)    # 2 = 紫
            else:                                  # 认不出 / 没手 → 先停，最安全
                ug.stop_chassis()
                ug.screen_print_text("等你比手势", 1)   # 1 = 白
            time.sleep(0.1)                        # 歇 0.1 秒，别让小专家太累
    except KeyboardInterrupt:
        print("你按了停止 → 手动急停")
    except Exception as 错误:                      # 不用裸 except，把真错误念出来
        print("出问题了，先急停：", 错误)
    finally:
        安全收尾()

def 场景2_两条读法比一比():
    """跑这个你会看到：镜头前比个手势，输出区同时打印 路 A（随语言变）和 路 B（恒英文）"""
    print("加载模型：", ug.load_models(['gesture']))
    ug.screen_print_text("比个手势", 5)        # 5 = 黄
    time.sleep(1)
    手势A = ug.get_gesture_result()            # 路 A：SDK 已拆好，值跟机器人语言变（不用 json.loads）
    raw = ug.VISION.gesture_inference()        # 路 B：原始纸条自己拆
    手势B = json.loads(raw).get('gesture') if raw else ''
    print("路A（简单版，随语言）→", 手势A)      # ★ 写 if == 之前一定先 print 看真实值！
    print("路B（稳定版，恒英文）→", 手势B)
    ug.screen_print_text("B:" + str(手势B), 6)
    ug.play_audio_tts(str(手势A), 0)
    安全收尾()

# ============ 趣味加餐 ============
def 彩蛋1_手势点播表情():
    """跑这个你会看到：换着比手势，机器人换不同表情+夸你一句（约 30 秒后自动结束）"""
    print("加载模型：", ug.load_models(['gesture']))
    上一个 = ""                                  # 记住上一个手势，认出"新的"才反应，不啰嗦
    try:
        for 第几眼 in range(300):               # 有界循环：约 30 秒，到点自动结束
            手势 = 看手势()
            if 手势 != "" and 手势 != 上一个:
                上一个 = 手势
                if 手势 == 'palm':
                    ug.screen_display_emotion("Smile")
                    ug.play_audio_tts("击掌，好朋友", 0)
                elif 手势 == 'good':
                    ug.screen_display_emotion("Proud")
                    ug.play_audio_tts("点赞小达人", 0)
                elif 手势 == 'ok':
                    ug.screen_display_emotion("Love")
                    ug.play_audio_tts("比心成功", 0)
                elif 手势 == 'stone':
                    ug.screen_display_emotion("Anger")
                    ug.play_audio_tts("石头好硬呀", 0)
                elif 手势 == 'scissor':
                    ug.screen_display_emotion("Blink")
                    ug.play_audio_tts("咔嚓咔嚓", 0)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你点了停止 → 手动急停")
    finally:
        安全收尾()

def 彩蛋2_变身高矮秀():
    """跑这个你会看到：轮足站好后蹲下→中等→长高挨个切换，最后复位（不出脚走）"""
    try:
        ug.wheelleg_start_balancing()   # 先站稳
        time.sleep(2)
        for 高度, 名字 in [(3, "低"), (2, "中"), (1, "高"), (2, "中"), (3, "低")]:
            ug.wheelleg_set_chassis_height(高度)   # 只能整数：1 高 / 2 中 / 3 低
            ug.screen_print_text("变" + 名字, 5)
            ug.play_audio_tts("我变" + 名字 + "啦", 0)
            time.sleep(2)
    except KeyboardInterrupt:
        print("你点了停止 → 手动急停")
    finally:
        安全收尾()

# ============ 想跑哪个，就去掉哪行前面的 # ============
场景2_两条读法比一比()    # ← 默认激活：本周最安全（不站不走，只认手势）
# 场景1_手势遥控器()
# 彩蛋1_手势点播表情()
# 彩蛋2_变身高矮秀()
