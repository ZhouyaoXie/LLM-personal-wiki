from dotenv import load_dotenv
from langchain.document_loaders import NotionDirectoryLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain import hub
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
import os

# skeleton code from https://python.langchain.com/docs/use_cases/question_answering/

# load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# load Notion DB 
loader = NotionDirectoryLoader("data", encoding='utf8')
docs = loader.load()
print("Notion data loaded!")

# Split documents first on headers then on char
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
chunk_size = 500
chunk_overlap = 30
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_header_splits = markdown_splitter.split_text(docs)
text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
splits = text_splitter.split_documents(md_header_splits)

# Embed and store splits
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# Prompt
# https://smith.langchain.com/hub/rlm/rag-prompt
rag_prompt = hub.pull("rlm/rag-prompt")

# LLM
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

# RAG chain
rag_chain = {"context": retriever, "question": RunnablePassthrough()} | rag_prompt | llm