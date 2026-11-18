import time
from contextlib import asynccontextmanager

from app.lib.log import get_logger
from app.lib.manage_processes import ManagedProcess
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# -----------------------------------------------------------------------------
# Managed processe list ( configuration )
# -----------------------------------------------------------------------------

PROCESSES: list[ManagedProcess] = [
    ManagedProcess("worker_uptime", ["uptime"], mode="once"),
    ManagedProcess("work_sleep", ["sleep", "90"], mode="once"),
]

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
log = get_logger("forge")


@asynccontextmanager
async def lifespan(app: FastAPI):

    log.info("Supervisor initialized.")
    for item in PROCESSES:
        await item.start()
    yield
    for item in reversed(PROCESSES):
        await item.stop()
    log.info("Supervisor shutdown complete.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "status": "online",
        "processes": {
            p.name: {
                "pid": p.pid,
                "running": p.is_running,
                "returncode": p.proc.returncode if p.proc else None,
            }
            for p in PROCESSES
        },
    }


# -----------------------------------------------------------------------------
# Healthcheck
# -----------------------------------------------------------------------------


@app.get("/healthz")
async def health_check():
    start_time = time.perf_counter()
    log = get_logger("health_check")

    report = {}
    for p in PROCESSES:
        report[p.name] = {
            "pid": p.pid,
            "running": p.is_running,
            "returncode": p.proc.returncode if p.proc else None,
            "mode": p.mode,
        }

    unhealthy = {}
    for name, info in report.items():
        proc = next(p for p in PROCESSES if p.name == name)

        if proc.mode == "always":
            is_healthy = info["running"]
        else:
            is_healthy = info["returncode"] == 0

        if not is_healthy:
            unhealthy[name] = info

    latency_ms = (time.perf_counter() - start_time) * 1000

    if unhealthy:
        log.error(f"Healthcheck failed — unhealthy processes: {list(unhealthy.keys())}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "latency_ms": round(latency_ms, 3),
                "processes": report,
            },
        )

    log.debug(f"Healthcheck validated in {latency_ms:.2f}ms.")
    return {
        "status": "healthy",
        "latency_ms": round(latency_ms, 3),
        "processes": report,
    }
