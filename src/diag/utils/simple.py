import sys
import signal
import logging


def catch_sigint(cleanup):
  def handle_sigint(sig, frame):
    print("\nCaught Ctrl+C! Exiting cleanly...")
    cleanup()
    sys.exit(0) 
  signal.signal(signal.SIGINT, handle_sigint)