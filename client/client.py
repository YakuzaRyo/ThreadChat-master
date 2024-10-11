import socket
import threading
import json
import time
from cmd import Cmd


class Client(Cmd):
    """
    客户端
    """
    prompt = ''
    intro = '[Welcome] ####ThreadChat Server####\n' + '[Welcome] 输入help来获取帮助\n'

    def __init__(self):
        """
        构造
        """
        super().__init__()
        self.__C_type = None
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__sender_id = None
        self.__sender_nickname = None
        self.__token = None
        self.__message = None
        self.__isLogin = False
        self.reconnect_flag = 0
        self.__type = None

    def __cs_data_build(self):
        data = {
            'C_type': self.__C_type,
            'sender_id': self.__sender_id,
            'token': self.__token,
            'sender_nickname': self.__sender_nickname,
            'sender_message': self.__message,
        }
        return data

    def __setMetaFlow_cs(self, C_type = None,sender_id=None, token=None, sender_nickname=None, message=None):
        metaFlow = [C_type, sender_id, token, sender_nickname, message]
        for i in range(len(metaFlow)):
            if metaFlow[i] is not None:
                if i == 0:
                    self.__C_type = metaFlow[i]
                elif i == 1:
                    self.__sender_id = metaFlow[i]
                elif i == 2:
                    self.__token = metaFlow[i]
                elif i == 3:
                    self.__sender_nickname = metaFlow[i]
                elif i == 4:
                    self.__message = metaFlow[i]



    def __receive_message_thread(self):
        """
        接受消息线程
        """
        while self.__isLogin:
            # noinspection PyBroadException
            try:
                buffer = self.__socket.recv(1024).decode()
                data_cs = json.loads(buffer)

                if data_cs['C_type'] == 'Initialize':
                    self.__setMetaFlow_cs(C_type='Initialized')
                    print('[Server]', data_cs['sender_message'])
                    self.__socket.send(json.dumps(self.__cs_data_build()).encode())

                elif data_cs['C_type'] == 'Token':
                    print('Use://',data_cs['message'], '//to join the chatroom')

                elif data_cs['C_type'] == 'goChat':
                    port = data_cs['port']
                    self.__socket.close()
                    thread = threading.Thread(target=self.start,args=(port,))
                    thread.setDaemon(True)
                    thread.start()
            except Exception:
                print('[Client] 无法从服务器获取数据')
                exit(0)

    def __send_message_thread(self, message):
        """
        发送消息线程
        :param message: 消息内容
        """
        print('start sending message')
        self.__setMetaFlow_cs(message=message)
        self.__socket.send(json.dumps(self.__cs_data_build()).encode())
        print('From send thread C_type:',self.__type)
        time.sleep(0.5)

    def start(self,host='127.0.0.1',port=8801):
        """
        启动客户端
        """
        self.__socket.connect((host, port))
        self.cmdloop()

    def do_login(self, args):
        """
        登录聊天室
        :param args: 参数
        """
        nickname = args.split(' ')[0]
        self.__setMetaFlow_cs(C_type='login', sender_nickname=nickname)
        # 将昵称发送给服务器，获取用户id
        self.__socket.send(json.dumps(self.__cs_data_build()).encode())
        # 尝试接受数据
        # noinspection PyBroadException
        try:
            buffer = self.__socket.recv(1024).decode()
            data_cs = json.loads(buffer)
            if data_cs['sender_id']:
                self.__setMetaFlow_cs(sender_id=data_cs['sender_id'],sender_nickname=nickname)
                self.__isLogin = True
                # 开启子线程用于接受数据
                thread = threading.Thread(target=self.__receive_message_thread)
                thread.setDaemon(True)
                thread.start()
            else:
                print('[Client] 无法登录到聊天室')
        except socket.error:
            print('正在重新连接')
            self.start()
            if self.reconnect_flag < 9:
                self.reconnect_flag += 1
                print('正在尝试第', self.reconnect_flag, '/9次重连')
                self.do_login(args)
            else:
                print('重连失败，正在退出程序...')
                time.sleep(1)
                exit(0)
        except Exception as e:
            print(e)


    def do_send(self, args):
        """
        发送消息
        :param args: 参数
        """
        message = args
        # 显示自己发送的消息
        print('['+str(self.__sender_nickname) + ']', message)
        # 开启子线程用于发送数据
        thread = threading.Thread(target=self.__send_message_thread, args=(message,))
        thread.setDaemon(True)
        thread.start()

    def do_logout(self, args=None):
        """
        登出
        :param args: 参数
        """
        self.__socket.send(json.dumps({
            'C_type': 'logout',
            'sender_id': self.__sender_id
        }).encode())
        self.__isLogin = False
        return True

    def do_create(self,args=None):
        """
        创建聊天室
        """
        message = self.__sender_nickname
        self.__type = 'ChatRoom'
        # 开启子线程用于发送数据
        thread = threading.Thread(target=self.__send_message_thread, args=(message,))
        thread.setDaemon(True)
        thread.start()

    def do_join(self, args):
        """
        加入房间
        :param args: 参数（用户输入token）
        """
        message = args
        self.__type = 'Join'
        # 开启子线程用于发送数据
        thread = threading.Thread(target=self.__send_message_thread, args=(message,))
        thread.setDaemon(True)
        thread.start()

    def do_help(self, arg=None):
        """
        帮助
        :param arg: 参数
        """
        command = arg.split(' ')[0]
        if command == '':
            print('[Help] login sender_nickname - 登录到聊天室，nickname是你选择的昵称')
            print('[Help] join token - 加入指定聊天室')
            print('[Help] send message - 发送消息，message是你输入的消息')
            print('[Help] create - 创建指定聊天室')
            print('[Help] logout - 退出聊天室')

        else:
            print('[Help] 没有查询到你想要了解的指令')
    def __del__(self):
        self.__socket.close()
        del self.__socket
        del self.__sender_id
        del self.__token
        del self.__sender_nickname
        del self.__message
        del self.__C_type
        del self.__isLogin

    def do_exit(self, args=None):
        self.__del__()
        exit(0)


