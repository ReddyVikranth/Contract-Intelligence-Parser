import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    try:
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DATABASE_NAME", "contract_parser")
        
        logger.info(f"Connecting to MongoDB at {mongodb_url}")
        db.client = AsyncIOMotorClient(mongodb_url)
        
        # Test the connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        db.database = db.client[db_name]
        
        # Create indexes
        await create_indexes()
        
    except ConnectionFailure as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        logger.info("Closing MongoDB connection")
        db.client.close()

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Index for contracts collection
        await db.database.contracts.create_index("contract_id", unique=True)
        await db.database.contracts.create_index("status")
        await db.database.contracts.create_index("created_at")
        await db.database.contracts.create_index("confidence_score")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database():
    """Get database instance"""
    return db.database