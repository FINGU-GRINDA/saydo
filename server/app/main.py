from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from app.api import auth, meetings, integrations, demo, bot, agent, websocket, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up Rinda CallOps server...")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Rinda CallOps API",
    description="Meeting agent with Google integrations",
    version="0.1.0",
    lifespan=lifespan,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(meetings.router, prefix="/api")
app.include_router(integrations.router, prefix="/api")
app.include_router(demo.router, prefix="/api")
app.include_router(bot.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(websocket.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Rinda CallOps API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )