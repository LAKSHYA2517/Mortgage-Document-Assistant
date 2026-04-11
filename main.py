import os
import shutil
import logging
from fastapi import FastAPI,UploadFile,File,HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
LLM_MODEL=os.getenv("LLM_MODEL", "llama3")
QUERY_TOP_K=int(os.getenv("QUERY_TOP_K", "2"))
LLM_TIMEOUT=float(os.getenv("LLM_TIMEOUT", "60"))

os.makedirs(UPLOAD_DIR,exist_ok=True)

#Global engine initialization
engine=None
retriever=None
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializing the connection to DB and local models when the server starts"""

    global engine, retriever
    print("Initializing RAG engine..")

    db=chromadb.PersistentClient(path=DB_PATH)
    chroma_collection=db.get_or_create_collection(COLLECTION_NAME)
    vector_store=ChromaVectorStore(chroma_collection=chroma_collection)

    #update for future----------------------------------------------------------
    embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
    index=VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model
    )
    retriever = index.as_retriever(similarity_top_k=QUERY_TOP_K)

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

    try:
        llm=Ollama(model=LLM_MODEL,request_timeout=LLM_TIMEOUT)
        engine = index.as_query_engine(
            llm=llm,
            similarity_top_k=QUERY_TOP_K,
            text_qa_template=qa_prompt_tmpl
        )
        print(f"RAG config -> model: {LLM_MODEL}, top_k: {QUERY_TOP_K}, timeout: {LLM_TIMEOUT}s")
        print("RAG engine initialized successfully!")
    except Exception as e:
        engine = None
        logger.exception("RAG engine initialization failed. The API will stay up, but /query is unavailable until Ollama is reachable.")
        print(
            "RAG engine is unavailable because Ollama is not reachable. "
            "Start Ollama and restart the API to enable /query."
        )

    yield
    print("Shutting down RAG engine...")

app=FastAPI(title="Mortgage Document Assistant",version="1.0",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#frontend endpoint
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        infer_table_structure=False,
        chunking_strategy="by_title",
        max_characters=3000
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
        raise HTTPException(
            status_code=503,
            detail="RAG engine unavailable: Ollama is not reachable. Start Ollama and restart the backend."
        )
        
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
        if "ReadTimeout" in f"{type(e).__name__}: {str(e)}" and retriever is not None:
            fallback_nodes = retriever.retrieve(request.question)
            sources = []
            source_names = []
            for node in fallback_nodes[:QUERY_TOP_K]:
                doc_name = node.metadata.get("source_file", "Unknown")
                sources.append(SourceNode(
                    text_snippet=node.text[:200] + "...",
                    doc_type=doc_name,
                    score=node.score or 0.0
                ))
                source_names.append(doc_name)

            best_excerpt = (
                fallback_nodes[0].text[:450] + "..."
                if fallback_nodes else
                "I cannot find this information in the provided documents."
            )
            fallback_answer = (
                "Model generation timed out. Returning best matched extracted context:\n\n"
                f"{best_excerpt}"
            )

            processing_time = (time.time() - start_time) * 1000
            db_log = models.AuditLog(
                user_query=request.question,
                ai_response=fallback_answer,
                sources_cited=", ".join(source_names),
                processing_time_ms=processing_time
            )
            db.add(db_log)
            db.commit()
            db.refresh(db_log)

            return QueryResponse(answer=fallback_answer, sources=sources)

        logger.exception("Query request failed")
        error_detail = f"{type(e).__name__}: {str(e) or 'Unknown error'}"
        raise HTTPException(status_code=500, detail=error_detail)