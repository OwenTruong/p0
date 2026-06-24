from data.cpu_track import CPU_Track
from data.memory_track import Memory_Track

import subprocess
import os

def _get_cpu_data() -> CPU_Track:
  try:
    top = subprocess.run(['top', '-b', '-n', '1'], capture_output=True)
    blist = top.stdout.split(b'\n')[0:3]
    
    minutes = list(map(lambda x: float(x.split()[-1].decode()), blist[0].split(b', ')[-3:]))
    current = float(blist[2].split()[7].decode())
    return CPU_Track(current=current, one_minute=minutes[0], five_minute=minutes[1], fifteen_minute=minutes[2])
  except:
    raise

def _get_memory_data() -> Memory_Track:
  try:
    free = subprocess.run(['free'], capture_output=True)
    blist = free.stdout.split(b'\n')[1:]
    mems = list(map(lambda x: float(x.decode()), blist[0].split()[1:]))
    swaps = list(map(lambda x: float(x.decode()), blist[1].split()[1:]))

    return Memory_Track(memory_total=mems[0], memory_used=mems[1], memory_free=mems[2], memory_swap_total=swaps[0], memory_swap_used=swaps[1])
  except:
    raise



def create_logs():
  _get_cpu_data()
  _get_memory_data()