from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Auth:
  timestamp: datetime
  hostname: str
  service: str
  message: str


@dataclass
class JournalCtl:
  timestamp: datetime
  hostname: str
  service: str
  message: str


@dataclass
class Logs:
  auth_li: List[Auth]
  journal_ctl_li: List[JournalCtl]