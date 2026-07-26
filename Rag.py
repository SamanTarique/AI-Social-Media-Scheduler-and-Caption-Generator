import os
import glob
import hashlib
import pandas as pd
from Knowladge_loader import load_knowledge, KB_FOLDER
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FAISS_FOLDER = os.path.join(SCRIPT_DIR, "faiss_index")
HASH_FILE = os.path.join(FAISS_FOLDER, "db_hash.txt")

_cache: dict = {}  


def calculate_folder_hash(folder_path: str = KB_FOLDER) -> str:
    files = sorted(glob.glob(os.path.join(folder_path, "*.csv")) + glob.glob(os.path.join(folder_path, "*.md")))
    if not files:
        raise FileNotFoundError(f"No CSV or Markdown files found inside {folder_path}.")

    hasher = hashlib.md5()
    for path in files:
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
    return hasher.hexdigest()


def build_csv_documents(csv_tables: dict) -> list[str]:
    docs = []
    for name, df in csv_tables.items():
        for _, row in df.iterrows():
            lines = [f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])]
            docs.append(f"[Source: {name}]\n" + "\n".join(lines))
    return docs


def get_mandatory_context(csv_tables: dict, md_data: list[str]) -> str:
    parts = []

    if "hashtags.csv" in csv_tables:
        df = csv_tables["hashtags.csv"]
        always = df[df["category"].astype(str).str.contains("always include", case=False, na=False)]
        if not always.empty:
            parts.append("MANDATORY hashtag(s) -- include on every post: " + ", ".join(always["hashtag"]))

    for doc in md_data:
        if "Universal Rules" in doc:
            start = doc.find("## Universal Rules")
            end = doc.find("##", start + 5)
            parts.append(doc[start:end if end != -1 else start + 800].strip())
            break

    return "\n\n".join(parts)


def get_vector_db():
    current_hash = calculate_folder_hash()

    if _cache.get("db_hash") == current_hash:
        return _cache["db"] 

    if os.path.exists(HASH_FILE) and open(HASH_FILE).read().strip() == current_hash:
        print(" No changes detected. Loading existing FAISS Database...")
        db = FAISS.load_local(FAISS_FOLDER, embedding_model, allow_dangerous_deserialization=True)
    else:
        print(" Knowledge Base changed. Creating fresh Vector Database...")
        csv_tables, md_data = load_knowledge()
        all_docs = build_csv_documents(csv_tables) + md_data
        chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).create_documents(all_docs)
        db = FAISS.from_documents(chunks, embedding_model)
        os.makedirs(FAISS_FOLDER, exist_ok=True)
        db.save_local(FAISS_FOLDER)
        with open(HASH_FILE, "w") as f:
            f.write(current_hash)
        print("New FAISS Database Created Successfully.")

    _cache["db"], _cache["db_hash"] = db, current_hash
    return db


def get_knowledge():
    current_hash = calculate_folder_hash()

    if _cache.get("kb_hash") != current_hash:
        csv_tables, md_data = load_knowledge()
        _cache["kb"] = (csv_tables, md_data)
        _cache["mandatory"] = get_mandatory_context(csv_tables, md_data)
        _cache["kb_hash"] = current_hash

    return _cache["kb"], _cache["mandatory"]


def search_knowledge(query: str, k: int = 6):
    docs = get_vector_db().similarity_search(query, k=k)
    _, mandatory_text = get_knowledge()
    return ([Document(page_content=mandatory_text)] if mandatory_text else []) + docs


if __name__ == "__main__":
    get_vector_db()
    print("\nSystem Ready\n")

    while True:
        query = input("Ask Something (exit to quit): ")
        if query.lower() == "exit":
            break
        for i, doc in enumerate(search_knowledge(query), start=1):
            print(f"========== Result {i} ==========\n{doc.page_content}\n")