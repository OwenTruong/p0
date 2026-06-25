

from diag.utils.exceptions import UnexpectedException

from diag.data.stats import CPU, Memory, Storage, NetworkLocal, NetworkTCP, Stats

import subprocess
import os

class StatsDAO:
  def _get_cpu(self) -> CPU:
    try:
      top = subprocess.run(['top', '-b', '-n', '1'], capture_output=True)
      blist = top.stdout.split(b'\n')[0:3]
      
      minutes = list(map(lambda x: float(x.split()[-1].decode()), blist[0].split(b', ')[-3:]))
      current = float(blist[2].split()[7].decode())
      return CPU(current=current, one_minute=minutes[0], five_minute=minutes[1], fifteen_minute=minutes[2])
    except:
      raise UnexpectedException()

  def _get_memory(self) -> Memory:
    try:
      free = subprocess.run(['free'], capture_output=True)
      blist = free.stdout.split(b'\n')[1:]
      mems = list(map(lambda x: float(x.decode()), blist[0].split()[1:]))
      swaps = list(map(lambda x: float(x.decode()), blist[1].split()[1:]))

      return Memory(memory_total=mems[0], memory_used=mems[1], memory_free=mems[2], memory_swap_total=swaps[0], memory_swap_used=swaps[1])
    except:
      raise UnexpectedException()

  def _get_storage(self) -> Storage:
    try:
      raise NotImplementedError()
    except:
      raise UnexpectedException()
    
  def _get_network_local(self) -> NetworkLocal:
    try:
      raise NotImplementedError()
    except:
      raise UnexpectedException()
    
  def _get_network_tcp(self) -> NetworkTCP:
    try:
      raise NotImplementedError()
    except:
      raise UnexpectedException()

  def get_stats(self):
    return Stats(
      cpu=self._get_cpu(),
      memory=self._get_memory(),
      storage=self._get_storage(),
      network_local=self._get_network_local(),
      network_tcp=self._get_network_tcp()
    )