# langchain의 기본 대화를 구성하는 3요소
# 1. 프롬프트와 파서: 대화의 양식 규정
# 2. 체인: |(파이프), LCEL 문법
# 3. 메모리: 사용자와의 이전 대화 내용 기억

#대화 대상 세팅
from langchain_openai import ChatOpenAI                     #챗 객체 생성
from openai import OpenAI
from langchain_core.prompts import ChatPromptTemplate       #llm에 질문할 정규 양식 생성. text로 넣어도 되는 이유
from langchain_core.output_parsers import StrOutputParser   #output 결과물 정제, 파싱
import os
from dotenv import load_dotenv 

#사용할 템플릿
import templates as T

#.env: 비밀 키 가져오는 역할
load_dotenv()

#사용할 gpt 모델
MODEL_NAME = 'gpt-4o'

#대화할 llm모델과의 채팅 방 만들기 절차
def get_chat(temperature=0.5, model=MODEL_NAME):
    return ChatOpenAI(temperature=temperature, model=model)


#prompttemplate가 {} 부분을 알아서 변환~

#프롬프팅 양식 세팅
#매개변수 chat은 gpt와의 채팅방
#prompt | chat 미리 정해놓은 prompt를 chat 채팅방에 넘겨주는 작동
#chat | StrOutPutParser()은 chat의 답변을 StrOutputParser로 넘겨주는 작동
def bulid_style_chain(chat):
    #{style}, {text}를 변수로 인식, 이를 채워줌
    prompt = ChatPromptTemplate.from_template(T.STYLE_TEMPLATE)
    #LCEL 문법: prompt를 chat에 넘기고 그 결과를 strOutPutParsers에 다시 넣어주는 연결(chain)
    return prompt | chat | StrOutputParser()

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
    style_chain = bulid_style_chain(chat)
    #chain을 실행할때 style, text를 넣어줄테니 prompt -> chat -> stroutputparser 파이프라인 타셈
    result = style_chain.invoke({'style':'Korean in a calm and respectful tone', 'text':customer})
    print(result)

    text = input(f'{result}에 대한 나의 답변')
    reply = style_chain.invoke({'style':'english in a calm and respectful tone if my response contains some bad words, plz translate it or remove it', 'text':text})
    print(reply)


from langchain_classic.output_parsers import ResponseSchema, StructuredOutputParser
def build_review_chain(chat):
    prompt = ChatPromptTemplate.from_template(T.REVIEW_TEMPLATE)
    #**StrOutputParser는 거의 아무것도 하지 않는 str만 추출하는 역할
    #StructuredOutputParser: gpt가 생성한 str을 특정한 자료형(구조)으로 파싱
    #schemas: 이러한 변수에는 다음과 같은 정보가 필요하다고 알려줌(name=변수 이름)
    schemas = [
    ResponseSchema(name="gift",
                    description="Was the item purchased as a gift for someone else? "
                                "Answer True if yes, False if not or unknown."),
    ResponseSchema(name="delivery_days",
                    description="How many days did it take for the product to arrive? "
                                "If this information is not found, output -1."),
    ResponseSchema(name="price_value",
                    description="Extract any sentences about the value or price, "
                                "and output them as a comma separated Python list."),
]
    #리뷰를 합친 prompt가 인풋 -> chat이 이를 확인 -> StructuredOutputParser가 chat이 생성한 결과를 schema에 따라 구조화
    return prompt | chat | StructuredOutputParser.from_response_schemas(schemas), StructuredOutputParser.from_response_schemas(schemas).get_format_instructions() 

#OutputParser의 종류를 바꿔 Parser의 역할 확인
#리뷰 속에 존재하는 다양한 정보를 parser가 골라 정리해주는 역할
def output_parsing():
    customer_review = """\
        This leaf blower is pretty amazing. It has four settings: candle blower, gentle breeze, \
        windy city, and tornado. It arrived in two days, just in time for my wife's anniversary \
        present. I think my wife liked it so much she was speechless. It's slightly more expensive \
        than the other leaf blowers out there, but I think it's worth it for the extra features.
        """
    chat = get_chat()
    parse_chain, format = build_review_chain(chat)
    #bulid_review_chain이 시작할 때 필요한 재료: prompt -> review_template -> 그 안에 있는 {}
    output = parse_chain.invoke({'text': customer_review, 'format_instructions':format})
    print(f'구조화된 파싱: {type(output).__name__, output}')
    print(f'구조화 결과 delivery : {output.get('delivery_days')}')

    # customer_review = 

    # parse_chain, format = 

    # output = 
    # print(f'구조화된 파싱: {}')


def Legacy_chat():
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

#LCEL로 넘겨주기 위해 runnarble 패밀리 사용
#https://modulabs.co.kr/community/momos/284/feeds/3525
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

def bulid_seq_chain(llm):
    #하려는 것: 질문이 들어옴 -> 질문을 분류(라우터) -> 각 chat이 대답함 -> 깔끔하게 리턴
    destination_chains = {
        p['name'] : ChatPromptTemplate.from_template(p['prompt_template']) | llm | StrOutputParser() for p in T.PROMPT_INFOS
    }
    print(destination_chains)
    default_chain = ChatPromptTemplate.from_template("") | llm | StrOutputParser()

    destination_str = '\n'.join(f"{p}" for p in T.PROMPT_INFOS)


if __name__ == '__main__':
    #output_parsing()
    llm = get_chat()
    bulid_seq_chain(llm)
