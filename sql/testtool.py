import sql_use
from sql.data import database

if __name__ == '__main__':
    r = sql_use.RoomList()
    r.find_room('8ba378f0aef43611a70d3fd525e65fcaf163a7e802b9fe5ce164de06ff81c8e5')
    print(r.getDebug())

