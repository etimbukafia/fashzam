from motor.motor_asyncio import AsyncIOMotorClient
import os
from gridfs import GridFS
from pymongo import MongoClient
import logging
from dotenv import load_dotenv
from pinecone import Pinecone
load_dotenv()

#Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    _client = None
    _db = None
    _collection = None
    _fs = None

    @classmethod
    async def connect(cls):
        if cls._client is None:
            try:
                uri = os.environ.get("MONGO_URI")
                print(f"Connecting to MongoDB with URI: {uri}")

                db_name = "product-database"
                collection_name = "product-collection"

                cls._client = AsyncIOMotorClient(uri,  maxPoolSize=50)
                cls._db = cls._client[db_name]
                cls._collection = cls._db[collection_name]
                cls._fs = GridFS(MongoClient(uri)[db_name])
                logger.info("Connected to MongoDB")
            except ConnectionError as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
        return cls._collection
    
    @classmethod
    async def close(cls):
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            cls._collection = None
            logger.info("Disconnected from MongoDB")

class vectorDatabase:
    _index = None

    @classmethod
    async def connect(cls):
        if cls._index is None:
            try:
                api_key = os.environ.get("PINECONE_API_KEY")
                if not api_key:
                    raise ValueError("Pinecone API key is missing.")
                
                pc = Pinecone(api_key)
                logging.info(f"Connecting to Pinecone with api_key")

                index_name = "dino-index"
                cls._index = pc.Index(index_name)
                logger.info(f"Connected to index: {cls._index}")
            except Exception as e:
                logger.error(f"error connecting to index: {e}")
                raise
        return cls._index