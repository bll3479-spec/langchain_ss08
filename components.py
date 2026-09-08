# langchain의 기본 대화를 구성하는 3요소
# 1. 프롬프트와 파서: 대화의 양식 규정
# 2. 체인: |(파이프), LCEL 문법
# 3. 메모리: 사용자와의 이전 대화 내용 기억

#대화 대상 세팅
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate       #llm에 질문할 정규 양식 생성
from langchain_core.output_parsers import StrOutPutParser   #output 결과물 정제, 파싱
import os
from dotenv import load_dotenv

#.env: 비밀 키 가져오는 역할
load_dotenv()

#사용할 gpt 모델
MODEL_NAME = 'gpt-4o'

#대화할 llm모델과의 채팅 방 만들기 절차
def get_chat(temperature=0.5, model=MODEL_NAME):
    return ChatOpenAI(temperature=temperature, model=model)

STYLE_TEMPLATE = """Translate the text \
that is delimited by triple backticks \
into a style that is {style}. \
text: ```{text}```
"""
#prompttemplate가 {} 부분을 알아서 변환~

#프롬프팅 양식 세팅
#매개변수 chat은 gpt와의 채팅방
#prompt | chat 미리 정해놓은 prompt를 chat 채팅방에 넘겨주는 작동
#chat | StrOutPutParser()은 chat의 답변을 StrOutputParser로 넘겨주는 작동
def bulid_style_chain(chat):
    #{style}, {text}를 변수로 인식, 이를 채워줌
    prompt = ChatPromptTemplate.from_template(STYLE_TEMPLATE)
    #LCEL 문법: prompt를 chat에 넘기고 그 결과를 strOutPutParsers에 다시 넣어주는 연결(chain)
    return prompt | chat | StrOutPutParser()

#프롬프팅, 파서
#인풋 텍스트 -> 특정한 양식에 맞추어 정제/답변
def parsing():
    #CS 고객이 문의한 내용을 특정한 양식에 맞춰 뽑아내기/변형하기
    #해적 손님의 메일
    customer = '''
        Arrr, I be fuming that me blender lid flew off and splattered me kitchen walls \
        with smoothie! And to make matters worse, the warranty don't cover the cost of \
        cleaning up me kitchen. I need yer help right now, matey!
                '''
    #gpt, 해적 손님의 메일을 격식을 갖춘 따뜻한 어투의 영어 메일로 바꿔줘.
    #gpt-4o 모델과 temperature=0.5로 만든 채팅방을 연 상태(방 이름: chat)
    chat = get_chat()
    #gpt에 위의 손님 메일 + (변형) 요청을 보내, 답변을 받아오는 체인 정의
    #style_chain은 prompt -> chat -> stroutputparser로 이어지는 파이프라인
    style_chain = build_style_chain(chat)

    result = style_chain.invoke({'style':'American English in a calm and respectful tone', 'text':customer})
s
    # customer_review = 

    # parse_chain, format = 

    # output = 
    # print(f'구조화된 파싱: {}')



if __name__ == '__main__':
    Chat = OpenAI()                  #direct
    #Chat = ChatOpenAI()             #indirect
    response = Chat.completions.create(                 #대화방 생성
        model = MODEL_NAME,       
        #role: system role(openai의 세팅), user role(사용자)
        messages = [{'role':'system', 'content':'말끝에다 멍을 붙여'}, {'role':'user','content':'한국은 어떤 나라니?'}],
        #답변의 창의성
        temperatures = 0.6
    )
    #답변.초이스[0].message.content: 답변 중 텍스트만 깔끔하게 추출.
    print(response)
    print(response.choices[0].message.content)