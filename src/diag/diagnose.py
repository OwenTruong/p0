import argparse
import enum
import logging
import subprocess
import sys
import time
import signal

import diag.utils
from diag.dao.systems import SystemsDAO
from diag.dao.logs import LogsDAO
from diag.utils.exceptions import UnexpectedException
from diag.utils.simple import catch_sigint

# class Mode(enum.Enum):
#   deploy = 'deploy'
#   stats = 'stats'

#   def __str__(self):
#     return self.value

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def start_web(port: int):
  command = [sys.executable, "-m", "uvicorn", "diag.app.app:app", "--port", str(port), "--host", "0.0.0.0", "--app-dir", "src"] 

  return subprocess.Popen(command)


def main():
  parser = argparse.ArgumentParser()
  # subparser = parser.add_subparsers(title='mode', dest='mode', required=True)
  # stats_parser = subparser.add_parser(name='stats')
  # deploy_parser = subparser.add_parser(name='deploy')

  # opts = parser.parse_args()
  # mode = opts.mode
  try:
    server_process = None
    def cleanup():
      pass
        

    catch_sigint(cleanup)

    choice = input("Start web server to view system diagnosis? (Y/n): ").strip() or "y"

    if choice.lower() == "y" or choice.lower() == "yes":
      port = input("Specify the port for the web server. (8082): ").strip() or "8082"
      if port.isdigit() and int(port) > 1000 and int(port) <= 65535:
        server_process = start_web(int(port))
        time.sleep(1)
      else:
        raise ValueError(f"Invalid port provided ('{port}'). Please provide a port between 1001 and 65535.")
    else:
      logging.info("Exiting")
      sys.exit(0)

    server_process.wait()
  except Exception as exc:
    raise exc
    


