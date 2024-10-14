import os
import signal
import socket

import sql.sql_use
from modules import verify, SecurityCheck


class Timer:
    def __init__(self):
        self.__countdown = 30  # min
        self.__timer_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__token_list = []
        self.__pid_list = []
        self.__verification_result = []

    def __Close(self, pid):
        os.kill(pid, signal.SIGINT)
        print('Closing Chat Server:',pid)

    def __timer(self, token, pid):
        room_id = SecurityCheck.room_id_generator(token)
        V = verify.Verify(room_id)
        self.__verification_result = V.verify()
        passport = self.__verification_result[0]
        if passport == 'Verified':
            print('Token Verified')
        else:
            try:
                r = sql.sql_use.RoomList()
                m = sql.sql_use.Map()
                r.logout(room_id)
                m.close_map(room_id)
                self.__Close(pid)
                print('Token_id: ',room_id,' Not Verified, Room Closed')
            except:
                print('T-code:0')

    def __task_timer(self):
        for i in range(1, len(self.__token_list)):
            token = self.__token_list[i]
            pid = self.__pid_list[i]
            self.__timer(token, pid)

    def run_timer(self, host='127.0.0.1', port=8802):
        self.__timer_connection.bind((host, port))
        self.__timer_connection.listen()
