# 랭그래프 3요소
# 상태(state): 노드들이 주고 밭는 데이터. typedic로 자료형 고정
# 노드(node): 상태를 받아서 "바뀐 부분만" 딕셔너리로 돌려주는 함수
# 엣지(edge): 노드를 잇는 화살표. 조건부 엣지면 갈림길이 생김

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END


#1. 상태 그래프 생성
#상태(그래프가 흐를 때 같이 가야함) -> 중간에 타입변형이 오면 캐치할 수 있도록
class ShippingState(TypedDict):
    order_id : str
    city : str
    address : str
    weather : str
    decision : str
    reason : str

WEATHER_DB = {
    '서울': '맑음',
    '부산': '비',
    '대구': '눈',
    '광주': '흐림',
    '제주': '비',
}

#2. 노드 생성
#주의: 노드는 반드시 '상태'를 매개변수로 가짐
def check_weather(state:ShippingState):
    weather = WEATHER_DB.get(state['city'], ['맑음'])
    print(f'날씨 체크: {state['city']} -> {weather}')
    return {'weather': weather}             #state의 weather

#날씨로 분기처리
def route_by_weather(state:ShippingState):
    if state['weather'] == '비':
        return 'hold'
    return 'delivery'


def start_delivery(state:ShippingState):

    print(f'{state['address']}로 배달을 시작합니다.')
    return {'decision':'배송 진행', 'reason':f'{state['city']} 지역 날씨가 {state['weather']}이므로 배송 진행'}


def hold_delivery(state:ShippingState):
    print(f'배송 중단합니다.')
    return {'decision':'배송 중단', 'reason':f'{state['city']} 지역 날씨가 {state['weather']}이므로 배송 중단'}


#3. 노드 연결(그래프 빌드)
def bulid_graph():
    workflow = StateGraph(ShippingState)

    workflow.add_node('check_weather', check_weather)
    workflow.add_node('start_delivery', start_delivery)
    workflow.add_node('hold_delivery', hold_delivery)

    #그래프 사이의 지점 연결
    workflow.add_edge(START, 'check_weather')

        #조건부 엣지
        #route_by_weather: 쪼개지는 조건
    workflow.add_conditional_edges('check_weather', route_by_weather, 
                                   {'hold':'hold_delivery',
                                    'delivery': 'start_delivery'})
    workflow.add_edge('hold_delivery', END)
    workflow.add_edge('start_delivery', END)

    return workflow.compile()       #그래프 고정


if __name__ == '__main__':
    #그래프 만들기
    #graph -> 고정시킨 workflow가 생성
    graph = bulid_graph()
    order_id = input('주문번호를 입력하세요')
    city = input('거주지를 입력하세요')
    address = input('상세주소를 입력하세요')
    graph.invoke({'order_id' : order_id, 'city': city, 'address': address})
