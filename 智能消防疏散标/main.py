'''
《智能消防疏散标》
作者：Limpu
'''
import parrot, audio, network, math
from umqtt.simple import MQTTClient
from machine import Timer
from mpython import *


def init_text_file(_path):
    '''初始化文本文件，有则清空，无则创建'''
    f = open(_path, 'w')
    f.close()

def write_data_to_file(_path, _data, _sep):
    '''写文件，无则创建'''
    f = open(_path, 'a')
    f.write(_data + _sep)
    f.close()


def timer10_tick(_):
    global onfire,selfname,pointD,mqtt
    mqtt.ping()
    if onfire and selfname not in onfire:
        rgb.fill((255,0,0)) # 全红
        rgb.write()
        audio.play('{}.wav'.format(pointD))
    else:
        rgb.fill((0,0,0)) # 全关
        rgb.write()
        sleep_ms(1)

def getDirection(real, tip):
    global pointD
    if real >= 315 or real < 45:# N
        pointD = direction.get('N').get(tip)
    elif real >= 45 and real < 135:# E
        pointD = direction.get('E').get(tip)
    elif real >= 135 and real < 225:# S
        pointD = direction.get('S').get(tip)
    else:# W
        pointD = direction.get('W').get(tip)

def get_list_from_file(_path, _sep):
    '''读取文件为列表，以分隔符分割'''
    f = open(_path, 'r')
    result = f.read().split(_sep)
    f.close()
    return result

def mqtt_callback(topic, msg):
    global mqtt, pointD, way, onfire, selfname, config
    #try:
    dmsg = msg.decode('utf-8', 'ignore')
    dmsg = dmsg.split(' ')
    if len(dmsg) < 2:
        pass
    else:
        if dmsg[1] == 'onfire':
            onfire.update(dmsg[0])
        elif dmsg[1] == 'notfire':
            try:
                onfire-={dmsg[0]}
            except:
                pass
        elif dmsg[0] == selfname and dmsg[1] == 'info':
            mqtt.publish(config[5], '@{},U={}mV,D={},W={}'.format(selfname, parrot.get_battery_level(), pointD, len(way)))
            try:
                mqtt.publish(config[5],'@{}{}'.format(selfname,str(onfire)))
            except:pass
        elif dmsg[0] == selfname and dmsg[1] == 'way':
            way.append(dmsg[2:])
            way.sort(key=lambda i:i[0])
            init_text_file('way.txt')
            write_data_to_file('way.txt', str(way), '\n')
        elif dmsg[0] == selfname and dmsg[1] == 'clearway':
            way = []
            init_text_file('way.txt')
    #except: print((topic, dmsg))

# value init
p0 = MPythonPin(0, PinMode.ANALOG) # 设置火焰传感器引脚p0.read_analog()
onfire = set() # 火点集合
pointD = 'Forward'
direction = {'N':{'N':'Forward','E':'Right','S':'Backward','W':'Left'},'E':{'N':'Left','E':'Forward','S':'Right','W':'Backward'},'S':{'N':'Backward','E':'Left','S':'Forward','W':'Right'},'W':{'N':'Right','E':'Backward','S':'Left','W':'Forward'}}
image_picture = Image()
audio.player_init(i2c)

# main
# 连接WIFI、mqtt
try:
    config = get_list_from_file('config.txt', '\n')
    my_wifi = wifi()
    try_connect_wifi(my_wifi,str(config[0]),str(config[1]),3)
    mqtt = MQTTClient('', '182.254.130.180', 1883, config[3], config[4], keepalive=30)
    mqtt.connect()
    mqtt.set_callback(mqtt_callback) # mqtt设置回调函数
    mqtt.subscribe(str(config[5])) # mqtt订阅主题
except:
    oled.fill(0)
    oled.DispChar(str('【请更新config.txt！】'), 0, 0, 1)
    oled.DispChar(str('连续6行依次输入：'), 0, 16, 1)
    oled.DispChar(str('WIFI名，密码，本机名，'), 0, 32, 1)
    oled.DispChar(str('IOT_id，pwd，topic'), 0, 48, 1)
    oled.show()
    while True:
        sleep(1)
tim10 = Timer(10)
tim10.init(period=5000, mode=Timer.PERIODIC, callback=timer10_tick)
magnetic.calibrate() # 校正罗盘
selfname = str(config[2]) # 获取本机名
try:
    way = get_list_from_file('way.txt', '\n')[0]
except:
    way = []
while True:
    mqtt.check_msg()
    if p0.read_analog() > 50: # 需要实际参数
        mqtt.publish(config[5], str(selfname)+' onfire')
        rgb.fill((255,0,0)) # 全红
        rgb.write()
        oled.fill(0)
        oled.DispChar(str('此处有火情！'), 36, 25, 1)
        oled.show()
        while p0.read_analog() > 50: # 需要实际参数
            pass
        rgb.fill((0,0,0)) # 全关
        rgb.write()
        mqtt.publish(config[5], str(selfname) + str(' notfire'))
    else:
        if not len(way):
            oled.fill(0)
            oled.DispChar('请更新逃生路线！', 30, 25, 1)
            oled.show()
        elif selfname in onfire:
            oled.fill(0)
            oled.DispChar(str('此处有火情！'), 36, 25, 1)
            oled.show()
        else:
            temp_way = way
            for i in range(len(way)+1):
                if i == len(way):
                    getDirection(math.atan2(magnetic.get_y(), -magnetic.get_z()) * (180 / 3.14159265) + 180 + 3, temp_way[0][1])
                    oled.fill(0)
                    oled.blit(image_picture.load('face/Information/{}.pbm'.format(pointD), 0), 24, 0)
                    oled.show()
                    break
                else:
                    for j in range(2,len(temp_way[i])+1):
                        if j == len(temp_way[i]):
                            break
                        elif temp_way[i][j] in onfire:
                            break
                    if j == len(temp_way[i]): # 该路线可行
                        getDirection(math.atan2(magnetic.get_y(), -magnetic.get_z()) * (180 / 3.14159265) + 180 + 3, temp_way[0][1])
                        oled.fill(0)
                        oled.blit(image_picture.load('face/Information/{}.pbm'.format(pointD), 0), 24, 0)
                        oled.show()
                        break
