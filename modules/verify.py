import jwt
import sql.sql_use

class Verify:
    def __init__(self, room_id):
        self.__token = ''
        self.__key = ''
        self.__port = 0
        self.__payload = None
        self.__isActive = False
        self.__room_id = room_id
        self.__token_map()

    def __token_map(self):
        tks = sql.sql_use.Keys()
        rsts = sql.sql_use.RoomList()
        rsts.find_room(self.__room_id)
        tks.find_key(self.__room_id)
        self.__token = tks.getToken()
        self.__key = tks.getKey()
        self.__isActive = rsts.getActive()
        self.__port = rsts.getPort()

    def verify(self):
        try:
            # 验证JWT
            decoded_payload = jwt.decode(self.__token, self.__key, algorithms=['HS256'])
            print('Decoded Payload:', decoded_payload)
            self.__payload = decoded_payload
            return 'Verified',self.__isActive, self.__port
        except jwt.ExpiredSignatureError:
            print('Token has expired.')
            return 'Close',self.__isActive, self.__port
        except jwt.InvalidTokenError:
            print('Invalid JWT.')
            return 'Invalid',self.__isActive, self.__port

    def getPayload(self):
        return self.__payload

