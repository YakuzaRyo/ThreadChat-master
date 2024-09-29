import os
import signal


def run():
    pid = os.getpid()
    print(pid)
    os.kill(pid, signal.SIGKILL)

if __name__ == '__main__':
    run()