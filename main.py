from IPython.display import Markdown
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyAeSmUxbXn-sjDpuxBUQEU7QqTgf258uXc"

from langchain_google_genai import ChatGoogleGenerativeAI
from vertexai.preview import generative_models

llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature = 0.05)


from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader

# loader = WebBaseLoader("https://developers.kakao.com/docs/latest/ko/kakaologin/rest-api" )
# data = loader.load()

from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("./qq/qq/2021가합586316.pdf")
print(loader)
data = loader.load_and_split()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=0)
splits = text_splitter.split_documents(data)

from langchain_community.embeddings import HuggingFaceEmbeddings
print("끝")
gemini = ChatGoogleGenerativeAI(model="gemini-pro", temperature = 0)

# VectorDB
model_name = "jhgan/ko-sbert-nli"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': True}

hf = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

from langchain_community.vectorstores import FAISS

db = FAISS.from_documents(splits, hf)

retriever = db.as_retriever(
                            search_type="similarity",
                            search_kwargs={'k':3, 'fetch_k': 10}
                        )

print("끝")
from langchain.retrievers.multi_query import MultiQueryRetriever

retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=retriever, llm=llm
)
print("끝")

# import logging

# logging.basicConfig()
# logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
print("끝")

question = "카카오 인가코드 받는 방법"
unique_docs = retriever_from_llm.get_relevant_documents(query=question)

len(unique_docs)
print(unique_docs)

from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableMap
from langchain.prompts import PromptTemplate

template = """
### [INST]
Instruction: Answer the question based on context.
Please write the responses in detail
If you find a corresponding result, Please also add "출처:"metadata.source as the source you referenced in the last line

Here is context to help:

{context}

### QUESTION:
{question}

[/INST]
 """
print("끝")


prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=template,
)

from langchain_core.runnables import RunnablePassthrough

# rag_chain = (
#  {"context": retriever, "question": RunnablePassthrough()}
#     | prompt | gemini
# )
# Markdown(rag_chain.invoke("카카오 인가코드 받는 방법").content)

# retriever_from_llm.get_relevant_documents(x[''question])
reg_chain = RunnableMap({
    "context": lambda x: retriever_from_llm.get_relevant_documents(x['question']),
    "question": lambda x: x['question']
}) | prompt | gemini

print(reg_chain.invoke({'question': "카카오 인가코드 받는 방법"}))
print("끝1")
print(reg_chain.invoke({'question': "카카오 인가코드 받는 방법"}).content)
print("끝")