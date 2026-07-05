import argparse
import logging
import subprocess
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import threading

from owentools.dao.linux.systems import SystemsDAO
from owentools.dao.db.metrics import MetricsDAO
from owentools.data.args import LocalArgs, AzureArgs, WebConfig, WatchConfig
from owentools.utils.exceptions import UnexpectedInputException
from owentools.utils.simple import catch_sigint, validate_port

from owentools.local import start_web, start_watch, define_web, define_watch
from owentools.azure import start_auth_step, start_vm_step, define_vm



def non_empty_str(value: str):
  if len(value) == 0:
    raise argparse.ArgumentTypeError("Argument should not be empty")
  
  return value

def good_port(value: str):
  try:
    validate_port(value)
    return int(value)
  except UnexpectedInputException as exc:
    raise argparse.ArgumentTypeError(str(exc))

def get_args():
  parser = argparse.ArgumentParser()
  parser.add_argument("--verbose", action="store_true", help="Enables verbose mode for more detailed logging.")
  subparser = parser.add_subparsers(title='mode', dest='mode', required=True)
  local_parser = subparser.add_parser(name='local')
  deploy_parser = subparser.add_parser(name='deploy')
  local_group = local_parser.add_argument_group("Local", description="Options for local linux diagnostics.")
  local_group.add_argument("--web", action=argparse.BooleanOptionalAction, help="Skips interactive prompt with --web or --no-web flag.")
  local_group.add_argument("--port", "-p", type=good_port, help="Specify port for web (defaults to 8082). Skips interactive prompt.")
  local_group.add_argument("--watch", action=argparse.BooleanOptionalAction, help="Skips interactive prompt with --watch or --no-watch flag.")

  azure_group = deploy_parser.add_argument_group("Azure VM", description="Options for Azure Authentication and Deployment.")
  azure_group.add_argument("--auth", action=argparse.BooleanOptionalAction, help="Skips interactive prompt with --auth or --no-auth flag.")

  azure_group.add_argument("--deploy", action=argparse.BooleanOptionalAction, help="Skips interactive prompt with --deploy or --no-deploy flag. If --no-deploy is set, the program will not bother with the deploy step and will finish after auth. Any other azure deployement flags set will be ignored.")

  azure_group.add_argument("--resource-group", type=non_empty_str, help="Skips interactive prompt for resource group.")
  
  azure_group.add_argument("--name", type=non_empty_str, help="Skips interactive prompt for name.")
  azure_group.add_argument("--image", type=non_empty_str, help="Skips interactive prompt for image.")
  
  azure_group.add_argument("--query-location", action=argparse.BooleanOptionalAction, help="Skips interactive prompt with --query-location or --no-query-location. If --no-query-location is set, the program will skip querying Azure for locations with the specified VM.")
  azure_group.add_argument("--location", type=non_empty_str, help="Skips interactive prompt for location. If this argument is used, the program will not bother with querying location.")

  azure_group.add_argument("--size", type=non_empty_str, help="Skips interactive prompt for VM size.")
  azure_group.add_argument("--storage-sku", type=non_empty_str, help="Skips interactive prompt for storage sku.")
  azure_group.add_argument("--boot-diagnostics-storage", type=str, help="Skips interactive prompt for boot diagnostics storage.")
  azure_group.add_argument("--admin-username", type=non_empty_str, help="Skips interactive prompt for admin username.")

  azure_group.add_argument("--generate-ssh-keys", action=argparse.BooleanOptionalAction, help="Skips interactive prompt with --generate-ssh-keys or --no-generate-ssh-keys.")
  azure_group.add_argument("--system-identity", action=argparse.BooleanOptionalAction, help="Skips interactive prompt with --system-identity or --no-system-identity.")

  azure_group.add_argument("--system-shutdown", action=argparse.BooleanOptionalAction, help="Skips interactive prompt with --system-shutdown or --no-system-shutdown")

  azure_group.add_argument("--lazy", action="store_true", help="Use to automatically create a VM lazily with preset config.")
  
  load_dotenv()
  opts = parser.parse_args()
  logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
  logging.debug(f"Options: {opts}")

  local_args = LocalArgs() if opts.mode == 'deploy' else LocalArgs(
    web=opts.web, 
    watch=opts.watch, 
    port=opts.port, 
  )

  azure_args = AzureArgs() if opts.mode == 'local' else AzureArgs(
    auth=opts.auth, 
    deploy=opts.deploy, 
    resource_group=opts.resource_group,
    name=opts.name,
    image=opts.image,
    query_location=opts.query_location,
    location=opts.location,
    size=opts.size,
    storage_sku=opts.storage_sku,
    boot_diagnostics_storage=opts.boot_diagnostics_storage,
    admin_username=opts.admin_username,
    generate_ssh_keys=opts.generate_ssh_keys,
    system_identity=opts.system_identity,
    system_shutdown=opts.system_shutdown,
    lazy=opts.lazy
  )

  return (opts.mode, local_args, azure_args)



def main():
  mode, local_args, azure_args = get_args()
  try:
    # Define variables
    logging.info("Starting main")
    ## Process & Threads
    fastapi_process = None
    watch_thread = None
    ## Vars to config
    web_config = None
    watch_config = None

    # Define Cleanup and Sigint Catching
    def cleanup():
      pass
    catch_sigint(cleanup)

    if mode == "local":
      # Define
      web_config = define_web(local_args.web, local_args.port)
      watch_config = define_watch(local_args.watch)

      # Run
      if web_config.run:
        fastapi_process = start_web(web_config.port)
        time.sleep(1)
      if watch_config.run:
        watch_thread = threading.Thread(target=start_watch, daemon=True)
        watch_thread.start()
      
      # Wait
      if fastapi_process:
        fastapi_process.wait()
      elif watch_thread:
        watch_thread.join()
    else:
      # Azure
      start_auth_step(azure_args)

      vm_config = define_vm(azure_args)
      start_vm_step(vm_config)

  except Exception as exc:
    raise exc