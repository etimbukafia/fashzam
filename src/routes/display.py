@app.get('/listings', response_model=List[House])
async def read_listings(limit: int = Query(20, ge=1, le=100), skip: int=0) -> List[House]:
    """
    Fetches house listings from the MongoDB collection, enriches them with image URLs,
    and returns the listings in a structured format as a list of `House` objects.

    Returns:
        List[House]: A list of house listings, each containing relevant details
        and an image URL if available.

        The read_listings() function returns a list of house listings, 
        including image URLs like https://hardly-sound-ringtail.ngrok-free.app/images/abc123.

    Raises:
        HTTPException: If there is a validation error with the data format.
    """

    result = collection.find({}).skip(skip).limit(limit)
    result_list = await result.to_list(length=limit)

    try:
        # Construct listings with image URLs
        listings_with_images = []
        for data in result_list:
            # Convert ObjectId fields to strings for compatibility
            data['_id'] = str(data['_id'])
            if 'image_id' in data:
                data['image_id'] = str(data['image_id'])
                # Construct the image URL using the image_id and add it to the data
                data['homeImage'] = f" https://4018-98-97-79-143.ngrok-free.app/images/{data['image_id']}"

            # Create a House object from the data and add it to the list
            listings_with_images.append(House(**data))

        # Return the list of enriched house listings
        return listings_with_images
    except ValidationError as e:
        # Log the validation error and raise an HTTP 400 exception with a relevant message
        app_logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail="Invalid data format")