import json
import os
import signal
import socket
import threading
import time

import sql.sql_use
from modules import verify


class Timer:
    def __init__(self):
        self.__interval = 30  # min
        self.__timer_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__chat_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__chat_port = 0
        self.__isActive = False
        self.__room_id = None
        self.__pid = None
        self.__server_message = None
        self.__receive_flag = 0
        self.__connections = []
        self.__room_list = []
        self.__pid_list = []
        self.__verification_result = []


    @property
    def __data_ts(self):
        data = {
            'T_type': 'Timer',
            'isActive': self.__isActive,
            'room_id': self.__room_id,
            'pid': self.__pid,
            'server_message': self.__server_message
        }
        return data

    def __setMetaFlow(self, isActive=None, room_id=None, pid=None,server_message=None):
        metaFlow = [isActive,room_id,pid,server_message]
        for i in range(len(metaFlow)):
            if metaFlow[i] is not None:
                if i == 0:
                    self.__isActive = metaFlow[i]
                elif i == 1:
                    self.__room_id = metaFlow[i]
                elif i == 2:
                    self.__pid = metaFlow[i]
                elif i == 3:
                    self.__server_message = metaFlow[i]

    @staticmethod
    def __Close(pid):
        os.kill(pid, signal.SIGINT)
        print('[Server] Closing Chat Server:', pid)

    def __timer(self, room_id):
        if room_id == 'Initialized-Server-id':
            print('[Server] No room started')
        V = verify.Verify(room_id)
        self.__verification_result = V.verify()
        passport = self.__verification_result[0]
        isActive = self.__verification_result[1]
        port = self.__verification_result[2]
        if isActive and port:
            if passport == 'Verified':
                print('[Server] Token Verified')
            else:
                try:
                    self.__sender_6(port=port)
                    r = sql.sql_use.RoomList()
                    m = sql.sql_use.Map()
                    r.logout(room_id)
                    m.close_map(room_id)
                    print('[Server] Token_id: ',room_id,' Not Verified, Room Closed')
                except:
                    print('[Server] T-code:0')
        if isActive is False:
            if passport == 'Verified':
                print('[Server] Token Verified')
            else:
                try:
                    r = sql.sql_use.RoomList()
                    m = sql.sql_use.Map()
                    r.logout(room_id)
                    m.close_map(room_id)
                    print('[Server] Token_id: ',room_id,' Not Verified, Room Closed')
                except:
                    print('[Server] T-code:0')
    def __t_timer(self,i):
        self.__timer(self.__room_list[i])

    def __task_timer(self):
        t_list = []
        r = sql.sql_use.RoomList()
        self.__room_list = r.room_list
        for i in range(len(self.__room_list)):
            t = threading.Thread(target=self.__t_timer, args=(i,))
            t_list.append(t)
        for t in t_list:
            t.setDaemon(True)
            t.start()


    def run_timer(self, host='127.0.0.1', port=8802, interval=14):
        self.__timer_connection.bind((host, port))
        self.__timer_connection.listen(10)
        self.__connections.clear()
        self.__room_list.clear()
        self.__pid_list.clear()
        self.__verification_result.clear()
        self.__interval = interval
        while True:
            connection, client_address = self.__timer_connection.accept()
            print('[Server] 收到一个新连接', connection.getsockname(), connection.fileno())
            self.__receive_flag = 1
            thread = threading.Thread(target=self.__Timer_thread, args=(connection,))
            thread.setDaemon(True)
            thread.start()

    def __sender_5(self, connection:socket):
        self.__setMetaFlow(server_message=200)
        connection.send(json.dumps(self.__data_ts).encode())

    class Message:
        def __init__(self, connection:socket):
            self.__connection = connection
        def __sender_6(self, host='127.0.0.1', port=0):
            # 关闭sender
            self.__connection.connect((host, port))
            self.__setMetaFlow(server_message=201)
            self.__chat_connection.send(json.dumps(self.__data_ts).encode())
            buffer = self.__chat_connection.recv(1024)
            data_ts = json.loads(buffer.decode())
            self.__pid_list.append(data_ts['pid'])


    def __Timer_thread(self, connection:socket):
        thread = threading.Thread(target=self.__sender_5, args=(connection,))
        thread.setDaemon(True)
        thread.start()

        while self.__receive_flag:
            try:
                buffer = connection.recv(1024).decode()
                data_ts = json.loads(buffer)

                if data_ts['T_type']:
                    if data_ts['T_type'] == 'Timer':
                        try:
                        except :
                            # 列表写入出错
                            print('[Server] T-code:1')
                    elif data_ts['server_message'] == '201':
                        print('[Server] T-code:4')

                else:
                    with open('log/T-log','ab') as t:
                        T_log = '[Warning] '+str(time.localtime(time.time())) + ' 错误连接 ' + connection.getsockname() + connection.fileno() + '\n'
                        t.write(T_log)
                        t.close()
                        print('[Server] T-code:3 -', connection.getsockname(), connection.fileno())
            except:
                # 连接出错
                print('[Server] T-code:2')
