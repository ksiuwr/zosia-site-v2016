import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def list_bucket_objects(bucket_name):
    '''List the objects in S3 bucket
    Sample response:
    [{
      'Key': 'cats/cute_cat.jpg',
      'LastModified': datetime(...),
      'ETag': 'abc...',
      'Size': 123,
      'StorageClass': '...'
    }]'''

    s3 = boto3.client('s3')

    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        pass
    except (ClientError, NoCredentialsError) as e:
        # AllAccessDisabled error == bucket not found
        print(f"Error: {e}")
        return None

    # Only return the contents if we found some keys
    if response['KeyCount'] > 0:
        return response['Contents']

    return None
