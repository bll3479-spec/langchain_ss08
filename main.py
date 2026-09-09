#주어진 txt를 파싱
#리뷰에 대한 댓글이 생성되도록(해적 메일 참고) 루틴 생성.
#10개로만 실행할 것.(토큰 아끼시오)
#main.py를 실행했을 때 각 리뷰에 대한 리플이 자동으로 생성되도록.
#원 데이터 링크:https://drive.google.com/file/d/1WnHJ7JpsAjg7ShrONua-AA2iCshjZ_Mo/view?usp=drive_link

import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI  
import templates as T

from dotenv import load_dotenv 
load_dotenv()

#권장방향
#1. (pandas)라이브러리 사용해서 txt 파일 읽어오기
def load_review(path):
    df = pd.read_csv(path, sep='\t')
    #print(df)
    #print(df['comment'])
    return df

#리플 체인 만들기
def build_reply_chain(chat):
    prompt = ChatPromptTemplate.from_template(T.REPLY_TEMPLATE)
    return prompt | chat | StrOutputParser()

#리뷰 한 줄마다 읽어서 build_reply_chain에 넣어주는 함수
def generate_reply(reviews, chat):
    reply_chain = build_reply_chain(chat)

    for i in range(len(reviews)):
        # print(review)
        # print(review['label'])
        # print(type(review['label']))
        #템플릿 2가지 요소:
        sentiment = '긍정' if reviews.loc[i]['label'] == 1 else '부정'
        comment = reviews.loc[i]['comment']
        result = reply_chain.invoke({'sentiment':sentiment, 'comment':comment })

        print(f'[답글 생성] 손님 댓글 {comment}\n 사장님 댓글 {result}' )

#2. 오늘 한 chain 함수를 이용해 댓글 분류(선택사항) -> 긍정/부정
#3. chain 함수를 이용해 댓글에 대한 답글 생성 -> (+) 프롬프팅에 페르소나 부여.

if __name__ == '__main__':
    #1. (pandas)라이브러리 사용해서 txt 파일 읽어오기
    df = load_review('./tarr_train.txt')
    #2. 오늘 한 chain 함수를 이용해 댓글 분류(선택사항) -> 긍정/부정
    chat = ChatOpenAI(temperature=0.7, model='gpt-4o')
    generate_reply(reviews = df, chat=chat)
    #3. chain 함수를 이용해 댓글에 대한 답글 생성 -> (+) 프롬프팅에 페르소나 부여.
