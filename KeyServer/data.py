import sqlite3
import os

class Database:
    def __init__(self):
        self.con = sqlite3.connect('data.db')
        self.cur = self.con.cursor()
        self.__stmt = None
        self.__tables = ['Keys','Map','Users','Rooms']


    def __Keys(self):
        self.__stmt = "CREATE TABLE Keys(id INTEGER PRIMARY KEY AUTOINCREMENT,hash TEXT,token TEXT,key TEXT, status TEXT DEFAULT '1',compute_time timestamp)"
        self.cur.execute(self.__stmt)
        self.con.commit()
        self.__stmt = None
        print("Keys table created")

    def __Map(self):
        self.__stmt = "CREATE TABLE Map(id INTEGER PRIMARY KEY AUTOINCREMENT,roomid TEXT,uid TEXT,compute_time timestamp)"
        self.cur.execute(self.__stmt)
        self.con.commit()
        self.__stmt = None
        print("Map table created")

    def __Users(self):
        self.__stmt = "CREATE TABLE Users(id INTEGER PRIMARY KEY AUTOINCREMENT,uid TEXT,nickname TEXT,compute_time timestamp)"
        self.cur.execute(self.__stmt)
        self.con.commit()
        self.__stmt = None
        print("Users table created")

    def __Rooms(self):
        self.__stmt = "CREATE TABLE Rooms(id INTEGER PRIMARY KEY AUTOINCREMENT,roomid TEXT,port TEXT,room_exist INTEGER default 1800,isActive BOOL DEFAULT FALSE,compute_time timestamp)"
        self.cur.execute(self.__stmt)
        self.con.commit()
        self.__stmt = None
        print("Rooms table created")

    def DROP_ALL(self):
        stmt = "DROP TABLE IF EXISTS"
        for table in self.__tables:
            self.__stmt = stmt + ' ' + table
            self.cur.execute(self.__stmt)
            self.con.commit()
        self.__stmt = None
        print("All table dropped")

    def Initialize_Database(self):
        self.__Keys()
        self.__Map()
        self.__Users()
        self.__Rooms()

