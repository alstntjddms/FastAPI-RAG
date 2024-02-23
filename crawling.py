from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 크롬 드라이버의 경로
driver_path = './chromedriver'

# 크롬 브라우저를 headless 모드로 실행하는 옵션 추가
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 브라우저를 실제로 표시하지 않음
options.add_argument('--no-sandbox')  # 리눅스 환경에서 실행 시 필요한 옵션 추가
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# 웹 드라이버 초기화
driver = webdriver.Chrome(options=options)

# URL 목록
urls = [
    "https://yulchon.com/ko/professionals/professionals-view/shkang/kang-seokhoon.do",
    "https://yulchon.com/ko/professionals/professionals-view/swc/cho-sangwook.do",
    "https://yulchon.com/ko/professionals/professionals-view/dohyeongkim19036/kim-dohyeong.do",
    "https://yulchon.com/ko/professionals/professionals-view/jiweonjeong18142/jeong-jiweon.do",
    "https://yulchon.com/ko/professionals/professionals-view/choks/cho-kyusok.do",
    "https://yulchon.com/ko/professionals/professionals-view/parkjw/park-jaewoo.do",
    "https://yulchon.com/ko/professionals/professionals-view/choks/cho-kyusok.do",
    "https://yulchon.com/ko/professionals/professionals-view/slee/lee-soojung.do",
    "https://yulchon.com/ko/professionals/professionals-view/jsyang21069/yang-jayson.do",
    "https://yulchon.com/ko/professionals/professionals-view/jailee/lee-jaiwook.do",
    "https://yulchon.com/ko/professionals/professionals-view/sbpark/park-sungbom.do",
    "https://yulchon.com/ko/professionals/professionals-view/parkhs/park-haesik.do",
    "https://yulchon.com/ko/professionals/professionals-view/leesj/lee-seukjoon.do",
    "https://yulchon.com/ko/professionals/professionals-view/cschung/chung-cecilsaehoon.do",
    "https://yulchon.com/ko/professionals/professionals-view/yhhwang23161/hwang-yoonhwan.do",
    "https://yulchon.com/ko/professionals/professionals-view/smj/jung-sungmoo.do",
    "https://yulchon.com/ko/professionals/professionals-view/sjlee/lee-seungjae.do"
]

for url in urls:
    # 특정 페이지에 접속
    driver.get(url)

    # 페이지가 로드될 때까지 최대 1초 기다림
    wait = WebDriverWait(driver, 2)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'content')))

    # 현재 페이지의 HTML 가져오기
    html_content = driver.page_source

    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(html_content, 'html.parser')

    # 특정 클래스명을 가진 요소만 추출
    content_element = soup.find(class_='content')

    if content_element:
        # 추출한 요소를 문자열로 변환하여 파일로 저장
        with open('/home/minsu/rag/docs/' + url.split('/')[-1].replace('.do', '') + ".html", 'w', encoding='utf-8') as f:
            f.write(str(content_element))

# 웹 드라이버 종료
driver.quit()
