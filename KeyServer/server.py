import socket
import threading
import json
import hashlib
import random
import sqlite3
import jwt
import uuid
from datetime import datetime, timedelta


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

    def __user_thread(self, user_id):
        """
        用户子线程
        :param user_id: 用户id
        """
        No = self.__uuids.index(user_id)
        connection = self.__connections[No]
        nickname = self.__nicknames[No]
        print('[Server] 用户', user_id, nickname, '已登录')
        self.__messaging(user_id, message='用户 ' + str(nickname) + '已登录')

        # 侦听
        while True:
            # noinspection PyBroadException
            try:
                buffer = connection.recv(1024).decode()
                # 解析成json数据
                obj = json.loads(buffer)
                # 如果是广播指令
                if obj['type'] == 'ChatRoom':
                    self.create_token(obj['message'])
                elif obj['type'] == 'Join':
                    token = obj['message']
                    if self.__rooms.index(token):
                        print('找到房间')

                else:
                    print('[Server] 无法解析json数据包:', connection.getsockname(), connection.fileno())
            except Exception:
                print('[Server] 连接失效:', connection.getsockname(), connection.fileno())
                self.__connections[user_id].close()
                self.__connections[user_id] = None
                self.__nicknames[user_id] = None

    def __messaging(self, user_id, message):
        """
        广播
        :param user_id: 用户id(0为系统)
        :param message: 广播内容
        """
        i = 0
        for user in self.__uuids:
            if user_id != user and self.__connections[i]:
                self.__connections[i].send(json.dumps({
                    'sender_id': user_id,
                    'sender_nickname': self.__nicknames[user_id],
                    'message': message
                }).encode())
                i += 1
            i += 1


    def __waitForLogin(self, connection):
        # 尝试接受数据
        # noinspection PyBroadException
        try:
            buffer = connection.recv(1024).decode()
            # 解析成json数据
            obj = json.loads(buffer)
            # 如果是连接指令，那么则返回一个新的用户编号，接收用户连接
            if obj['type'] == 'login':
                self.__connections.append(connection)
                uid = uuid.uuid1()
                self.__nicknames.append(obj['nickname'])
                self.__uuids.append(uid)
                self.__users.append((uid, obj['nickname']))
                connection.send(json.dumps({
                    'id': uid
                }).encode())

                # 开辟一个新的线程
                thread = threading.Thread(target=self.__user_thread, args=str(uid))
                thread.setDaemon(True)
                thread.start()
            else:
                print('[Server] 无法解析json数据包:', connection.getsockname(), connection.fileno())
        except Exception:
            print('[Server] 无法接受数据:', connection.getsockname(), connection.fileno())

    def start(self):
        """
        启动服务器
        """
        # 绑定端口
        self.__socket.bind(('127.0.0.1', 8888))
        # 启用监听
        self.__socket.listen(10)
        print('[Server] 服务器正在运行......')

        # 清空连接
        self.__connections.clear()
        self.__nicknames.clear()
        self.__connections.append(None)
        self.__nicknames.append('System')
        # 开始侦听
        while True:
            connection, address = self.__socket.accept()
            print('[Server] 收到一个新连接', connection.getsockname(), connection.fileno())

            thread = threading.Thread(target=self.__waitForLogin, args=(connection,))
            thread.setDaemon(True)
            thread.start()

    def create_token(self, Creator):
        token = self.__generate(Creator)
        self.__rooms.append(token)
        """
        发送方式需更改
        """

    def __generate(self, name):
        """
        生成token
        """
        num = str(random.randint(10**32, 10**33))
        secret_num = ''.join(random.choices(num, k=16))
        key_hash = hashlib.sha256()
        key_hash.update(name)
        key_hash.update(secret_num)
        self.__key = key_hash.hexdigest()
        name_hash = hashlib.sha256()
        name_hash.update(name)
        payload = {
            'exp': datetime.now() + timedelta(minutes=30),  # 令牌过期时间
            'username': name_hash  # 想要传递的信息,如用户名ID
        }

        encoded_jwt = jwt.encode(payload, self.__key, algorithm='HS256')
        self.__rooms.append((encoded_jwt, self.__key))
        self.__key = ''
        return encoded_jwt

    def __room_thread(self, user_id, token):
        """
        需加入端口检测机制
        """
        port = random.randint(1, 65535)
"""
    def join_token(self, user_id , token):
        temp_keys = []
        for room in self.__rooms:
            self.__chatroom.append(room[0])
            temp_keys.append(room[1])
        if token in temp_tokens:
            pos = temp_tokens.index(token)
            key = temp_keys[pos]
            try:
                # 验证JWT
                decoded_payload = jwt.decode(token, key, algorithms=['HS256'])
                print('Decoded Payload:', decoded_payload)
            except jwt.ExpiredSignatureError:
                print('JWT has expired.')
            except jwt.InvalidTokenError:
                print('Invalid JWT.')
"""






