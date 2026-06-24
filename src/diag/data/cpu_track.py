from dataclasses import dataclass


@dataclass
class CPU_Track:
  current: float
  one_minute: float
  five_minute: float
  fifteen_minute: float
