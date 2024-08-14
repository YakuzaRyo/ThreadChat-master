import sqlite3

"""

cur.execute("CREATE TABLE Keys(id INTEGER PRIMARY KEY AUTOINCREMENT,token TEXT,key TEXT)")

"""


con = sqlite3.connect('test.db')
cur = con.cursor()
# cur.execute("INSERT INTO Keys (token, key) VALUES ('1', '2') ")
con.commit()
cur.execute("select key from Keys")


key = cur.fetchall()[0][0]
print(key)
