from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import analyze, music

app = FastAPI(title="photo-maestro API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/analyze", tags=["analyze"])
app.include_router(music.router, prefix="/api/music", tags=["music"])


@app.get("/health")
async def health():
    return {"status": "ok"}
