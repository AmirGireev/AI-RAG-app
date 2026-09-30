import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# connect to the database
chroma_client = chromadb.PersistentClient(path="./chroma_db")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
collection = chroma_client.get_collection(
    name="iberian_conservation",
    embedding_function=sentence_transformer_ef
)

def ask_iberian_assistant(question):
    print(f"Searching...")
    
    results = collection.query(query_texts=[question], n_results=3)
    
    context_text = ""
    for i in range(len(results['documents'][0])):
        text = results['documents'][0][i]
        source = results['metadatas'][0][i]['source']
        page = results['metadatas'][0][i]['page']
        
        context_text += f"\nSource: {source} (Page: {page}) ---\n{text}\n"
    
    # Telling the AI model to answer based on tose statements
    system_prompt = (
                "Answer the question using ONLY the context below. "
                "If the answer is in the context, cite the source file and page for each claim. "
                "If the answer isn't in the context, say you don't know and DO NOT include any sources or citations. "
                "You MUST answer in the EXACT SAME language as the user's QUESTION."
            )
    
    user_prompt = f"CONTEXT:\n{context_text}\n\nQUESTION: {question}"
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b", 
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0 
    )
    
    answer = response.choices[0].message.content
    
    print("\n==================================================")
    print(f"Question: {question}")
    print("--------------------------------------------------")
    print(f"Answer:\n{answer}")
    print("==================================================\n")

ask_iberian_assistant("What are the main threats to the Iberian wolf?")
ask_iberian_assistant("Wie wird der Iberische Luchs geschützt?")
ask_iberian_assistant("What is 10x10?")