import subprocess
import sys
import signal
import logging
from collections.abc import Callable

from owentools.utils.exceptions import UnexpectedInputException


def catch_sigint(cleanup):
  def handle_sigint(sig, frame):
    print("\nCaught Ctrl+C! Exiting cleanly...")
    cleanup()
    sys.exit(0) 
  signal.signal(signal.SIGINT, handle_sigint)


def no_validate(string: str):
  return string

def validate_non_empty_str(string: str):
  """
    Raises:
    - `UnexpectedInputException` for empty string
  """
  if len(string) == 0:
    raise UnexpectedInputException("String is empty.")
  
  return string

def validate_port(port: str):
  """
    Raises:
    - `UnexpectedInputException` if it port is not between (1000, 65535]
  """
  if port.isdigit() and int(port) > 1000 and int(port) <= 65535:
    return port
  else:
    raise UnexpectedInputException(f"Invalid port {port} provided. Please provide a port between (1000, 65535].")

def run_az_command(command_list, capture_output=True):
  """Utility function to safely execute an Azure CLI command array"""
  print(f"Executing: {' '.join(command_list)}")
  try:
    # run() executes the command and waits for it to complete
    result = subprocess.run(command_list, check=True, text=True, capture_output=capture_output)
    if capture_output:
      print(result.stdout)
    return result.stdout
  except subprocess.CalledProcessError as exc:
    print(f"\n Error executing command!", file=sys.stderr)
    print(f"Error Code: {exc.returncode}", file=sys.stderr)
    print(f"Details: {exc.stderr}", file=sys.stderr)
    sys.exit(1)


def validate_choice(choice: str):
  """Checks if input is yes or no in lowercase (y|yes|n|no). 
  
  Raises:
    - `UnexpectedInputException` if it is none of the four choice
  """
  lowc = choice.lower()
  if lowc == "y" or lowc == "yes" or lowc == "n" or lowc == "no": return choice
  else: raise UnexpectedInputException("Invalid choice provided.")


def repeat_input(text: str, validate: Callable[[str], str], default: str = "") -> str:
  while True:
    inp = None
    try:
      inp = input(text).strip() or default
      validate(inp)
      return inp
    except UnexpectedInputException as exc:
      # logging.error(exc)
      print(f"{str(exc)}. Please try again!")
