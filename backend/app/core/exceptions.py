from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class GermanGPTError(Exception):
    """Base application error."""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthenticationError(GermanGPTError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "AUTH_ERROR")


class AuthorizationError(GermanGPTError):
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, "AUTHZ_ERROR")


class NotFoundError(GermanGPTError):
    def __init__(self, resource: str, identifier: str | int):
        super().__init__(f"{resource} '{identifier}' not found", "NOT_FOUND")


class ValidationError(GermanGPTError):
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR")


class LLMError(GermanGPTError):
    def __init__(self, message: str, provider: str = "unknown"):
        self.provider = provider
        super().__init__(f"LLM error ({provider}): {message}", "LLM_ERROR")


class RateLimitError(GermanGPTError):
    def __init__(self):
        super().__init__("Rate limit exceeded. Please try again later.", "RATE_LIMIT")


class VoiceProcessingError(GermanGPTError):
    def __init__(self, message: str):
        super().__init__(message, "VOICE_ERROR")


class RAGError(GermanGPTError):
    def __init__(self, message: str):
        super().__init__(message, "RAG_ERROR")


async def germangpt_exception_handler(request: Request, exc: GermanGPTError) -> JSONResponse:
    status_map = {
        "AUTH_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHZ_ERROR": status.HTTP_403_FORBIDDEN,
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "RATE_LIMIT": status.HTTP_429_TOO_MANY_REQUESTS,
        "LLM_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "VOICE_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "RAG_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
    }
    http_status = status_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    return JSONResponse(
        status_code=http_status,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "HTTP_ERROR", "message": exc.detail}},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}},
    )
