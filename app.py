import os
import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

# Website Design
st.set_page_config(
    page_title="Iberian Wildlife AI", 
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("<h1 style='text-align: center;'>Iberian Wildlife Assistant</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: gray;'>Ask questions about Iberian wildlife and get answers based on the provided documents.</p>", 
    unsafe_allow_html=True
)
st.divider()

# Load Backend Services
@st.cache_resource
def init_system():
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    collection = chroma_client.get_collection(
        name="iberian_conservation",
        embedding_function=sentence_transformer_ef
    )
    return client, collection

client, collection = init_system()

with st.form(key="query_form"):
    question = st.text_input(
        "Your Question:", 
        placeholder="What are the main threats to the Iberian Lynx?"
    )
    submit_button = st.form_submit_button("Ask")

if submit_button:
    if question.strip():
        with st.spinner("Searching the database and analyzing documents..."):
            
            results = collection.query(query_texts=[question], n_results=3)
            
            context_text = ""
            for i in range(len(results['documents'][0])):
                text = results['documents'][0][i]
                source = results['metadatas'][0][i]['source']
                page = results['metadatas'][0][i]['page']
                context_text += f"\n Source: {source} (Page: {page}) ---\n{text}\n"


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

            st.info(answer)
  
            with st.expander("context"):
                st.markdown(context_text)