# API 事实表（ugot 0.2.13 · 唯一校对基准）

> 本表逐条核对自本机实际安装的 `ugot 0.2.13` 源码（`ugot/ugot.py`、`src/enum.py`、`src/model_client.py`、`src/vision_client.py`）。
> **用途**：16 周教案 / 实践手册里所有代码以本表为准。与《UGOT_Python学习指南.md》《产品备查.md》《UGOT_API说明书》冲突时，**以本表（= 源码）为准**，冲突条目见文末「勘误」。
> 源码可自查：`grep -n "def 方法名" ugot/ugot.py`，每个方法的 docstring 就是权威参数说明。

---

## 0. 连接与通用

```python
from ugot import ugot
import time                      # 需要等待时用

ug = ugot.UGOT()
ug.initialize("192.168.x.x")     # 机器人「设置→系统信息(关于)」里的真实 IP，电脑需同一 WiFi
```

| 方法 | 说明 |
|---|---|
| `ug.scan_device()` | 返回 `{设备名: IP}` 字典，可自动找 IP |
| `ug.get_wifi_status()` / `ug.get_power_status()` | 查 WiFi / 电量 |
| `ug.get_device_name()` / `ug.get_mac_address()` | 查设备信息 |
| `ug.stop_chassis()` | **急停**，停所有形态运动（通用，不分形态） |
| `ug.perform_action(actionId)` | 通用动作，`actionId` 是**字符串**：`"WakeUp"/"Smile"/"Doubt"/"Resist"/"Love"/"Anger"/"Proud"/"Ticklish"/"Sleep"` |
| `ug.model_common_move(speed, turn_speed)` | 当前形态通用"速度+转向" |

**重要教学事实：参数写错时，SDK 大多数方法只是 `print` 一行提示后 `return`，不抛异常、机器人毫无反应。**
例：`ug.screen_print_text("你好", "FFFF0000")` 会打印
`TypeError: screen_print_text(): invalid value of color, expected [0-8], got FFFFFF00`
——屏幕不显示任何字。所以"机器人没反应"要先怀疑**参数类型/取值**，不是程序崩了。

---

## 1. 屏幕（颜色一律是整数 0-8，**不是**十六进制字符串）

`0黑 1白 2紫 3红 4橙 5黄 6绿 7青 8蓝` → **想红就填 3，想绿填 6，黄填 5，白填 1**

| 方法 | 参数 |
|---|---|
| `ug.screen_print_text(text, color)` | text 字符串，color 整数 0-8 |
| `ug.screen_print_text_newline(text, color)` | 显示并换行 |
| `ug.screen_display_background(color)` | color 整数 0-8 |
| `ug.screen_display_emotion(name, loop=False)` | name 字符串：`WakeUp/Smile/Doubt/Search/Breathe/Blink/Resist/Love/Anger/Proud/Ticklish/Weakness/Sleep/SleepCirculate/Switch` |
| `ug.screen_clear()` | 清屏 |

---

## 2. 运动（方向数字：前进 0 / 后退 1 / 左转 2 / 右转 3）

形态前缀：麦轮 `mecanum_`、平衡车 `balance_`、轮足 `wheelleg_`、四足狗 `dog_`、蜘蛛 `spider_`、变形车 `transform_`。
**工程车（engineer）底盘按麦轮处理 → 运动照用 `mecanum_*`，只有机械臂才是 `mechanical_*`。**

每个形态都有这 5 个核心方法（前缀替换即可）：

| 方法 | 签名 | 会不会自动停 |
|---|---|---|
| `X_move_speed(direction, speed)` | direction 0/1，speed 单位 cm/s | ❌ 不停，要自己 `stop_chassis()` |
| `X_turn_speed(turn, speed)` | turn 2/3，speed 单位 °/s | ❌ 不停，要自己 `stop_chassis()` |
| `X_move_speed_times(direction, speed, times, unit)` | times 0~360，**unit 只能是 0=秒 / 1=厘米** | ✅ 自动停 |
| `X_turn_speed_times(turn, speed, times, unit)` | times 0~360，**unit 只能是 0=秒 / 2=度** | ✅ 自动停 |
| `X_move_turn(direction, speed, turn, turn_speed)` | 边走边转 | ❌ 不停 |

**⚠️ 各形态限速完全不同**（源码 `__limit_speed_by_model` + 方法 docstring 实测，超范围会被 `num_normal` **悄悄压到上限**，不报错）：

| 形态 | 前进/后退 speed | 转弯 speed |
|---|---|---|
| 麦轮 `mecanum_` / 工程车 engineer | **5~80** cm/s | **5~280** °/s |
| 变形车 `transform_` | 5~80 | 5~280 |
| 平衡车 `balance_` | 5~80 | **5~360** |
| 轮足 `wheelleg_` | **5~60** | **5~180** |
| 蜘蛛 `spider_` | **0~25** | **0~60** |
| 四足狗 `dog_` | **0~25** | **0~20** |

> 教学要点：麦轮用的 `40` 直接抄给蜘蛛/狗会"不动或疯转"——**狗转向超过 20 就被压住**。换形态时速度要重新试，这本身就是很好的调试练习。
> `ug.mecanum_move_xyz(x, y, z)` 范围：x/y **-80~80**，z **-280~280**（可为负）。
> 舵机 `turn_servo_speed(id, speed)`：**-100~100**；电机 `turn_motor_speed(id, speed)`：**-140~140**。

> ⚠️ 单位坑：`move_speed_times` 不能用 2（度），`turn_speed_times` 不能用 1（厘米）。写错会打印 `invalid value of unit` 然后**不动**。
> 教学建议：**优先教 `_times` 版本**（自动停、更安全），`move_speed/turn_speed` 作为"要自己喊停"的对比。

其它麦轮专属：`ug.mecanum_translate_speed(angle, speed)`（斜向平移）、`ug.mecanum_translate_speed_times(angle, speed, times, unit)`、`ug.mecanum_move_xyz(x_speed, y_speed, z_speed)`（横向/纵向/旋转，**名字是 `move_xyz`，不是 `xyz_control`**）、`ug.mecanum_motor_control(lf, rf, lb, rb)`（四轮独立）、`ug.mecanum_stop()`。

形态专属：
- 平衡车：`ug.balance_start_balancing()`（先站起来，**动之前必调**）、`ug.balance_stop_balancing()`、`ug.balance_set_acceleration(a)`、`ug.balance_reset_acceleration()`
- 轮足：`ug.wheelleg_set_chassis_height(height)`（**1 高 / 2 中 / 3 低**，整数）、`ug.wheelleg_restory()`（恢复中等高度）、`ug.wheelleg_set_decline_angle(angle)`、`ug.wheelleg_start_balancing()` / `wheelleg_stop_balancing()`、`ug.wheelleg_adaption_control(True/False)`
- 变形车：`ug.transform_set_chassis_height(height)`（**整数 2~7，单位厘米**）、`ug.transform_adaption_control(True/False)`、`ug.transform_arm_control(joint, position, time)`、`ug.transform_motor_control(lf,rf,lb,rb)`、`ug.transform_restory()` / `transform_stop()`
- 四足狗：`ug.dog_perform_action(actionId)`（动作名是**字符串**，实测 6 个：`"crawling"/"squatting"/"standing"/"handshake"/"urination"/"stretch"`；与通用 `perform_action()` 的表情名是**两套不同清单**，别混用）、`ug.dog_set_decline_angle(pose, angle)`、`ug.dog_restory()`、`ug.dog_stop()`、`ug.dog_adaption_control(True/False)`
- 蜘蛛：`ug.spider_restory()`、`ug.spider_stop()`

结构件（舵机/电机，工程车等外接件用）：
`ug.turn_servo_angle(id, angle, duration_ms, wait=False)`、`ug.turn_servo_speed(id, speed)`、`ug.turn_servo_speed_times(id, speed, times)`、`ug.read_servo_angle(id)`、`ug.stop_servo(id, lock=False)`、`ug.stop_all_servos()`；
`ug.turn_motor_speed(id, speed)`、`ug.turn_motor_speed_times(id, speed, times)`、`ug.turn_motor_angle(id, angle, duration_ms, wait=False)`、`ug.read_motor_speed(id)`、`ug.read_motor_angle(id)`、`ug.stop_motor(id, lock=False)`。

---

## 3. 灯光（灯带编号 0 顶 / 1 左 / 2 右 / 3 底；列表里只能放 0-3）

| 方法 | 参数 |
|---|---|
| `ug.show_light_rgb(lights, red, green, blue)` | lights 列表，R/G/B 各 **0~255** |
| `ug.show_light_hsv(lights, hue_percent, saturation, value)` | 三者都是 **0~100**（注意不是 0-360） |
| `ug.show_light_rgb_effect(red, green, blue, effect)` | effect **0 常亮 / 1 关 / 2 呼吸 / 3 闪烁**（**没有 lights 参数**） |
| `ug.show_light_hsv_effect(hue, sat, val, effect)` | 同上，0~100 |
| `ug.turn_off_lights()` | 全关 |

> 闪红灯报警**一行就够**：`ug.show_light_rgb_effect(255, 0, 0, 3)`，不用自己写循环开关。

---

## 4. 声音

| 方法 | 参数 |
|---|---|
| `ug.play_audio_tts(data, voice_type=0, wait=False)` | voice_type **0 女声 / 1 男声**；`wait=True` 会等说完 |
| `ug.set_volume(volume)` | **0~100**（源码 `num_normal(volume,100,0)`）。学习指南里"1~5"是**错的**——填 3 几乎听不见；建议 `set_volume(60)` |
| `ug.get_volume()` | 返回 `[音量, 是否静音]` |
| `ug.stop_audio()` | 停播 |
| `ug.play_tone(tone, beat, wait=False)` | 蜂鸣/音符 |
| `ug.start_audio_asr()` / `ug.start_audio_nlp(data, wait=False)` | 语音识别 / 自然语言对话 |
| `ug.get_audio_direction()` | 声源方向（配 `enable_audio_direction()`） |

---

## 5. 传感器

| 方法 | 返回 |
|---|---|
| `ug.read_distance_data(id)` | **TOF 距离，单位厘米（浮点）**；id 一般填 1；没读到返回 **-1**（另有可能返回 0，判断要一起防） |
| `ug.read_gyro_data()` | 9 元素列表 `[pitch, roll, yaw, gyro_x, gyro_y, gyro_z, accel_x, accel_y, accel_z]`，已 round 2 位 |
| `ug.get_attitude()` | 7 个布尔 `[前倾, 后倾, 左倾, 右倾, 屏幕朝上, 屏幕朝下, 摇晃]` |

避障判断务必写成 `if 距离 != -1 and 距离 < 30:`，否则没读数时 `-1 < 30` 恒真会误停。

---

## 6. AI 视觉

**先加载模型**：`ug.load_models(['模型名'])`（返回列表 True/False；可一次多个）；用完 `ug.release_models(['模型名'])`（不传参=全卸）。

合法模型名（源码 `load_models` docstring）：
`gesture` 手势 · `color_recognition` 颜色 · `face_recognition` 人脸 · `face_attribute` 表情/人脸属性 · `traffic_sign` 交通标志 · `human_pose` 人体姿态 · `word_recognition` 文字 · `apriltag_qrcode` 二维码/AprilTag · `line_recognition` **单/双轨巡线** · `lpd_recognition` 车牌 · `toy_recognition` 玩具

**返回值一律是"解析好的 Python 列表"，不要再 `json.loads()`：**

| 方法 | 返回 |
|---|---|
| `ug.get_gesture_result()` | **字符串**，石头/剪刀/布/OK/点赞（按机器人语言设置！中文机返回中文） |
| `ug.get_color_total_info()` | `[颜色, 形状, center_x, center_y, height, width, area]`，没认到时前面是空字符串、坐标是 -1 |
| `ug.get_face_recognition_total_info()` | `[[名字, center_x, center_y, height, width, area], ...]`；**没录入的人返回翻译值**（中文机=「陌生人」，英文机=Unknown 类），不是空串 |
| `ug.get_traffic_total_info()` | `[[标志, center_x, center_y, height, width, area], ...]`（绿灯/鸣笛/左转/右转/斑马线/红灯/注意儿童/禁止长时间停车/进入隧道/黄灯） |
| `ug.get_pose_total_info()` | `[[17 组关键点 x,y 共 34 个数], ...]` |
| `ug.get_qrcode_total_info()` / `get_apriltag_total_info()` / `get_qrcode_apriltag_total_info()` | 二维码 / AprilTag / 合并结果 |
| `ug.get_words_result()` | 字符串（多个词用逗号连） |
| `ug.get_single_track_total_info()` | `[offset 偏移, type 类型, x, y]`；**type 1 直线 / 2 Y字路口 / 3 十字路口 / 0 无线** |
| `ug.get_double_track_total_info()` | `[offset, type, x, y]`；双轨 **type 1 直线 / 2 路口 / 0 无线** |
| `ug.set_track_recognition_line(line_type)` | 巡线前设线型：**0 单轨 / 1 双轨** |
| `ug.get_license_plate_total_info()` / `ug.get_toy_total_info()` | 车牌 / 玩具识别 |
| `ug.get_knn_result(model_name)`、`ug.knn_train(model_name, label_list)`、`ug.knn_query()`、`ug.knn_rename()`、`ug.knn_delete()` | 本地训练（KNN） |
| `ug.face_recognition_add_name(name)`、`ug.face_recognition_get_all_names()`、`ug.face_recognition_delete_name(name)` | 人脸录入/管理。**`face_recognition_add_name()` 自己就会加载模型、开摄像头、屏显 3 秒倒计时、拍照上传并在编辑器 print 进度**——不必去 UGOT APP 录入；调用时人要正对镜头、光线充足，后面接 `time.sleep(1)` 再判断 |
| `ug.open_camera()` / `ug.read_camera_data()` | 开摄像头 / 读当前帧（base64，失败返回 None） |
| `ug.create_pid_controller()` | 返回 PID 对象：`pid.update(feedback, current_time)`、`pid.set_pid(kp, ki, kd)` |

**想要稳定的英文判定值**（不受机器人语言影响）时，读原始 JSON：
```python
import json
raw = ug.VISION.gesture_inference()          # 原始 JSON 字符串
手势 = json.loads(raw)["gesture"]            # 'stone'/'scissor'/'palm'/'ok'/'good'
```
颜色原始值：`json.loads(ug.VISION.color_identify())` → 列表，每项 `{'color': 'red', 'shape': 'ball', 'position': [x, y, w, h], 'area': ...}`。

**巡线最小可用组合**：
```python
ug.load_models(['line_recognition'])
ug.set_track_recognition_line(0)             # 0=单轨
数据 = ug.get_single_track_total_info()       # [偏移, 类型, x, y]
偏移 = 数据[0]
```

---

## 7. 其它常用

GPIO / 串口：`set_pin_level(pin, level)`、`read_pin_level(pin)`、`set_pin_pwm(pin, duty_cycle)`、`set_pin_pwm_duty_cycle(pin, frequency, duty_cycle)`、`set_serial_serbaud(baudrate)`、`write_serial_string(newline, text)`、`read_serial_string()`、`clear_gpio_serial()`。
多机互联：`enable_broadcast()` / `send_broadcast_message(message)` / `get_broadcast_message()` / `set_broadcast_channel(channel)`。
手柄：`get_joypad_pressing_buttons()` / `get_joypad_coordinate()`。

---

## 8. 勘误（参考文档里需要修正的点）

| 出处 | 文档写法 | 源码事实 |
|---|---|---|
| 学习指南 §屏幕 | `screen_print_text("文字", "FFFF0000")`、"颜色是 ARGB 十六进制" | color 是**整数 0-8**；传字符串只会打印 TypeError 提示并**不显示** |
| 学习指南 §AI | `raw = ug.VISION.gesture_inference()` + `json.loads` 为唯一路径 | 推荐直接用 `ug.get_gesture_result()`（返回已解析字符串，但**随机器人语言变化**）；`VISION.*` 是取原始 JSON 的备用路径 |
| 学习指南 §AI | 未提 `line_recognition` | 巡线模型名是 **`line_recognition`**，配 `set_track_recognition_line()` + `get_single_track_total_info()` |
| 学习指南 §运动 | `mecanum_move_speed_times(0, 40, 2, 0)` 备注"0=秒,1=厘米,2=度" | 分方法：`move_*` 只认 0秒/1厘米；`turn_*_speed_times` 只认 0秒/2度 |
| 学习指南 / 课程安排 | 颜色结果用 `json.loads(...)['info'][0]['color']` | `get_color_total_info()` 返回的是 **list**，直接 `结果[0]` 取颜色；再 `json.loads` 会 `TypeError` |
| API 说明书 | `ug.mecanum_xyz_control(...)` | 真实方法名 `ug.mecanum_move_xyz(x, y, z)` |
| API 说明书 | 屏幕/表情未列 `screen_display_emotion` | 存在，15 个表情名，做"表情/心情"类项目很好用 |
| 课程安排 §第15周 | `ug.mechanical_move(...)` / `ug.mechanical_turn(...)` | **不存在**。工程车底盘按麦轮处理 → 用 `mecanum_*`；机械臂只有 7 个：`mechanical_joint_control` / `mechanical_single_joint_control` / `mechanical_move_axis` / `mechanical_clamp_close` / `mechanical_clamp_release` / `mechanical_get_clamp_status` / `mechanical_arms_restory` |
| 课程安排 §第14周 | 车身升降"占位方法名" | 真实：`ug.transform_set_chassis_height(2~7 厘米)` |
| 产品备查 | 形态只有 7 种、代码前缀 6 种 | 补充：SDK 内部设备型号串为 `mecanum/balance/transform/wheel_legged/spider/dog/engineer/box` |

---

## 9. 每周通用安全检查清单（改完自查）

1. 全文搜 `screen_print_text(` —— 第二个参数**必须是整数 0-8**，不能是 `"FF..."`。
2. 全文搜 `ug.` —— 每个方法名都能在本表或源码 `grep "def "` 找到，一个编造的都不能有。
3. 视觉/传感器返回值解析方式与本表一致（list 不要 `json.loads`）。
4. 换形态的周：运动前缀与本表 §2 一致；工程车用 `mecanum_*` + `mechanical_*`。
5. 每段完整代码：连接三行 → 必要初始化（`load_models` / `balance_start_balancing` / `set_track_recognition_line`）→ 主体 → 收尾（`stop_chassis()` / `turn_off_lights()` / `screen_clear()`）。
6. 教案与同周实践手册的**项目名、知识点、形态、API 写法**完全一致；手册末尾"下周预告"与下一周教案主题一致。
7. 安全三件事（同 WiFi、干爽平整场地、先想急停）在手册开头保留。
8. 距离判断带 `-1` 防呆；`while True` 循环里带 `time.sleep(0.1)` 之类喘息；裸 `except:` 改成交代清楚的写法（至少 `print` 出错误或只捕 `KeyboardInterrupt`）。
