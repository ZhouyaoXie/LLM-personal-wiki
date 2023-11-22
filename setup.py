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
import re 
import json
import webbrowser 

def remove_link(text):
  """Remove link from markdown string.

  Args:
    text: The markdown string to remove link from.

  Returns:
    The markdown string without link.
  """

  # Remove the link from the markdown string.
  text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', text)

  # Remove the square brackets from the markdown string.
  text = text.replace('[', '').replace(']', '')

  return text

def get_link(text, d):
  text = text.split('\\')[-1]
  try:
    page_link = d[text].strip() 
    return page_link
  except:
    print("page not found in directory for {}".format(text))

def open_url(url):
    webbrowser.open(url)


if __name__ == "__main__":
  # skeleton code from https://python.langchain.com/docs/use_cases/question_answering/
  data_dir = 'data'
  # load environment variables
  load_dotenv()
  OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

  # load all files from Notion DB
  # TODO: load csv files with CSVLoader
  t1 = time.time()
  loader = NotionDirectoryLoader("data", encoding='utf8')
  docs = loader.load()
  t2 = time.time()
  print("{} pages of Notion data loaded in {}s!".format(len(docs), int(t2 - t1)))

  # add page url to page metadata 
  with open(os.path.join(data_dir, "directory_name.json"), 'r') as json_file:
    d = json.load(json_file)
  for doc in docs:
    doc.metadata['url'] = "https://www.notion.so/zhouyaoxie/" + get_link(doc.metadata['source'], d)

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
    # remove page links from Markdown
    # TODO: debug not all page links got removed 
    for split in splits:
        split.metadata.update(doc.metadata)
        split.page_content = remove_link(split.page_content)
    # remove empty splits 
    if len(splits) > 0:
        md_header_splits.extend(splits)
  print("Split pages by Markdown headers into {} splits!".format(len(md_header_splits)))

  text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size, chunk_overlap = chunk_overlap)
  splits = text_splitter.split_documents(md_header_splits)
  splits = [split for split in splits if len(split.page_content.strip()) > 0]
  print("Data splitted to {} chunks with size {}, overlap {}".format(len(splits), chunk_size, chunk_overlap))

  # Embed and store splits to disk
  t1 = time.time()
  embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
  vectorstore = Chroma.from_documents(documents=splits, embedding=embedding, persist_directory="chroma_db")
  t2 = time.time()
  print("Save data to vectorstore in {}s!".format(int(t2 - t1)))
