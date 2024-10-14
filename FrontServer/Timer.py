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

    def __timer(self, room_id, pid):
        if room_id == 'Initialized-Server-id':
            print('[Server] No room started')
        V = verify.Verify(room_id)
        self.__verification_result = V.verify()
        passport = self.__verification_result[0]
        if passport == 'Verified':
            print('[Server] Token Verified')
        else:
            try:
                r = sql.sql_use.RoomList()
                m = sql.sql_use.Map()
                r.logout(room_id)
                m.close_map(room_id)
                self.__Close(pid)
                print('[Server] Token_id: ',room_id,' Not Verified, Room Closed')
            except:
                print('[Server] T-code:0')

    def __task_timer(self):
        for i in range(1, len(self.__room_list)):
            room_id = self.__room_list[i]
            pid = self.__pid_list[i]
            self.__timer(room_id, pid)

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
            thread = threading.Thread(target=self.__receive_thread, args=(connection,))
            thread.setDaemon(True)
            thread.start()

    def __sender_5(self, connection:socket):
        self.__setMetaFlow(server_message=200)
        connection.send(json.dumps(self.__data_ts).encode())


    def __receive_thread(self, connection:socket):
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
                            self.__room_list.append(data_ts['room_id'])
                            self.__pid_list.append(data_ts['pid'])
                            print('[Server] Room ',data_ts['room_id'],'added')
                        except :
                            # 列表写入出错
                            print('[Server] T-code:1')
                    elif data_ts['server_message'] == '201':
                        self.__room_list.remove(data_ts['room_id'])
                        self.__pid_list.remove(data_ts['pid'])
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
