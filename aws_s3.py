import os
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

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
        folders_list = []
        for submission_id in folders:
            input_files = list_files_in_folder(submission_id=submission_id)
            for files in input_files:
                folders_list.append(files)
        return folders_list
    else:
        return []


def list_files_in_folder(submission_id=None):
    # List objects in the specified folder within the "input" directory of the bucket
    prefix = f'input/{submission_id}/'
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    # Check if the response contains Contents which denotes the files
    if 'Contents' in response:
        files_list = []
        for content in response['Contents']:
            filename = content['Key'].replace(prefix, '')
            url = f'https://{bucket_name}.s3.amazonaws.com/{content["Key"]}'
            last_modified = content['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
            file_details = {
                "submission_id": submission_id,
                "file_name": filename,
                "url": url,
                "last_modified": last_modified
            }
            files_list.append(file_details)
        return files_list
    else:
        return []


def check_document_exists(S3_bucket, prefix, key):
    s3 = boto3.client('s3')
    full_key = f"{prefix}/{key}"
    try:
        s3.head_object(Bucket=S3_bucket, Key=full_key)
        print(f"Document exists: {S3_bucket}/{full_key}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Document not found: {S3_bucket}/{full_key}")
        else:
            print("An error occurred:", e.response['Error']['Message'])
        return False
