import json
import os
import boto3
from langchain_community.vectorstores.chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from datetime import datetime

from create_database import generate_data_store

load_dotenv()

openai_api = os.getenv("OPENAI_API_KEY")
aws_bucket = os.getenv("AWS_UNDERWRITER_BUCKET")
aws_secret = os.getenv("AWS_SECRET_ACCESS_KEY")
aws_access = os.getenv("AWS_ACCESS_KEY_ID")
s3 = boto3.client('s3', aws_access_key_id=aws_access, aws_secret_access_key=aws_secret)

PROMPT_TEMPLATE = """
Answer the question based only on the following context don't give reference:
{context}
---
Answer the question based on the above context : {question}
"""


def generate_content_from_documents(submission_id, file_name):

    response = generate_data_store(submission_id=submission_id, file_name=file_name)
    if not response:
        return None
    file_name = file_name.split('.')[0]
    query_text = '''extract all the details in json format '''
    chroma_path = f"./chroma/{submission_id}/{file_name}"
    # Prepare the DB.
    embedding_function = OpenAIEmbeddings(openai_api_key=openai_api)
    db = Chroma(persist_directory=chroma_path, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.5:
        return None
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    model = ChatOpenAI(model="gpt-4o")
    response_text = model.predict(prompt)
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    if not response_text:
        return None
    formatted_source = []
    for source in sources:
        url = "/".join(source.split("/")[3:])
        formatted_url = f"https://{aws_bucket}.s3.amazonaws.com/{url}"
        if formatted_url not in formatted_source:
            formatted_source.append(formatted_url)

    s3.put_object(Bucket=aws_bucket, Key=f"{submission_id}/output/{file_name}_output.json", Body=response_text)
    url = f"https://{aws_bucket}.s3.amazonaws.com/{submission_id}/output/{file_name}_output.json"
    formatted_response = json.dumps({
        "response": response_text,
        "sources": formatted_source,
        "date": datetime.now().date().strftime("%Y-%m-%d"),
        "url": url
    })
    if response_text is not None:
        return formatted_response
    return None
