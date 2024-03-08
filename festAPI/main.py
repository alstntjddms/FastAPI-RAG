from typing import Union
from VectorDB import LanguageChainProcessor
from Scraper import YulchonScraper 
from fastapi import FastAPI
from pydantic import BaseModel
import os
import re

app = FastAPI()

# 랭체인
processor = LanguageChainProcessor()
# YulchonScraper 인스턴스 생성
scraper = YulchonScraper()

class Q(BaseModel):
    question: str

class D(BaseModel):
    name: str

class U(BaseModel):
    url: str
    name : str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/ai/question")
def read_item(q: Q):
    print(q.question)
    response = processor.process_question(q.question)
    return {"q": response}

@app.post("/ai/edu")
def edu_url(u: U):
    print(u.url)
    response = scraper.scrape_and_save(u.url, u.name, '/home/minsu/rag/docs/')
    if(response == "이미 학습되어 있는 파일이 존재함."):
        return {"url" : response}
    
    result = processor.additional_learning(response)
    return {"url" : result}

@app.delete("/ai/edu")
def edu_url(d: D):
    print(d.name)
    return processor.deleteEduByName(d.name)
    

@app.get("/ai/edu/all")
def read_root():
    return find_files_in_directory("/home/minsu/rag/docs/vector_id_lists")

def find_files_in_directory(directory_path):
    try:
        # 디렉토리 내의 파일 리스트를 가져옴
        files = os.listdir(directory_path)
        # 추출한 이름들을 저장할 빈 리스트
        names = []

        # 파일명에서 이름을 추출하여 리스트에 추가
        for file_name in files:
            # 파일명에서 이름 부분을 정규표현식을 사용하여 추출
            match = re.match(r'(.+?)\.html_vector_id_list\.txt', file_name)
            if match:
                name = match.group(1)
                names.append(name)

        # 추출한 이름들을 반환
        return names

    except FileNotFoundError:
        # 디렉토리가 존재하지 않는 경우 예외 처리
        print("Directory not found.")
        return []


#  시작 명령어 uvicorn main:app --reload