from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_ollama import OllamaLLM

texts = [
    "Artificial intelligence is transforming many industries.",
    "Machine learning models require large amounts of data.",
    "Baking cakes requires flour, sugar, and eggs.",
    "Neural networks can approximate complex functions."
]

docs = [Document(page_content=t) for t in texts]

class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name: str = "BAAI/bge-large-en"):
        self.model = SentenceTransformer(model_name)
    def embed_documents(self, texts):
        """Used when embedding multiple documents."""
        return self.model.encode(texts, show_progress_bar=False)
    def embed_query(self, text):
        """Used when embedding a single query for retrieval."""
        return self.model.encode(text, show_progress_bar=False)
    
embedder = SentenceTransformerEmbeddings()

faiss_storage = FAISS.from_documents(documents=docs, embedding=embedder)

# TODO: save db to a file
#==============================================================
# TODO: open a db file

user_query = "I want to know smth about baking cakes."

results_with_scores = faiss_storage.similarity_search_with_score(query=user_query
, k=2)

context = results_with_scores[0][0].page_content

# Prompt with three placeholders
prompt_template = ChatPromptTemplate.from_template(
    "Context: " \
    "{context}." \
    "Request: {query}. Provide a helpful answer based ONLY on the context."
    
)

prompt = prompt_template.format(context=context, query=user_query)

# Local model via Ollama
llm = OllamaLLM(model="gpt-oss:20B")

result = llm.invoke(prompt)

print(result)
