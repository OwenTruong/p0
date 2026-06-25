import argparse
import enum
import logging

from diag.dao.stats import StatsDAO

class Mode(enum.Enum):
  deploy = 'deploy'
  stats = 'stats'

  def __str__(self):
    return self.value

def main():
  parser = argparse.ArgumentParser()
  subparser = parser.add_subparsers(title='mode', dest='mode')
  stats_parser = subparser.add_parser(name='stats')
  deploy_parser = subparser.add_parser(name='deploy')

  opts = parser.parse_args()
  mode = opts.mode

  if (mode == 'stats'):
    logging.info("Everything doing fine!")
  elif mode == 'deploy':
    raise NotImplementedError()
  else:
    raise SystemError("mode is not supposed to accept values other than 'deploy' or 'stats'")