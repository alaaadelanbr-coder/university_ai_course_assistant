from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Load the syllabus PDF

PDF_PATH = "syllabus.pdf"

loader = PyPDFLoader(PDF_PATH)

documents = loader.load()

# Split the document

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80
)

chunks = text_splitter.split_documents(documents)

#  Create Embeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

#  Create FAISS Vector Store

vectorstore = FAISS.from_documents(
    chunks,
    embedding_model
)

#  Create Retriever

retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}
)
#  Function for searching
def retrieve_relevant_documents(query: str):
    """
    Search the syllabus for documents
    relevant to the user's question.
    """

    results = retriever.invoke(query)

    return results