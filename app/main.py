from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.api_router import api_router
from core.database import DatabaseManager

def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG-FAST",
        version="0.1.0",
        description="API para RAG com FastAPI"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    db_manager = DatabaseManager()

    return app

app = create_app()

@app.get('/')
def hello_World():
    return {"message": "APP online ✅"}