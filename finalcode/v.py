from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# -------- Load PDFs --------
pdf1 = PyPDFLoader("Document/doing business.pdf").load()
pdf2 = PyPDFLoader("Document/bhutan business.pdf").load()
pdf3 = PyPDFLoader("Document/rules and regulation.pdf").load()

all_docs = pdf1 + pdf2 + pdf3

# -------- Split --------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(all_docs)

# -------- Embedding --------
embedding_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

# -------- Create Chroma DB (auto persists) --------
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory="chroma_db"
)

print("✅ Chroma DB created and saved automatically")