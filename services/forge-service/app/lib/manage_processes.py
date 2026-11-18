# Process management helpers
# An Eve Production <3

import asyncio
import logging
from typing import Optional


class _ProcessLogAdapter(logging.LoggerAdapter):
    """A small LoggerAdapter that injects a PID tag via the 'extra' dict.

    This is safer than mutating the log message directly, especially when
    using custom formatters.
    """

    def process(self, msg, kwargs):
        proc = self.extra.get("proc")
        pid = getattr(proc, "pid", None) if proc else None
        tag = f"PID {pid}" if pid is not None else ""

        extra = kwargs.setdefault("extra", {})
        extra["pid_tag"] = f"[{tag:<9}] " if tag else ""

        return msg, kwargs


class ManagedProcess:
    """A managed long-running (or one-shot) process.

    This class is responsible for starting, monitoring, and stopping
    a subprocess while providing basic health information and logging.

    Attributes:
        name: Human-readable name for the process (used in logs).
        cmd: The command (as a list) that will be executed.
        mode: Either "always" (long-running service) or "once" (one-shot task).
        proc: The underlying asyncio subprocess, if started.
    """

    def __init__(
        self,
        name: str,
        cmd: list[str],
        mode: str = "always",
        parent_logger: str = "forge",
    ):
        """Initialize a ManagedProcess.

        Args:
            name: Identifier for this process (used for logging).
            cmd: Command to run, passed as a list (e.g. ["sleep", "60"]).
            mode: "always" for services that should stay running,
                  "once" for tasks that are expected to exit.
            parent_logger: Base logger name (defaults to "forge").
        """
        self.name = name
        self.cmd = cmd
        self.mode = mode
        self.proc: Optional[asyncio.subprocess.Process] = None
        self._stream_tasks: list[asyncio.Task] = []

        base_log = logging.getLogger(f"{parent_logger}.{name}")
        self.log = _ProcessLogAdapter(base_log, {"proc": self})

    @property
    def is_running(self) -> bool:
        """Return True if the process is currently running."""
        return self.proc is not None and self.proc.returncode is None

    @property
    def is_healthy(self) -> bool:
        """Return whether the process is considered healthy based on its mode.

        - "always": healthy only while still running
        - "once": healthy if it finished with returncode 0 (or is still running)
        """
        if self.proc is None:
            return False

        if self.mode == "always":
            return self.proc.returncode is None
        else:
            return self.proc.returncode is None or self.proc.returncode == 0

    @property
    def pid(self) -> Optional[int]:
        """Return the process ID if the process has been started."""
        return self.proc.pid if self.proc else None

    async def _pump_stream(
        self, stream: Optional[asyncio.StreamReader], log_fn
    ) -> None:
        """Internal helper to stream stdout/stderr into the logger."""
        if not stream:
            return
        while line := await stream.readline():
            text = line.decode(errors="replace").rstrip()
            if text:
                log_fn("%s", text)

    async def start(self) -> None:
        """Start the subprocess.

        If the process is already running, this is a no-op.
        """
        if self.is_running:
            return

        self.proc = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # self.log.info("Started: %s", " ".join(self.cmd))

        self._stream_tasks = [
            asyncio.create_task(self._pump_stream(self.proc.stdout, self.log.debug)),
            asyncio.create_task(self._pump_stream(self.proc.stderr, self.log.warning)),
        ]

    async def stop(self, timeout: float = 10.0) -> None:
        """Gracefully stop the subprocess.

        Sends SIGTERM first, then SIGKILL if it doesn't exit in time.
        """
        if not self.is_running or not self.proc:
            return

        self.proc.terminate()
        try:
            await asyncio.wait_for(self.proc.wait(), timeout=timeout)
            self.log.info("Stopped cleanly.")
        except asyncio.TimeoutError:
            self.log.warning("Timed out on SIGTERM; sending SIGKILL.")
            self.proc.kill()
            await self.proc.wait()
            self.log.info("Killed.")

        for task in self._stream_tasks:
            task.cancel()
        self._stream_tasks.clear()
