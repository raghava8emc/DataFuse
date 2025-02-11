from fastapi import FastAPI
from api.routes import router as api_router
import uvicorn

def create_app():
    app = FastAPI(
        title="Data Ingestion Platform",
        description="Ingest data from various sources using a REST API",
        version="1.0.0"
    )
    app.include_router(api_router)
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)