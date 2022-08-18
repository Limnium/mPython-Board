'''
作者：Limpu
早期项目，代码使用mPython生成，未经整理，可能无法运行。

某创客活动、某科创大赛获奖作品（迫真）
'''
import _thread, time, math, music, ubinascii, network, machine, audio, urequests, json
from mpython import *
from machine import Timer
from umqtt.simple import MQTTClient

_is_shaked = _is_thrown = False
_last_x = _last_y = _last_z = _count_shaked = _count_thrown = 0
def on_shaked():pass
def on_thrown():pass

tim11 = Timer(11)

def timer11_tick(_):
    global _is_shaked, _is_thrown, _last_x, _last_y, _last_z, _count_shaked, _count_thrown
    if _is_shaked:
        _count_shaked += 1
        if _count_shaked == 5: _count_shaked = 0
    if _is_thrown:
        _count_thrown += 1
        if _count_thrown == 10: _count_thrown = 0
        if _count_thrown > 0: return
    x=accelerometer.get_x(); y=accelerometer.get_y(); z=accelerometer.get_z()
    _is_thrown = (x * x + y * y + z * z < 0.25)
    if _is_thrown: on_thrown();return
    if _last_x == 0 and _last_y == 0 and _last_z == 0:
        _last_x = x; _last_y = y; _last_z = z; return
    diff_x = x - _last_x; diff_y = y - _last_y; diff_z = z - _last_z
    _last_x = x; _last_y = y; _last_z = z
    if _count_shaked > 0: return
    _is_shaked = (diff_x * diff_x + diff_y * diff_y + diff_z * diff_z > 1)
    if _is_shaked: on_shaked()

tim11.init(period=100, mode=Timer.PERIODIC, callback=timer11_tick)

def _E4_BC_A0_E6_84_9F():
    global bushu, _msg, msg
    if light.read() <= 1 and not (get_tilt_angle('X') >= 175 and get_tilt_angle('X') <= 185):
        rgb[1] = (int(255), int(255), int(255))
        rgb.write()
        time.sleep_ms(1)
        rgb[2] = (int(255), int(255), int(255))
        rgb.write()
        time.sleep_ms(1)
    else:
        rgb[1] = (0, 0, 0)
        rgb.write()
        time.sleep_ms(1)
        rgb[2] = (0, 0, 0)
        rgb.write()
        time.sleep_ms(1)
    if get_tilt_angle('X') > 115 and get_tilt_angle('X') < 150:
        music.play('A4:1')

msg = None

def mqtt_topic_5a30797262436f4d67(_msg):
    global bushu, msg
    msg = _msg
    rgb[0] = (int(255), int(255), int(51))
    rgb.write()
    time.sleep_ms(1)
    music.play('B5:8')

my_wifi = wifi()

my_wifi.connectWiFi('SSID', 'PAS')

mqtt = MQTTClient('', '', , '', '', keepalive=30)

try:
    mqtt.connect()
    print('Connected')
except:
    print('Disconnected')

bushu = None

_msg = None

def _E6_A0_A1_E5_BE_BD():
    global bushu, _msg, msg
    oled.fill(0)
    oled.blit(image_picture.load('logo.bmp', 0), 65, 0)
    oled.DispChar(str('xxx School'), 0, 17, 1)
    oled.DispChar(str('xxx'), 0, 33, 1)
    oled.show()

def Get_asr_start():
    audio.recorder_init(i2c)
    audio.record("temp.wav", 3)
    audio.recorder_deinit()

def Get_asr_result_discern(filename):
    _response = urequests.post("http://119.23.66.134:8085/file_upload",
        files={"file":(filename, "audio/wav")},
        params={"appid":"1", "mediatype":"2", "deviceid":ubinascii.hexlify(machine.unique_id()).decode().upper()})
    rsp_json = _response.json()
    _response.close()
    if "text" in rsp_json:
        return rsp_json["text"]
    elif "Code" in rsp_json:
        return "."
    else:
        return rsp_json

def _E6_A0_A1_E5_9B_AD_E6_B6_88_E6_81_AF():
    global bushu, _msg, msg
    oled.fill(0)
    oled.DispChar(str('校园消息'), 38, 0, 1)
    oled.fill_circle(64, 61, 2, 1)
    oled.DispChar(str(msg), 0, 16, 1)
    oled.show()
    Get_asr_start()
    oled.fill_rect(0, 48, 128, 16, 0)
    oled.circle(64, 61, 2, 1)
    oled.show()
    get_asr_result_discern = Get_asr_result_discern("temp.wav")
    if get_asr_result_discern != '':
        oled.DispChar(str(get_asr_result_discern), 0, 32, 1)
        oled.show()
        if get_asr_result_discern.find('Help') != -1 or get_asr_result_discern.find('救命') != -1:
            mqtt.publish('Z0yrbCoMg', bytes('请求帮助！', 'utf-8'))
        else:
            mqtt.publish('Z0yrbCoMg', bytes(get_asr_result_discern, 'utf-8'))
        time.sleep(3)
        rgb[0] = (0, 0, 0)
        rgb.write()
        time.sleep_ms(1)

def _E4_B8_AA_E4_BA_BA_E5_90_8D_E7_89_87():
    global bushu, _msg, msg
    oled.fill(0)
    myUI.qr_code('www.baidu.com', 65, 0, scale=2)
    oled.DispChar(str('class'), 0, 17, 1)
    oled.DispChar(str('name'), 0, 33, 1)
    oled.DispChar(str(str((str(bushu))) + str('步')), 0, 49, 1)
    oled.show()

def thread_2():
    global bushu, _msg, msg
    while True:
        if _is_shaked:
            bushu = bushu + 1
            time.sleep(1)

def get_tilt_angle(_axis):
    _Ax = accelerometer.get_x()
    _Ay = accelerometer.get_y()
    _Az = accelerometer.get_z()
    if 'X' == _axis:
        _T = math.sqrt(_Ay ** 2 + _Az ** 2)
        if _Az < 0: return math.degrees(math.atan2(_Ax , _T))
        else: return 180 - math.degrees(math.atan2(_Ax , _T))
    elif 'Y' == _axis:
        _T = math.sqrt(_Ax ** 2 + _Az ** 2)
        if _Az < 0: return math.degrees(math.atan2(_Ay , _T))
        else: return 180 - math.degrees(math.atan2(_Ay , _T))
    elif 'Z' == _axis:
        _T = math.sqrt(_Ax ** 2 + _Ay ** 2)
        if (_Ax + _Ay) < 0: return 180 - math.degrees(math.atan2(_T , _Az))
        else: return math.degrees(math.atan2(_T , _Az)) - 180
    return 0

def mqtt_callback(topic, msg):
    try:
        topic = topic.decode('utf-8', 'ignore')
        _msg = msg.decode('utf-8', 'ignore')
        eval('mqtt_topic_' + bytes.decode(ubinascii.hexlify(topic)) + '("' + _msg + '")')
    except: print((topic, msg))

mqtt.set_callback(mqtt_callback)

mqtt.subscribe("")

def timer14_tick(_):
    mqtt.ping()

tim14 = Timer(14)
tim14.init(period=20000, mode=Timer.PERIODIC, callback=timer14_tick)

def thread_1():
    global bushu, _msg, msg
    while True:
        mqtt.wait_msg()

image_picture = Image()

myUI = UI(oled)
oled.fill(0)
oled.DispChar(str('智能校徽'), 38, 17, 1)
oled.DispChar(str('启动'), 49, 33, 1)
oled.show()
try:
    pass
except:
    oled.fill(0)
    oled.DispChar(str('CONNECT WIFI FAILED'), 0, 16, 1)
    oled.show()
    while not button_b.value() == 0:
        pass
    machine.reset()
_thread.start_new_thread(thread_1, ())
bushu = 0
_msg = ''
msg = ''
while True:
    if get_tilt_angle('X') >= 170 and get_tilt_angle('X') <= 190:
        oled.fill(0)
        oled.show()
    elif button_b.value() == 0:
        _E4_B8_AA_E4_BA_BA_E5_90_8D_E7_89_87()
        time.sleep(3)
    elif button_a.value() == 0:
        rgb[0] = (0, 0, 0)
        rgb.write()
        time.sleep_ms(1)
        _E6_A0_A1_E5_9B_AD_E6_B6_88_E6_81_AF()
    else:
        _E6_A0_A1_E5_BE_BD()
    _E4_BC_A0_E6_84_9F()
