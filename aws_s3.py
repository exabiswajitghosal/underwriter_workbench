import os
import boto3
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
AWS_UNDERWRITER_BUCKET = os.getenv("AWS_UNDERWRITER_BUCKET")
AWS_ACCESS_KEY_ID = os.getenv("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = os.getenv("aws_secret_access_key")
# AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    # aws_session_token=AWS_SESSION_TOKEN,
)


def upload_file_to_s3(submission_id=None, filename=None, content=None):
    try:
        # file = f"./static/uploads/{submission_id}_input.xlsx"
        # s3_client.upload_file(file, AWS_UNDERWRITER_BUCKET, f'{submission_id}_input.xlsx')
        response = s3_client.put_object(Bucket=AWS_UNDERWRITER_BUCKET, Key=f"input/{submission_id}/{filename}",
                                        Body=content)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        url = f"https://{AWS_UNDERWRITER_BUCKET}.s3.amazonaws.com/{submission_id}/{filename}"
        if status == 200:
            return url
        return None
    except Exception as e:
        print(e)
        return False
