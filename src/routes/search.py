from models import Product, SearchResponse
from fastapi import UploadFile, File, APIRouter, Request
from helpers import get_single_dino_image_embedding, get_image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post('/search', response_model=SearchResponse)
async def search(request:Request, image: UploadFile = File(...)) -> SearchResponse: 
    try:
        index = request.app.state.config["index"]   
        model = request.app.state.config["model"]
        device = request.app.state.config["device"]

        # Extracts the query and filter from the incoming request
        image = await get_image(image)

        # Performs search with filters
        similar_products_embeddings = get_single_dino_image_embedding(image, model, device)

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