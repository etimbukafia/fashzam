from fastapi import APIRouter, Request, Query, HTTPException
from models import Products
from typing import List, Optional

router = APIRouter()

@router.get('/display', response_model=List[Products])
async def display(request: Request, limit: int = Query(20, ge=1, le=100), skip: Optional[int] = None) -> List[Products]:
    """
    Fetches products data from the MongoDB collection and returns the products in a structured format as a list of `Products` objects.

    Returns:
        List[Products]: A list of Products metadata, each containing relevant details
        and the image URL.

        The read_listings() function returns a list of products data, 
        including image URLs.

    Raises:
        HTTPException: If there is a validation error with the data format.
    """
    # If 'skip' is not provided, set is as 1 x limit
    if skip is None:
        skip = limit

    collection = request.app.state.config["collection"]  
    
    try:
        # MongoDB query to get the product data with limit and skip
        result = collection.find({}).skip(skip).limit(limit)
        result_list = await result.to_list(length=limit)

        products = []

        for data in result_list:
            data["cloudinaryUrl"] = data.get("image_link", None)
        
            try:
                # Create a Products instance and append it to the products list
                products.append(Products(**data))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error parsing product: {str(e)}")
            
        if not products:
            raise HTTPException(status_code=404, detail="No products found")
        
        return products
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")