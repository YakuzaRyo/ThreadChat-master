import hashlib

def hash_generator(content):
    m = hashlib.sha256()
    m.update(content.encode())
    return m.hexdigest()