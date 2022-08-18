#mPythonType:0
from mpython import *
import json, urequests, network, ntptime, machine, time, math, audio, ubinascii
from machine import Timer

def get_list_from_file(_path, _sep):
    f = open(_path, 'r')
    result = f.read().split(_sep)
    f.close()
    return result

def changer():
    global walk_num, page, RGB, WIFI_SSID, WIFI_password, ai
    if touchpad_p.was_pressed():
        page = 0
        P0()
    if touchpad_t.was_pressed():
        page = 1
        P1()
    if touchpad_o.was_pressed():
        page = 2
        P2()
    if touchpad_n.was_pressed():
        RGB = RGB + 1
        if RGB % 2 == 1:
            rgb.fill((int(102), int(102), int(102)))
            rgb.write()
            time.sleep_ms(1)
        else:
            rgb.fill( (0, 0, 0) )
            rgb.write()
            time.sleep_ms(1)

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

def on_shaked():
    global page, walk_num, RGB, WIFI_SSID, WIFI_password, ai
    walk_num = walk_num + 1
    time.sleep(1)

def P0():
    global walk_num, page, RGB, WIFI_SSID, WIFI_password, ai
    oled.fill(0)
    oled.DispChar(str(time.localtime()[1]) + str(str('月') + str(str(time.localtime()[2]) + str('日'))), 72, 1, 1, False)
    oled.DispChar(str('星期') + str((time.localtime()[6]+1 + 1)), 77, 17, 1, False)
    oled.DispChar(w1["results"][0]["now"]["text"], 65, 49, 1, False)
    oled.DispChar(str(w1["results"][0]["now"]["temperature"]) + str('℃'), 100, 49, 1, False)
    while not page != 0:
        my_clock.clear()
        oled.fill_rect(0, 32, 128, 16, 0)
        oled.DispChar(str('步数') + str(walk_num), 65, 33, 1, False)
        my_clock.settime()
        my_clock.drawClock()
        oled.show()
        changer()

def P1():
    global walk_num, page, RGB, WIFI_SSID, WIFI_password, ai
    while not page != 1:
        oled.fill(0)
        oled.DispChar(str(w1["results"][0]["location"]["name"]) + str('天气'), 0, 0, 2, False)
        oled.DispChar(str('今天') + str(str(w2["results"][0]["daily"][0]["text_day"]) + str(str(w2["results"][0]["daily"][0]["high"]) + str(str('/') + str(str(w2["results"][0]["daily"][0]["low"]) + str('℃'))))), 0, 16, 1, False)
        oled.DispChar(str('明天') + str(str(w2["results"][0]["daily"][1]["text_day"]) + str(str(w2["results"][0]["daily"][1]["high"]) + str(str('/') + str(str(w2["results"][0]["daily"][1]["low"]) + str('℃'))))), 0, 32, 1, False)
        oled.DispChar(str('后天') + str(str(w2["results"][0]["daily"][2]["text_day"]) + str(str(w2["results"][0]["daily"][2]["high"]) + str(str('/') + str(str(w2["results"][0]["daily"][2]["low"]) + str('℃'))))), 0, 48, 1, False)
        oled.circle(112, 19, 15, 1)
        oled.line(112, 19, (round(15 * math.sin(magnetic.get_heading() / 180.0 * math.pi)) + 112), (round(15 * math.cos(magnetic.get_heading() / 180.0 * math.pi)) + 19), 1)
        oled.show()
        changer()

def Get_asr_start():
    audio.recorder_init(i2c)
    audio.record("temp.wav", 2)
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

def P2():
    global walk_num, page, RGB, WIFI_SSID, WIFI_password, ai
    oled.fill(0)
    oled.DispChar('Artificial Intelligence', 0, 0, 1, False)
    oled.DispChar('    正在录音（2秒）...', 0, 48, 1, False)
    oled.show()
    Get_asr_start()
    oled.fill(0)
    oled.DispChar('Artificial Intelligence', 0, 0, 1, False)
    oled.DispChar('        正在识别...', 0, 48, 1, False)
    oled.show()
    get_asr_result_discern = Get_asr_result_discern("temp.wav")
    ai = get_asr_result_discern
    oled.fill(0)
    oled.DispChar(ai, 0, 0, 1, True)
    oled.DispChar('        等待响应...', 0, 48, 1, False)
    oled.show()
    try:
        _response = urequests.get(str('http://api.qingyunke.com/api.php?key=free&appid=0&msg=') + str(ai))
        oled.fill(0)
        oled.DispChar((_response.text[23 : -2]), 0, 0, 1, True)
        oled.show()
    except:
        oled.fill(0)
        oled.DispChar('响应超时呜~', 0, 0, 1, True)
        oled.show()
    while not page != 2:
        changer()

image_picture = Image()

def get_seni_weather(_url, _location):
    _url = _url + "&location=" + _location.replace(" ", "%20")
    response = urequests.get(_url)
    json = response.json()
    response.close()
    return json

my_clock = Clock(oled, 32, 32, 30)
if button_b.value() == 0:
    # 删print
    exec(open('wifi.py').read(), globals())
else:
    oled.fill(0)
    oled.blit(image_picture.load('logo.bmp', 0), 32, 0)
    oled.show()
    try:
        WIFI_SSID = get_list_from_file('WIFI.txt', ',')[0]
        WIFI_password = get_list_from_file('WIFI.txt', ',')[1]
        import network
        my_wifi = wifi()
        my_wifi.connectWiFi(WIFI_SSID,WIFI_password)
        w1 = get_seni_weather("https://api.seniverse.com/v3/weather/now.json?key=Sa4NEgoErgVX_7OIE", "nanjing")
        w2 = get_seni_weather("https://api.seniverse.com/v3/weather/daily.json?key=Sa4NEgoErgVX_7OIE", "nanjing")
        ntptime.settime(8, "ntp.aliyun.com")
        magnetic.calibrate()
        RGB = 0
        walk_num = 0
    except:
        oled.fill(0)
        oled.DispChar('     【WiFi连接失败】', 0, 16, 1, False)
        oled.DispChar('长按B键直到出现二维码', 0, 32, 1, False)
        oled.show()
        while not button_b.value() == 0:
            pass
        machine.reset()
    page = 0
    P0()
