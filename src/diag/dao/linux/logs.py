
from diag.utils.exceptions import UnexpectedException

from diag.data.logs import Auth, JournalCtl, Logs

from datetime import datetime
from typing import List
import subprocess
import os

class LogsDAO:
  def _get_auth_li(self) -> List[Auth]:
    try:
      res = subprocess.run(['cat', '/var/log/auth.log'], capture_output=True)
      res = res.stdout.decode()
      res = [line.split(' ') for line in res.split('\n')]
      res = list(filter(lambda li: len(li) > 1, res))
      authli: List[Auth] = []

      for lineli in res:
        auth = Auth(
          timestamp=datetime.fromisoformat(lineli[0]),
          hostname=lineli[1],
          service=lineli[2].split('[')[0],
          message=' '.join(lineli[3:])
        )
        authli.append(auth)
      return authli
    except Exception as exc:
      raise UnexpectedException(exc)
    
  def _get_journal_ctl_li(self) -> List[JournalCtl]:
    try:
      res = subprocess.run(['journalctl', '-k'], capture_output=True)
      res = res.stdout.decode()
      res = [line.split(' ') for line in res.split('\n')] 
      res = list(filter(lambda li: len(li) > 1, res))
      journal_ctl_li: List[JournalCtl] = []

      for lineli in res:
        journal_ctl = JournalCtl(
          timestamp=datetime.strptime(' '.join(lineli[0:3]), "%b %d %H:%M:%S"),
          hostname=lineli[3],
          service=lineli[4][:-1],
          message=' '.join(lineli[5:])
        )
        journal_ctl_li.append(journal_ctl)
      return journal_ctl_li

    except Exception as exc:
      raise UnexpectedException(exc)
    
  def get_logs(self):
    try:
      return Logs(
        auth_li=self._get_auth_li(),
        journal_ctl_li=self._get_journal_ctl_li()
      )
    except Exception as exc:
      raise UnexpectedException(exc)
    