import time

from fastapi import FastAPI, Request, status
from routes.auth import auth_router
from routes.gym import gym_router
from fastapi.responses import JSONResponse

app = FastAPI(title="GYM Logs")

# Custom Middlewares


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Logging Middleware
    This middleware can log information about incoming requests, such as the request method, URL, and processing time. It can help you keep track of how your API is being used and diagnose potential issues.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.include_router(auth_router)
app.include_router(gym_router)

# @app.middleware("http")
# async def handle_errors(request: Request, call_next):
#     """
#     Error Handling Middleware
#     This middleware can catch and handle exceptions raised by your route handlers, allowing you to provide consistent error responses.
#     """
#     try:
#         response = await call_next(request)
#         return response
#     except Exception as e:
#         return JSONResponse(content={"error": "An ErroR occurred"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
