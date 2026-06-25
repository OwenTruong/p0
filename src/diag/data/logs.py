from dataclasses import dataclass
from datetime import datetime

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
  auth: Auth
  journal_ctl: JournalCtl