from dataclasses import dataclass

@dataclass
class Storage:
  parent: Storage | None
  total: int
  used: int
  fs_type: str
  uuid: str | None
  mount_point: str | None