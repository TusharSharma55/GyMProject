import time

from fastapi import FastAPI, Request, status
from routes.auth import auth_router
from routes.gym import gym_router
from middleware.middleware import HandleError, ResponseMiddleware


app = FastAPI(title="GYM Logs")

# Custom Middlewares


app.add_middleware(ResponseMiddleware)
app.add_middleware(HandleError)

app.include_router(auth_router)
app.include_router(gym_router)
