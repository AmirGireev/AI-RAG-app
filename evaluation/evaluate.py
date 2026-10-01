import chromadb
from chromadb.utils import embedding_functions

from eval_set import EVAL_SET  # the 25 questions live in eval_set.py

K_VALUES = [1, 3, 5]
MAX_K = max(K_VALUES)

# connect to database
chroma_client = chromadb.PersistentClient(path="./chroma_db")
ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)
collection = chroma_client.get_collection(
    name="iberian_conservation", embedding_function=ef
)


def find_rank(item):
    """Returns the rank (1-based) of the first correct chunk, or None."""
    res = collection.query(query_texts=[item["question"]], n_results=MAX_K)
    for rank, meta in enumerate(res["metadatas"][0], start=1):
        if meta["source"] == item["source"] and meta["page"] in item["pages"]:
            return rank
    return None


ranks = [find_rank(item) for item in EVAL_SET]
n = len(EVAL_SET)

print(f"\nEvaluated {n} questions\n")
for k in K_VALUES:
    hits = sum(1 for r in ranks if r is not None and r <= k)
    print(f"Hit rate@{k}: {hits}/{n} = {hits / n:.2%}")

mrr = sum(1 / r for r in ranks if r is not None) / n
print(f"MRR@{MAX_K}: {mrr:.3f}")

# --- breakdown per language ---
print("\nPer language (hit rate@3):")
for lang in sorted({item["lang"] for item in EVAL_SET}):
    idx = [i for i, item in enumerate(EVAL_SET) if item["lang"] == lang]
    hits = sum(1 for i in idx if ranks[i] is not None and ranks[i] <= 3)
    print(f"  {lang}: {hits}/{len(idx)} = {hits / len(idx):.2%}")

# --- show the failures: this is where you learn the most ---
print("\nMissed (not in top 5):")
for item, r in zip(EVAL_SET, ranks):
    if r is None:
        print(f"  - [{item['lang']}] {item['question']}")
