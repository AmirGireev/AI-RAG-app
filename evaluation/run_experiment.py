"""Step 9: chunk-size experiment.
Builds one temporary in-memory index per chunk size, runs your 25 evaluation
questions against each, and prints a Markdown table for your README.

Run:  python run_experiment.py        (takes a few minutes: it embeds everything 3x)
Needs: the PDFs in ./data and eval_set.py in the same folder.
"""
import os

import chromadb
import fitz
from chromadb.utils import embedding_functions

from eval_set import EVAL_SET

DATA_FOLDER = "data"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

CONFIGS = [(400, 75), (800, 150), (1200, 225)]
K_VALUES = [1, 3, 5]
MAX_K = max(K_VALUES)
BATCH_SIZE = 100


def load_pages():
    pages = []
    for filename in sorted(os.listdir(DATA_FOLDER)):
        if not filename.endswith(".pdf"):
            continue
        doc = fitz.open(os.path.join(DATA_FOLDER, filename))
        for page_num in range(len(doc)):
            text = doc.load_page(page_num).get_text()
            if text.strip():
                pages.append({"source": filename, "page": page_num + 1, "text": text})
        doc.close()
    return pages


def make_chunks(pages, size, overlap):
    chunks = []
    for p in pages:
        text = p["text"]
        for i in range(0, len(text), size - overlap):
            piece = text[i:i + size]
            if len(piece.strip()) > 50:
                chunks.append({"source": p["source"], "page": p["page"], "text": piece})
    return chunks


def build_collection(client, ef, name, chunks):
    col = client.create_collection(name=name, embedding_function=ef)
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start:start + BATCH_SIZE]
        col.add(
            documents=[c["text"] for c in batch],
            metadatas=[{"source": c["source"], "page": c["page"]} for c in batch],
            ids=[f"chunk_{start + j}" for j in range(len(batch))],
        )
    return col


def evaluate(col):
    questions = [item["question"] for item in EVAL_SET]
    res = col.query(query_texts=questions, n_results=MAX_K)
    ranks = []
    for item, metas in zip(EVAL_SET, res["metadatas"]):
        rank = None
        for r, m in enumerate(metas, start=1):
            if m["source"] == item["source"] and m["page"] in item["pages"]:
                rank = r
                break
        ranks.append(rank)
    return ranks


def hit_rate(ranks, k, idx=None):
    idx = range(len(ranks)) if idx is None else idx
    idx = list(idx)
    return sum(1 for i in idx if ranks[i] is not None and ranks[i] <= k) / len(idx)


def main():
    pages = load_pages()
    print(f"Loaded {len(pages)} pages from {DATA_FOLDER}/")

    client = chromadb.EphemeralClient() 
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)

    langs = sorted({item["lang"] for item in EVAL_SET})
    rows = []
    lang_rows = []
    for size, overlap in CONFIGS:
        chunks = make_chunks(pages, size, overlap)
        print(f"\nChunk size {size}: {len(chunks)} chunks -> embedding...")
        col = build_collection(client, ef, f"exp_{size}", chunks)
        ranks = evaluate(col)

        mrr = sum(1 / r for r in ranks if r is not None) / len(ranks)
        rows.append(
            f"| {size} | {overlap} | {len(chunks)} | "
            + " | ".join(f"{hit_rate(ranks, k):.0%}" for k in K_VALUES)
            + f" | {mrr:.3f} |"
        )
        per_lang = []
        for lang in langs:
            idx = [i for i, item in enumerate(EVAL_SET) if item["lang"] == lang]
            per_lang.append(f"{hit_rate(ranks, 3, idx):.0%}")
        lang_rows.append(f"| {size} | " + " | ".join(per_lang) + " |")

    header = "| Chunk size | Overlap | # chunks | " + " | ".join(f"Hit@{k}" for k in K_VALUES) + " | MRR@5 |"
    sep = "|" + "---|" * (3 + len(K_VALUES) + 1)
    table1 = "\n".join([header, sep] + rows)

    header2 = "| Chunk size | " + " | ".join(langs) + " |"
    sep2 = "|" + "---|" * (1 + len(langs))
    table2 = "\n".join([header2, sep2] + lang_rows)

    out = f"## Chunk size experiment ({len(EVAL_SET)} questions)\n\n{table1}\n\n### Hit@3 per question language\n\n{table2}\n"
    print("\n" + out)
    with open("results.md", "w", encoding="utf-8") as f:
        f.write(out)
    print("Saved to results.md")


if __name__ == "__main__":
    main()
