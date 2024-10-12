import hashlib
import json
import random
import socket
import threading
from datetime import datetime, timedelta

import jwt

import sql.sql_use
from modules.PorCheck import PortCheck
from modules.SecurityCheck import hash_generator, room_id_generator
from modules.verify import Verify


class KeyServer:
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
        self.__sender_nicknames = list()
        self.__rooms = list()
        self.__chatroom = list()
        self.__verification_result = list()
        self.__ports = list()
        self.__C_type = None
        self.__S_type = None
        self.__port = 0
        self.__S_type_list = ['Initialize', 'Key', 'Chat', 'ALL']
        self.__C_type_list = ['ChatRoom', 'Join', 'goChat', 'Close', 'Initialize']


    def __type_match(self, s=0, c=0):
        self.__S_type = self.__S_type_list[s]
        self.__C_type = self.__C_type_list[c]

    def __server_type_verification(self, connection):
        # 尝试接受数据
        # noinspection PyBroadException
        #try:
            buffer = connection.recv(1024).decode()
            # 解析成json数据
            data_ss = json.loads(buffer)
            # 如果是连接指令，那么则返回一个新的用户编号，接收用户连接
            if data_ss['S_type'] == 'Key':
                self.__type_match(1,4)
                self.__connections.append(connection)
                self.__sender_nicknames.append(data_ss['sender_nickname'])
                sender_id = data_ss['sender_id']
                sender_nickname = data_ss['sender_nickname']
                print('[Server] Searching for user', sender_id)
                data_ss = {'sender_id': sender_id, 'sender_nickname': sender_nickname,'server_message':'200'}
                # 查找是否存在sender_id
                U = sql.sql_use.UserList()
                user_id = U.search_uid(sender_nickname)
                if user_id == sender_id:
                    print('[Server] User', user_id, 'found')
                    self.__uuids.append(sender_id)
                    connection.send(json.dumps(data_ss).encode())
                    # 开辟一个新的线程
                    u = UserThread(sender_id, sender_nickname, connection)
                    thread = threading.Thread(target=u.user_thread)
                    thread.setDaemon(True)
                    thread.start()
                else:
                    print('[Server] User not found')
            elif data_ss['S_type'] == 'Chat':
                print('Wrong connection code:0')
            elif data_ss['S_type'] == 'All':
                print('Executing')
            else:
                print('[Server] Wrong connection code:1:')
        #except Exception:
        #    print('[Server] 无法接受数据:', connection.getsockname(), connection.fileno())

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
        self.__sender_nicknames.clear()
        self.__uuids.clear()
        self.__connections.append(None)
        self.__uuids.append(None)
        self.__sender_nicknames.append('System')
        # 开始侦听
        while True:
            connection, address = self.__socket.accept()
            print('[Server] 收到一个新连接', connection.getsockname(), connection.fileno())
            thread = threading.Thread(target=self.__server_type_verification, args=(connection,))
            thread.setDaemon(True)
            thread.start()


class UserThread:
    def __init__(self, sender_id, sender_nickname, connection:socket):
        self.__sender_id = sender_id
        self.__sender_nickname = sender_nickname
        self.__connection: socket = connection
        self.__S_type_list = ['Initialize', 'Key', 'Chat', 'ALL']
        self.__C_type_list = ['ChatRoom', 'Join', 'goChat', 'Close', 'Initialize']
        self.__dst_port = 0
        self.__isActive = None  # False
        self.__token = None
        self.__room_id = None
        self.__pid = None
        self.__sender_message = None
        self.__server_message = None
        self.__S_type = None
        self.__C_type = None
        self.__key = None

    @property
    def __data_ss(self):
        data = {
            'S_type': self.__S_type,
            'C_type': self.__C_type,
            'sender_id': self.__sender_id,
            'port': self.__dst_port,
            'isActive': self.__isActive,
            'token': self.__token,
            'room_id': self.__room_id,
            'pid': self.__pid,
            'sender_nickname': self.__sender_nickname,
            'sender_message': self.__sender_message,
            'server_message': self.__server_message
        }
        return data

    def __setMetaFlow(self, sender_id=None, port=None, isActive=None, token=None, room_id=None, pid=None,
                      sender_nickname=None, sender_message=None, server_message=None):
        metaFlow = [sender_id,port,isActive,token,room_id,pid,sender_nickname,sender_message,server_message]
        for i in range(len(metaFlow)):
            if metaFlow[i] is not None:
                if i == 0:
                    self.__sender_id = metaFlow[i]
                elif i == 1:
                    self.__dst_port = metaFlow[i]
                elif i == 2:
                    self.__isActive = metaFlow[i]
                elif i == 3:
                    self.__token = metaFlow[i]
                elif i == 4:
                    self.__room_id = metaFlow[i]
                elif i == 5:
                    self.__pid = metaFlow[i]
                elif i == 6:
                    self.__sender_nickname = metaFlow[i]
                elif i == 7:
                    self.__sender_message = metaFlow[i]
                elif i == 8:
                    self.__server_message = metaFlow[i]

    def __type_match(self, s=0, c=0):
        self.__S_type = self.__S_type_list[s]
        self.__C_type = self.__C_type_list[c]

    def user_thread(self):
        """
        用户子线程
        """
        print('[Server] 用户', self.__sender_id ,'已连接')
        thread = threading.Thread(target=self.__sender_1, args=( self.__sender_id,))
        thread.start()
        # 侦听
        while True:
            # noinspection PyBroadException
            #try:
            buffer = self.__connection.recv(1024).decode()
            # 解析成json数据
            data_ss = json.loads(buffer)
            if data_ss['C_type'] == 'ChatRoom':
                self.__create_token(data_ss['sender_nickname'],self.__sender_id)
            elif data_ss['C_type'] == 'Join':
                token = data_ss['message']
                hash_id = hash_generator(token)
                M = sql.sql_use.Map()
                M.mapping(room_id=hash_id)
                self.__key_thread(hash_id)
                passport = self.__verification_result[0]
                isActive = self.__verification_result[1]
                port = self.__verification_result[2]
                if M.getUid() and passport == 'Verified':
                    if isActive:
                        self.__connection.send(json.dumps({
                            'type': 'goChat',
                            'port': port,
                        }).encode())
                        print('[KeyServer] Asking transmission server to ChatServer')

                    else:
                        thread = threading.Thread(target=self.__room_thread, args=(token,port))
                        self.__connection.send(json.dumps({
                            'type': 'goChat',
                            'port': port,
                        }).encode())
                        thread.setDaemon(True)
                        thread.start()
                elif passport == 'Close':
                    thread = threading.Thread(target=self.__messaging, args=(self.__sender_id, 'Room Closed'))
                    thread.setDaemon(True)
                    thread.start()
                    M = sql.sql_use.Map()
                    R = sql.sql_use.RoomList()
                    R.logout(hash_id)
                    M.close_map(hash_id)

                elif passport == 'Invalid':
                    thread = threading.Thread(target=self.__messaging, args=( self.__sender_id, 'Invalid token'))
                    thread.setDaemon(True)
                    thread.start()
            else:
                print('[KeyServer] 无法解析json数据包')

            """except Exception:
                print('[Server] 连接失效:', self.__connection.getsockname(), self.__connection.fileno())
                self.__connections[No].close()
                self.__connections[No] = None
                self.__sender_nicknames[No] = None"""

    def __key_thread(self, room_id):
        V = Verify(room_id)
        self.__verification_result = V.verify()
        print('Verification program closed')

    def __sender_1(self,user_id):
        """
        初始化sender
        """
        self.__type_match(1,0)
        self.__setMetaFlow(sender_id=user_id, server_message='Connected')
        print('[Server]',self.__data_ss)
        self.__connection.send(json.dumps(self.__data_ss).encode())

    def __sender_2(self,user_id):
        """
        关闭sender
        """
        self.__type_match(3,3)
        self.__setMetaFlow(sender_id=user_id, sender_message='[Server] Room Closed',server_message='[Server] Room Closed')
        self.__connection.send(json.dumps(self.__data_ss).encode())

    def __sender_3(self,user_id,server_message):
        """
        服务器变更sender
        """
        self.__type_match(1,2)
        self.__setMetaFlow(sender_id=user_id,token=self.__token,isActive=True,server_message=server_message)
        self.__connection.send(json.dumps(self.__data_ss).encode())

    def __sender_4(self,user_id,token):
        """
        token sender
        """
        self.__type_match(1,2)
        self.__setMetaFlow(sender_id=user_id, token=token,server_message='Connected')
        print('[Server]',self.__data_ss)
        self.__connection.send(json.dumps(self.__data_ss).encode())

    def __create_token(self, Creator, user_id):
        print('[KeyServer] Start Creating Token')
        token = self.__generate(Creator, user_id)
        print('[Server]',token)
        # 选择端口
        p = PortCheck(0)
        self.__port = p.getRecommendedPort()
        R = sql.sql_use.RoomList()
        R.logRoom(room_id_generator(token), self.__port)
        R.login()
        self.__sender_4(user_id,token)

    def __generate(self, name, uid):
        """
        生成token
        """
        num = str(random.randint(10 ** 32, 10 ** 33))
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
        M.map_update(room_id_generator(encoded_jwt), uid)
        K.token_insert(encoded_jwt, self.__key)
        # 写入本地数据库
        return encoded_jwt

    @staticmethod
    def __room_thread(token, port):
        """
        写入RoomList
        用户加入后分配端口和线程
        """
        room_id = hash_generator(token)
        R = sql.sql_use.RoomList()
        R.logRoom(room_id, port)
        R.login()
        R.room_status_update(room_id, True)






