from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name: str = "BAAI/bge-large-en"):
        self.model = SentenceTransformer(model_name)
    def embed_documents(self, texts):
        """Used when embedding multiple documents."""
        return self.model.encode(texts, show_progress_bar=False)
    def embed_query(self, text):
        """Used when embedding a single query for retrieval."""
        return self.model.encode(text, show_progress_bar=False)
