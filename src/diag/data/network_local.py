from dataclasses import dataclass

@dataclass
class Network_Local:
  type: str
  state: str
  path: str | None