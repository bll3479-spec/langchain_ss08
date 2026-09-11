#여러 에이전트(노드)가 협력해서 에세이를 작성하는 멀티 에이전트 시스템

#                      +-----------+
#                      | __start__ |
#                      +-----------+
#                             *
#                             *
#                             *
#                       +---------+
#                       | planner |
#                       +---------+
#                             *
#                             *
#                             *
#                      +------------+
#                      | researcher |
#                      +------------+
#                             *
#                             *
#                             *
#                      +-----------+
#                      | generator |
#                    ..+-----------+***
#                ....         .        ****
#            ....             .            ****
#          ..                 .                ****
# +---------+           +---------+                **
# | __end__ |           | reflect |               **
# +---------+           +---------+             **
#                                 ***         **
#                                    *      **
#                                     **   *
#                                  +----------+
#                                  | critique |
#                                  +----------+
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, List

from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver


class AgentState(TypedDict):
    task : str
    plan : str
    draft : str
    critique : str
    content : List[str]
    revision_number : int
    max_revisions : int

# ── 프롬프트 ──────────────────────────────────────────────────────────────────
PLAN_PROMPT = (
    "You are an expert writer. "
    "Write a high-level outline for an essay on the given topic. "
    "Include relevant notes or instructions for each section."
)

WRITER_PROMPT = """You are an essay assistant writing excellent 5-paragraph essays.
Generate the best essay possible for the user's request and the initial outline.
If the user provides critique, respond with a revised version of your previous attempt.
Use the following reference content as needed:

------

{content}"""

REFLECTION_PROMPT = (
    "You are a teacher grading an essay submission. "
    "Provide detailed critique and recommendations including length, depth, and style."
)

RESEARCH_PROMPT = (
    "You are a researcher. Generate up to 3 Wikipedia search queries "
    "to gather information relevant to the given topic or critique. "
    "Return only the queries as a JSON list."
)
# ──────────────────────────────────────────────────────────────────────────

#pydantic의 상속을 받음
class Queries(BaseModel):
    queries : List[str]

model = ChatOpenAI(model='gpt-4o', temperature=0)

def plan_node(state:AgentState):
    print(f'[plan node] ... 계획 수립 중')
    response = model.invoke([
        #1. system propmt 정의
        #2. human request 넣기
        SystemMessage(content = PLAN_PROMPT),
        HumanMessage(content = state['task'])       #사용자의 요청, 지시사항을 Agentstate의 plan으로
    ])
    return {'plan':response.content}

#주제에 관련된 내용을 문헌 검색
def research_node(state:AgentState):
    print(f'[research node] ... 리서치 중')
    return run_research(state, state['task'])

#검색된 내용 기반으로 주제 관련 에세이 생성
def generate_node(state:AgentState):
    print(f'[generate node] ... 에세이 생성 중')
    #생성 시도 제한(max_revision, revison_number)
    rev = state.get('revision_number', 1)
    #갖고 있던 content 목록 -> content_str
    content_str = '\n'.join(state.get('content') or [])
    response = model.invoke([
        SystemMessage(content=WRITER_PROMPT.format(content=content_str)),
        HumanMessage(content = f'{state['content']} Here is my Plan {state['plan']}')
    ])
    return {'draft':response.content, 'revision_number': rev+1}

#에세이 비평
def reflection_node(state:AgentState):
    print(f'[reflection node] ... 에세이 비평 중')
    response = model.invoke([
        SystemMessage(content=REFLECTION_PROMPT),
        HumanMessage(content=state['draft'])
    ])
    return {'critique':response.content}

#검색 결과에 대해 평가
def critique_node(state:AgentState):
    print(f'[critique node] ... 검색 결과 평가 중')    
    return run_research(state, state['critique'])       #나온 에세이 평가를 체크 위한 검색을 추가로 실행함.(검증)

def run_research(state:AgentState, user_content):
    #structured_output: 아웃풋 형태 지정(List[str])
    queries_ = model.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_PROMPT),
        HumanMessage(content=user_content)
    ])
    content = list(state.get('content') or [])
    #결과물로 받은 List[str] 형태의 쿼리들을 for문 q로 하나씩 빼옴
    for q in queries_.queries:
        print(f'검색 중... : {q}')
        try:
            result = wiki.invoke({'query': q})
        except Exception as e:
            print(f'검색 실패...')
            continue
        content.append(result)
    return {'content':content}

#내가 state에 갖고 있는 revision_number가 max_revision를 넘으면 끝
#그렇지 않으면 다시 reflect로 이동
def should_continue(state:AgentState):
    if state['revision_number'] >= state['max_revisions']:
        return END
    else: 
        return 'reflect'




def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node('planner', plan_node)
    graph.add_node('researcher', research_node)
    graph.add_node('generator', generate_node)
    graph.add_node('reflect', reflection_node)
    graph.add_node('critique', critique_node)

    #연결
    graph.set_entry_point('planner')
    graph.add_edge('planner', 'researcher')
    graph.add_edge('researcher','generator')
    graph.add_edge('researcher','generator')
    graph.add_conditional_edges('generator', should_continue, {END:END, 'reflect': 'reflect'})

    graph.add_edge('reflect', 'critique')
    graph.add_edge('critique', 'generator')

    memory = MemorySaver()
    return graph.compile(checkpointer=memory)

import wikipedia
wikipedia.set_user_agent('bll3479@gmail.com')

wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(
    top_k_results=2, doc_content_chars_max=1000
))


if __name__ == '__main__':
    graph = build_graph()
    print(graph.get_graph().print_ascii())

    task = input('어떤 주제로 글 쓸까? \n')
    thread_id = {'configurable' : {'thread_id':'essay-1'}}
    #graph에 필요한 값: stream({초기값}, configure)
    for s in graph.stream(
        {'task':task,
        'max_revisions':2,
        'revision_number': 1,
        'content':[]},
        thread_id):
        node_list = list(s.keys())[0]
        print(f'{node_list} 완료')
    final = graph.get_state(thread_id)
    print(final.values['draft'])