#Import Required Packages

import uuid
import os
from langchain_community.document_loaders import AzureAIDocumentIntelligenceLoader
#from langchain.text_splitter import TokenTextSplitter
from azure.ai.formrecognizer import DocumentAnalysisClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.config import *
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import dotenv
from openai import AzureOpenAI


dotenv.load_dotenv()

azure_client = AzureOpenAI(
  azure_endpoint = AZURE_OPENAI_ENDPOINT,
  api_key=AZURE_OPENAI_KEY,  
  api_version=AZURE_OPENAI_DEPLOYMENT_VERSION
)


#Chunking the text and convert to embeddings and dump to json
def chunk_text(file_path,index_name):
    #loader = AzureAIDocumentIntelligenceLoader(file_path = file_path, api_key = DOC_INTELLIGENCE_KEY, api_endpoint = DOC_INTELLIGENCE_ENDPOINT, api_model="prebuilt-layout")
    #documents =  loader.load()

    document_analysis_client = DocumentAnalysisClient(
        endpoint=DOC_INTELLIGENCE_ENDPOINT, credential=AzureKeyCredential(DOC_INTELLIGENCE_KEY)
    )
        
    poller = document_analysis_client.begin_analyze_document_from_url(
            "prebuilt-read", file_path)
    resumetxt = poller.result()

    documents = resumetxt.content
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
    documents =  text_splitter.split_text(documents)

    #Construct json
    docs = []
    i = 0
    file_name = os.path.basename(file_path).split('/')[-1]
    for doc in documents:
        print(f' Text files are chunked and send to embedding' + doc)
        docs.append({"documentId":file_name.replace('.','-')+'_'+str(i),"content":doc,"embedding":generate_embeddings(doc),"filepath":file_path})
        i= i+1

    search_client = SearchClient(endpoint=AZURE_SEARCH_SERVICE_ENDPOINT, index_name=index_name, credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY))
    result = search_client.upload_documents(docs)


# Function to generate embeddings for title and content fields, also used for query embeddings
#text-embedding-ada-002
def generate_embeddings(text_to_embed): 
    print(f' text to embed {text_to_embed} ')  
    text_to_embed = text_to_embed.replace("\n", " ")
    # Get the embeddings for the question
    response = azure_client.embeddings.create(input=[text_to_embed], model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME)
    # Extract the AI output embedding as a list of floats
    embedding = response.data[0].embedding
    print(f' embeddings are {embedding} created')
    return embedding

def upload(file_path,index_name):
    chunk_text(file_path,index_name)
    print(f' embedded documents are uploaded successfully')

