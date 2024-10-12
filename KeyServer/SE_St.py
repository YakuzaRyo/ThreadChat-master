import server

if __name__ == "__main__":
    #d = data.database()
    #d.Initialize_Database()
    server = server.KeyServer()
    server.start()
