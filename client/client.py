import socket
import threading
import json
import time
from cmd import Cmd

host = '127.0.0.1'
port = 8888


class Client(Cmd):
    """
    客户端
    """
    prompt = ''
    intro = '[Welcome] 简易聊天室客户端(Cli版)\n' + '[Welcome] 输入help来获取帮助\n'

    def __init__(self):
        """
        构造
        """
        super().__init__()
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__id = None
        self.__nickname = None
        self.__isLogin = False
        self.reconnect_flag = 0

    def __receive_message_thread(self):
        """
        接受消息线程
        """
        while self.__isLogin:
            # noinspection PyBroadException
            try:
                buffer = self.__socket.recv(1024).decode()
                obj = json.loads(buffer)
                print('[' + str(obj['sender_nickname']) + '(' + str(obj['sender_id']) + ')' + ']', obj['message'])
            except Exception:
                print('[Client] 无法从服务器获取数据')

    def __send_message_thread(self, Type, message):
        """
        发送消息线程
        :param message: 消息内容
        """
        self.__socket.send(json.dumps({
            'type': Type,
            'sender_id': self.__id,
            'message': message
        }).encode())

    def start(self):
        """
        启动客户端
        """
        global host
        global port
        self.__socket.connect((host, port))
        self.cmdloop()

    def do_login(self, args):
        """
        登录聊天室
        :param args: 参数
        """
        nickname = args.split(' ')[0]

        # 将昵称发送给服务器，获取用户id
        self.__socket.send(json.dumps({
            'type': 'login',
            'nickname': nickname
        }).encode())
        # 尝试接受数据
        # noinspection PyBroadException
        try:
            buffer = self.__socket.recv(1024).decode()
            obj = json.loads(buffer)
            if obj['id']:
                self.__nickname = nickname
                self.__id = obj['id']
                self.__isLogin = True
                print('[Client] 成功登录到聊天室')

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

    def do_send(self, Type, args):
        """
        发送消息
        :param args: 参数
        """
        message = args
        # 显示自己发送的消息
        print('[' + str(self.__nickname) + '(' + str(self.__id) + ')' + ']', message)
        # 开启子线程用于发送数据
        thread = threading.Thread(target=self.__send_message_thread, args=(Type, message,))
        thread.setDaemon(True)
        thread.start()

    def do_logout(self, args=None):
        """
        登出
        :param args: 参数
        """
        self.__socket.send(json.dumps({
            'type': 'logout',
            'sender_id': self.__id
        }).encode())
        self.__isLogin = False
        return True

    def create_chatroom(self):
        """
        创建聊天室
        """
        message = self.__nickname
        # 开启子线程用于发送数据
        thread = threading.Thread(target=self.__send_message_thread, args=('ChatRoom', message,))
        thread.setDaemon(True)
        thread.start()

    def do_join(self, args):
        """
        加入房间
        :param args: 参数（用户输入token）
        """
        message = args
        # 开启子线程用于发送数据
        thread = threading.Thread(target=self.__send_message_thread, args=('Join', message,))
        thread.setDaemon(True)
        thread.start()

    def do_help(self, arg):
        """
        帮助
        :param arg: 参数
        """
        command = arg.split(' ')[0]
        if command == '':
            print('[Help] login nickname - 登录到聊天室，nickname是你选择的昵称')
            print('[Help] send message - 发送消息，message是你输入的消息')
            print('[Help] logout - 退出聊天室')
        elif command == 'start':
            print('[Help] start - 创建聊天房间')
        elif command == 'login':
            print('[Help] login nickname - 登录到聊天室，nickname是你选择的昵称')
        elif command == 'send':
            print('[Help] send message - 发送消息，message是你输入的消息')
        elif command == 'logout':
            print('[Help] logout - 退出聊天室')
        elif command == 'join':
            print('[Help] join token - 加入指定聊天室')

        else:
            print('[Help] 没有查询到你想要了解的指令')

