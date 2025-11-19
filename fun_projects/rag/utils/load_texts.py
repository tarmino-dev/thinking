from langchain_core.documents import Document

def load_texts(filepath="data/texts.txt", separator="@#@"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    raw_texts = [t.strip() for t in content.split(separator)]
    raw_texts = [t for t in raw_texts if t]

    docs = [Document(page_content=t) for t in raw_texts]
    return docs
