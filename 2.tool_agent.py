#Agent가 포함된 랭 그래프

from dotenv import load_dotenv
load_dotenv()

#Annotated[자료형, 누적] : 자료형 데이터가 여기 들어오고 데이터가 새로 들어올 때 누적 할 것.
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END

#에이전트 구성을 위해 필요한 langchain component
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

#검색을 하기 위한 툴(tools)
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_openai import ChatOpenAI

#리스트 합쳐줌[] [] => []/ operator.add
import operator

class AgentState(TypedDict):
    messages : Annotated[list[AnyMessage], operator.add]

#이름만 agent, langgraph로 구현함.
class Agent:
    #langgraph 구현
    def __init__(self, system,tools, model):
        self.system = system       #시스템에 대한 전반적인 답변 매너를 정하는 프롬프트

        #그래프 정의
        graph = StateGraph(AgentState)
        graph.add_node('llm', self.call_openai)     #1. 채팅을 함
        graph.add_node('tool', self.take_action)    #2. 채팅 중 도구 필요하면 쓴다

        graph.add_conditional_edges('llm', self.exist_action, {True : 'tool', False : END})

        graph.add_edge('tool', 'llm')
        graph.set_entry_point('llm')        #START 노드에서 시작하지 않았으므로 시작점이 llm 함수임을 알림
        self.graph = graph.compile()

        self.tools = {t.name : t for t in tools}
        self.model = model.bind_tools(tools)
        
    # 조건 판단 -> tool이 있나 없나
    def exist_action(self, state:AgentState):
        return len(state['messages'][-1].tool_calls) > 0
    
    # 실행(execute)
    def call_openai(self, state:AgentState):
        messages = state['messages']                #통신 기록이 쌓인 채팅 내역
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)       #gpt 통신(invoke하며 이전 채팅 내역을 보여줌)
        return {'messages': [message]}              #통신한 상태를 return
    
    # 도구 실행
    def take_action(self, state:AgentState):
        tool_calls = state['messages'][-1].tool_calls

        results = []
        # t 1개의 개별 도구(함수, API)
        for t in tool_calls:
            print(f"도구 호출: {t['name']} ->{t['args']}")
            if t['name'] not in self.tools:
                result = '존재하지 않는 도구입니다'
            else:
                #self.tools = 함수, api라 .invoke(도구 실행에 필요한 매개변수)
                result = self.tools[t['name']].invoke(t['args'])
            results.append(
                #tool의 id, name, content(툴을 쓴 결과)
                ToolMessage(tool_call_id = t['id'], name=t['name'], content = str(result))
            )
            print(f'모델로 복귀 \n')
            return {'messages':results}

if __name__ == '__main__':
    model = ChatOpenAI(temperature=0.5, model ='gpt-4o')
    system = '''
            당신은 유능한 리서처입니다.
            위키피디아를 이용하여 정보를 검색하세요.
            다중 calls를 실행하는 것도 허용합니다.(순차적, 병렬적 call 가능)
            당신이 원하는 것이 정확히 지정되었을 때만 정보를 검색하세요.
            '''
    tools = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=1000))
    bot = Agent(system, [tools], model)

    question = input('질문해주세요: \n')
    message = HumanMessage(content=question)
    result = bot.graph.invoke({'messages':[message]})
    print(f'{result['messages'][-1].content}')