import json
import chromadb
from chromadb.utils import embedding_functions

# crate database
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# download multilingual model
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

# create table "collections" in database
collection = chroma_client.get_or_create_collection(
    name="iberian_conservation",
    embedding_function=sentence_transformer_ef
)

# load chunks
print("Lese chunks.json...")
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

documents = []
metadatas = []
ids = []

# formatting data for ChromaDB
for i, chunk in enumerate(chunks):
    documents.append(chunk["text"])
    metadatas.append({"source": chunk["source"], "page": chunk["page"]})
    ids.append(f"chunk_{i}")

# safe data in the databank
batch_size = 100
for i in range(0, len(documents), batch_size):
    print(f"Speichere Chunk {i} bis {i+batch_size}...")
    collection.add(
        documents=documents[i:i+batch_size],
        metadatas=metadatas[i:i+batch_size],
        ids=ids[i:i+batch_size]
    )

print("\nfinished :)")