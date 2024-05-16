import streamlit as st
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders.pdf import UnstructuredPDFLoader
from langchain_community.document_loaders.image import UnstructuredImageLoader
from langchain_community.document_loaders import ImageCaptionLoader
from langchain_community.docstore.document import Document
import os
import openai
from dotenv import load_dotenv
load_dotenv()

# Chat UI title
st.header("Upload your own files and ask questions like ChatGPT")
st.subheader('File types supported: IMG/PDF/DOCX/TXT')

# File uploader in the sidebar on the left
with st.sidebar:
    # Input for OpenAI API Key
    openai_api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY"))

    # Check if OpenAI API Key is provided
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # Set OPENAI_API_KEY as an environment variable
    os.environ["OPENAI_API_KEY"] = openai_api_key

# Initialize ChatOpenAI model
llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k", streaming=True)


# Load version history from the text file
def load_version_history():
    with open("version_history.txt", "r") as file:
        return file.read()


# Sidebar section for uploading files and providing a YouTube URL
with st.sidebar:
    uploaded_files = st.file_uploader("Please upload your files", accept_multiple_files=True, type=None)
    # youtube_url = st.text_input("YouTube URL")

    # Create an expander for the version history in the sidebar
    # with st.sidebar.expander("**Version History**", expanded=False):
    # st.write(load_version_history())

    st.info("Please refresh the browser if you decide to upload more files to reset the session", icon="🚨")

if uploaded_files:
    # Print the number of files uploaded or YouTube URL provided to the console
    st.write(f"Number of files uploaded: {len(uploaded_files)}")

    # Load the data and perform preprocessing only if it hasn't been loaded before
    if "processed_data" not in st.session_state:
        if uploaded_files:
            # Load the data from uploaded files
            documents = []
            for uploaded_file in uploaded_files:
                # Get the full file path of the uploaded file
                file_path = os.path.join(os.getcwd() + "/archive/uploaded_file")
                if not os.path.exists(file_path):
                    # os.rmdir(file_path)
                    os.mkdir(file_path)
                file_path += "/" + uploaded_file.name
                if os.path.exists(file_path):
                    os.remove(file_path)
                # Save the uploaded file to disk
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                # Check if the file is an image
                if file_path.endswith((".png", ".jpg")):
                    # Use ImageCaptionLoader to load the image file
                    # image_loader = ImageCaptionLoader(images=file_path)
                    image_loader = UnstructuredFileLoader(file_path=file_path)
                    # Load image captions
                    image_documents = image_loader.load()

                    # Append the Langchain documents to the documents list
                    documents.extend(image_documents)

                elif file_path.endswith((".pdf", ".docx", ".txt")):
                    # Use UnstructuredFileLoader to load the PDF/DOCX/TXT file
                    if file_path.endswith(".pdf"):
                        loader = UnstructuredPDFLoader(file_path)
                    else:
                        loader = UnstructuredFileLoader(file_path)
                    loaded_documents = loader.load()
                    # Extend the main documents list with the loaded documents
                    documents.extend(loaded_documents)

                # Chunk the data, create embeddings, and save in vectorstore
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=150)
                document_chunks = text_splitter.split_documents(documents)

                embeddings = OpenAIEmbeddings()
                vectorstore = Chroma.from_documents(document_chunks, embeddings)

                # Store the processed data in session state for reuse
                st.session_state.processed_data = {
                    "document_chunks": document_chunks,
                    "vectorstore": vectorstore,
                }

    else:
        # If the processed data is already available, retrieve it from session state
        document_chunks = st.session_state.processed_data["document_chunks"]
        vectorstore = st.session_state.processed_data["vectorstore"]

    # Initialize Langchain's QA Chain with the vectorstore
    qa = ConversationalRetrievalChain.from_llm(llm, vectorstore.as_retriever())

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask your questions?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Query the assistant using the latest chat history
        result = qa({"question": prompt,
                     "chat_history": [(message["role"], message["content"]) for message in st.session_state.messages]})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = result["answer"]
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
        print(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

else:
    st.write("Please upload your files")
