import hashlib

def hash_generator(content):
    m = hashlib.sha256()
    m.update(content.encode())
    return m.hexdigest()

def room_id_generator(content:str):
    m = hashlib.sha256()
    buffer = content.split('.')
    for text in buffer:
        m.update(text.encode())
    return m.hexdigest()
