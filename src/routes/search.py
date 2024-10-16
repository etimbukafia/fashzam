from models import Product, SearchResponse
from fastapi import UploadFile, File, APIRouter, Request
from helpers import get_single_dino_image_embedding, get_image
import logging
from bson import ObjectId
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post('/search', response_model=SearchResponse)
async def search(request:Request, image: UploadFile = File(...)) -> SearchResponse: 
    try:
        index = request.app.state.config["index"]   
        model = request.app.state.config["model"]
        device = request.app.state.config["device"]
        collection = request.app.state.config["collection"]

        # Extracts the query and filter from the incoming request
        image = await get_image(image)

        # Performs search with filters
        similar_products_embeddings = get_single_dino_image_embedding(image, model, device)

        result = index.query(vector=similar_products_embeddings, top_k=5, include_metadata=True)

        match_ids = [ObjectId(match['metadata'].get('product_id', ''),) for match in result['matches']]
        records_cursor = collection.find({"_id": {"$in": match_ids}})
        records = await records_cursor.to_list(length=len(match_ids))

        id_to_product_Display_Name = {record['_id']: record.get("productDisplayName", None) for record in records}
        id_to_gender = {record['_id']: record.get("gender", None) for record in records}
        id_to_article_Type = {record['_id']: record.get("articleType", None) for record in records}
        id_to_image_link = {record['_id']: record.get("image_link", None) for record in records}
        

        # Prepares the response object by populating it with the similar listings
        response = SearchResponse(
            products=[
                Product(
                    productName = id_to_product_Display_Name.get(ObjectId(match['metadata'].get('product_id', '')), None),
                    gender = id_to_gender.get(ObjectId(match['metadata'].get('product_id', '')), None),
                    articleType = id_to_article_Type.get(ObjectId(match['metadata'].get('product_id', '')), None),
                    image_link = id_to_image_link.get(ObjectId(match['metadata'].get('product_id', '')), None),  # Map back to match
                    score = match['score'],
                ) for match in result['matches']
            ]
        )

        return response
    
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(products=[])