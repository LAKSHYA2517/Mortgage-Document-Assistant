import os
import shutil
from fastapi import FastAPI,UploadFile,File,HTTPException
from pydantic import BaseModel
import chromadb
from llama_index.core import VectorStoreIndex,PromptTemplate,Document,StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from unstructured.partition.pdf import partition_pdf

DB_PATH="./chroma_db"
COLLECTION_NAME="mortgage_docs"
UPLOAD_DIR="./temp_upload"

os.makedirs(UPLOAD_DIR,exist_ok=True)

app=FastAPI(title="Mortgage Document Assistant",version="1.0")

