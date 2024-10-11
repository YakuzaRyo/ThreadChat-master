import hashlib
import sqlite3


class Keys:
    def __init__(self):
        self.__token= ''
        self.__key = ''
        self.__id = '0'*64 # 64Byte
        self.__statement = None
        self.__status = ''
        self.debug = None

    def token_insert(self, token, key):
        self.__token = token
        self.__key = key
        self.__id_sha256()
        self.__statement = (self.__id, self.__token, self.__key)
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("INSERT INTO Keys(hash, token, key, compute_time) VALUES (?,?,?,datetime())", self.__statement)
        con.commit()
        self.__statement = None
        print('[Server] Keys updated')

    def __token_metas(self):
        """
        使用固定长度的hash值进行查找
        """
        self.__statement = self.__id
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("SELECT key, token, status FROM Keys where hash=?",(self.__statement,))
        debug = cur.fetchall()
        self.__key = debug[0][0]
        self.__token = debug[0][1]
        self.__status = debug[0][2]
        #self.debug = cur.fetchall()
        self.__statement = None

    def find_key(self, room_id: str):
        self.__id = room_id
        self.__token_metas()

    def __token_delete(self, Hash: str):
        self.__statement = Hash
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("DELETE  from 'Keys' where hash=?",(self.__statement,))
        con.commit()
        self.__statement = None
        print('[Server] Keys deleted')

    def status_update(self, status: str):
        self.__status = status
        self.__statement = (self.__id, status)
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("UPDATE Keys set status=? where hash=?",self.__statement)
        con.commit()
        print('[Server] Keys updated')

    def strip_token(self, Hash: str):
        self.__token_delete(Hash)

    def __id_sha256(self):
        token_hash = hashlib.sha256()
        token_hash.update(self.__token.encode())
        self.__id =token_hash.hexdigest()

    def getKey(self):
        return self.__key

    def getToken(self):
        return self.__token

    def getStatus(self):
        return self.__status

    def getDebug(self):
        return self.debug

class Map:
    def __init__(self):
        self.__uid=None
        self.__room_id=None
        self.__statement=None

    def __map_insert(self):
        self.__statement = (self.__room_id, self.__uid)
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("INSERT INTO Map(roomid, uid, compute_time) VALUES (?,?,datetime())", self.__statement)
        con.commit()
        self.__statement = None
        print('[Server] Map added')

    def map_update(self, room_id, uid):
        self.__room_id = room_id
        self.__uid = uid
        self.__map_insert()

    def __map_delete(self, room_id):
        self.__statement = room_id
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("DELETE from Map where roomid=?", (self.__statement,))
        con.commit()
        self.__statement = None

    def mapping(self, room_id = None, uid = None):
        self.__room_id = room_id
        self.__uid = uid
        self.__map_metas()

    def __map_metas(self):
        """
        uid：n
        room_id：n
        """
        if self.__uid:
            self.__statement = self.__uid
            con = sqlite3.connect('../KeyServer/data.db')
            cur = con.cursor()
            cur.execute("select roomid from 'Map' where uid=?", (self.__statement,))
            debug = cur.fetchall()
            self.__room_id = debug[0][0]
            self.__statement = None
        else:
            self.__statement = self.__room_id
            con = sqlite3.connect('../KeyServer/data.db')
            cur = con.cursor()
            cur.execute("select uid from 'Map' where roomid=?", (self.__statement,))
            debug = cur.fetchall()
            self.__uid = debug[0][0]
            self.__statement = None

    def getMappingKey(self):
        return self.__room_id, self.__uid

    def getUid(self):
        return self.__uid

    def close_map(self,room_id):
        self.__map_delete(room_id)

class UserList:
    def __init__(self):
        self.__uid = None
        self.__nickname = ''
        self.__statement = None

    def user_login(self,nickname:str, uid:str):
        self.__uid = uid
        self.__nickname = nickname
        self.__user_insert()

    def user_logout(self,nickname:str,uid = None):
        self.__nickname = nickname
        self.__uid = uid
        self.__user_metas()
        self.__user_delete()

    def __user_metas(self):
        self.__statement = self.__nickname
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("select uid from 'Users' where nickname=?", (self.__statement,))
        debug = cur.fetchall()
        self.__uid = debug[0][0]
        self.__statement = None

    def __user_insert(self):
        self.__statement = (self.__uid, self.__nickname)
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("INSERT INTO Users(uid,nickname,compute_time) VALUES (?,?,datetime())", self.__statement)
        con.commit()
        self.__statement = None
        print('[Server] User added')

    def __user_delete(self):
        """
        优先使用nickname
        """
        if self.__uid :
            self.__statement = self.__uid
            con = sqlite3.connect('../KeyServer/data.db')
            cur = con.cursor()
            cur.execute("DELETE from Users where uid=?", (self.__statement,))
            con.commit()
            self.__statement = None
            print('[Server] User deleted')
        else:
            self.__statement = self.__nickname
            con = sqlite3.connect('../KeyServer/data.db')
            cur = con.cursor()
            cur.execute("DELETE from Users where nickname=?", (self.__statement,))
            con.commit()
            self.__statement = None
            print('[Server] User deleted')

    def getUid(self):
        return self.__uid

class RoomList:
    def __init__(self):
        self.__room_id = None
        self.__statement = None
        self.__port = None
        self.__isActive = None
        self.__room_exist = None

    def logRoom(self, room_id,port):
        self.__room_id = room_id
        self.__port = port

    def __logRoomIn(self):
        self.__statement = (self.__room_id, self.__port)
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("INSERT INTO Rooms(roomid,port,compute_time) VALUES (?,?,datetime())", self.__statement)
        con.commit()
        self.__statement = None
        print('[Server] Room added')

    def __logRoomOut(self,room_id):
        self.__statement = room_id
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("DELETE from Rooms where roomid=?", (self.__statement,))
        con.commit()
        self.__statement = None
        print('[Server] Room deleted')

    def __room_metas(self):
        self.__statement = self.__room_id
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("SELECT port, room_exist, isActive FROM Rooms where roomid=?", (self.__statement,))
        self.debug = cur.fetchall()
        print(self.debug)
        self.__port = self.debug[0][0]
        self.__room_exist = self.debug[0][1]
        self.__isActive = self.debug[0][2]
        self.__statement = None


    def find_room(self,room_id):
        self.__room_id = room_id
        self.__room_metas()

    def room_status_update(self, room_id ,isActive):
        self.__statement = isActive
        con = sqlite3.connect('../KeyServer/data.db')
        cur = con.cursor()
        cur.execute("UPDATE Rooms set isActive=? where roomid=?",(self.__statement,room_id))
        con.commit()
        self.__statement = None

    def getRoomId(self):
        return self.__room_id

    def login(self):
        self.__logRoomIn()

    def logout(self, room_id):
        self.__logRoomOut(room_id)

    def getActive(self):
        return self.__isActive

    def getPort(self):
        return self.__port

    def getDebug(self):
        return self.debug