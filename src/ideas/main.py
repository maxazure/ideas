from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import init_db
from .routers import ideas, agent, web_auth
from .auth import verify_api_key


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Idea Execution Loop",
    description="A system for executing ideas with AI Agent collaboration",
    version="0.1.0",
    lifespan=lifespan,
)

# Static files directory
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Web auth routes (no API key required)
app.include_router(web_auth.router, prefix="/auth", tags=["auth"])

# API routes (with optional API key)
app.include_router(ideas.router, prefix="/api/ideas", tags=["ideas"], dependencies=[Depends(verify_api_key)])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"], dependencies=[Depends(verify_api_key)])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def serve_index():
    """Serve the main web app."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Ideas Web App - Static files not found"}


@app.get("/login")
async def serve_login():
    """Serve the login page."""
    login_file = STATIC_DIR / "login.html"
    if login_file.exists():
        return FileResponse(login_file)
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/add")
async def serve_add():
    """Serve the add/edit idea page."""
    add_file = STATIC_DIR / "add.html"
    if add_file.exists():
        return FileResponse(add_file)
    return FileResponse(STATIC_DIR / "index.html")
