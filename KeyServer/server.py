import socket
import threading
import json
import hashlib
import random
import os
import jwt
import uuid
from datetime import datetime, timedelta
import sql.sql_use
from modules.PorCheck import PortCheck
from modules.verify import Verify

class Server:
    """
    服务器类
    """

    def __init__(self):
        """
        构造
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connections = list()
        self.__uuids = list()
        self.__users = list()
        self.__nicknames = list()
        self.__rooms = list()
        self.__chatroom = list()
        self.__key = ''
        self.__verification_result = list()
        self.__ports = list()
        self.__isActive = False
        self.__port = 0
        self.__type = ''

    def __user_thread(self, user_id):
        """
        用户子线程
        :param user_id: 用户id
        """
        No = self.__uuids.index(user_id)
        print(No)
        connection = self.__connections[No]
        print(connection)
        nickname = self.__nicknames[No]
        print('[Server] 用户', user_id, nickname, '已登录')
        print('端口加载中')
        P = PortCheck(0)
        self.__ports = P.getAvailable_ports()
        print('加载完成')
        thread = threading.Thread(target=self.__init_sender, args=(user_id, '用户 ' + str(nickname) + '已登录'))
        thread.setDaemon(True)
        thread.start()

        # 侦听
        while True:
            # noinspection PyBroadException
            #try:
            buffer = connection.recv(1024).decode()
            # 解析成json数据
            data = json.loads(buffer)
            if data['type'] == 'ChatRoom':
                self.create_token(data['message'],user_id)
            elif data['type'] == 'Join':
                token = data['message']
                hash_id = hash_generator(token)
                M = sql.sql_use.Map()
                M.mapping(room_id=hash_id)
                self.__key_thread(hash_id)
                passport = self.__verification_result[0]
                isActive = self.__verification_result[1]
                port = self.__verification_result[2]
                if M.getUid() and passport == 'Verified':
                    if isActive:
                        connection.send(json.dumps({
                            'type': 'goChat',
                            'port': port,
                        }).encode())
                        print('Asking transmission server to ChatServer')

                    else:
                        thread = threading.Thread(target=self.__room_thread, args=(token,port))
                        connection.send(json.dumps({
                            'type': 'goChat',
                            'port': port,
                        }).encode())
                        thread.setDaemon(True)
                        thread.start()
                elif passport == 'Close':
                    thread = threading.Thread(target=self.__messaging, args=(user_id, 'Room Closed'))
                    thread.setDaemon(True)
                    thread.start()
                    M = sql.sql_use.Map()
                    R = sql.sql_use.RoomList()
                    R.logout(hash_id)
                    M.close_map(hash_id)

                elif passport == 'Invalid':
                    thread = threading.Thread(target=self.__messaging, args=( user_id, 'Invalid token'))
                    thread.setDaemon(True)
                    thread.start()
            else:
                print('[Server] 无法解析json数据包')

            """except Exception:
                print('[Server] 连接失效:', connection.getsockname(), connection.fileno())
                self.__connections[No].close()
                self.__connections[No] = None
                self.__nicknames[No] = None"""

    def __key_thread(self, room_id):
        V = Verify(room_id)
        self.__verification_result = V.verify()
        print('Verification program closed')

    def __messaging(self,user_id, message):
        """
        广播
        :param user_id: 用户id(0为系统)
        :param message: 广播内容
        """
        No = self.__uuids.index(user_id)
        self.__connections[No].send(json.dumps({
            'type':self.__type,
            'sender_id': user_id,
            'sender_nickname': self.__nicknames[No],
            'message': message
        }).encode())
        print(message)

    def __init_sender(self,user_id,message):
        No = self.__uuids.index(user_id)
        for i in range(1, len(self.__connections)):
            if No != i and self.__connections[i]:
                self.__connections[i].send(json.dumps({
                    'type':'Initialize',
                    'sender_id': user_id,
                    'sender_nickname': self.__nicknames[No],
                    'message': message
                }).encode())

    def start(self,host='127.0.0.1', port=8888):
        """
        启动服务器
        """
        # 绑定端口
        self.__socket.bind((host, port))
        # 启用监听
        self.__socket.listen(10)
        print('[Server] 服务器正在运行......')
        # 清空连接
        self.__connections.clear()
        self.__nicknames.clear()
        self.__uuids.clear()
        self.__connections.append(None)
        self.__uuids.append(None)
        self.__nicknames.append('System')
        # 开始侦听
        while True:
            connection, address = self.__socket.accept()
            print('[Server] 收到一个新连接', connection.getsockname(), connection.fileno())
            thread = threading.Thread(target=self.__waitForLogin, args=(connection,))
            thread.setDaemon(True)
            thread.start()

    def create_token(self, Creator, user_id):
        print('Start Creating Token')
        token = self.__generate(Creator,user_id)
        print(token)
        self.__type = 'Token'
        self.__port = random.choice(self.__ports)
        R = sql.sql_use.RoomList()
        R.logRoom(hash_generator(token),self.__port)
        R.login()
        No = self.__uuids.index(user_id)
        self.__connections[No].send(json.dumps({
                'type': self.__type,
                'sender_id': user_id,
                'sender_nickname': self.__nicknames[No],
                'message': token
                }).encode())

    def __generate(self, name, uid):
        """
        生成token
        """
        num = str(random.randint(10**32, 10**33))
        secret_num = ''.join(random.choices(num, k=16))
        key_hash = hashlib.sha256()
        key_hash.update(name.encode())
        key_hash.update(secret_num.encode())
        self.__key = key_hash.hexdigest()
        name_hash = hashlib.sha256()
        name_hash.update(name.encode())

        payload = {
            'exp': datetime.now() + timedelta(minutes=30),  # 令牌过期时间
            'username': name_hash.hexdigest()  # 想要传递的信息,如用户名ID
        }

        encoded_jwt = jwt.encode(payload, self.__key, algorithm='HS256')

        K = sql.sql_use.Keys()
        M = sql.sql_use.Map()
        M.map_update(hash_generator(encoded_jwt), uid)
        K.token_insert(encoded_jwt, self.__key)
        # 写入本地数据库
        self.__key = ''
        return encoded_jwt

    def __room_thread(self, token,port):
        """
        写入RoomList
        用户加入后分配端口和线程
        """
        room_id = hash_generator(token)
        R = sql.sql_use.RoomList()
        R.logRoom(room_id, port)
        R.login()
        R.room_status_update(room_id, True)



def hash_generator(content):
    m = hashlib.sha256()
    m.update(content.encode())
    return m.hexdigest()







