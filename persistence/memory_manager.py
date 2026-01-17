"""
Memory Persistence Module with MongoDB

Provides conversation history and research result persistence.
Supports MongoDB as the backend database.

Classes:
    MemoryManager: Manages research queries and results storage/retrieval
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import json


load_dotenv()

# Configure logging for memory manager
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console handler if not already configured
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [MEMORY] %(levelname)s: %(message)s', datefmt='%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

logger.info("Memory Manager module loaded")


class MemoryManager:
    """
    Manages research query history and results using MongoDB.
    
    Attributes:
        client: MongoDB client connection
        db: MongoDB database
        collection: MongoDB collection for storing research
    """
    
    def __init__(
        self,
        mongo_uri: Optional[str] = None,
        db_name: str = "research_agent",
        collection_name: str = "queries"
    ):
        """
        Initialize MemoryManager.
        
        Args:
            mongo_uri (str, optional): MongoDB connection string.
                Defaults to MONGO_URI from .env
            db_name (str): Database name. Defaults to "research_agent"
            collection_name (str): Collection name. Defaults to "queries"
        
        Raises:
            ValueError: If MongoDB connection fails
        """
        self.mongo_uri = mongo_uri or os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        self.collection_name = collection_name
        
        logger.info(f"Initializing MemoryManager...")
        logger.debug(f"MONGO_URI: {self.mongo_uri[:50]}..." if len(self.mongo_uri) > 50 else f"MONGO_URI: {self.mongo_uri}")
        logger.debug(f"Database: {db_name}, Collection: {collection_name}")
        
        try:
            logger.info("Connecting to MongoDB...")
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            
            # Test connection
            logger.debug("Testing MongoDB connection with ping...")
            self.client.admin.command('ping')
            logger.info("✅ MongoDB connection successful")
            
            # Get database and collection
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            logger.info(f"✅ Connected to database: {db_name}")
            logger.info(f"✅ Using collection: {collection_name}")
            
            # Create text index on query field for search
            logger.debug("Creating text index on 'query' field...")
            self.collection.create_index("query", name="query_index")
            logger.debug("✅ Text index created on 'query'")
            
            # Create index on created_at for sorting
            logger.debug("Creating index on 'created_at' field...")
            self.collection.create_index("created_at", name="created_at_index")
            logger.debug("✅ Index created on 'created_at'")
            
            # Log existing documents
            doc_count = self.collection.count_documents({})
            logger.info(f"✅ Collection ready. Existing documents: {doc_count}")
            
        except ServerSelectionTimeoutError as e:
            error_msg = (
                f"❌ FAILED to connect to MongoDB at {self.mongo_uri}\n"
                f"   Error: {str(e)}\n"
                f"   Make sure MongoDB is running:\n"
                f"   - Local: mongod\n"
                f"   - Docker: docker-compose up -d\n"
                f"   - Check your MONGO_URI in .env file"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"❌ MongoDB initialization error: {str(e)}\nDetails: {type(e).__name__}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def save_research(
        self,
        query: str,
        research: str,
        critique: str,
        final_answer: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Save a research query and results to MongoDB.
        
        Args:
            query (str): Original research query
            research (str): Research findings
            critique (str): Critical review
            final_answer (str): Final summary
            metadata (dict, optional): Additional metadata
        
        Returns:
            str: Inserted document ID
        """
        try:
            logger.info("="*70)
            logger.info("SAVE_RESEARCH() CALLED")
            logger.info(f"Query: '{query[:60]}{'...' if len(query) > 60 else ''}'")
            logger.debug("Raw parameters received:")
            logger.debug(f"  - query type: {type(query).__name__}, length: {len(query) if query else 0}")
            logger.debug(f"  - research type: {type(research).__name__}, length: {len(research) if research else 0}")
            logger.debug(f"  - critique type: {type(critique).__name__}, length: {len(critique) if critique else 0}")
            logger.debug(f"  - final_answer type: {type(final_answer).__name__}, length: {len(final_answer) if final_answer else 0}")
            logger.debug(f"  - metadata: {metadata}")
            
            # Build document
            logger.info("Building document for MongoDB...")
            full_document = {
                "query": query,
                "research": research,
                "critique": critique,
                "final_answer": final_answer,
                "created_at": datetime.utcnow(),
                "metadata": metadata or {}
            }
            
            logger.debug(f"Document keys: {list(full_document.keys())}")
            logger.debug(f"Document created_at: {full_document['created_at']}")
            
            # Verify collection is accessible
            logger.debug(f"Collection: {self.collection.name}")
            logger.debug(f"Database: {self.db.name}")
            
            # Insert document
            logger.info("Inserting document into MongoDB...")
            result = self.collection.insert_one(full_document)
            doc_id = str(result.inserted_id)
            
            logger.info("✅✅✅ DOCUMENT SAVED SUCCESSFULLY ✅✅✅")
            logger.info(f"   Document ID: {doc_id}")
            logger.info(f"   Acknowledged: {result.acknowledged}")
            logger.debug(f"   Query length: {len(query)} chars")
            logger.debug(f"   Research length: {len(research)} chars")
            logger.debug(f"   Critique length: {len(critique)} chars")
            logger.debug(f"   Final answer length: {len(final_answer)} chars")
            
            # Verify document was inserted
            logger.info("Verifying document in collection...")
            verify = self.collection.find_one({"_id": result.inserted_id})
            if verify:
                logger.info("✅ Document verified in collection")
            else:
                logger.warning("⚠️ Document not found after insertion!")
            
            logger.info("="*70)
            return doc_id
            
        except Exception as e:
            logger.error("="*70)
            logger.error("❌❌❌ ERROR IN SAVE_RESEARCH ❌❌❌")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception message: {str(e)}")
            logger.error(f"Collection name: {self.collection.name}")
            logger.error(f"Database name: {self.db.name}")
            import traceback
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            logger.error("="*70)
            raise
    
    def get_research(self, research_id: str) -> Optional[Dict]:
        """
        Retrieve a specific research by ID.
        
        Args:
            research_id (str): MongoDB object ID
        
        Returns:
            dict: Research document or None
        """
        from bson.objectid import ObjectId
        
        try:
            logger.info(f"Retrieving research: {research_id}")
            
            result = self.collection.find_one({"_id": ObjectId(research_id)})
            
            if result:
                result["_id"] = str(result["_id"])
                result["created_at"] = result["created_at"].isoformat()
                logger.info(f"✅ Research found: '{result.get('query', 'Unknown')[:50]}...'")
                logger.debug(f"   Document keys: {list(result.keys())}")
                return result
            else:
                logger.warning(f"⚠️ Research not found: {research_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error retrieving research: {str(e)}")
            return None
    
    def search_research(self, query_text: str, limit: int = 10) -> List[Dict]:
        """
        Search research by query text.
        
        Args:
            query_text (str): Search query
            limit (int): Max results to return
        
        Returns:
            list: Matching research documents
        """
        try:
            logger.info(f"Searching research for: '{query_text}'")
            
            results = self.collection.find(
                {"query": {"$regex": query_text, "$options": "i"}},
            ).sort("created_at", -1).limit(limit)
            
            documents = []
            for doc in results:
                doc["_id"] = str(doc["_id"])
                doc["created_at"] = doc["created_at"].isoformat()
                documents.append(doc)
            
            logger.info(f"✅ Found {len(documents)} matching research(s)")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error searching: {str(e)}")
            return []
    
    def get_all_research(self, limit: int = 50, skip: int = 0) -> List[Dict]:
        """
        Get all research queries, newest first.
        
        Args:
            limit (int): Max results
            skip (int): Number to skip (for pagination)
        
        Returns:
            list: Research documents
        """
        try:
            logger.info(f"Fetching research history: limit={limit}, skip={skip}")
            
            results = self.collection.find().sort(
                "created_at", -1
            ).skip(skip).limit(limit)
            
            documents = []
            for doc in results:
                doc["_id"] = str(doc["_id"])
                doc["created_at"] = doc["created_at"].isoformat()
                documents.append(doc)
            
            logger.info(f"✅ Retrieved {len(documents)} research(s)")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Error fetching research: {str(e)}")
            return []
    
    def get_recent_research(self, days: int = 7) -> List[Dict]:
        """
        Get research from the last N days.
        
        Args:
            days (int): Number of days to look back
        
        Returns:
            list: Recent research documents
        """
        from datetime import timedelta
        
        try:
            logger.info(f"Fetching research from last {days} days...")
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            results = self.collection.find(
                {"created_at": {"$gte": cutoff_date}}
            ).sort("created_at", -1)
            
            documents = []
            for doc in results:
                doc["_id"] = str(doc["_id"])
                doc["created_at"] = doc["created_at"].isoformat()
                documents.append(doc)
            
            logger.info(f"✅ Retrieved {len(documents)} recent research(s)")
            return documents
        except Exception as e:
            logger.error(f"❌ Error fetching recent research: {str(e)}")
            return []
    
    def delete_research(self, research_id: str) -> bool:
        """
        Delete a research document.
        
        Args:
            research_id (str): MongoDB object ID
        
        Returns:
            bool: Success status
        """
        from bson.objectid import ObjectId
        
        try:
            logger.info(f"Deleting research: {research_id}")
            
            result = self.collection.delete_one({"_id": ObjectId(research_id)})
            
            if result.deleted_count > 0:
                logger.info(f"✅ Research deleted successfully")
                return True
            else:
                logger.warning(f"⚠️ Research not found for deletion: {research_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting research: {str(e)}")
            return False
    
    def update_research(self, research_id: str, updates: Dict) -> bool:
        """
        Update a research document.
        
        Args:
            research_id (str): MongoDB object ID
            updates (dict): Fields to update
        
        Returns:
            bool: Success status
        """
        from bson.objectid import ObjectId
        
        try:
            logger.info(f"Updating research: {research_id}")
            result = self.collection.update_one(
                {"_id": ObjectId(research_id)},
                {"$set": {**updates, "updated_at": datetime.utcnow()}}
            )
            if result.modified_count > 0:
                logger.info(f"✅ Research updated successfully: {research_id}")
                return True
            logger.warning(f"⚠️ Research not found for update: {research_id}")
            return False
        except Exception as e:
            logger.error(f"❌ Error updating research: {str(e)}")
            return False
    
    def get_stats(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            dict: Statistics including total count, recent count, etc.
        """
        from datetime import timedelta
        
        try:
            logger.info("Fetching database statistics...")
            
            total_count = self.collection.count_documents({})
            week_count = self.collection.count_documents({
                "created_at": {"$gte": datetime.utcnow() - timedelta(days=7)}
            })
            
            stats = {
                "total_research": total_count,
                "this_week": week_count,
                "database": self.db_name,
                "collection": self.collection_name
            }
            
            logger.info(f"✅ Stats retrieved: {total_count} total, {week_count} this week")
            logger.debug(f"   Database: {self.db_name}, Collection: {self.collection_name}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {str(e)}")
            return {}
    
    def close(self):
        """Close MongoDB connection."""
        try:
            logger.info("Closing MongoDB connection...")
            self.client.close()
            logger.info("✅ MongoDB connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing connection: {str(e)}")


# Global memory manager instance
_memory_instance: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get or create global memory manager instance."""
    global _memory_instance
    if _memory_instance is None:
        logger.info("Creating new MemoryManager instance...")
        _memory_instance = MemoryManager()
        logger.info("✅ MemoryManager instance created and ready")
    else:
        logger.debug("Using existing MemoryManager instance")
    return _memory_instance
