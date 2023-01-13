import queue,time
import paho.mqtt.client as mqtt

def test(row:int, col:int, marked:list) -> bool:
    '''
    检测(row,col)是否有效
    '''
    if row >= rowt or row < 0 or col >= len(map[row]) or col<0: return False # 出界
    if map[row][col] == ' ': return False # 墙
    if (row, col) in marked: return False # 这条路径已到过该点
    return True

def BFS(S:tuple) -> list:
    way = [] # 存放所有可行的路径。way[n][0]->int为该路径步数，way[n][1]->str为路径详细。
    q = queue.Queue()
    q.put(S) # 起点入队
    while not q.empty():
        top = q.get() # 队首出队
        if map[top[0]][top[1]]=='*': # 如果是出口则存储路径，继续搜索
            way.append([len(top[4]), top[2]+' '+' '.join(top[3])])
        for i in range(4): # 依次搜索周围4个点
            newRow = top[0] + dRow[i]
            newCol = top[1] + dCol[i]
            if test(newRow, newCol, top[4]): # 如果通过测试则入队
                q.put((newRow, newCol, direction[i] if top[2]=='' else top[2], \
                    top[3]+[map[newRow][newCol]] if (map[newRow][newCol]!='#' and map[newRow][newCol]!='*')\
                    else top[3], top[4]+[(newRow,newCol)]))
    way.sort(key=lambda i:i[0]) # 根据路径步数排序
    return way

def findTerminal() -> list:
    '''
    查找终端位置，返回列表包裹元组，元组[0][1]为位置，[2]为终端名称。
    '''
    locat = []
    for r in range(rowt):
        for c in range(len(map[r])):
            if map[r][c] not in ('#','*',' '):
                locat.append((r,c,map[r][c]))
    return locat

def on_message(client, userdata, msg):
    m=msg.payload.decode("utf-8")
    print('\033[1;34m·收到消息：\033[0m'+('\033[1;31m'+m if 'onfire' in m else m)+'\033[0m')

def on_connect(client,userdata,flags,rc):
    global clientRc
    clientRc = rc

def on_disconnect(client, userdata, rc):
    client.loop_stop()
    exit(f'\033[1;31m·连接断开[{rc}]\033[0m')

def on_connect_fail(client, userdata):
    client.loop_stop()
    exit(f'\033[1;31m·连接失败[{userdata}]\033[0m')

# value init
clientRc=-2
dRow = (-1,0,1,0) # 行数变化
dCol = (0,1,0,-1) # 列数变化
direction = ('N','E','S','W') # 对应的方向

# main
if __name__=='__main__':
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    client.on_connect_fail = on_connect_fail
    print('\033[1;34m·感谢使用《智能消防疏散标》配套的命令行工具！\n·本项目IOT基于iot.dfrobot.com.cn\n·\033[1;36m/help\033[1;34m获取帮助，\033[1;36m/about\033[1;34m获取详细信息\033[0m')
    uid = input('\033[1;34m请输入账号：\033[0m')
    pwd = input('\033[1;34m请输入密码：\033[0m')
    tpc = input('\033[1;34m请输入topic：\033[0m')
    client.username_pw_set(uid, pwd)
    client.connect('iot.dfrobot.com.cn', 1883, 60)
    client.subscribe(tpc)
    client.loop_start()
    time.sleep(1)
    if clientRc==0:
        print('\033[1;32m·连接成功\033[0m')
    else:
        client.loop_stop()
        exit(f'\033[1;31m·连接错误[{clientRc}]\033[0m')
    while True:
        txt = input('')
        match txt:
            case '/map':
                map = [] # map[行][列] -> str
                get = input('\033[1;34m·请输入地图，上方为北，请保证处处相连。#为道路，*为出口，单个字母表示终端，空格占位。空行则结束输入：\n\033[0m')
                while get != '':
                    map.append(get)
                    get = input()
                rowt = len(map) # 总行数
                terminal = findTerminal()
                for t in terminal:
                    client.publish(tpc, '{} clearway'.format(t[2]))
                    road:list[list] = BFS((t[0],t[1],'',[],[(t[0],t[1])]))
                    for r in range(len(road)):
                        client.publish(tpc, '{} way {} {}'.format(t[2],r,road[r][1]))
            case '/exit':
                client.loop_stop()
                exit('\033[1;32m·成功退出软件\033[0m')
            case '/help':
                print('\033[1;34m·\033[1;36m/map\033[1;34m 更新地图，\033[1;36m/about\033[1;34m获取详细信息，\033[1;36m/exit\033[1;34m 退出软件\n\
·\033[1;36m<name> way <level(0~+∞)> <direction(N/S/W/E)> <name of terminal passed>+\033[1;34m 设置路径（建议使用\033[1;36m/map\033[1;34m）\n\
·\033[1;36m<name> clearway\033[1;34m 清除路径信息\n\
·\033[1;36m<name> info\033[1;34m 获取运行状态，返回\033[1;36m@<name> <power(mV)> <direction> <onfire list> <way>\033[1;34m\n\
·\033[1;36m<name> onfire\033[1;34m 报警\n\
·\033[1;36m<name> notfire\033[1;34m 取消报警\033[0m')
            case '/about':
                print('\033[1;34m·本项目由Limpu开发。\n\
·硬件使用掌中宝+火焰传感器（钱包痛），代码用到宽搜、物联网通信等。') 
            case _:
                client.publish(tpc, txt)
