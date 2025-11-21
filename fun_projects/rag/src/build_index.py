from langchain_community.vectorstores import FAISS
from embedder import SentenceTransformerEmbeddings
from loaders import load_texts

docs = load_texts()

embedder = SentenceTransformerEmbeddings()

faiss_storage = FAISS.from_documents(documents=docs, embedding=embedder)

faiss_storage.save_local("vectorstore")

print("FAISS index saved to ./vectorstore/")
