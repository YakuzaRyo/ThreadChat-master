import hashlib

import PorCheck
import multiprocessing
import uuid

def run(test):
    pool = multiprocessing.Pool(multiprocessing.cpu_count())

def hash_run(content):
    m = hashlib.sha256()
    m.update(content.encode())
    return m.hexdigest()


if __name__ == '__main__':
    print(hash_run('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjYzMTQ0MzcsInVzZXJuYW1lIjoiMzNiYjA0MzI4NzEwNzAzOTE1MTViMmJmMjRkNDc1NDM2NjExOWZlNjM2MWQwNDZmZDA3ZjBiN2RkZDc4NDlmOSJ9.7H6oUdymgpt2WsO3P2CeX-6V6pIWOPc3rhXKN480mxA'))