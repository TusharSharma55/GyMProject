import time
import logging

from fastapi import FastAPI, Request, status
from routes.auth import auth_router
from routes.gym import gym_router
from middleware.middleware import HandleError, ResponseMiddleware

from logging_config import file_handler, log_formatter

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


# Now you can use the logger in your code
# logger.debug("This is a debug message")
# logger.info("This is an info message")
# logger.warning("This is a warning message")
# logger.error("This is an error message")

app = FastAPI(title="GYM Logs")

# Custom Middlewares

app.add_middleware(ResponseMiddleware)
app.add_middleware(HandleError)

app.include_router(auth_router)
app.include_router(gym_router)
