
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    local_files_only=True
)

docs = [
    "FastAPI uses Depends for dependency injection.",
    "SQLite uses PRAGMA foreign_keys = ON to enable foreign keys.",
    "Git merge combines branches."
]

query = "How do I enable foreign keys in SQLite?"

doc_embeddings = model.encode(docs)

def search(query,docs,k=2,threshold=0.5):

    query_embedding = model.encode(query)

    scores = cos_sim(query_embedding,doc_embeddings)

    top_scores,top_indices = scores.topk(k=min(k,len(docs)))

    results = []

    for score,index in zip(top_scores[0],top_indices[0]):
        score_value = score.item()
        index_value = index.item()
        
        if score_value > threshold:
            results.append({
                "text":docs[index_value],
                "score":score_value
            })

    return results