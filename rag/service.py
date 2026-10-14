import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

_model = None

client = chromadb.PersistentClient(path="./chroma_data")

collection = client.get_or_create_collection(
    name="rag_study_notes",
    configuration={"hnsw":{"space":"cosine"}}
)

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            local_files_only=True
        )
    return _model

def load_markdown(file_path):
    return Path(file_path).read_text(encoding="utf-8")

def split_markdown(text):
    chunks = []
    current_chunk = []

    for line in text.splitlines():

        if line.startswith(("# ","## ","### ")):
            if current_chunk:
                chunks.append("\n".join(current_chunk).strip())
                current_chunk = []
            current_chunk.append(line)
            continue

        current_chunk.append(line)

    if current_chunk:
        chunks.append("\n".join(current_chunk).strip())

    return chunks