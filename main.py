import os
import shutil
from fastapi import FastAPI,UploadFile,File,HTTPException
from pydantic import BaseModel
import chromadb
from llama_index.core import VectorStoreIndex,PromptTemplate,Document,StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from unstructured.partition.pdf import partition_pdf
from contextlib import asynccontextmanager
from fastapi import Depends
from sqlalchemy.orm import Session
import time
import models
from database import engine, get_db

# Create the database tables automatically on startup
models.Base.metadata.create_all(bind=engine)

DB_PATH="./chroma_db"
COLLECTION_NAME="mortgage_docs"
UPLOAD_DIR="./temp_upload"

os.makedirs(UPLOAD_DIR,exist_ok=True)

#Global engine initialization
engine=None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializing the connection to DB and local models when the server starts"""

    global engine
    print("Initializing RAG engine..")

    db=chromadb.PersistentClient(path=DB_PATH)
    chroma_collection=db.get_or_create_collection(COLLECTION_NAME)
    vector_store=ChromaVectorStore(chroma_collection=chroma_collection)

    #update for future----------------------------------------------------------
    embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    llm=Ollama(model="llama3",request_timeout=120.0)

    index=VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model
    )

    qa_prompt_tmpl_str = (
        "You are an expert mortgage underwriting assistant for Outamation.\n"
        "Context information is below.\n"
        "---------------------\n"
        "{context_str}\n"
        "---------------------\n"
        "Given the context information and strictly no prior knowledge, "
        "answer the query. If the answer is not in the context, output exactly: "
        "'I cannot find this information in the provided documents.' Do not guess.\n"
        "Query: {query_str}\n"
        "Answer: "
    )

    qa_prompt_tmpl=PromptTemplate(qa_prompt_tmpl_str)

    engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=5, 
        text_qa_template=qa_prompt_tmpl
    )
    
    print("RAG engine initialized successfully!")
    yield
    print("Shutting down RAG engine...")

app=FastAPI(title="Mortgage Document Assistant",version="1.0",lifespan=lifespan)

#pydantic models
class QueryRequest(BaseModel):
    question:str
class SourceNode(BaseModel):
    text_snippet: str
    doc_type: str
    score: float
class QueryResponse(BaseModel):
    answer:str
    sources:list[SourceNode]

#endpoints
@app.get("/")
def health_check():
    return {
        "message":"Mortagage Assistance system",
        "version":"1.0"
    }

@app.post("/upload")
async def upload_document(file:UploadFile=File(...)):
    """Ingest a pdf,parse tabel and text and adds to chromaDB"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400,detail="Only PDF files are allowed")
    
    file_path=os.path.join(UPLOAD_DIR,file.filename)

    #saving uploaded file temporary
    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)
    
    try:
        elements=partition_pdf(
        filename=file_path,
        strategy="fast",#changed from hi_res
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_characters=1500
        )
    
        llama_docs=[]

        for element in elements:
            text=element.text
            
            metadata={
                "source_file":os.path.basename(file_path),
                "doc_type":"closing Disclosure",#change during production
                "element_type":type(element).__name__
            }

            #check if table
            if hasattr(element.metadata,"text_as_html") and element.metadata.text_as_html:
                text=f"TABLE_CONTENT:\n{element.metadata.text_as_html}"
                metadata["is_table"]=True
            
            llama_docs.append(Document(text=text,metadata=metadata))

        db=chromadb.PersistentClient(path=DB_PATH)
        chroma_collection=db.get_or_create_collection(COLLECTION_NAME)
        vector_store=ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context=StorageContext.from_defaults(vector_store=vector_store)
        embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

        VectorStoreIndex.from_documents(
            llama_docs,
            storage_context=storage_context,
            embed_model=embed_model
        )

        return{
            "status":"Success",
            "messages":f"Ingested {len(llama_docs)} chunks from {file.filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest, db: Session = Depends(get_db)):
    """Answers underwriter questions and logs the transaction for compliance."""
    if not engine: # referring to your global RAG engine from earlier
        raise HTTPException(status_code=500, detail="Engine not initialized.")
        
    start_time = time.time()
        
    try:
        # 1. Get the RAG response
        response = engine.query(request.question)
        
        # 2. Extract sources
        sources = []
        source_names = []
        for node in response.source_nodes:
            doc_name = node.metadata.get("source_file", "Unknown")
            sources.append(SourceNode(
                text_snippet=node.text[:200] + "...",
                doc_type=doc_name,
                score=node.score or 0.0
            ))
            source_names.append(doc_name)
            
        processing_time = (time.time() - start_time) * 1000
            
        # 3. Save to Compliance Audit Log
        db_log = models.AuditLog(
            user_query=request.question,
            ai_response=str(response),
            sources_cited=", ".join(source_names),
            processing_time_ms=processing_time
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)
            
        return QueryResponse(answer=str(response), sources=sources)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))