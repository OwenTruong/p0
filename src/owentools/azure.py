import sys
import subprocess
import logging
from datetime import datetime, timedelta
import time
import json

from owentools.data.args import Args
from owentools.utils.simple import run_az_command, no_validate, validate_choice, validate_non_empty_str, repeat_input
from owentools.utils.exceptions import UnexpectedInputException

def create_vm(
    rg_name, 
    vm_name, 
    location, 
    image="Ubuntu2404", 
    size="Standard_B2ats_v2",
    storage_sku="Standard_LRS",
    boot_diagnostics_storage="",
    admin_user="azureuser",
    generate_ssh_keys=True,
    system_identity = True, 
    ):
    vm_check_output = run_az_command(["az", "vm", "list", "-g", rg_name, "--query", f"[?name=='{vm_name}'].name", "-o", "tsv"])
    
    if not vm_check_output:
      print(f"VM {vm_name} not found. Provisioning now...")
      cmd = [
          "az", "vm", "create", 
          "-g", rg_name, 
          "-n", vm_name, 
          "--image", image, 
          "--location", location, 
          "--size", size,
          "--storage-sku", storage_sku,
          "--boot-diagnostics-storage", boot_diagnostics_storage,
          "--admin-username", admin_user,
          "--output", "table"
      ]

      if generate_ssh_keys:
          cmd.append("--generate-ssh-keys")

      if system_identity:
          cmd.extend(["--assign-identity", "[system]"])

      run_az_command(cmd, capture_output=False)


def placeholder(args: Args):
  logging.info("Starting Azure Auth and Deployment")

  if args.auth:
    run_az_command(["az", "login", "--use-device-code"], capture_output=False)
  elif args.deploy == None:
    choice = input("Would you like to authenticate into Azure? (Y/n):  ").strip() or "y"
    if (validate_choice(choice)):
      run_az_command(["az", "login", "--use-device-code"], capture_output=False)

  FREE_TIER_SIZE_NAME="Standard_B2ats_v2"

  create_new_rg = False
  resource_group = ""
  resource_group_location = "" # only set this if we are creating a resource group
  name = ""
  image = ""
  location = ""
  size = ""
  storage_sku = ""
  boot_diagnostics_storage = ""
  admin_username = ""
  generate_ssh_keys = False
  system_identity = False
  system_shutdown = False
  
  # Define configurations
  logging.info("Now beginning deployment configuration")
  if args.resource_group:
    resource_group = args.resource_group
  else:
    choice = repeat_input("Would you like to create a new resource group for this? Choose no if you would like to use one already generated. (Y/n): ", validate=validate_choice, default="y")
    if (choice.lower() == "y" or choice.lower() == "yes"):
      create_new_rg = True
      resource_group_location = repeat_input("Location of the resource group (useast): ", validate=validate_non_empty_str, default="useast")
    resource_group = repeat_input("Name of the resource group: ", validate=validate_non_empty_str)
  name = args.name or repeat_input("Name of the VM: ", validate=validate_non_empty_str)
  image = args.image or repeat_input("VM Image (Ubuntu2404): ", validate=validate_non_empty_str, default="Ubuntu2404")

  if args.location:
    location = args.location
  else:
    choice = repeat_input(f"Would you like to view all locations/regions for the size {FREE_TIER_SIZE_NAME}? (Y/n) ", validate=validate_choice, default="y")
    if (choice.lower() == "y" or choice.lower() == "yes"):
      print("Please hold on for a minute... This may take a while")
      json_arr = run_az_command([
        "az", "vm", "list-skus", "--size", FREE_TIER_SIZE_NAME
      ])
      if json_arr is None:
        logging.error(f"'az vm list-skus --size {FREE_TIER_SIZE_NAME}' returned nothing. Continuing...")
      else:
        vm_list = list(filter(lambda vm_dic: vm_dic["restrictions"] == [],json.loads(json_arr)))
        locations_available = [loc for vm in vm_list for loc in vm["locations"]]
        print("Locations available: \n" + "\n".join(locations_available))
    
    location = repeat_input("Location (westcentralus): ", validate=validate_non_empty_str, default="westcentralus")

  size = args.size or repeat_input(f"VM Size ({FREE_TIER_SIZE_NAME}): ", validate=validate_non_empty_str, default=FREE_TIER_SIZE_NAME)
  storage_sku = args.storage_sku or repeat_input("VM Storage SKU (Standard_LRS): ", validate=validate_non_empty_str, default=FREE_TIER_SIZE_NAME)
  boot_diagnostics_storage = args.boot_diagnostics_storage or repeat_input("VM Boot Diagnostics Group (''): ", validate=no_validate, default='')
  admin_username = args.admin_username or repeat_input("VM Admin Username (azureuser): ", validate=validate_non_empty_str, default='azureuser')
  
  if args.generate_ssh_keys:
    generate_ssh_keys = args.generate_ssh_keys
  else:
    choice = repeat_input("VM should generate ssh keys? (Y/n)", validate=validate_choice, default='y')
    if choice.lower() == "y" or choice.lower() == "yes":
      generate_ssh_keys = True

  if args.system_identity:
    system_identity = args.system_identity
  else:
    choice = repeat_input("VM should have system identity enabled? (Y/n)", validate=validate_choice, default='y')
    if choice.lower() == "y" or choice.lower() == "yes":
      system_identity = True

  if args.system_shutdown:
    system_shutdown = args.system_shutdown
  else:
    choice = repeat_input("Configure VM to auto shutdown at 17:30 UTC? (Y/n): ", validate=validate_choice, default='y')
    if choice.lower() == "y" or choice.lower() == "yes":
      system_shutdown = True

  # Create resources
  logging.info("Now beginning deployment")

  logging.info(f"""Now creating a new VM with the following:
- Create New Resource Group: {"YES" if create_new_rg else "NO"}
- Resource Group: {resource_group}
- Name: {name}
- Image: {image}
- Location: {location}
- Size: {size}
- Storage SKU: {storage_sku}
- Boot Diagnostics Storage: {"''" if boot_diagnostics_storage == '' else boot_diagnostics_storage }
- Admin Username: {admin_username}
- Should Generate SSH Keys: {"YES" if generate_ssh_keys else "NO"}
- Should Enable System Identity: {"YES" if system_identity else "NO"}
- Should Configure Auto Shutdown: {"YES" if system_shutdown else "NO"}
  """)

  choice = repeat_input("Confirm? (y/N): ", validate=validate_choice, default='n')
  if choice.lower() == "y" or choice.lower() == "yes":
    if create_new_rg:
      logging.info(f"Creating new resource group, {resource_group}, at location, {resource_group_location}")
      run_az_command(["az", "group", "create", "--name", resource_group, "--location", resource_group_location, "--output", "table"], capture_output=False)

    logging.info(f"Creating VM...")
    create_vm(
      rg_name=resource_group,
      vm_name=name,
      location=location,
      image=image,
      size=size,
      storage_sku=storage_sku,
      boot_diagnostics_storage=boot_diagnostics_storage,
      admin_user=admin_username,
      generate_ssh_keys=generate_ssh_keys,
      system_identity=system_identity
    )

    if system_shutdown:
      logging.info("Configuring VM Auto Shutdown")
      run_az_command(["az", "vm", "auto-shutdown", "-g", resource_group, "-n", name, "--time", "1730"])

    #     print(f"az group delete --name {rg_name} --no-wait --yes")
    choice = repeat_input("Would you like to delete the group associated with the VM? (y/N)", validate=validate_choice, default='n')
    if choice.lower() == "y" or choice.lower() == "yes":
      logging.info(f"Deleting group {resource_group}...")
      run_az_command(["az", "group", "delete", "--name", resource_group, "--no-wait", "--yes"], capture_output=False)







