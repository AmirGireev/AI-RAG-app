import chromadb
from chromadb.utils import embedding_functions

# connect to the database
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# load multilingual model
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

# Get collection from the database
collection = chroma_client.get_collection(
    name="iberian_conservation",
    embedding_function=sentence_transformer_ef
)

# Search function
def retrieve(question, k=3):
    print("\n==================================================")
    print(f"Question: '{question}'")
    print("==================================================")
    
    results = collection.query(
        query_texts=[question],
        n_results=k
    )
    
    # Print results
    for i in range(len(results['documents'][0])):
        text = results['documents'][0][i]
        source = results['metadatas'][0][i]['source']
        page = results['metadatas'][0][i]['page']

        print("\n---------------------------------------------------")
        print(f" Hit {i+1}: (source: {source}, page: {page}) ---")
        print(text[:300].strip() + "...")
        print("--------------------------------------------------")

# testing the system
retrieve("Does the Iberian Lynx have another name?")

retrieve("Wie wird der Iberische Luchs noch genannt?")