import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.config import settings
from contextlib import asynccontextmanager
from core.database import DatabaseManager
from api.v1.assets import router as asset_router
from api.v1.categories import router as category_router
from api.v1.admin_assets import router as admin_router
from api.v1.auth import router as auth_router
from api.v1.images import router as image_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Startup: Initialize the database pool
    db_manager = DatabaseManager()
    await db_manager.connect()
    yield
    # Shutdown: Close the database pool
    await db_manager.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for Valemix Assets Catalog",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,  # ty:ignore[invalid-argument-type]
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(asset_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(image_router, prefix="/api/v1")

# Mount Static Files for Image Served Locally
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
async def root():
    try:
        return {"message": f"Welcome to {settings.APP_NAME} API"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
