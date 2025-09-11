from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.settings
from src.api.routes import router as api_router
from src.database.load_database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting AI Canvas Scoops Backend...")
    print("🔧 Environment variables loaded from .env")

    # Check for required environment variables
    import src.settings as settings

    if not settings.OPENAI_API_KEY:
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment")
        print("   Get your key from: https://platform.openai.com/account/api-keys")
    else:
        print("✅ OpenAI API key configured")

    if not settings.STABILITY_AI_KEY:
        print("⚠️  WARNING: STABILITY_AI_KEY not found in environment")
        print("   Get your key from: https://platform.stability.ai/account/keys")
    else:
        print("✅ Stability AI API key configured")

    await init_db()
    print("✅ Application startup complete")
    yield
    # Shutdown (if needed)
    print("🛑 Shutting down AI Canvas Scoops Backend...")
    pass


app = FastAPI(
    title="AI Canvas Scoops Backend",
    description="Backend API for the AI Canvas Scoops ice cream game",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "AI Canvas Scoops Backend API", "status": "running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
