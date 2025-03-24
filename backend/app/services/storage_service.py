from google.cloud import storage
from flask import current_app
import uuid

def upload_file_to_gcs(file_obj, destination_blob_name):
    """
    Upload a file to Google Cloud Storage
    Returns: Public URL of the uploaded file
    """
    client = storage.Client()
    bucket = client.bucket(current_app.config['GCP_BUCKET_NAME'])
    blob = bucket.blob(destination_blob_name)
    
    blob.upload_from_file(file_obj)
    
    blob.make_public()
    
    return f"gs://{current_app.config['GCP_BUCKET_NAME']}/{destination_blob_name}"

def delete_file_from_gcs(blob_name):
    """
    Delete a file from Google Cloud Storage
    """
    client = storage.Client()
    bucket = client.bucket(current_app.config['GCP_BUCKET_NAME'])
    blob = bucket.blob(blob_name)
    
    blob.delete()
    
    return True