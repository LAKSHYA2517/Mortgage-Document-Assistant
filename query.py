import chromadb 
from llama_index.core import VectorStoreIndex,PromptTemplate
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama

DB_PATH="./chroma_db"
COLLECTION_NAME="mortages_docs"

def setup_query_engine():
    print("Connecting to chromaDB..")
    db=chromadb.PersistentClient(path=DB_PATH)
    chroma_collection=db.get_or_create_collection(COLLECTION_NAME)
    vector_store=ChromaVectorStore(chroma_collection=chroma_collection)

    print("Loading local embeddings models")
    embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    print("Loading Local LLM via Ollama(Llama 3)..")
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

    query_engine = index.as_query_engine(
        llm=llm,
        similarity_top_k=5, 
        text_qa_template=qa_prompt_tmpl
    )
    
    return query_engine

if __name__ == "__main__":
    engine = setup_query_engine()
    
    # 3. Interactive Loop
    print("\n" + "="*50)
    print("Mortgage Intelligence System Initialized.")
    print("Type 'exit' to quit.")
    print("="*50 + "\n")
    
    while True:
        user_query = input("\nUnderwriter Question: ")
        if user_query.lower() in ['exit', 'quit']:
            break
            
        print("Searching documents and generating answer...\n")
        response = engine.query(user_query)
        
        print(f"System Answer: {response}\n")
        
        # Optional: Print the sources to verify accuracy
        print("--- Sources Used ---")
        for i, node in enumerate(response.source_nodes):
            print(f"Source {i+1} (Score: {node.score:.3f}): {node.metadata.get('doc_type', 'Unknown Doc')} - {node.text[:100]}...")