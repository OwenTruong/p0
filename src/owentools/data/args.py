from dataclasses import dataclass

@dataclass
class Args:
  # Local Linux Diagnostics
  web: bool | None
  watch: bool | None
  port: int | None
  
  # Azure
  auth: bool | None
  deploy: bool | None

  resource_group: str | None
  name: str | None
  image: str | None

  query_location: bool | None
  location: str | None

  size: str | None
  storage_sku: str | None
  boot_diagnostics_storage: str | None
  admin_username: str | None

  generate_ssh_keys: bool | None
  system_identity: bool | None

  system_shutdown: bool | None


@dataclass
class WebConfig:
  run: bool
  port: int

@dataclass
class WatchConfig:
  run: bool