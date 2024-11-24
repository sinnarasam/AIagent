from common import client, makeup_response  # 필요한 도구들을 가져옵니다
import math  # 수학 계산을 위한 라이브러리를 가져옵니다

class Chatbot:
    # 채팅봇을 처음 만들 때 필요한 기본 설정을 하는 함수
    def __init__(self, model, system_role, instruction):
        # 대화 기록을 저장할 리스트를 만들고, 시스템 역할을 첫 번째로 저장합니다
        self.context = [{"role": "system", "content": system_role}]
        self.model = model  # 사용할 AI 모델
        self.instruction = instruction  # 챗봇에게 줄 추가 지시사항
        self.max_token_size = 16 * 1024  # 최대로 사용할 수 있는 토큰(단어) 수
        self.available_token_rate = 0.9  # 실제로 사용할 토큰의 비율 (90%)

    # 사용자의 메시지를 대화 기록에 추가하는 함수
    def add_user_message(self, user_message):
        self.context.append({"role": "user", "content": user_message})

    # AI에게 실제로 메시지를 보내고 응답을 받는 함수
    def _send_request(self):
        try:
            # AI 모델에게 메시지를 보내고 응답을 받습니다
            response = client.chat.completions.create(
                model=self.model,  # 사용할 AI 모델
                messages=self.context,  # 지금까지의 대화 기록
                temperature=0.5,  # 응답의 창의성 정도 (0: 항상 같은 답, 1: 매번 다른 답)
                top_p=1,  # 응답 선택의 다양성
                max_tokens=256,  # 응답의 최대 길이
                frequency_penalty=0,  # 같은 말 반복 방지 정도
                presence_penalty=0  # 새로운 주제 도입 정도
            ).model_dump()
        except Exception as e:  # 오류가 발생했을 때
            print(f"Exception 오류({type(e)}) 발생:{e}")
            # 메시지가 너무 길면 짧게 해달라고 요청
            if 'maximum context length' in str(e):
                self.context.pop()  # 마지막 메시지 삭제
                return makeup_response("메시지 조금 짧게 보내줄래?")
            else:  # 다른 오류가 발생하면 일시적 문제라고 안내
                return makeup_response("[챗봇에 문제가 발생했습니다. 잠시 뒤 이용해주세요]")
        
        return response

    # 사용자 메시지에 지시사항을 추가하고 AI에게 보내는 함수
    def send_request(self):
        self.context[-1]['content'] += self.instruction  # 마지막 메시지에 지시사항 추가
        return self._send_request()

    # AI의 응답을 대화 기록에 추가하는 함수
    def add_response(self, response):
        self.context.append({
                "role" : response['choices'][0]['message']["role"],  # 응답자 역할
                "content" : response['choices'][0]['message']["content"],  # 응답 내용
            }
        )

    # 가장 최근 응답의 내용을 가져오는 함수
    def get_response_content(self):
        return self.context[-1]['content']

    # 사용자 메시지에서 지시사항을 제거하는 함수
    def clean_context(self):
        # 뒤에서부터 찾아서 가장 최근의 사용자 메시지를 찾습니다
        for idx in reversed(range(len(self.context))):
            if self.context[idx]["role"] == "user":
                # 지시사항 부분을 제거하고 앞부분만 남김
                self.context[idx]["content"] = self.context[idx]["content"].split("instruction:\n")[0].strip()
                break

    # 대화 기록이 너무 길어지지 않도록 관리하는 함수
    def handle_token_limit(self, response):
        try:
            # 현재 사용 중인 토큰의 비율을 계산
            current_usage_rate = response['usage']['total_tokens'] / self.max_token_size
            # 허용된 비율을 초과한 정도를 계산
            exceeded_token_rate = current_usage_rate - self.available_token_rate
            
            # 허용된 비율을 초과했다면
            if exceeded_token_rate > 0:
                # 대화 기록의 10%를 삭제 (첫 번째 시스템 역할은 유지)
                remove_size = math.ceil(len(self.context) / 10)
                self.context = [self.context[0]] + self.context[remove_size+1:]
        except Exception as e:
            print(f"handle_token_limit exception:{e}")
