import oss2
import os
import uuid
from datetime import datetime

# Initialize OSS Config
# Use environment variables for security
ACCESS_KEY_ID = os.getenv("ALIYUN_ACCESS_KEY_ID")
ACCESS_KEY_SECRET = os.getenv("ALIYUN_ACCESS_KEY_SECRET")
BUCKET_NAME = os.getenv("ALIYUN_OSS_BUCKET")
ENDPOINT = os.getenv("ALIYUN_OSS_ENDPOINT") # e.g., oss-cn-hangzhou.aliyuncs.com

def get_bucket():
    if not all([ACCESS_KEY_ID, ACCESS_KEY_SECRET, BUCKET_NAME, ENDPOINT]):
        print("Warning: OSS credentials not fully set.")
        return None
    
    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)
    return bucket

def upload_file_to_oss(file_obj, filename: str, folder: str = "community") -> str:
    """
    Uploads a file-like object to OSS and returns the public URL.
    """
    bucket = get_bucket()
    if not bucket:
        return None

    # Generate unique path: folder/YYYYMMDD/uuid_filename
    date_str = datetime.now().strftime("%Y%m%d")
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    object_name = f"{folder}/{date_str}/{unique_name}"

    try:
        # Put Object
        bucket.put_object(object_name, file_obj)
        
        # Construct URL (Assuming public-read or using authorized signing logic if private)
        # For public-read buckets: https://bucket-name.endpoint/object-name
        # For private buckets, we need to sign, but here we return the permanent key 
        # or a public link if the user sets ACL to public-read.
        # Let's assume standard public access pattern for web apps:
        url = f"https://{BUCKET_NAME}.{ENDPOINT}/{object_name}"
        return url
    except Exception as e:
        print(f"OSS Upload Error: {e}")
        return None
