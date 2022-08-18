'''
作者：Limpu
早期项目，代码使用mPython生成，未经整理。

使用'掌控板+'小程序通过蓝牙获取WIFI信息，存取WIFI.txt。
非常实用（逃
'''
from mpython import *
from mpython_ble.application import BLEUART
import machine, time, ubinascii

_ble_uart = None
def _ble_uart_irq():pass

def init_text_file(_path):
    f = open(_path, 'w')
    f.close()

def write_data_to_file(_path, _data, _sep):
    f = open(_path, 'a')
    f.write(_data + _sep)
    f.close()

myUI = UI(oled)

def _ble_uart_irq():
    _received_data = bytes(_ble_uart.read())
    init_text_file('WIFI.txt')
    write_data_to_file('WIFI.txt', (_received_data).decode('UTF-8','ignore'), ',')
    time.sleep(0.5)
    _ble_uart.close()
    machine.reset()
oled.fill(0)
oled.DispChar('请稍后...', 45, 24, 1)
oled.show()
_ble_uart = BLEUART(name=bytes(str('mpy_') + str((ubinascii.hexlify(machine.unique_id()).decode().upper().upper())), 'utf-8'))
_ble_uart.irq(handler=_ble_uart_irq)
oled.fill(0)
oled.fill_rect(2, 2, 60, 60, 1)
myUI.qr_code(str('http://static.steamaker.cn/wx/?mac=') + str((ubinascii.hexlify(machine.unique_id()).decode().upper().upper())), 3, 3, scale=2)
oled.DispChar('请微信扫码', 65, 1, 1)
oled.DispChar('按提示操作', 65, 17, 1)
oled.DispChar((ubinascii.hexlify(machine.unique_id()).decode().upper()[ : 6]), 65, 33, 1)
oled.DispChar((ubinascii.hexlify(machine.unique_id()).decode().upper()[6 : ]), 65, 49, 1)
oled.show()
