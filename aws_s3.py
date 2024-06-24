import os
import boto3
from dotenv import load_dotenv

load_dotenv()

# Retrieve AWS credentials and region from environment variables
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
bucket_name = os.getenv('AWS_UNDERWRITER_BUCKET')

# Create a session using your AWS credentials
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)
s3_client = session.client('s3')


def upload_file_to_s3(submission_id=None, filename=None, content=None):
    try:
        # file = f"./static/uploads/{submission_id}_input.xlsx"
        # s3_client.upload_file(file, AWS_UNDERWRITER_BUCKET, f'{submission_id}_input.xlsx')
        response = s3_client.put_object(Bucket=bucket_name, Key=f"input/{submission_id}/{filename}",
                                        Body=content)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        url = f"https://{bucket_name}.s3.amazonaws.com/{submission_id}/{filename}"
        if status == 200:
            return url
        return None
    except Exception as e:
        print(e)
        return False


def list_folders():
    # List objects in the bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='input/', Delimiter='/')
    # Check if the response contains CommonPrefixes which denotes the folders
    if 'CommonPrefixes' in response:
        folders = [prefix['Prefix'] for prefix in response['CommonPrefixes']]
        # Remove the 'input/' prefix from folder names
        folders = [folder.replace('input/', '').replace('/', '') for folder in folders]
        return folders
    else:
        return []


def list_files_in_folder(submission_id=None):
    # List objects in the specified folder within the "input" directory of the bucket
    prefix = f'input/{submission_id}/'
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    # Check if the response contains Contents which denotes the files
    if 'Contents' in response:
        files = [content['Key'] for content in response['Contents']]
        # Remove the 'input/{folder_name}/' prefix from file names
        files = [file.replace(prefix, '') for file in files]
        return files
    else:
        return []
