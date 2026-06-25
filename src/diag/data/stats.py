from __future__ import annotations

from dataclasses import dataclass


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

@dataclass
class NetworkLocal:
  type: str
  state: str
  path: str | None

@dataclass
class NetworkTCP:
  local_address: str
  local_port: int
  foreign_address: str
  foreign_port: int
  state: str

@dataclass
class Storage:
  parent: Storage | None
  total: int
  used: int
  fs_type: str
  uuid: str | None
  mount_point: str | None

@dataclass
class Stats:
  cpu: CPU
  memory: Memory
  network_local: NetworkLocal
  network_tcp: NetworkTCP
  storage: Storage