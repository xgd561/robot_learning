# -*- coding: utf-8 -*-
# ============================================================
#  第9周 · 综合整合：巡线 + 避障 + 手势遥控（麦轮车）—— 课堂代码备查 + 趣味加餐
#  知识点：三关叠加做综合项目（巡线 / TOF 避障 / 手势模式切换）+ 麦轮专属 move_xyz、translate_speed
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
# ============================================================
from ugot import ugot
import json          # 本周读手势要用：ug.VISION.gesture_inference() 给的是原始 JSON 纸条
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)              # 音量 0~100，写 3 几乎听不见

def 安全收尾():
    ug.stop_chassis()
    ug.turn_off_lights()
    ug.screen_clear()

# ============ 课堂代码复现 ============

def 巡线一步(前进速度, 修正速度, 阈值):
    """三关共用的巡线积木：读一次巡线结果并打方向（返回【列表】，直接下标取，不要 json.loads）"""
    信息 = ug.get_single_track_total_info()   # [偏移量, 线型, x, y]；线型 1直/2Y字/3十字/0没线
    if 信息[1] == 0:                          # 没看到线：先停，别乱冲
        ug.stop_chassis()
        ug.screen_print_text("找线", 5)       # 5 = 黄
    elif 信息[0] > 阈值:
        ug.mecanum_turn_speed(3, 修正速度)    # 3=右转（5~280；正负修偏方向以你车实测为准）
    elif 信息[0] < -阈值:
        ug.mecanum_turn_speed(2, 修正速度)    # 2=左转
    else:
        ug.mecanum_move_speed(0, 前进速度)    # 基本居中：直走（5~80）

# —— 场景1（关1）：纯巡线 ——
def 场景1_纯巡线():
    # 跑这个你会看到：机器人沿黑线自己走，线偏了它会自己修回来（要先在地上贴一条黑线）
    ug.load_models(['line_recognition'])      # 装"认黑线"模型（返回 True 才算装上）
    ug.set_track_recognition_line(0)          # 别漏：0=单轨 / 1=双轨；漏了永远"没线"且不报错
    ug.screen_print_text("巡线准备", 5)
    前进速度 = 30   # mecanum_move_speed 允许 5~80
    修正速度 = 90   # mecanum_turn_speed 允许 5~280
    阈值 = 10       # 偏移量比它还小，就当"正对着"
    try:
        while True:
            巡线一步(前进速度, 修正速度, 阈值)
            time.sleep(0.1)                   # 每圈喘口气，必写
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.release_models(['line_recognition'])

# —— 场景2（关2）：巡线 + 避障 ——
def 场景2_巡线加避障():
    # 跑这个你会看到：巡线中遇墙（<30cm）自动停、红灯闪、只喊一遍"前方有障碍"；挪开又接着走
    ug.load_models(['line_recognition'])
    ug.set_track_recognition_line(0)          # ← 又别漏
    安全距离 = 30
    前进速度 = 30
    修正速度 = 90
    阈值 = 10
    报警中 = False   # 开关变量：保证一次障碍只喊一遍，不当复读机
    try:
        while True:
            距离 = ug.read_distance_data(1)   # TOF 厘米（浮点），没读到 -1（也可能 0）
            if 距离 != -1 and 距离 != 0 and 距离 < 安全距离:   # 🥇保命：真读到、而且很近
                ug.stop_chassis()
                ug.screen_print_text("障碍!", 3)              # 3 = 红
                ug.show_light_rgb_effect(255, 0, 0, 3)        # 红灯闪烁（effect 3=闪，一行搞定）
                if not 报警中:
                    ug.play_audio_tts("前方有障碍", 0)        # 0 = 女声
                    报警中 = True
            else:                              # 没障碍（含读不到=前方空旷）→ 继续巡线
                if 报警中:                     # 障碍刚挪走：恢复绿灯，下次还能再喊
                    报警中 = False
                    ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)
                巡线一步(前进速度, 修正速度, 阈值)
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.release_models(['line_recognition'])

# —— 场景3（关3 · 终极整合）：巡线 + 避障 + 手势遥控（本周大作品）——
def 场景3_巡线避障手势整合():
    # 跑这个你会看到（验收五步）：巡线中（绿灯）→ 遇障停（红闪+喊话）→ 比手掌切手动（青灯）→
    #   比剪刀/OK 指挥转弯、比手掌绕开障碍（转可以、撞不行）→ 比石头回巡线
    print("模型装上了吗：", ug.load_models(['line_recognition', 'gesture']))   # 一次叫两个专家
    ug.set_track_recognition_line(0)          # ← 还是别漏
    安全距离 = 30
    前进速度 = 30
    修正速度 = 90
    转向速度 = 120   # 手动时原地转，允许 5~280
    阈值 = 10
    手动模式 = False # 状态开关：只有 palm 能进、只有 stone 能出
    报警中 = False
    def 看手势():
        """路 B：读原始 JSON，返回值恒为 stone/scissor/palm/ok/good，认不出给空字符串"""
        raw = ug.VISION.gesture_inference()   # 原始纸条可能是空的，直接 loads 会报错，先兜住
        if not raw:
            return ''
        return (json.loads(raw) or {}).get('gesture') or ''
    try:
        while True:
            手势 = 看手势()                    # ① 先问：人要不要抢方向盘？
            if 手势 == 'palm' and not 手动模式:
                手动模式 = True
                ug.play_audio_tts("手动模式", 0)
            elif 手势 == 'stone' and 手动模式:
                手动模式 = False
                ug.play_audio_tts("回到巡线", 0)
            距离 = ug.read_distance_data(1)
            有障碍 = 距离 != -1 and 距离 != 0 and 距离 < 安全距离
            if 有障碍 and not 手动模式:        # ② 🥇保命：自动驾驶时近=立刻停
                ug.stop_chassis()
                ug.screen_print_text("障碍!", 3)
                ug.show_light_rgb_effect(255, 0, 0, 3)
                if not 报警中:
                    ug.play_audio_tts("前方有障碍", 0)
                    报警中 = True
            elif 手动模式:                     # ③ 🥈听人：比什么做什么（转可以、撞不行）
                报警中 = False
                ug.show_light_rgb([0, 1, 2, 3], 0, 255, 255)   # 青灯 = 我在听你的
                ug.screen_print_text("手动", 5)
                if 手势 == 'palm' and not 有障碍:   # 手掌=前进，但前面有东西不给走
                    ug.mecanum_move_speed(0, 前进速度)
                elif 手势 == 'scissor':             # 剪刀=原地左转
                    ug.mecanum_turn_speed(2, 转向速度)
                elif 手势 == 'ok':                  # OK=原地右转
                    ug.mecanum_turn_speed(3, 转向速度)
                else:                               # good/没手势/前方有障碍：立正待着
                    ug.stop_chassis()
            else:                              # ④ 🥉干活：交给巡线
                报警中 = False
                ug.show_light_rgb([0, 1, 2, 3], 0, 255, 0)     # 常亮绿灯
                巡线一步(前进速度, 修正速度, 阈值)
            time.sleep(0.2)                    # 手势和判断不用一秒看十几次
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()
        ug.release_models(['line_recognition', 'gesture'])     # 两个专家都送走

# ============ 趣味加餐 ============

# —— 彩蛋1：方块走位（麦轮专属 move_xyz：x 左右 / y 前后 / z 原地转）——
def 彩蛋1_方块走位():
    # 跑这个你会看到：小车不用掉头也能平移——前→右→后→左走一个方块，最后原地转圈谢幕，共演 2 轮
    ug.screen_print_text("方块舞步", 7)    # 7 = 青
    ug.play_audio_tts("看我走位", 0, True) # True = 说完再动
    舞步 = [(0, 40, 0, 2), (40, 0, 0, 1.5), (0, -40, 0, 2), (-40, 0, 0, 1.5)]   # (x, y, z, 秒)
    try:
        for 轮数 in range(2):              # 有界循环：演 2 轮自动收工
            for x, y, z, 秒 in 舞步:
                ug.mecanum_move_xyz(x, y, z)   # x/y 范围 -80~80，z 范围 -280~280
                time.sleep(秒)
                ug.stop_chassis()          # move_xyz 不会自己停，要喊停
                time.sleep(0.3)
            ug.mecanum_move_xyz(0, 0, 120) # 最后原地转 3 秒谢幕
            time.sleep(3)
            ug.stop_chassis()
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()

# —— 彩蛋2：斜 45° 走位秀（麦轮专属 translate_speed：车头不转、斜着飘）——
def 彩蛋2_斜45度走位():
    # 跑这个你会看到：斜 45° 飘出去 → 原地掉头 → 再斜 45° 飘回出发点 → 转回原朝向（平移方向永远跟着车头）
    ug.screen_print_text("斜走位", 8)      # 8 = 蓝
    try:
        for 轮数 in range(2):              # 有界循环
            for 自转 in [120, -120]:       # 第一圈掉头约 180°，第二圈转回原朝向
                ug.mecanum_translate_speed(45, 40)   # 右前方 45° 飘（角度 -180~180 左负右正，速度 5~80）
                time.sleep(1.5)
                ug.stop_chassis()
                time.sleep(0.3)
                ug.mecanum_move_xyz(0, 0, 自转)      # 原地自转（120 度/秒 × 1.5 秒 ≈ 180°）
                time.sleep(1.5)
                ug.stop_chassis()
                time.sleep(0.3)
    except KeyboardInterrupt:
        print("你按了停止，正在收尾…")
    finally:
        安全收尾()

# ============ 想跑哪个，就去掉哪行前面的 # ============
彩蛋1_方块走位()      # ← 默认激活：本周最安全（空地有界演示，不用贴线不用模型）
# 场景1_纯巡线()      # 要先在地上贴一条黑线
# 场景2_巡线加避障()  # 黑线 + 一个纸箱当障碍
# 场景3_巡线避障手势整合()   # 本周大作品：黑线 + 障碍 + 手势切模式（验收五步）
# 彩蛋2_斜45度走位()
