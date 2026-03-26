from fastapi import FastAPI
from app.database import Base, engine
from app.routes import upload, search
from app.services.qdrant_service import create_collection

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup():
    create_collection()

app.include_router(upload.router)
app.include_router(search.router)


