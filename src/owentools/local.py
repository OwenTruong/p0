import sys
import os
import subprocess
import logging
from datetime import datetime, timedelta
import time

from owentools.dao.linux.systems import SystemsDAO
from owentools.dao.db.metrics import MetricsDAO
from owentools.data.args import WatchConfig, WebConfig
from owentools.utils.simple import validate_port, validate_choice, repeat_input
from owentools.utils.exceptions import UnexpectedInputException

def start_web(port: int):
  command = [sys.executable, "-m", "uvicorn", "owentools.app.app:app", "--port", str(port), "--host", "0.0.0.0", "--app-dir", "src"] 

  return subprocess.Popen(command, cwd=os.path.dirname(os.path.abspath(__file__)))

def start_watch():
  while True:
    try:
      logging.info("Starting watch")
      # Record local linux stats every 15 minutes
      RECORD_TIME = 15
      now = datetime.now()

      minutes_to_add = RECORD_TIME - (now.minute % RECORD_TIME)
      next_run = now + timedelta(minutes=minutes_to_add)
      next_run = next_run.replace(second=0, microsecond=0)

      seconds_to_wait = (next_run - now).total_seconds()
      logging.info(f"It is currently {now.now()}. Going to sleep for another {seconds_to_wait} second{'' if seconds_to_wait == 1 else 's'}")
      time.sleep(seconds_to_wait)

      systems_dao = SystemsDAO()
      metrics_dao = MetricsDAO()
      systems = systems_dao.get_systems()
      
      metrics_dao.create(
        systems.cpu.logical_cores,
        systems.cpu.fifteen_minute,
        systems.memory.memory_total,
        systems.memory.memory_free
      )
    except Exception as exc:
      logging.critical(f"Failed to log metrics: {exc}")

def define_web(arg_web: bool | None, arg_port: int | None):
  """Define if program should start web process for reporting"""
  should_start_web = False
  web_port = 8082

  if arg_web == True:
    should_start_web = True
  elif arg_web is None:
    choice = repeat_input("Start web server to view system diagnosis? (Y/n): ", validate=validate_choice, default="y")
    if choice.lower() == "y" or choice.lower() == "yes":
      should_start_web = True


  if should_start_web and arg_port:
    web_port = arg_port
  elif should_start_web == True:
    port = repeat_input(f"Specify the port for the web server. ({web_port}): ", validate=validate_port, default=str(web_port))
    web_port = int(port)
    
  return WebConfig(run=should_start_web, port=web_port)

def define_watch(arg_watch: bool | None):
  """Define if program should start watch to monitor system statistics like cpu and memory"""
  if arg_watch == True:
    return WatchConfig(True)
  elif arg_watch is None:
    choice = repeat_input("Start watch for monitoring system statistics? (Y/n): ", validate=validate_choice, default="y",)
    return WatchConfig(choice.lower() == "y" or choice.lower() == "yes")
    
  return WatchConfig(False)