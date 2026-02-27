import os
from unstructured.partition.pdf import partition_pdf
from llama_index.core import Document,VectorStoreIndex,StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

FILE_PATH="closing_disclosure.pdf"
DB_PATH="./chroma_db"
COLLECTION_NAME="mortage_docs"

def extract_and_parse_document(file_path):
    print(f"Parsing {file_path} using Unstructured (may take a moment as it is detecting tables)....")

    elements=partition_pdf(
        filename=file_path,
        strategy="hi-res",
        infer_table_structure=True,
        chunking_strategy="by_title",
        max_character=1500
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

    print(f"Extracted {len(llama_docs)} semantic chunks")

def build_vector_database(documents):
    print("Initializing local HuggingFace Embeddings...")
    embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    print("Setting up chromaDB...")
    db=chromadb.PersistentClient(path=DB_PATH)
    chroma_collection=db.get_or_create_collection(COLLECTION_NAME)

    vector_store=ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context=StorageContext.from_defaults(vector_store=vector_store)

    print("Embedding document saving to Vector DB")

    index=VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        show_progress=True
    )

    print("Ingestion completed. Database is Ready")

if __name__ =="__main__":
    if not os.path.exists(FILE_PATH):
        print(f"Error: Please place a sample PDF named '{FILE_PATH} in the directory.'")
    else:
        parsed_docs=extract_and_parse_document(FILE_PATH)
        index=build_vector_database(parsed_docs)