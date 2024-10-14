import asyncio
import itertools
import os

import psutil


async def it(process_id, content):
    process = psutil.Process(process_id)
    for c in itertools.cycle('|/-\\'):
        cpu_percent = process.cpu_percent(interval=1 / 120)
        print('\r',content, c,f"CPU 使用率: {cpu_percent}%",end='')
        await asyncio.sleep(1 / 120)

if __name__ == '__main__':
    pid = os.getpid()
    asyncio.run(it(pid,'Loading...'))
    i = 0
    for i in range(1293809812938):
        i = i * i
    print(i)
