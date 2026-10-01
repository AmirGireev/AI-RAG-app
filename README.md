# Iberian Wildlife Assistant

An AI assistant using a RAG pipeline. The interactive Streamlit web app searches official Spanish, Portuguese and English documents about Iberian wildlife and uses a large language model to answer user questions.

**Live demo:** [amirgireevragapp.streamlit.app](https://amirgireevragapp.streamlit.app/)

## How it works

Built with Python, PyMuPDF, sentence-transformers, ChromaDB, Streamlit and the Groq API.

The prompt tells the model to answer only from the retrieved text and to cite the file and page. It answers "I don't know" if the answer is missing, and it replies in the language of the question.

## Results

Retrieval was tested on 25 questions (English, Spanish, Portuguese, German) with a known correct page. A question counts as a hit if the correct page is among the top k results. The evaluation scripts are in the `evaluation/` folder.

| Chunk size | Hit@1 | Hit@3 | Hit@5 |
|---|---|---|---|
| 400 | 40% | 64% | 72% |
| 800 | 36% | 64% | 68% |
| 1200 | 28% | 60% | 64% |


- Chunks of 400 and 800 characters perform about the same. 1200 is slightly worse. I use 800 now.
- English and Portuguese questions work best (80% Hit@3), Spanish is weaker (50%). One large Spanish document makes up 43% of all chunks and often crowds out the right answer.
- 5 of the 8 failed questions had the correct page at rank 6-9.
