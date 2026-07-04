from datetime import datetime
from dataclasses import dataclass

@dataclass
class Metrics:
  id: int
  cpu_logical_core_count: int
  cpu_average: float
  memory_total: int
  memory_used: int
  created_on: datetime