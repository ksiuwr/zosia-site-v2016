import boto3
from botocore.exceptions import ClientError
from django.conf import settings


def list_bucket_objects(bucket_name):
    '''List the objects in S3 bucket
    Example response:
    [{'Key': 'cats/cute_cat.jpg', 'LastModified': datetime(..), 'ETag': 'abc...', 'Size': 123, 'StorageClass': '...'}]
    '''

    if settings.ENV == "prod":
        s3 = boto3.client('s3')
    else:
        # TODO: Try to load developers key from env variables
        return None

    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
    except ClientError as e:
        # AllAccessDisabled error == bucket not found
        print(e)
        return None

    # Only return the contents if we found some keys
    if response['KeyCount'] > 0:
        return response['Contents']

    return None
