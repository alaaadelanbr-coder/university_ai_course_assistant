from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

PDF_PATH = "syllabus.pdf"

loader = PDFPlumberLoader(PDF_PATH)
documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=250
)

chunks = text_splitter.split_documents(documents)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.from_documents(
    chunks,
    embedding_model
)

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 6}
)

def retrieve_relevant_documents(query: str):
    results = retriever.invoke(query)
    return results