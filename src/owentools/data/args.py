from dataclasses import dataclass
from typing import Literal


@dataclass
class LocalArgs:
  # Local Linux Diagnostics
  web: bool | None = None
  watch: bool | None = None
  port: int | None = None

@dataclass
class AzureArgs:
  # Azure
  auth: bool | None = None
  deploy: bool | None = None

  resource_group: str | None = None
  name: str | None = None
  image: str | None = None

  query_location: bool | None = None
  location: str | None = None

  size: str | None = None
  storage_sku: str | None = None
  boot_diagnostics_storage: str | None = None
  admin_username: str | None = None

  generate_ssh_keys: bool | None = None
  system_identity: bool | None = None

  system_shutdown: bool | None = None

  lazy: Literal[True] | None = None


@dataclass
class WebConfig:
  run: bool
  port: int

@dataclass
class WatchConfig:
  run: bool

@dataclass
class VMConfig:
  create_new_rg: bool
  resource_group: str
  resource_group_location: str
  name: str
  image: str
  location: str
  size: str
  storage_sku: str
  boot_diagnostics_storage: str
  admin_username: str
  generate_ssh_keys: bool
  system_identity: bool
  system_shutdown: bool