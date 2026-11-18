# -*- coding: utf-8 -*-
# ============================================================
#  第4周 · 传感器与判断（蜘蛛）—— 课堂代码备查 + 趣味加餐
#  知识点：TOF 测距、if/elif/else、布尔值 True/False、while True、try/except 安全网
#  ⚠️ 蜘蛛限速：走 0~25、转 0~60（超了被悄悄压上限，不报错）；
#     走里的 2/3 是"左右平移"（螃蟹步），左右转要用 spider_turn_speed！
#  用法：每个场景都是一个函数。想跑哪个，到文件最底部把那行
#        前面的 # 去掉，再点 Run（一次只跑一个！）
#  ⚠️ 先把下面的 IP 换成你机器人「设置→关于」里的真实 IP！
# ============================================================
from ugot import ugot
import time

ug = ugot.UGOT()
ug.initialize("192.168.x.x")   # ←←← 换成你的机器人 IP
ug.set_volume(60)

def 安全收尾():
    # 每个场景跑完都叫它一声：停车 + 关灯 + 擦屏幕
    ug.stop_chassis()
    ug.turn_off_lights()
    ug.screen_clear()

def 蜘蛛收工():
    # 蜘蛛专属收尾：停稳后把四条腿摆回标准站姿
    安全收尾()
    ug.spider_restory()

# ============ 课堂代码复现 ============

def 场景1_读一次距离_眼睛测试():
    # 跑这个你会看到：编辑器打印距离、屏幕红色数字、女声念出来（不动腿，最安全）
    ug.spider_restory()                # 运动前先把四条腿摆回标准站姿
    距离 = ug.read_distance_data(1)    # TOF 眼睛：厘米带小数，最远 150
    print("读到的距离：", 距离)        # 没读到是 -1（也可能 0），别慌
    ug.screen_print_text(str(距离), 3) # 颜色必须是 0~8 整数，3 = 红
    ug.play_audio_tts(str(距离), 0)    # 0 = 女声
    time.sleep(2)
    蜘蛛收工()

def 场景2_课堂项目_避障巡逻():
    # 跑这个你会看到：蜘蛛对墙走，30cm 处红字 STOP 自己停下；空旷处黄「?」保守停；
    #                 离得远绿字 GO 慢慢走。在编辑器点「停止运行」才退出
    # ⚠️ 运动！正前方 1~2 米内要有墙或大纸板，路上别有桌角/台阶/宠物
    ug.spider_restory()
    安全距离 = 30                       # 厘米：前方小于这个就停
    try:
        while True:                     # 一直看路，直到你喊停
            距离 = ug.read_distance_data(1)
            print("距离 =", 距离)       # 边跑边打，看它到底读到几
            if 距离 == -1 or 距离 == 0:
                ug.stop_chassis()                # 读不到 = "瞎了"：宁可停，不要闯
                ug.screen_print_text("?", 5)     # 5 = 黄：我在发呆
            elif 距离 < 安全距离:
                ug.stop_chassis()                # 真的离墙太近，停！
                ug.screen_print_text("STOP", 3)  # 3 = 红
            else:
                ug.spider_move_speed(0, 15)      # 安全：慢慢前进（蜘蛛上限 25）
                ug.screen_print_text("GO", 6)    # 6 = 绿
            time.sleep(0.1)             # ★ 必写：一秒看 10 次刚刚好，没有它会卡
    except KeyboardInterrupt:
        print("你按了停止，程序退出循环。")
    except Exception as 错误:           # 别写光秃秃的 except:，要把真话念出来
        print("出意外了，真实原因是：", 错误)
    finally:                            # 保险绳：不管走哪条路都保证急停
        蜘蛛收工()
        print("急停完成，安全第一。")

# ============ 趣味加餐 ============

def 彩蛋1_螃蟹步():
    # 跑这个你会看到：蜘蛛横着向左溜 2 秒、再向右溜 2 秒——四条腿才有的独门本事
    # ⚠️ 运动！左右要留出 1 米空间
    ug.spider_restory()
    ug.screen_print_text("螃蟹步", 7)   # 7 = 青
    ug.spider_move_speed(2, 15)         # 走里的 2 = 向左平移（不是左转！）
    time.sleep(2)
    ug.stop_chassis()                   # 不带 _times 的要走完手动喊停
    time.sleep(0.5)
    ug.spider_move_speed(3, 15)         # 3 = 向右平移
    time.sleep(2)
    ug.stop_chassis()
    蜘蛛收工()

def 彩蛋2_原地转一圈():
    # 跑这个你会看到：蜘蛛原地自转整整一圈（360 度）后稳稳停住
    # ⚠️ 运动！
    ug.spider_restory()
    ug.screen_print_text("转圈圈", 2)   # 2 = 紫
    ug.spider_turn_speed_times(2, 40, 360, 2)   # 左转 / 速度40(上限60) / 360 / 单位2=度
    time.sleep(9.3)                     # 40 度/秒转 360 度要 9 秒，Python 得陪它等
    ug.stop_chassis()
    蜘蛛收工()

def 彩蛋3_贴脸报警():
    # 跑这个你会看到：你拿手/盒子慢慢靠近它的"眼睛"，越近灯越红、女声报出距离数字；
    #                 测满 10 轮自动结束，不用你喊停
    ug.spider_restory()
    for 轮数 in range(10):              # 有界循环：只测 10 轮，跑得完
        距离 = ug.read_distance_data(1)
        print("第", 轮数 + 1, "轮距离 =", 距离)
        if 距离 == -1 or 距离 == 0:
            ug.show_light_rgb_effect(255, 0, 0, 3)   # 读不到也当危险：红灯闪
            ug.screen_print_text("?", 5)
        elif 距离 < 20:
            ug.show_light_rgb_effect(255, 0, 0, 3)   # 贴脸：红灯闪（效果 3=闪烁）
            ug.screen_print_text("危险!", 3)
        elif 距离 < 50:
            ug.show_light_rgb_effect(255, 0, 0, 0)   # 有点近：红灯常亮（效果 0=常亮）
            ug.screen_print_text("注意", 4)
        else:
            ug.show_light_rgb_effect(0, 255, 0, 0)   # 安全：绿灯常亮
            ug.screen_print_text("安全", 6)
        ug.play_audio_tts(str(距离), 0)  # 女声把距离数字念出来
        time.sleep(1)                    # 歇一拍再测下一轮（比 0.1 更从容）
    蜘蛛收工()

# ============ 想跑哪个，就去掉哪行前面的 # ============
场景1_读一次距离_眼睛测试()    # ← 默认激活：只读眼睛不动腿，最安全
# 场景2_课堂项目_避障巡逻()     # 运动！先清场、正对墙、第一次用手虚扶
# 彩蛋1_螃蟹步()                # 运动！
# 彩蛋2_原地转一圈()            # 运动！
# 彩蛋3_贴脸报警()              # 不动腿，但要拿东西凑近它的眼睛
