

from typing import List

from diag.utils.exceptions import UnexpectedException

from diag.data.systems import CPU, Memory, Storage, NetworkLocal, NetworkTCP, Systems, UnixSocketState

import subprocess
import os

class SystemsDAO:
  def _get_cpu(self) -> CPU:
    try:
      top = subprocess.run(['top', '-b', '-n', '1'], capture_output=True)
      blist = top.stdout.split(b'\n')[0:3]
      
      minutes = list(map(lambda x: float(x.split()[-1].decode()), blist[0].split(b', ')[-3:]))
      current = (100 - float(blist[2].split()[7].decode())) / 100
      return CPU(current=current, one_minute=minutes[0], five_minute=minutes[1], fifteen_minute=minutes[2])
    except Exception as exc:
      raise UnexpectedException(exc)

  def _get_memory(self) -> Memory:
    try:
      free = subprocess.run(['free'], capture_output=True)
      blist = free.stdout.split(b'\n')[1:]
      mems = list(map(lambda x: float(x.decode()), blist[0].split()[1:]))
      swaps = list(map(lambda x: float(x.decode()), blist[1].split()[1:]))

      return Memory(memory_total=mems[0], memory_used=mems[1], memory_free=mems[2], memory_swap_total=swaps[0], memory_swap_used=swaps[1])
    except Exception as exc:
      raise UnexpectedException(exc)

  def _get_storage_li(self) -> List[Storage]:
    try:
      lsblk = subprocess.run(['df'], capture_output=True)
      twodim = list(
        filter(
          lambda x: len(x) != 0, 
          [el.decode().split() for el in lsblk.stdout.split(b'\n')[1:]]
        )
      )
      storages = []
      for [fs, blk, used, ava, usep, mounted_on] in twodim:
        storages.append(Storage(
          filesystem=fs, 
          total_capacity=int(blk), 
          used_capacity=int(used),
          mount_path=mounted_on
        ))
      return storages
    except Exception as exc:
      raise UnexpectedException(exc)
    
  def _get_network_local_li(self) -> List[NetworkLocal]:
    try:
      netstat = subprocess.run(['netstat'], capture_output=True)
      rows = list(filter(lambda row: row[0:4] == "unix", netstat.stdout.decode().split('\n')[1:]))
      rows = [row.split() for row in rows]
      network_local_li: List[NetworkLocal] = []
      for row in rows:
        if (row[5].isdigit()):
          network_local_li.append(NetworkLocal(
            proto=row[0], 
            type=row[4], 
            state=UnixSocketState(""), 
            path=(row[6] if len(row) >= 7 else None)
          ))
        else:
          network_local_li.append(NetworkLocal(
            proto=row[0],
            type=row[4],
            state=UnixSocketState(row[5]),
            path=(row[7] if len(row) >= 8 else None)
          ))
      return network_local_li
    except Exception as exc:
      raise UnexpectedException(exc)
    
  def _get_network_tcp_li(self) -> List[NetworkTCP]:
    try:
      netstat = subprocess.run(['netstat'], capture_output=True)
      rows = list(filter(lambda row: row[0:3] == "tcp", netstat.stdout.decode().split('\n')[1:]))
      rows = [row.split() for row in rows]
      rows = [NetworkTCP(
        proto=row[0], 
        local_address=row[3], 
        foreign_address=row[4], 
        state=row[5]) for row in rows]
      return rows
    except Exception as exc:
      raise UnexpectedException(exc)

  def get_systems(self):
    return Systems(
      cpu=self._get_cpu(),
      memory=self._get_memory(),
      storage_li=self._get_storage_li(),
      network_local_li=self._get_network_local_li(),
      network_tcp_li=self._get_network_tcp_li()
    )