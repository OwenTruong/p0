from dataclasses import dataclass


@dataclass
class CPU:
  arch: str
  threads: int
