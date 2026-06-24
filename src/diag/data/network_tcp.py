from dataclasses import dataclass

@dataclass
class Network_TCP:
  local_address: str
  local_port: int
  foreign_address: str
  foreign_port: int
  state: str