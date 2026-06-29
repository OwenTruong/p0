from __future__ import annotations

from dataclasses import dataclass
from typing import List
from enum import Enum



@dataclass
class CPU:
  current: float
  one_minute: float
  five_minute: float
  fifteen_minute: float

@dataclass
class Memory:
  memory_total: float
  memory_used: float
  memory_free: float
  memory_swap_total: float
  memory_swap_used: float

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