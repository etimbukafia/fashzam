import os
import requests
import IPython.display
from collections import OrderedDict
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import ValidationError
from fastapi.middleware.cors import CORSMiddleware
from helpers import get_model_info, get_single_image_embedding, get_image
from models import Product, SearchRequest, SearchResponse
from config import vectorDatabase
import logging
from contextlib import asynccontextmanager

#Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

"""converts the function into something called an async context manager. 
A context manager in Python is something that you can use in a with statement, for example, open() can be used as a context manager"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    fashzam_index = await vectorDatabase.connect()
    # Get model, processor & tokenizer
    clip_model, clip_processor, _, device = get_model_info()
    
    app.state.config = {
        "index": fashzam_index,
        "model": clip_model, 
        "processor": clip_processor, 
        "device": device
    }
    yield

    app.state.config.clear()

app = FastAPI(lifespan=lifespan)

# Endpoint for searching, which accepts a POST request and returns a SearchResponse
@app.post('/search', response_model=SearchResponse)
async def search(image: UploadFile = File(...)) -> SearchResponse: 
    try:
        index = app.state.config["index"]
        clip_model = app.state.config["model"]
        clip_processor = app.state.config["processor"]
        device = app.state.config["device"]

        # Extracts the query and filter from the incoming request
        image = await get_image(image)

        # Performs search with filters
        similar_products_embeddings = get_single_image_embedding(image, clip_processor, clip_model, device)

        result = index.query(vector=similar_products_embeddings, top_k=5, include_metadata=True)

        # Prepares the response object by populating it with the similar listings
        response = SearchResponse(
            products=[
                Product(
                        _id=match['id'],
                        productName=match['metadata'].get('productDisplayName', ''),
                        product_id=match['metadata'].get('product_id', ''),
                        score = match['score']
                ) for match in result['matches']
            ]
        )

        return response
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(products=[])
    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, log_level="info")



