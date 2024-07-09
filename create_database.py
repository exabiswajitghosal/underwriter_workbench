from langchain_community.document_loaders import S3DirectoryLoader, S3FileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma
import os
import shutil
from dotenv import load_dotenv
import boto3

from aws_s3 import check_document_exists

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
S3_bucket = os.getenv("AWS_UNDERWRITER_BUCKET")
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_REGION')
session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)
s3_client = session.client('s3')


def load_documents(submission_id, file_name):
    try:
        document_exist = check_document_exists(S3_bucket=S3_bucket, prefix="input/"+submission_id, key=file_name)
        if not document_exist:
            return None
        # loader = S3DirectoryLoader(bucket=S3_bucket, prefix="input/"+submission_id)
        file_path = "input/"+submission_id+"/"+file_name
        loader = S3FileLoader(bucket=S3_bucket, key=file_path)
        documents = loader.load()
        return documents

        # file_object = s3_client.get_object(Bucket=S3_bucket, Key="input/"+submission_id+"/"+file_name)
        # file_content = file_object['Body'].read()
        # print(file_content)
        # return file_content
    except Exception as e:
        print("Unable to load documents.", e)
        return None


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=5000,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)

    return chunks


def save_to_chroma(chunks: list[Document], submission_id, file_name):
    file = file_name.split(".")[0]
    chroma_path = f"chroma/{submission_id}/{file}"
    # Clear out the database first.
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY), persist_directory=chroma_path
    )
    db.persist()


def generate_data_store(submission_id, file_name):
    try:
        documents = load_documents(submission_id=submission_id, file_name=file_name)
        if not documents:
            return False
        chunks = split_text(documents=documents)
        save_to_chroma(chunks=chunks, submission_id=submission_id, file_name=file_name)
        return True
    except Exception as e:
        print("Unable to generate the data store.", e)
        return False
