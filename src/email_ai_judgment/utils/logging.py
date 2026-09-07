# 结构化日志辅助工具。


from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from typing import Iterator

def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

@contextmanager
def log_step(logger: logging.Logger, email_id: str | None, step: str) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    except Exception as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        error_type = getattr(exc, "error_type", None)
        logger.error(
            "step_failed email_id=%s step=%s elapsed_ms=%.2f error_type=%s",
            email_id,
            step,
            elapsed_ms,
            error_type,
        )
        logger.debug("step_failed_stack", exc_info=True)
        raise
    else:
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info("step_succeeded email_id=%s step=%s elapsed_ms=%.2f", email_id, step, elapsed_ms)
