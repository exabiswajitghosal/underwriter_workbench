import zipfile

from langchain_community.document_loaders import S3DirectoryLoader, S3FileLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma
import os
import shutil
from dotenv import load_dotenv
import boto3

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
S3_bucket = os.getenv("AWS_UNDERWRITER_BUCKET")


def download_directory_from_s3(bucket_name, prefix, local_dir):
    s3 = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    # Ensure the local directory exists
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)

    # List objects in the specified S3 bucket with the given prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if 'Contents' not in response:
        print("No files found.")
        return

    for obj in response['Contents']:
        key = obj['Key']
        # Remove the prefix from the key to get the relative path
        relative_path = os.path.relpath(key, prefix)
        local_file_path = os.path.join(local_dir, relative_path)
        local_file_dir = os.path.dirname(local_file_path)

        # Ensure the local directory for the file exists
        if not os.path.exists(local_file_dir):
            os.makedirs(local_file_dir)

        print(f"Downloading {key} to {local_file_path}...")

        # Download the file
        s3.download_file(bucket_name, key, local_file_path)

        # If the file is a zip file, extract it
        if local_file_path.endswith('.zip'):
            with zipfile.ZipFile(local_file_path, 'r') as zip_ref:
                zip_ref.extractall(local_file_dir)
            os.remove(local_file_path)  # Remove the zip file after extraction
            print(f"Extracted {key} to {local_file_dir}")


def load_documents(submission_id=None):
    try:
        # local_dir = './archive/temp'
        # download_directory_from_s3(bucket_name=S3_bucket, prefix=submission_id, local_dir=local_dir)
        # loader = DirectoryLoader(path=local_dir)
        # chroma_path = f"chroma/{submission_id}"
        # # Clear out the database first.
        # if os.path.exists(chroma_path):
        #     return
        loader = S3DirectoryLoader(S3_bucket, prefix="input/"+submission_id)
        documents = loader.load()
        return documents
    except Exception as e:
        print("Unable to load documents.", e)
        return []


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=5000,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)

    return chunks


def save_to_chroma(chunks: list[Document], submission_id=None):
    chroma_path = f"chroma/{submission_id}"
    # Clear out the database first.
    # if os.path.exists(chroma_path):
    #     shutil.rmtree(chroma_path)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY), persist_directory=chroma_path
    )
    db.persist()


def generate_data_store(submission_id=None):
    try:
        documents = load_documents(submission_id=submission_id)
        if not documents:
            return True
        chunks = split_text(documents=documents)
        save_to_chroma(chunks=chunks, submission_id=submission_id)
        return True
    except Exception as e:
        print("Unable to generate the data store.", e)
        return False
