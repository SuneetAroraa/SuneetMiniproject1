from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db
from image_catalogue import query_images,fetch_images

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/catalogue")
async def catalogue():
    await fetch_images()   
    images = query_images()
    return {"images": images}

@app.get("/search")
async def search(format: str):
    results = query_images(format) 
    return {"results": results}