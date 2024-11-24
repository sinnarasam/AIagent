# 필요한 라이브러리들을 가져옵니다
from flask import Flask, render_template, request  # Flask: 웹 서버를 만드는 도구
import sys  # 시스템 관련 기능을 사용하기 위한 라이브러리
from common import model, currTime  # 우리가 만든 공통 모듈에서 필요한 것들을 가져옴
from chatbot import Chatbot  # 채팅봇 클래스를 가져옴
from characters import system_role, instruction  # 채팅봇의 설정을 가져옴
from concurrent.futures import ThreadPoolExecutor  # 여러 작업을 동시에 처리하기 위한 도구
import requests  # 인터넷으로 데이터를 주고받기 위한 라이브러리
import concurrent

# 채팅봇을 만듭니다
bot = Chatbot(
    model = model.basic,  # 기본 모델 사용
    system_role = system_role,  # 채팅봇의 역할 설정
    instruction = instruction  # 채팅봇에게 줄 지시사항
)

# Flask 웹 서버 애플리케이션을 만듭니다
application = Flask(__name__)

# 웹사이트의 첫 페이지 주소(/)에 접속하면 실행되는 함수
@application.route("/")
def hello():
    return "Hello goorm!"  # "Hello goorm!" 이라는 메시지를 보여줍니다

# /welcome 주소로 접속하면 실행되는 함수
@application.route("/welcome")
def welcome():
    return "Hello goorm!"  # 위와 같은 메시지를 보여줍니다

# /chat-app 주소로 접속하면 실행되는 함수
@application.route("/chat-app")
def chat_app():
    return render_template("chat.html")  # chat.html 페이지를 보여줍니다

# /chat-api 주소로 메시지를 보내면 실행되는 함수
@application.route('/chat-api', methods=['POST'])
def chat_api():
    # 사용자가 보낸 메시지를 가져옵니다
    request_message = request.json['request_message']
    print("request_message:", request_message)
    
    # 채팅봇에게 메시지를 전달하고 응답을 받습니다
    bot.add_user_message(request_message)  # 사용자 메시지 추가
    response = bot.send_request()  # 응답 요청
    bot.add_response(response)  # 응답 저장
    response_message = bot.get_response_content()  # 응답 내용 가져오기
    bot.handle_token_limit(response)  # 메시지 길이 제한 처리
    bot.clean_context()  # 대화 내용 정리
    
    print("response_message:", response_message)
    return {"response_message": response_message}  # 응답 메시지 반환

# 카카오톡 채팅봇을 위한 응답 형식을 만드는 함수
def format_response(resp, useCallback=False):
    data = {
        "version": "2.0",
        "useCallback": useCallback,
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": resp
                    }
                }
            ]
        }
    }
    return data

# 동시에 여러 작업을 처리하기 위한 실행기를 만듭니다
executor = ThreadPoolExecutor(max_workers=1)

# 카카오톡 채팅봇이 메시지를 보내면 실행되는 함수
@application.route('/chat-kakao', methods=['POST'])
def chat_kakao():
    print("request.json:", request.json)
    # 카카오톡에서 받은 메시지를 가져옵니다
    request_message = request.json['userRequest']['utterance']
    print("request_message:", request_message)
    
    # 채팅봇에게 메시지를 전달하고 응답을 받습니다
    bot.add_user_message(request_message)
    response = bot.send_request()
    bot.add_response(response)
    response_message = bot.get_response_content()
    bot.handle_token_limit(response)
    bot.clean_context()
    
    print("response_message:", response_message)
    # 카카오톡 형식에 맞게 응답을 변환하여 반환합니다
    return format_response(response_message)

# 프로그램을 실행할 때 포트 번호를 입력하지 않으면 안내 메시지를 보여줍니다
if len(sys.argv) < 2:
    print("Usage: python application.py <port>")
    sys.exit(1)

# 입력받은 포트 번호로 웹 서버를 시작합니다
port = int(sys.argv[1])
application.run(host='0.0.0.0', port=port)
