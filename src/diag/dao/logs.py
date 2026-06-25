
from diag.utils.exceptions import UnexpectedException

from diag.data.logs import Auth, JournalCtl, Logs

import subprocess
import os

class LogsDAO:
  def _get_auth() -> Auth:
    try:
      raise NotImplementedError()
    except:
      raise UnexpectedException()
    
  def _get_journal_ctl() -> JournalCtl:
    try:
      raise NotImplementedError()
    except:
      raise UnexpectedException()
    
  def get_logs():
    try:
      raise NotImplementedError()
    except:
      raise UnexpectedException()
    