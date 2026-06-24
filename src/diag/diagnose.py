import argparse
import enum
from service.create_logs import create_logs

class Mode(enum.Enum):
  deploy = 'deploy'
  stats = 'stats'

  def __str__(self):
    return self.value

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('mode', type=str, choices=['deploy', 'stats'])
  opts = parser.parse_args()
  mode = opts.mode

  if (mode == 'stats'):
    print("Everything doing fine!")
    create_logs()
  elif mode == 'deploy':
    raise NotImplementedError()
  else:
    raise SystemError("mode is not supposed to accept values other than 'deploy' or 'stats'")