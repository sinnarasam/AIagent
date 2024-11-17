from flask import Flask, render_template, request
import sys
from common import model, currTime
from chatbot import Chatbot
from characters import system_role, instruction
from concurrent.futures import ThreadPoolExecutor
import requests
import concurrent


# bot 인스턴스 생성
bot = Chatbot(
    model = model.basic,
    system_role = system_role,
    instruction = instruction    
)

application = Flask(__name__)

@application.route("/")
def hello():
    return "Hello goorm!" 

@application.route("/welcome")
def welcome(): # 함수명은 꼭 welcome일 필요는 없습니다.
    return "Hello goorm!" 

@application.route("/chat-app")
def chat_app():
    return render_template("chat.html")

@application.route('/chat-api', methods=['POST'])
def chat_api():
    request_message = request.json['request_message']
    print("request_message:", request_message)
    bot.add_user_message(request_message)
    response = bot.send_request()
    bot.add_response(response)
    response_message = bot.get_response_content()
    bot.handle_token_limit(response)
    bot.clean_context()
    print("response_message:", response_message)
    return {"response_message": response_message}

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

executor = ThreadPoolExecutor(max_workers=1)



@application.route('/chat-kakao', methods=['POST'])
def chat_kakao():
    print("request.json:", request.json)
    request_message = request.json['userRequest']['utterance']
    print("request_message:", request_message)
    bot.add_user_message(request_message)
    response = bot.send_request()
    bot.add_response(response)
    response_message = bot.get_response_content()
    bot.handle_token_limit(response)
    bot.clean_context()    
    print("response_message:", response_message)
    return format_response(response_message)


if len(sys.argv) < 2:
    print("Usage: python application.py <port>")
    sys.exit(1)

port = int(sys.argv[1])
application.run(host='0.0.0.0', port=port)