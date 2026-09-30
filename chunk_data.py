import os
import json
import fitz  
import pymupdf 

# method
def chunk(text, size=800, overlap=150):
    return [text[i:i+size] for i in range(0, len(text), size - overlap)]

# read PDFs
pages = []
data_folder = "data"

for filename in os.listdir(data_folder):
    if filename.endswith(".pdf"):
        filepath = os.path.join(data_folder, filename)
        pdf_document = fitz.open(filepath)
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text()
            
            if text.strip():
                pages.append({
                    "source": filename,
                    "page": page_num + 1, 
                    "text": text
                })
        pdf_document.close()

# cut pdf text into chunks
chunks = []
for p in pages:
    for c in chunk(p["text"]):
        if len(c.strip()) > 50:
            chunks.append({
                "source": p["source"],
                "page": p["page"],
                "text": c
            })

# 4. Safe chunks to file
with open("chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)

print(f"finished :)")