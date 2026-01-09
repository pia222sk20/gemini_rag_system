import os
import hashlib
import json
from typing import List, Dict, Any
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.vectorstore import get_vectorstore

DOC_DIR = os.path.join(os.getcwd(), "DOC")
CACHE_FILE = os.path.join(os.getcwd(), "file_cache.json")

class FileHashCache:
    def __init__(self, cache_file: str):
        self.cache_file = cache_file
        self.cache = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_cache(self):
        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(self.cache, f, indent=4, ensure_ascii=False)

    def get_file_hash(self, filepath: str) -> str:
        """Calculate SHA256 hash of a file."""
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def is_modified(self, filepath: str) -> bool:
        """Check if file is modified based on hash."""
        filename = os.path.basename(filepath)
        if filename not in self.cache:
            return True
        
        current_hash = self.get_file_hash(filepath)
        return self.cache[filename]["hash"] != current_hash

    def update_cache(self, filepath: str):
        """Update cache with current file hash."""
        filename = os.path.basename(filepath)
        self.cache[filename] = {
            "hash": self.get_file_hash(filepath),
            "last_modified": os.path.getmtime(filepath)
        }
        self._save_cache()

    def remove_from_cache(self, filename: str):
        """Remove file from cache."""
        if filename in self.cache:
            del self.cache[filename]
            self._save_cache()
    
    def get_cached_files(self) -> List[str]:
        return list(self.cache.keys())

def _remove_from_vectorstore(filename: str):
    """
    Remove documents from vectorstore that match the source filename.
    """
    vectorstore = get_vectorstore()
    # Assuming the 'source' metadata contains the absolute path.
    # We will search for documents where 'source' ends with the filename.
    # Note: Chroma's filter capability is somewhat limited, but we can try exact match if we construct the path carefully.
    
    # Since we don't have a direct "delete by metadata partial match" in standard simple interfaces easily,
    # we might need to rely on the fact that we know the full path if it was ingested correctly.
    full_path = os.path.join(DOC_DIR, filename)
    
    # Try to delete by 'source' metadata
    try:
        # Chroma specific delete
        vectorstore._collection.delete(where={"source": full_path})
        print(f"Deleted documents for {filename} from vectorstore.")
    except Exception as e:
        print(f"Error deleting {filename} from vectorstore: {e}")

def ingest_documents():
    """
    Syncs DOC folder with Vector Store:
    1. Ingests new or modified files.
    2. Removes deletions from Vector Store.
    3. Updates Cache.
    """
    if not os.path.exists(DOC_DIR):
        os.makedirs(DOC_DIR)
        return {"status": "empty", "message": "DOC directory created."}

    cache_manager = FileHashCache(CACHE_FILE)
    existing_files = [f for f in os.listdir(DOC_DIR) if os.path.isfile(os.path.join(DOC_DIR, f)) and not f.startswith(".")]
    cached_files = cache_manager.get_cached_files()
    
    # 1. Identify deleted files
    deleted_files = [f for f in cached_files if f not in existing_files]
    for f in deleted_files:
        _remove_from_vectorstore(f)
        cache_manager.remove_from_cache(f)
    
    # 2. Identify new or modified files
    files_to_ingest = []
    
    for filename in existing_files:
        filepath = os.path.join(DOC_DIR, filename)
        if filename.endswith(('.txt', '.pdf', '.docx')):
            if cache_manager.is_modified(filepath):
                files_to_ingest.append(filepath)
    
    if not files_to_ingest:
        return {
            "status": "success", 
            "message": "No new or modified documents to ingest. Sync complete.",
            "deleted": len(deleted_files)
        }

    docs = []
    
    # Load specific files
    for filepath in files_to_ingest:
        ext = os.path.splitext(filepath)[1].lower()
        loader = None
        if ext == '.txt':
            loader = TextLoader(filepath, encoding='utf-8')
        elif ext == '.pdf':
            loader = PyPDFLoader(filepath)
        elif ext == '.docx':
            loader = Docx2txtLoader(filepath)
            
        if loader:
            try:
                docs.extend(loader.load())
            except Exception as e:
                print(f"Failed to load {filepath}: {e}")

    if not docs:
         return {
            "status": "warning", 
            "message": "Files detected but failed to load content."
        }

    # Split text
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # Clean up old vectors for modified files before re-adding
    # (We already handled 'deleted' files, but for 'modified' ones, strict overwrite is usually delete+add)
    for filepath in files_to_ingest:
        filename = os.path.basename(filepath)
        _remove_from_vectorstore(filename)

    # Add to vectorstore
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents=splits)
    
    # Update cache
    for filepath in files_to_ingest:
        cache_manager.update_cache(filepath)

    return {
        "status": "success", 
        "count": len(splits), 
        "ingested_files": [os.path.basename(f) for f in files_to_ingest],
        "deleted_files": deleted_files,
        "message": f"Ingested {len(splits)} chunks from {len(files_to_ingest)} files. Deleted {len(deleted_files)} old files."
    }
