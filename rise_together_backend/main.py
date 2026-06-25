from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.database import Base
from core.database import engine

import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    lifespan=lifespan,
)