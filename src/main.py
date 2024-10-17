from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware
from src.helpers import get_model_info
from config import vectorDatabase, Database
import logging
from contextlib import asynccontextmanager
from routes.search import router as search_router
from routes.display import router as display_router

#Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""converts the function into something called an async context manager. 
A context manager in Python is something that you can use in a with statement, for example, open() can be used as a context manager"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to pinecone index
    dino_index = await vectorDatabase.connect()
    # Get model, processor & tokenizer
    dino_model, device = get_model_info()
    # Connect to mongodb
    collection = await Database.connect()

    
    app.state.config = {
        "index": dino_index,
        "model": dino_model,
        "device": device,
        "collection": collection
    }
    yield

    app.state.config.clear()

app = FastAPI(lifespan=lifespan)

app.include_router(search_router)
app.include_router(display_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")



