# resume_processor/utils/mongodb.py
import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from django.conf import settings

load_dotenv()
logger = logging.getLogger(__name__)

class MongoDBService:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        """Singleton pattern to ensure only one MongoDB connection is created"""
        if cls._instance is None:
            cls._instance = super(MongoDBService, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        """Initialize MongoDB connection"""
        try:
            # Get MongoDB connection details from environment variables
            # Use your environment variable naming
            environment = os.getenv('NODE_ENV', 'development').lower()
            
            if environment == 'production':
                mongodb_uri = os.getenv('MONGODB_URL_PRODUCTION')
            elif environment == 'test':
                mongodb_uri = os.getenv('MONGODB_URL_TEST')
            else:
                mongodb_uri = os.getenv('MONGODB_URL_DEVELOPMENT')
            
            # Default to development if no connection string is found
            if not mongodb_uri:
                mongodb_uri = os.getenv('MONGODB_URL_DEVELOPMENT')
                environment = 'development'
            
            # Extract database name from connection string or use default
            if '/' in mongodb_uri:
                db_name = mongodb_uri.split('/')[-1].split('?')[0]
            else:
                db_name = 'optimized_cv_dev'  # Default name
                
            logger.info(f"Connecting to MongoDB ({environment}): {mongodb_uri}")
            
            # Create MongoDB client
            self._client = MongoClient(mongodb_uri)
            
            # Test the connection
            self._client.admin.command('ping')
            logger.info("MongoDB connection successful")
            
            # Set database
            self._db = self._client[db_name]
            
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            self._client = None
            self._db = None
            
        except Exception as e:
            logger.error(f"Error initializing MongoDB connection: {str(e)}")
            self._client = None
            self._db = None

    @property
    def client(self):
        """Get MongoDB client instance"""
        if not self._client:
            self._initialize_connection()
        return self._client

    @property
    def db(self):
        """Get MongoDB database instance"""
        if not self._db:
            self._initialize_connection()
        return self._db
    
    def insert_enhanced_resume(self, resume_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[str]:
        """
        Insert an enhanced resume document into MongoDB
        
        Args:
            resume_data: The resume data to insert
            user_id: Optional user ID to associate with the resume
            
        Returns:
            str: ID of the inserted document, or None if insertion failed
        """
        try:
            # Get the enhanced_data collection
            collection = self._db.enhanced_data
            
            # Add user_id if provided
            if user_id:
                resume_data['user_id'] = user_id
                
            # Add metadata
            from datetime import datetime
            resume_data['created_at'] = datetime.utcnow()
            resume_data['updated_at'] = datetime.utcnow()
            
            # Insert document
            result = collection.insert_one(resume_data)
            
            if result.inserted_id:
                logger.info(f"Enhanced resume document inserted with ID: {result.inserted_id}")
                return str(result.inserted_id)
            
            logger.warning("Enhanced resume document insertion failed")
            return None
            
        except PyMongoError as e:
            logger.error(f"MongoDB error inserting enhanced resume: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error inserting enhanced resume: {str(e)}")
            return None
    
    def get_enhanced_resume(self, resume_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an enhanced resume document by ID
        
        Args:
            resume_id: The ID of the resume to retrieve
            
        Returns:
            Dict: The resume document, or None if not found
        """
        try:
            from bson.objectid import ObjectId
            
            # Get the enhanced_data collection
            collection = self._db.enhanced_data
            
            # Query by ID
            resume = collection.find_one({"_id": ObjectId(resume_id)})
            
            if resume:
                # Convert ObjectId to string for JSON serialization
                resume['_id'] = str(resume['_id'])
                return resume
            
            logger.warning(f"Enhanced resume with ID {resume_id} not found")
            return None
            
        except PyMongoError as e:
            logger.error(f"MongoDB error getting enhanced resume: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting enhanced resume: {str(e)}")
            return None
    
    def update_enhanced_resume(self, resume_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update an enhanced resume document
        
        Args:
            resume_id: The ID of the resume to update
            update_data: The data to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        try:
            from bson.objectid import ObjectId
            from datetime import datetime
            
            # Get the enhanced_data collection
            collection = self._db.enhanced_data
            
            # Add updated timestamp
            update_data['updated_at'] = datetime.utcnow()
            
            # Update document
            result = collection.update_one(
                {"_id": ObjectId(resume_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Enhanced resume with ID {resume_id} updated successfully")
                return True
            
            logger.warning(f"Enhanced resume with ID {resume_id} not found or not modified")
            return False
            
        except PyMongoError as e:
            logger.error(f"MongoDB error updating enhanced resume: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating enhanced resume: {str(e)}")
            return False
    
    def get_user_enhanced_resumes(self, user_id: str) -> list:
        """
        Get all enhanced resumes for a user
        
        Args:
            user_id: The ID of the user
            
        Returns:
            list: List of enhanced resume documents
        """
        try:
            # Get the enhanced_data collection
            collection = self._db.enhanced_data
            
            # Query by user_id
            cursor = collection.find({"user_id": user_id})
            
            # Convert cursor to list and prepare for JSON serialization
            resumes = []
            for resume in cursor:
                resume['_id'] = str(resume['_id'])
                resumes.append(resume)
            
            return resumes
            
        except PyMongoError as e:
            logger.error(f"MongoDB error getting user enhanced resumes: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting user enhanced resumes: {str(e)}")
            return []