from langchain_community.vectorstores import FAISS
from embedder import SentenceTransformerEmbeddings
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_ollama import OllamaLLM

embedder = SentenceTransformerEmbeddings()

loaded_faiss = FAISS.load_local("vectorstore", embedder, allow_dangerous_deserialization=True)

print("FAISS index loaded\nDocs in FAISS:", len(loaded_faiss.docstore._dict))

user_query = input("Ask anything (e.g. 'How to fly to space?'): ")

results_with_scores = loaded_faiss.similarity_search_with_score(query=user_query
, k=2)

# Print results docs titles with their scores
new_line = '\n'
for doc, score in results_with_scores:
    print(f"Score={score:.4f}  |  Text='{doc.page_content.split(new_line)[0]}'")

# Pick the most relevant doc
context = results_with_scores[0][0].page_content

# Prompt with placeholders
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
