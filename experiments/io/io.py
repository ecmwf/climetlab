SIZE = 100*1024*1024*1024

import os
from tqdm import tqdm
from climetlab.utils.humanize import bytes
import time

import sys

def unbytes(x):
    if x[-1].lower() == 'k':
        return int(x[:-1]) * 1024
    if x[-1].lower() == 'm':
        return int(x[:-1]) * 1024 * 1024
    if x[-1].lower() == 'g':
        return int(x[:-1]) * 1024 * 1024 * 1024
    return int(x)

seek = unbytes(sys.argv[1])
write = unbytes(sys.argv[2])

if seek < write:
    print('seek < write. Aborting')
    exit()

#filename = f'io.{seek}.{write}.bin'
filename = 'binfile'
print(f'Writing {bytes(SIZE)} by chunks of {bytes(write)} with seeks of {bytes(seek)} (i.e. {seek/write} passes).')

#for datavalue in ['a' , 'b', 'c']:
#    print()
#    data = (str(datavalue)[0] * write).encode('ascii')

data = (str('a')[0] * write).encode('ascii')
class Tic:
    def __init__(self):
        self.start = time.time()
        self.current = self.start

    def __call__(self, msg, mult):
        new = time.time()
        delta = new - self.current
        print(msg, delta, 'seconds', f"(Total will be {mult*delta} sec)")
        self.current = new 
    
    @property
    def total(self):
        return time.time() - self.start


tic = Tic()

with open(filename, 'wb') as f:

    for i,offset in enumerate(tqdm(range(0, seek, write), desc='offset')):
        #tic(f"{i}: {offset}/{SIZE}", offset/SIZE)
        for cursor in tqdm(list(range(0, SIZE, seek)), desc = 'seek', leave=False):

        # for i, cursor in tqdm(enumerate(range(0, SIZE, seek))):
            # data = (str(i)[0] * write).encode('ascii')
            f.write(data)
            f.seek(cursor)
            if tic.total > 60:
                exit()

print(f'Wrote {bytes(SIZE)} by chunks of {bytes(write)} with seeks of {bytes(seek)} (i.e. {seek/write} passes) in {tic.total} seconds.:::{write}, {seek}, {tic.total}')

os.makedirs('iologs', exist_ok=True)
with open(f'iologs/io.{seek}.{write}.csv', 'w+') as f:
    print(f'{write}, {seek}, {tic.total}', file=f)