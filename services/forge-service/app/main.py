import asyncio
import hashlib
import logging
import secrets
import time
from contextlib import asynccontextmanager

from app.lib.core import get_logger, get_random_free_port
from fastapi import FastAPI

get_logger()

main_log = logging.getLogger("forge")
math_log = logging.getLogger("math_log")
chk_log = logging.getLogger("health_check")
sys_log = logging.getLogger("sys_log")


async def run_system_check():
    """Runs a quick, non-blocking arbitrary shell command to check container entropy."""
    sys_log.info("Querying system kernel entropy pools...")
    process = await asyncio.create_subprocess_exec(
        "cat",
        "/proc/sys/kernel/random/entropy_avail",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, _ = await process.communicate()
    entropy = stdout.decode().strip() or "N/A"
    sys_log.info(f"Container system entropy available: [ {entropy} bits ]")


async def run_bitwise_benchmark(iterations: int = 50_000):
    """Generates random bits and processes intensive matrix-like XOR math."""
    math_log.debug(
        f"Initiating fast-path bitwise crunch loop ({iterations:,} cycles)..."
    )
    start_time = asyncio.get_running_loop().time()

    raw_bytes = secrets.token_bytes(iterations)
    accumulator = 0
    for byte in raw_bytes:
        accumulator ^= (byte << 2) | (byte >> 6)

    duration = (asyncio.get_running_loop().time() - start_time) * 1000
    math_log.debug(
        f"Bitwise crunch completed in {duration:.4f}ms. Checksum: {hex(accumulator)}"
    )


PRE_STARTUP_COMMANDS = [run_system_check, run_bitwise_benchmark]


@asynccontextmanager
async def lifespan(app: FastAPI):
    main_log.info("📡 Forge Daemon Sequence Activated")

    for command in PRE_STARTUP_COMMANDS:
        await command()

    main_log.info("🚀 Engine Online. Accepting HTTP Sockets.")
    yield
    main_log.info("🛑 Graceful termination received. Shutting down.")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {
        "status": "online",
        "entropy_check": "passed",
        "transient_internal_port": get_random_free_port(),
    }


@app.get("/healthz")
async def health_check():
    start_time = time.perf_counter()

    payload = b"cozy-forge-health-token-verification"
    for _ in range(5000):
        payload = hashlib.sha256(payload).digest()

    latency_ms = (time.perf_counter() - start_time) * 1000

    metrics = {
        "status": "healthy",
        "crypto_latency_ms": round(latency_ms, 3),
        "engine": "uvicorn+gunicorn daemon",
    }

    if latency_ms > 15.0:
        chk_log.warning(f"Engine latency warning: {latency_ms:.2f}ms response window.")
    else:
        chk_log.info(f"Healthcheck validated in {latency_ms:.2f}ms.")

    return metrics
