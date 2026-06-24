from dataclasses import dataclass


@dataclass
class Memory_Track:
  memory_total: float
  memory_used: float
  memory_free: float
  memory_swap_total: float
  memory_swap_used: float