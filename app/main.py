from fastapi import FastAPI
from app.routes import router
from app.memory import init_db

app = FastAPI(
    title="CommitIQ",
    description="Cross-Meeting Execution Intelligence Engine",
    version="1.0.0"
)

# Initialize database on startup
@app.on_event("startup")
def startup():
    init_db()

# Register all routes
app.include_router(router, prefix="/api/v1")

# Health check
@app.get("/")
def root():
    return {
        "name": "CommitIQ",
        "status": "running",
        "message": "Cross-Meeting Execution Intelligence Engine"
    }