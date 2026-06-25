from contextlib import asynccontextmanager

from fastapi import FastAPI

from  app.core.database import Base
from  app.core.database import engine

import  app.models as models


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    lifespan=lifespan,
)