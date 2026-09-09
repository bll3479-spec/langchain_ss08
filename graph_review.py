#components에서는 라우터, lcel로만 분기했으나
#여기서는 langraph의 조건부 엣지로 그래프 자체를 분기
#순서: 리뷰 파싱, 상태 정의, 노드 2개(감사, 보완), 분기함수, 그래프

import os
import pandas as pd

from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import templates as T
from typing import TypedDict

from dotenv import load_dotenv
load_dotenv()

class State(TypedDict):
    comment : str
    label : str
    reply : str

def thanks_node(state, chat):
    chain = ChatPromptTemplate.from_template(T.THANKS_TEMPLATE) | chat | StrOutputParser
    reply = chain.invoke({'comment':state['comment']})  #결과 -> gpt의 답변
    return {'reply':reply}
def sorry_node(state, chat):
    chain = ChatPromptTemplate.from_template(T.IMPROVE_TEMPLATE) | chat | StrOutputParser
    reply = chain.invoke({'comment':state['comment']})
    return {'reply':reply}

def route_by_sentiment(state):
    if state['label'] == '1':
        return 'thanks'
    else:
        return 'sorry'


def build_graph():
    graph = StateGraph(State)
    graph.add_node('thanks', thanks_node)
    graph.add_node('sorry', sorry_node)
    graph.add_conditional_edges(START, route_by_sentiment, 
                                {'thanks': 'thanks',
                                 'sorry':'sorry'})

    graph.add_edge('thanks', END)
    graph.add_edge('sorry', END)
    return graph.complie()