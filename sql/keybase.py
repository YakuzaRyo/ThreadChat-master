import sqlite3
import os
import hashlib

class Keys:
    def __init__(self, token :str, key: str):
        self.__token :str= token
        self.__key = key
        self.__id = '0'*32
        self.__statement = None
        self.__database_check()
        self.__token_insert()
        self.__id_sha256()

    def __database_check(self):
        """
        创建database
        """
        if os.path.exists('Keys.db'):
            print('SK database Existed')
        else:
            con = sqlite3.connect('Keys.db')
            cur = con.cursor()
            self.__statement = "CREATE TABLE Keys(id INTEGER PRIMARY KEY AUTOINCREMENT,hash TEXT,token TEXT,key TEXT)"
            cur.execute(self.__statement)
            con.commit()
            self.__statement = None
            print('SK database established')

    def __token_insert(self):
        self.__statement = (self.__id, self.__token, self.__key)
        con = sqlite3.connect('Keys.db')
        cur = con.cursor()
        cur.execute("INSERT INTO Keys(hash,token,key) VALUES(?,?,?)",self.__statement)
        con.commit()
        self.__statement = None
        print('Keys updated')

    def __token_metas(self, Hash: str):
        """
        使用固定长度的hash值进行查找
        """
        self.__statement = Hash
        con = sqlite3.connect('Keys.db')
        cur = con.cursor()
        cur.execute("SELECT key from Keys where hash=?",(self.__statement,))
        self.__statement = None

    def __token_delete(self, key: str):
        self.__statement = key
        con = sqlite3.connect('Keys.db')
        cur = con.cursor()
        cur.execute("DELETE  from Keys where key=?",(self.__statement,))
        self.__statement = None



    def __id_sha256(self):
        token_hash = hashlib.sha256()
        token_hash.update(self.__token.encode())
        self.__id =token_hash.hexdigest()




