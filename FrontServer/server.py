import signal
import socket
import os
import json
import uuid
import hashlib
import threading
import sql
import modules.verify

class FrontServer:
    def __init__(self):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__dst_port = 0
        self.__FrontServer_port = 8801
        self.__Function_mode = 0 # 0:登录 1:创建 2:加入 3:聊天 4:登出
        self.__connections = []
        self.__S_type = None
        self.__C_type = None
        self.__sender_nickname = None
        self.__sender_id = None
        self.__KeyServer_port = 8888
        self.__isActive = None # False
        self.__token = None
        self.__room_id = None
        self.__pid = None
        self.__sender_message = None
        self.__server_message = None
        self.__S_type_list = ['Initialize','Key','Chat','ALL']
        self.__C_type_list = ['login','ChatRoom','Join','logout','goChat','Close','Initialize']
        self.__token_list = []
        self.__pid_list = []
        self.__uuids = []
        self.__nicknames = []
        self.__verification_result = []

    def __waitForLogin(self, connection):
        # 尝试接受数据
        # noinspection PyBroadException
        try:
            buffer = connection.recv(1024).decode()
            # 解析成json数据
            data_cs = json.loads(buffer)
            print(data_cs)
            # 如果是连接指令，那么则返回一个新的用户编号，接收用户连接
            if data_cs['C_type'] == 'login':
                self.__type_match(0,6)
                self.__connections.append(connection)
                self.__nicknames.append(data_cs['sender_nickname'])
                uid = uuid.uuid1()
                self.__setMetaFlow(sender_id=str(uid),sender_nickname=data_cs['sender_nickname'])
                data_cs = self.__cs_data_build()
                U = sql.sql_use.UserList()
                U.user_login(data_cs['sender_nickname'], str(uid))
                self.__uuids.append(str(uid))
                connection.send(json.dumps(data_cs).encode())
                # 开辟一个新的线程
                thread = threading.Thread(target=self.__user_thread, args=(str(uid),))
                thread.setDaemon(True)
                thread.start()
            else:
                print('[Server] 无法解析json数据包:', connection.getsockname(), connection.fileno())
        except Exception:
            print('[Server] 无法接受数据:', connection.getsockname(), connection.fileno())

    def __Forward(self, data_ss):
        """
        端口转发
        """
        rs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rs.connect(('localhost', self.__dst_port))
        """
        data{
            S_type: 服务类型,
            C_type: 通信类型,
            sender_id: 发送方的id,
            port: 聊天服务器(房间)访问端口,
            isActive: 房间是否已激活(第一个用户加入房间时激活),
            token: JWT生成的可验证的token payload用于用户加入房间,
            room_id: 房间id(生成自token),
            pid: 房间进程
            sender_nickname: 用户昵称,
            message: 用户使用send指令发送的信息
            }
        """
        rs.sendall(data_ss)
        data_ss = rs.recv(1024)
        rs.listen(5)
        return data_ss

    def __type_match(self, s=0,c=0):
        self.__S_type = self.__S_type_list[s]
        self.__C_type = self.__C_type_list[c]

    def __ss_data_build(self):
        data={
            'S_type': self.__S_type,
            'C_type': self.__C_type,
            'sender_id': self.__sender_id,
            'port': self.__dst_port,
            'isActiv': self.__isActive,
            'token': self.__token,
            'room_id': self.__room_id,
            'pid': self.__pid,
            'sender_nickname': self.__sender_nickname,
            'sender_message': self.__sender_message,
            'server_message': self.__server_message
        }
        return data

    def __cs_data_build(self):
        data = {
            'C_type': self.__C_type,
            'sender_id': self.__sender_id,
            'token': self.__token,
            'sender_nickname': self.__sender_nickname,
            'sender_message': self.__sender_message,
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
                    self.__port = metaFlow[i]
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
    @staticmethod
    def __chat_thread_start(port, token):
        cmd = "python3.9 chatroom_start.py --port " + port + ' --interface ' + token
        os.system(cmd)

    def __Close(self, pid):
        os.kill(pid, signal.SIGINT)
        print('Closing Chat Server:',pid)
        self.__Function_mode = 0

    def __timer(self, token, pid):
        room_id = hash_generator(token)
        V = modules.verify.Verify(room_id)
        self.__verification_result = V.verify()
        passport = self.__verification_result[0]
        if passport == 'Verified':
            print('Token Verified')
        else:
            self.__Close(pid)
            print('Token_id: ',room_id,' Not Verified, Room Closed')

    def __task_timer(self):
        for i in range(1, len(self.__token_list)):
            token = self.__token_list[i]
            pid = self.__pid_list[i]
            self.__timer(token, pid)

    def run(self,host = '127.0.0.1', port = 8801):
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
        self.__nicknames.append('[System]')
        self.__pid_list.append(os.getpid())
        # 开始侦听
        while True:
            connection, address = self.__socket.accept()
            print('[Server] 收到一个新连接', connection.getsockname(), connection.fileno())
            thread = threading.Thread(target=self.__waitForLogin, args=(connection,))
            thread.setDaemon(True)
            thread.start()
            thread1 = threading.Timer(870, self.__task_timer)
            thread1.setDaemon(True)
            thread1.start()

    def __user_thread(self, user_id):
        """
        用户子线程
        :param user_id: 用户id
        """
        No = self.__uuids.index(user_id)
        connection = self.__connections[No]
        nickname = self.__nicknames[No]
        print('[Server] 用户', user_id, nickname, '已登录')
        thread = threading.Thread(target=self.__sender_0, args=(user_id, '用户 ' + str(nickname) + ' 已登录'))
        thread.setDaemon(True)
        thread.start()

        # 侦听
        while True:
            # noinspection PyBroadException
            try:
                buffer = connection.recv(1024).decode()
                # 解析成json数据
                data_cs = json.loads(buffer)
                self.__setMetaFlow(sender_id=data_cs['sender_id'], token=data_cs['token'],
                                   sender_nickname=data_cs['sender_nickname'], sender_message=data_cs['sender_message'])
                if data_cs['C_type'] == 'ChatRoom':
                    """
                    接收create信息
                    """
                    self.__setMetaFlow(port=8888)
                    self.__type_match(1,1)
                    data_ss = self.__ss_data_build()
                    self.__Forward(data_ss)
                    data_cs = self.__Forward(data_ss)
                    connection.send(json.dumps(data_cs).encode())
                    print()
                elif data_cs['C_type'] == 'Join':
                    """
                    接收join信息
                    """
                    self.__setMetaFlow(port=8888)
                    self.__type_match(1, 2)
                    data_ss = self.__ss_data_build()
                    print(data_ss)
                    data_cs = self.__Forward(data_ss)
                    connection.send(json.dumps(data_cs).encode())

                elif data_cs['C_type'] == 'logout':
                    """
                    接收logout信息
                    """
                    self.__type_match(3, 3)
                    data_ss = self.__ss_data_build()
                    self.__Forward(data_ss)
                    data_cs = self.__Forward(data_ss)
                    connection.send(json.dumps(data_cs).encode())

                elif data_cs['C_type'] == 'goChat':
                    """
                    接收send信息
                    """
                    self.__setMetaFlow(port=88)
                    self.__type_match(2, 4)
                    data_ss = self.__ss_data_build()
                    self.__Forward(data_ss)
                    data_cs = self.__Forward(data_ss)
                    connection.send(json.dumps(data_cs).encode())

                elif data_cs['C_type'] == 'Initialized':
                    print('Client ',self.__sender_id,' Initialized')

                else:
                    print('[Server] 无法解析json数据包')
            except Exception :
                print('发生了某些错误，已关闭连接')
                del self.__connections[No]

    def __sender_0(self,user_id,message):
        self.__type_match(3,6)
        self.__setMetaFlow(sender_id=user_id,sender_message=message)
        data_cs = self.__cs_data_build()
        No = self.__uuids.index(user_id)
        print('start first try')
        print(data_cs)
        for i in range(1, len(self.__connections)):
            if No == i and self.__connections[i]:
                self.__connections[i].send(json.dumps(data_cs).encode())

    def __setDst_port(self, port):
        self.__dst_port = port

def hash_generator(content):
    m = hashlib.sha256()
    m.update(content.encode())
    return m.hexdigest()