# FastAPI 应用工厂
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from email_ai_judgment.api.routes import explain, feedback, judgment, recommend
from email_ai_judgment.config.settings import get_settings
from email_ai_judgment.exceptions.judgment_exceptions import JudgmentException, ValidationError, unknown_error
from email_ai_judgment.models.error import JudgmentResponse
from email_ai_judgment.utils.logging import configure_logging

def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    app = FastAPI(title="Enterprise Email AI Judgment Agent", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8080"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(judgment.router, prefix="/api/v1")
    app.include_router(explain.router, prefix="/api/v1")
    app.include_router(recommend.router, prefix="/api/v1")
    app.include_router(feedback.router, prefix="/api/v1")

    @app.exception_handler(JudgmentException)
    async def judgment_exception_handler(request: Request, exc: JudgmentException):
        response = JudgmentResponse[dict](success=False, data=None, error=exc.to_error())
        return JSONResponse(status_code=200, content=response.model_dump(mode="json"))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        err = ValidationError("api_request_validation", "Request validation failed", str(exc)).to_error()
        response = JudgmentResponse[dict](success=False, data=None, error=err)
        return JSONResponse(status_code=422, content=response.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def unknown_exception_handler(request: Request, exc: Exception):
        response = JudgmentResponse[dict](success=False, data=None, error=unknown_error("api_unknown", exc))
        return JSONResponse(status_code=500, content=response.model_dump(mode="json"))

    return app

app = create_app()
