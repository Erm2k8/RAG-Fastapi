from fastapi import FastAPI
from api.v1.routes import router as v1_router

def create_app() -> FastAPI:
    app = FastAPI(title="RAG-FAST")
    app.include_router(v1_router, prefix="/v1")
    return app

app = create_app()

@app.get("/")
def hello_world():
    """Just to confirm that the API is online"""
    return {"Hello": "World"}