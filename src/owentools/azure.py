import sys
import subprocess
import logging
from datetime import datetime, timedelta
import time
import json
import random
import string

from owentools.data.args import AzureArgs, VMConfig
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

def start_auth_step(args: AzureArgs):
  if args.auth:
    run_az_command(["az", "login", "--use-device-code"], capture_output=False)
  elif args.auth == None:
    choice = input("Would you like to authenticate into Azure? (Y/n):  ").strip() or "y"
    if (validate_choice(choice)):
      if (choice.lower() == "y" or choice.lower() == "yes"):
        run_az_command(["az", "login", "--use-device-code"], capture_output=False)
        logging.info("Auth ran")

def start_vm_step(vm_config: VMConfig):
  logging.info("Now beginning deployment")

  logging.info(f"""Now creating a new VM with the following:
- Create New Resource Group: {"YES" if vm_config.create_new_rg else "NO"}
- Resource Group: {vm_config.resource_group}
- Name: {vm_config.name}
- Image: {vm_config.image}
- Location: {vm_config.location}
- Size: {vm_config.size}
- Storage SKU: {vm_config.storage_sku}
- Boot Diagnostics Storage: {"''" if vm_config.boot_diagnostics_storage == '' else vm_config.boot_diagnostics_storage }
- Admin Username: {vm_config.admin_username}
- Should Generate SSH Keys: {"YES" if vm_config.generate_ssh_keys else "NO"}
- Should Enable System Identity: {"YES" if vm_config.system_identity else "NO"}
- Should Configure Auto Shutdown: {"YES" if vm_config.system_shutdown else "NO"}
  """)

  choice = repeat_input("Confirm? (y/N): ", validate=validate_choice, default='n')
  if choice.lower() == "y" or choice.lower() == "yes":
    if vm_config.create_new_rg:
      logging.info(f"Creating new resource group, {vm_config.resource_group}, at location, {vm_config.resource_group_location}")
      run_az_command(["az", "group", "create", "--name", vm_config.resource_group, "--location", vm_config.resource_group_location, "--output", "table"], capture_output=False)

    logging.info(f"Creating VM...")
    create_vm(
      rg_name=vm_config.resource_group,
      vm_name=vm_config.name,
      location=vm_config.location,
      image=vm_config.image,
      size=vm_config.size,
      storage_sku=vm_config.storage_sku,
      boot_diagnostics_storage=vm_config.boot_diagnostics_storage,
      admin_user=vm_config.admin_username,
      generate_ssh_keys=vm_config.generate_ssh_keys,
      system_identity=vm_config.system_identity
    )

    if vm_config.system_shutdown:
      logging.info("Configuring VM Auto Shutdown")
      run_az_command(["az", "vm", "auto-shutdown", "-g", vm_config.resource_group, "-n", vm_config.name, "--time", "1730", '-l', vm_config.location])

    choice = repeat_input("Would you like to delete the group associated with the VM? (y/N)", validate=validate_choice, default='n')
    if choice.lower() == "y" or choice.lower() == "yes":
      logging.info(f"Deleting group {vm_config.resource_group}...")
      run_az_command(["az", "group", "delete", "--name", vm_config.resource_group, "--no-wait", "--yes"], capture_output=False)

def define_vm(args: AzureArgs):
  FREE_TIER_SIZE_NAME="Standard_B2ats_v2"

  create_new_rg = True
  resource_group = ''.join(random.choices(string.ascii_lowercase, k=10))
  resource_group_location = "eastus" # only set this if we are creating a resource group
  name = ''.join(random.choices(string.ascii_lowercase, k=10))
  image = "Ubuntu2404"
  location = "westcentralus"
  size = FREE_TIER_SIZE_NAME
  storage_sku = "Standard_LRS"
  boot_diagnostics_storage = ""
  admin_username = "azureuser"
  generate_ssh_keys = True
  system_identity = False
  system_shutdown = True

  if args.lazy:
    return VMConfig(
      create_new_rg=create_new_rg,
      resource_group=resource_group,
      resource_group_location=resource_group_location,
      name=name,
      image=image,
      location=location,
      size=size,
      storage_sku=storage_sku,
      boot_diagnostics_storage=boot_diagnostics_storage,
      admin_username=admin_username,
      generate_ssh_keys=generate_ssh_keys,
      system_identity=system_identity,
      system_shutdown=system_shutdown
    )
  
  # Define configurations
  logging.info("Now beginning deployment configuration")
  if args.resource_group:
    resource_group = args.resource_group
  else:
    choice = repeat_input("Would you like to create a new resource group for this? Choose no if you would like to use one already generated. (Y/n): ", validate=validate_choice, default="y")
    if (choice.lower() == "y" or choice.lower() == "yes"):
      create_new_rg = True
      resource_group_location = repeat_input(f"Location of the resource group ({resource_group_location}): ", validate=validate_non_empty_str, default=resource_group_location)
    else:
      create_new_rg = False
    resource_group = repeat_input(f"Name of the resource group {resource_group}: ", validate=validate_non_empty_str, default=resource_group)
  name = args.name or repeat_input(f"Name of the VM ({name}): ", validate=validate_non_empty_str, default=name)
  image = args.image or repeat_input(f"VM Image ({image}): ", validate=validate_non_empty_str, default=image)

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
    
    location = repeat_input(f"Location ({location}): ", validate=validate_non_empty_str, default=location)

  size = args.size or repeat_input(f"VM Size ({size}): ", validate=validate_non_empty_str, default=size)
  storage_sku = args.storage_sku or repeat_input(f"VM Storage SKU ({storage_sku}): ", validate=validate_non_empty_str, default=storage_sku)
  boot_diagnostics_storage = args.boot_diagnostics_storage or repeat_input(f"VM Boot Diagnostics Group ({boot_diagnostics_storage}): ", validate=no_validate, default=boot_diagnostics_storage)
  admin_username = args.admin_username or repeat_input(f"VM Admin Username ({admin_username}): ", validate=validate_non_empty_str, default=admin_username)
  
  if args.generate_ssh_keys:
    generate_ssh_keys = args.generate_ssh_keys
  else:
    choice = repeat_input("VM should generate ssh keys? (Y/n)", validate=validate_choice, default='y')
    if choice.lower() == "y" or choice.lower() == "yes":
      generate_ssh_keys = True
    else:
      generate_ssh_keys = False

  if args.system_identity:
    system_identity = args.system_identity
  else:
    choice = repeat_input("VM should have system identity enabled? (Y/n)", validate=validate_choice, default='y')
    if choice.lower() == "y" or choice.lower() == "yes":
      system_identity = True
    else:
      system_identity = False

  if args.system_shutdown:
    system_shutdown = args.system_shutdown
  else:
    choice = repeat_input("Configure VM to auto shutdown at 17:30 UTC? (Y/n): ", validate=validate_choice, default='y')
    if choice.lower() == "y" or choice.lower() == "yes":
      system_shutdown = True
    else:
      system_shutdown = False


  return VMConfig(
    create_new_rg=create_new_rg,
    resource_group=resource_group,
    resource_group_location=resource_group_location,
    name=name,
    image=image,
    location=location,
    size=size,
    storage_sku=storage_sku,
    boot_diagnostics_storage=boot_diagnostics_storage,
    admin_username=admin_username,
    generate_ssh_keys=generate_ssh_keys,
    system_identity=system_identity,
    system_shutdown=system_shutdown
  )




