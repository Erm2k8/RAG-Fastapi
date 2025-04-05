from fastapi import FastAPI
from api.api_router import api_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG-FAST",
        version="0.1.0",
    )
    app.include_router(api_router, prefix="/v1")
    return app

app = create_app()

@app.get("/")
def hello_world():
    """Just to confirm that the API is online"""
    return {"Hello": "World"}