
# System & Third Party
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import time
import logging
from pathlib import Path

# First Party
from diag.dao.logs import LogsDAO
from diag.dao.systems import SystemsDAO
import diag.utils


app = FastAPI(title="Dashboard")
# security = HTTPBearer()
# FIXME: change wildcard to accept origin from env
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

APP_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

@app.middleware("http")
async def log_request_execution_latency(request: Request, call_next):
  start_time = time.time()
  response = await call_next(request)
  logging.info(f"HTTP {request.method} {request.url.path} processed in {time.time() - start_time:.4f}s")
  return response

@app.get("/dump", status_code=200)
async def get_health():
  try:
    systems_dao = SystemsDAO()
    logs_dao = LogsDAO()
    systems = systems_dao.get_systems()
    logs = logs_dao.get_logs()
    return {
      "status": "healthy",
      "systems": systems,
      "logs": logs
    }
  except Exception as exc:
    raise HTTPException(status_code=500, detail=str(exc))
  

@app.get("/", status_code=200, response_class=HTMLResponse)
async def serve(request: Request):
  CPU_FACTOR = 100
  MEMORY_FACTOR = 1024 * 1024
  STORAGE_FACTOR = 1024
  systems_dao = SystemsDAO()
  logs_dao = LogsDAO()
  systems = systems_dao.get_systems()
  logs = logs_dao.get_logs()

  storages_display = []
  network_locals_display = []

  # systems.network_local_li[0].state.value

  for storage in systems.storage_li:
    storages_display.append({
      "filesystem": storage.filesystem,
      "total_capacity": round(storage.total_capacity / STORAGE_FACTOR, 2),
      "used_capacity": round(storage.used_capacity / STORAGE_FACTOR, 2),
      "mount_path": storage.mount_path
    })

  for net in systems.network_local_li:
    network_locals_display.append({
      "proto": net.proto,
      "type": net.type,
      "state": net.state.value,
      "path": net.path
    })


  return templates.TemplateResponse(
    name="index.html",
    context={
      "request": request,
      "cpu": {
        "current": round(systems.cpu.current * CPU_FACTOR, 1),
        "one_minute": round(systems.cpu.one_minute * CPU_FACTOR, 1),
        "five_minute": round(systems.cpu.five_minute * CPU_FACTOR, 1),
        "fifteen_minute": round(systems.cpu.fifteen_minute * CPU_FACTOR, 1)
      },
      "memory": {
        "memory_total": round(systems.memory.memory_total / MEMORY_FACTOR, 2),
        "memory_used": round(systems.memory.memory_used / MEMORY_FACTOR, 2),
        "memory_swap_total": round(systems.memory.memory_swap_total / MEMORY_FACTOR, 2),
        "memory_swap_used": round(systems.memory.memory_swap_used / MEMORY_FACTOR, 2)
      },
      "storages": storages_display,
      "network": {
        "local": network_locals_display,
        "tcp": systems.network_tcp_li
      },
      "auth_logs": logs.auth_li,
      "jctl_logs": logs.journal_ctl_li
    }
  )