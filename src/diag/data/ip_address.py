from dataclasses import dataclass

@dataclass
class IP_Address:
  name: str
  ipv4: str | None
  submask: str | None
  gateway: str | None