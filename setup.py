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
import time 

# skeleton code from https://python.langchain.com/docs/use_cases/question_answering/

# load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# load Notion DB 
t1 = time.time()
loader = NotionDirectoryLoader("data", encoding='utf8')
docs = loader.load()
t2 = time.time()
print("{} pages of Notion data loaded in {}s!".format(len(docs), int(t2 - t1)))

# TODO: remove empty docs 

# Split documents first on Markdown headers then on char
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
chunk_size = 500
chunk_overlap = 30
markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_header_splits = []
for doc in docs:
    splits = markdown_splitter.split_text(doc.page_content)
    # TODO: remove empty splits
    for split in splits:
        split.metadata.update(doc.metadata)
    md_header_splits.extend(splits)
print("Split pages by Markdown headers into {} splits!".format(len(md_header_splits)))

text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
splits = text_splitter.split_documents(md_header_splits)
# TODO: remove empty splits
print("Data splitted to {} chunks with size {}, overlap {}".format(len(splits), chunk_size, chunk_overlap))

# Embed and store splits to disk
t1 = time.time()
embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
vectorstore = Chroma.from_documents(documents=splits, embedding=embedding, persist_directory="chroma_db")
t2 = time.time()
print("Save data to vectorstore in {}s!".format(int(t2 - t1)))
