from google.cloud import storage
import os
from datetime import datetime, timedelta

class StorageService:
    """Service for handling Google Cloud Storage operations"""
    
    def __init__(self, bucket_name=None):
        """Initialize the storage client with optional bucket name"""
        self.client = storage.Client()
        self.bucket_name = bucket_name or os.environ.get('GCS_BUCKET_NAME')
        
    def upload_to_cloud_storage(self, local_file_path, destination_blob_name):
        """
        Upload a file to Google Cloud Storage
        
        Args:
            local_file_path: Path to local file
            destination_blob_name: Destination path in bucket
            
        Returns:
            str: Public URL of the uploaded file
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        
        # Upload the file
        blob.upload_from_filename(local_file_path)
        
        return f"gs://{self.bucket_name}/{destination_blob_name}"
        
    def delete_from_cloud_storage(self, blob_name):
        """
        Delete a file from Google Cloud Storage
        
        Args:
            blob_name: Name of blob to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        
        try:
            blob.delete()
            return True
        except Exception:
            return False
            
    def get_signed_url(self, blob_name, expiration_minutes=30):
        """
        Generate a signed URL for temporary access to a file
        
        Args:
            blob_name: Name of blob
            expiration_minutes: Minutes until URL expires
            
        Returns:
            str: Signed URL
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        
        # Generate URL that expires in specified minutes
        expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        
        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET"
        )
        
        return url
        
    def schedule_deletion(self, blob_name, delay_hours=24):
        """
        Schedule a file for deletion after specified delay
        
        Args:
            blob_name: Name of blob to delete
            delay_hours: Hours before deletion
            
        Returns:
            bool: True if scheduled successfully
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        
        # Set object lifecycle to delete after delay
        lifecycle_rules = bucket.lifecycle_rules
        
        # Add rule to delete this specific object
        deletion_rule = {
            'action': {'type': 'Delete'},
            'condition': {
                'age': delay_hours * 3600,  # Convert hours to seconds
                'matchesPrefix': [blob_name]
            }
        }
        
        # Add rule if not already present
        if deletion_rule not in lifecycle_rules:
            lifecycle_rules.append(deletion_rule)
            bucket.lifecycle_rules = lifecycle_rules
            bucket.update()
        
        return True

# Create instance for easier importing
storage_service = StorageService()

# Export individual functions for convenience
upload_to_cloud_storage = storage_service.upload_to_cloud_storage
delete_from_cloud_storage = storage_service.delete_from_cloud_storage
get_signed_url = storage_service.get_signed_url
schedule_deletion = storage_service.schedule_deletion