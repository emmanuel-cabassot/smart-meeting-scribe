"""
S3 Service - Helper functions for interacting with MinIO/S3 storage.
"""
import json
import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Dict, Any

from app.core.config import settings


def get_s3_client():
    """Create a boto3 S3 client configured for MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.MINIO_ENDPOINT}",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY
    )


def parse_s3_path(s3_path: str) -> tuple[str, str]:
    """
    Parse an S3 path into bucket and key.
    
    Handles different formats:
    - "s3://processed/20260117_xxx"
    - "Résultat : s3://processed/20260117_xxx"
    
    Returns: (bucket, key) tuple
    """
    # Clean the path - remove any prefix like "Résultat : "
    clean_path = s3_path.strip()
    
    # Find the s3:// part and extract from there
    s3_index = clean_path.find("s3://")
    if s3_index == -1:
        raise ValueError(f"Invalid S3 path (no s3:// found): {s3_path}")
    
    # Extract the actual S3 path
    actual_path = clean_path[s3_index + 5:]  # Remove "s3://"
    
    # Split bucket and key
    parts = actual_path.split("/", 1)
    if len(parts) < 2:
        raise ValueError(f"Invalid S3 path format (missing key): {s3_path}")
    
    return parts[0], parts[1]


def get_transcript_from_s3(s3_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch the fusion.json transcript from S3.
    
    Args:
        s3_path: Base S3 path (e.g., "s3://processed/20260117_xxx")
        
    Returns:
        List of transcript segments or None if not found
        
    Raises:
        ClientError: If S3 operation fails
        ValueError: If path is invalid
    """
    if not s3_path:
        return None
    
    bucket, base_key = parse_s3_path(s3_path)
    
    # The fusion.json file is stored at {base_key}/fusion.json
    object_key = f"{base_key}/fusion.json"
    
    s3_client = get_s3_client()
    
    try:
        response = s3_client.get_object(Bucket=bucket, Key=object_key)
        content = response['Body'].read().decode('utf-8')
        return json.loads(content)
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        if error_code == 'NoSuchKey':
            return None
        raise
