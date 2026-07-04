
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
from fastapi.staticfiles import StaticFiles
import numpy as np

# First Party
from owentools.dao.db.metrics import MetricsDAO
from owentools.dao.linux.logs import LogsDAO
from owentools.dao.linux.systems import SystemsDAO

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Dashboard")
# security = HTTPBearer()
# FIXME: change wildcard to accept origin from env
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory=(BASE_DIR / "static")), name="static")

APP_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

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
  metrics_dao = MetricsDAO()
  systems = systems_dao.get_systems()
  logs = logs_dao.get_logs()
  metrics = metrics_dao.read_all()

  storages_display = []
  network_locals_display = []
  metrics_display = []

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

  for metric in metrics:
    metrics_display.append({
      "cpu_logical_core_count": metric.cpu_logical_core_count,
      "cpu_average": round((metric.cpu_average / metric.cpu_logical_core_count) * CPU_FACTOR, 1),
      "memory_total": round(metric.memory_total / MEMORY_FACTOR, 2),
      "memory_used": round(metric.memory_used / MEMORY_FACTOR, 2),
      "created_on": metric.created_on
    })

  cpu_avg_li = [ metric["cpu_average"] for metric in metrics_display ]
  memory_used_li = [ metric["memory_used" ] for metric in metrics_display ]


  return templates.TemplateResponse(
    name="generated/index.html",
    context={
      "request": request,
      "metrics": metrics_display,
      "metrics_summary": {
        "cpu": {
          "min": np.min(cpu_avg_li),
          "q1": np.percentile(cpu_avg_li, 25),
          "median": np.median(cpu_avg_li),
          "q3": np.percentile(cpu_avg_li, 75),
          "max": np.max(cpu_avg_li),
          "p85": np.percentile(cpu_avg_li, 85),
          "p90": np.percentile(cpu_avg_li, 90),
          "p95": np.percentile(cpu_avg_li, 95),
          "p99": np.percentile(cpu_avg_li, 99),
        },
        "memory_used": {
          "min": np.min(memory_used_li),
          "q1": np.percentile(memory_used_li, 25),
          "median": np.median(memory_used_li),
          "q3": np.percentile(memory_used_li, 75),
          "max": np.max(memory_used_li),
          "p85": np.percentile(memory_used_li, 85),
          "p90": np.percentile(memory_used_li, 90),
          "p95": np.percentile(memory_used_li, 95),
          "p99": np.percentile(memory_used_li, 99),
        }
      },
      "cpu": {
        "logical_cores": systems.cpu.logical_cores,
        "current": round((systems.cpu.current / systems.cpu.logical_cores) * CPU_FACTOR, 1),
        "one_minute": round((systems.cpu.one_minute / systems.cpu.logical_cores) * CPU_FACTOR, 1),
        "five_minute": round((systems.cpu.five_minute / systems.cpu.logical_cores) * CPU_FACTOR, 1),
        "fifteen_minute": round((systems.cpu.fifteen_minute / systems.cpu.logical_cores) * CPU_FACTOR, 1)
      },
      "memory": {
        "memory_total": round(systems.memory.memory_total / MEMORY_FACTOR, 2),
        "memory_used": round(systems.memory.memory_used / MEMORY_FACTOR, 2),
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