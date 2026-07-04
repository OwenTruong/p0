from __future__ import annotations

from dataclasses import dataclass
from typing import List
from enum import Enum



@dataclass
class CPU:
  logical_cores: int
  current: float # 1 - idle
  one_minute: float # cpu load average over 1 minute
  five_minute: float # cpu load average over 5 minute
  fifteen_minute: float # cpu laod average over 15 minute
  # load average scales to the # of logical cores

@dataclass
class Memory:
  memory_total: int # in blocks of 1024 bytes
  memory_used: int
  memory_free: int

class UnixSocketState(Enum):
  FREE = "FREE"
  LISTENING = "LISTENING"
  CONNECTING = "CONNECTING"
  CONNECTED = "CONNECTED"
  DISCONNECTING = "DISCONNECTING"
  UNCONNECTED = ""
  UNKNOWN = "UNKNOWN"

@dataclass
class NetworkLocal:
  proto: str
  type: str
  state: UnixSocketState
  path: str | None

@dataclass
class NetworkTCP:
  proto: str
  local_address: str
  foreign_address: str
  state: str # TODO: Add Enum for TCP state?

@dataclass
class Storage:
  filesystem: str
  total_capacity: int # in blocks of 1024 bytes
  used_capacity: int
  mount_path: str

@dataclass
class Systems:
  cpu: CPU
  memory: Memory
  network_local_li: List[NetworkLocal]
  network_tcp_li: List[NetworkTCP]
  storage_li: List[Storage]