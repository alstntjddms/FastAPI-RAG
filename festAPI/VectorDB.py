import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.schema.runnable import RunnableMap
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAI
from langchain_community.document_loaders import UnstructuredHTMLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.docstore.document import Document

import logging
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

class LanguageChainProcessor:
    def __init__(self):
        self.initialize()

    def initialize(self):
        print("Initialization started...")
        os.environ["GOOGLE_API_KEY"] = "AIzaSyAeSmUxbXn-sjDpuxBUQEU7QqTgf258uXc"
        os.environ["OPENAI_API_KEY"] = "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"

        self.llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.05)
        # self.llm = OpenAI(model_name="gpt-3.5-turbo-instruct", temperature = 0)
        self.hf = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sbert-nli",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # self.db = FAISS.load_local("/home/minsu/rag/saved_db", self.hf)
        if os.path.exists("/home/minsu/rag/saved_db/index.faiss"):
            # 파일이 존재하면 로드
            self.db = FAISS.load_local("/home/minsu/rag/saved_db", self.hf)
        else:
            self.db = FAISS.from_documents([Document(page_content=' ')], self.hf)
            self.db.save_local("/home/minsu/rag/saved_db")
            self.db = FAISS.load_local("/home/minsu/rag/saved_db", self.hf)

        self.retriever = self.db.as_retriever(
            search_type="similarity",
            search_kwargs={'k': 5, 'fetch_k': 10}
        )

        self.QUERY_PROMPT = PromptTemplate(
            input_variables=["question"],
            template="""You are an AI language model assistant. Your task is to generate five 
            different versions of the given user question in korean to retrieve relevant documents from a vector database. 
            By generating multiple perspectives on the user question, your goal is to help
            the user overcome some of the limitations of the distance-based similarity search. 
            Provide these alternative questions separated by newlines.
            The last response is always user question.
            The purpose of the question is to generate a question to find several people.
            Original question: {question}""",
        )

        self.retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=self.retriever, llm=self.llm, prompt=self.QUERY_PROMPT
        )

        self.template = """
        ### [INST]
        <<SYS>>
        You are a knowledgeable assistant with access to human information, providing detailed and informative responses to questions.
        Please respond comprehensively and include additional relevant information when possible.
        If possible, show me the results of several people.
        If possible, please include the reason for the response.
        Base your answer on the provided context.
        Information about context should be used only as information about people in ''metadata.name''.
        If you find supporting evidence, please include 출처: ''metadata.source of context'' at the end of your response.
        <</SYS>>

        Here is some context to assist you:

        {context}

        ### QUESTION:
        {question}

        [/INST]
        """

        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=self.template,
        )

        self.reg_chain = RunnableMap({
            "context": lambda x: self.retriever_from_llm.get_relevant_documents(x['question']),
            "question": lambda x: x['question']
        }) | self.prompt | self.llm

        print("Initialization completed.")

    def process_question(self, question):
        return self.reg_chain.invoke({'question': question}).content

    def additional_learning(self, fileName):
        print("Additional learning initiated...")
        file_path = os.path.join("/home/minsu/rag/docs/", fileName)

        # PDF 파일 로드 및 분할
        loader = UnstructuredHTMLLoader(file_path)
        data = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=10)
        texts = text_splitter.split_documents(data)
        for text in texts:
            text.metadata['name'] = fileName

        text_splitter2 = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=10)
        texts2 = text_splitter2.split_documents(data)
        for text in texts2:
            text.metadata['name'] = fileName

        text_splitter3 = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
        texts3 = text_splitter3.split_documents(data)
        for text in texts3:
            text.metadata['name'] = fileName

        text_splitter4 = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=10)
        texts4 = text_splitter4.split_documents(data)
        for text in texts4:
            text.metadata['name'] = fileName
        
        l1 = self.db.add_documents(texts)
        l1 += self.db.add_documents(texts2)
        l1 += self.db.add_documents(texts3)
        l1 += self.db.add_documents(texts4)

        # 각각의 벡터 ID 리스트를 파일로 저장
        save_directory = "/home/minsu/rag/docs/vector_id_lists"
        os.makedirs(save_directory, exist_ok=True)  # 디렉토리가 없으면 생성
        with open(os.path.join(save_directory, f"{fileName}_vector_id_list.txt"), "w") as file:
            for vector_id in l1:
                file.write(f"{vector_id}\n")

        self.db.save_local("/home/minsu/rag/saved_db")
        self.initialize()  # Re-initialize the processor
        return fileName

    def deleteEduByName(self, name):
        file_path = f"/home/minsu/rag/docs/vector_id_lists/{name}.html_vector_id_list.txt"
        try:
            with open(file_path, "r") as file:
                vector_id_list = [line.strip() for line in file.readlines()]  # 개행 문자 제거
            # 파일 내용을 배열로 불러오고 파일 삭제
            self.db.delete(vector_id_list)
            self.db.save_local("/home/minsu/rag/saved_db")
            self.initialize()
            os.remove(file_path)
            return "Deleted successfully"
        except FileNotFoundError:
            # return []  # 파일이 없을 경우 빈 배열 반환
            return "삭제 성공"
        