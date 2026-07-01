import argparse
import enum
import logging
import subprocess
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import threading

from diag.dao.linux.systems import SystemsDAO
from diag.dao.db.metrics import MetricsDAO
from diag.utils.simple import catch_sigint


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def start_web(port: int):
  command = [sys.executable, "-m", "uvicorn", "diag.app.app:app", "--port", str(port), "--host", "0.0.0.0", "--app-dir", "src"] 

  return subprocess.Popen(command)


def start_watch():
  while True:
    try:
      logging.info("Starting watch")
      # Record local linux stats every 15 minutes
      RECORD_TIME = 2
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


def get_args():
  parser = argparse.ArgumentParser()
  # subparser = parser.add_subparsers(title='mode', dest='mode', required=True)
  # stats_parser = subparser.add_parser(name='stats')
  # deploy_parser = subparser.add_parser(name='deploy')
  parser.add_argument("--no-watch", action="store_true", help="Disable collection of system metrics")
  load_dotenv()
  opts = parser.parse_args()
  return opts


def main():
  opts = get_args()
  try:
    logging.info("Starting main")
    fastapi_process = None
    watch_thread = None
    def cleanup():
      pass

    catch_sigint(cleanup)

    choice = input("Start web server to view system diagnosis? (Y/n): ").strip() or "y"

    if choice.lower() == "y" or choice.lower() == "yes":
      port = input("Specify the port for the web server. (8082): ").strip() or "8082"
      if port.isdigit() and int(port) > 1000 and int(port) <= 65535:
        fastapi_process = start_web(int(port))
        time.sleep(1)
      else:
        raise ValueError(f"Invalid port provided ('{port}'). Please provide a port between 1001 and 65535.")
    
    if opts.no_watch != True:
      watch_thread = threading.Thread(target=start_watch, daemon=True)
      watch_thread.start()

    if fastapi_process:
      fastapi_process.wait()
    elif watch_thread:
      watch_thread.join()
  except Exception as exc:
    raise exc