from contextlib import asynccontextmanager
from fastapi import FastAPI

from .database import init_db
from .routers import ideas, agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Idea Execution Loop",
    description="A system for executing ideas with AI Agent collaboration",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(ideas.router, prefix="/api/ideas", tags=["ideas"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
