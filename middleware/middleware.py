import time
import logging

from starlette.middleware import base
from fastapi import FastAPI, Request, status
# from main import app
from fastapi.responses import JSONResponse
from logging_config import formater, file_handler


logger = logging.getLogger(__name__)
file_handler.setFormatter(formater)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


class ResponseMiddleware(base.BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Logging Middleware
        This middleware can log information about incoming requests, such as the request method, URL, and processing time. It can help you keep track of how your API is being used and diagnose potential issues.
        """
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            "Request method=%s path=%s status_code=%s process_time=%.5f",
            request.method,
            response.status_code,
            request.url,
            process_time,
        )
        response.headers["X-Process-Time"] = str(process_time)
        return response


class HandleError(base.BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """
        Error Handling Middleware
        This middleware can catch and handle exceptions raised by your route handlers, allowing you to provide consistent error responses.
        """
        try:
            response = await call_next(request)
            if response.status_code < 400:
                logger.info(
                    f"Request to {request.url} responded with status code {response.status_code}")
            else:
                logger.warning(
                    f"Request to {request.url} responded with status code {response.status_code}")
            return response
        except Exception as e:
            logger.exception("An error occurred")
            return JSONResponse(content={"error": "An ErroR occurred"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
