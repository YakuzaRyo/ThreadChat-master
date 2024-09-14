# 用于分配聊天服务器端口
import socket
import random
import multiprocessing



class PortCheck:
    def __init__(self, flag):
        self.__process = None
        self.__threads = []
        self.__available_ports = []
        self.__unavailable_ports = []
        self.__process_start()
        # self.__threads_start()
        self.recommend_port = 0
        #self.__set_port()
        if flag:
            self.__debug()

    def __is_port_in_use(self, port):  # Rough check
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                self.__available_ports.append(port)
            except:
                s.close()
                # print('Port: %s Unavailable'%port)
                # self.__unavailable_ports.append(port)
            finally:
                s.close()
        """
        result = os.system(f"nc -zv 127.0.0.1 {port} > /dev/null 2>&1")
        if result == 0:
            self.__available_ports.append(port)
        else:
            print('Port: %s Unavailable'%port)

    def __threads_start(self):
        for i in range(0, 65536):
            t = threading.Thread(target=self.__is_port_in_use, args=(i,))
            self.__threads.append(t)
        for th in self.__threads:
            th.start()
        for ts in self.__threads:
            ts.join()"""

    def __process_start(self):
        # print(multiprocessing.cpu_count())
        self.__process = multiprocessing.Pool(16)
        for i in range(8889,65536):
            self.__process.apply_async(self.__is_port_in_use(i))
        self.__process.close()
        """for th in self.__process:
            th.start()

        for ts in self.__threads:
            ts.join()
        """
    def getAvailable_ports(self):
        return self.__available_ports

    def getUnavailable_ports(self):
        return  self.__unavailable_ports

    def __set_port(self):
        self.__recommend_port = random.choice(self.__available_ports)
        del self.__available_ports
        del self.__unavailable_ports

    def getRecommendedPort(self):
        return self.__recommend_port

    def __debug(self):
        print('Recommend Port:', self.__recommend_port)

class BufferP:
    def __init__(self):
        self.__ports = []

    def setPort(self, ports):
        self.__ports = ports

    def getPort(self):
        return self.__ports