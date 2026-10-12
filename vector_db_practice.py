import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="./chroma_data")

collection = client.get_or_create_collection(
    name="study_notes"
)

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    local_files_only=True
)


docs = [
    "FastAPI uses Depends for dependency injection.",
    "SQLite uses PRAGMA foreign_keys = ON to enable foreign keys.",
    "Git merge combines branches."
]
ids = ["doc_001", "doc_002", "doc_003"]
embeddings = model.encode(docs).tolist()
collection.upsert(
    ids=ids,
    documents=docs,
    embeddings=embeddings,
    metadatas=[
        {"category":"fastapi"},
        {"category":"database"},
        {"category":"git"}
    ]
)

print("记录数量:",collection.count())


query = "How do I enable foreign keys in SQLite"

query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=2
)

for doc,distance in zip(
    results["documents"][0],
    results["distances"][0]
):
    print("文档：",doc)
    print("距离：",distance)
