from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from embedder import SentenceTransformerEmbeddings

texts = [
    "Artificial intelligence is transforming many industries.",
    "Machine learning models require large amounts of data.",
    "Baking cakes requires flour, sugar, and eggs.",
    "Neural networks can approximate complex functions."
]

docs = [Document(page_content=t) for t in texts]

embedder = SentenceTransformerEmbeddings()

faiss_storage = FAISS.from_documents(documents=docs, embedding=embedder)

faiss_storage.save_local("vectorstore")

print("FAISS index saved to ./vectorstore/")
